"""
Document management endpoints
"""
from typing import Any, List
from uuid import UUID
from datetime import datetime, timedelta
from pathlib import Path
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_document import crud_document
from app.db.database import get_db
from app.models.user import User
from app.schemas.document import Document as DocumentSchema, DocumentCreate, DocumentUpdate, DocumentResponse
from app.services.s3_storage import s3_storage
from app.services.cdn_service import cdn_service
from app.services.backup_service import backup_service
from app.services.document_processor import DocumentProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize document processor
document_processor = DocumentProcessor()


@router.get("/", response_model=List[DocumentResponse])
def read_documents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    document_type: str = Query(None, description="Filter by document type"),
    deal_id: UUID = Query(None, description="Filter by deal"),
    status: str = Query(None, description="Filter by status"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve documents for the current user's organization
    """
    documents = crud_document.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        document_type=document_type,
        deal_id=deal_id,
        status=status
    )
    return documents


@router.post("/", response_model=DocumentResponse)
def create_document(
    *,
    db: Session = Depends(get_db),
    document_in: DocumentCreate,
    current_user: User = Depends(deps.check_permission("documents:upload")),
) -> Any:
    """
    Create new document record
    """
    # Add organization and uploader info
    document_data = document_in.dict()
    document_data["organization_id"] = current_user.organization_id
    document_data["uploaded_by_id"] = current_user.id
    
    document = crud_document.create(db=db, obj_in=document_data)
    return document


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(..., description="Document title"),
    document_type: str = Form("general", description="Document type"),
    deal_id: str = Form(None, description="Associated deal ID"),
    client_id: str = Form(None, description="Associated client ID"),
    is_confidential: str = Form("false", description="Is document confidential"),
    current_user: User = Depends(deps.check_permission("documents:upload")),
) -> Any:
    """
    Upload a new document file
    """
    # Validate file type and size
    if file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")
    
    # Convert string form data to appropriate types
    deal_uuid = None
    if deal_id and deal_id.strip():
        try:
            deal_uuid = UUID(deal_id)
        except ValueError:
            pass

    client_uuid = None
    if client_id and client_id.strip():
        try:
            client_uuid = UUID(client_id)
        except ValueError:
            pass

    is_confidential_bool = is_confidential.lower() in ('true', '1', 'yes')

    try:
        # Upload file to S3 with proper organization isolation
        upload_result = await s3_storage.upload_file(
            file=file,
            organization_id=str(current_user.organization_id),
            document_type=document_type,
            is_confidential=is_confidential_bool,
            metadata={
                "title": title,
                "uploaded_by": str(current_user.id),
                "deal_id": str(deal_uuid) if deal_uuid else "",
                "client_id": str(client_uuid) if client_uuid else ""
            }
        )

        # Create document record with S3 information
        document_data = {
            "title": title,
            "filename": file.filename,
            "file_path": upload_result["file_key"],  # S3 object key
            "file_size": upload_result["file_size"],
            "file_type": upload_result["content_type"],
            "file_extension": file.filename.split('.')[-1] if '.' in file.filename else '',
            "document_type": document_type,
            "deal_id": deal_uuid,
            "client_id": client_uuid,
            "is_confidential": is_confidential_bool,
            "organization_id": current_user.organization_id,
            "uploaded_by_id": current_user.id,
            "status": "uploaded"
        }

        document = crud_document.create(db=db, obj_in=document_data)

        # Process document through enhanced pipeline
        try:
            # Reset file pointer for processing
            await file.seek(0)

            processing_result = await document_processor.process_document_pipeline(
                file=file,
                document_id=str(document.id),
                organization_id=str(current_user.organization_id)
            )

            # Update document with processing results
            update_data = {
                "processing_status": "completed",
                "metadata": processing_result.get("metadata", {}),
                "text_analysis": processing_result.get("text_analysis", {}),
                "search_keywords": processing_result.get("search_index", {}).get("keywords", []),
                "thumbnail_path": processing_result.get("thumbnail", {}).get("s3_key"),
                "extracted_text_path": processing_result.get("artifacts", {}).get("extracted_text", {}).get("s3_key"),
                "search_index_path": processing_result.get("artifacts", {}).get("search_index", {}).get("s3_key")
            }

            document = crud_document.update(db=db, db_obj=document, obj_in=update_data)

            logger.info(f"Document {document.id} processed successfully")

        except Exception as e:
            logger.error(f"Document processing failed for {document.id}: {e}")
            # Update document status to indicate processing failure
            crud_document.update(db=db, db_obj=document, obj_in={"processing_status": "failed"})

        # Schedule automatic backup for confidential documents
        if is_confidential_bool:
            try:
                backup_service.backup_file(
                    upload_result["file_key"],
                    metadata={
                        "document_id": str(document.id),
                        "backup_type": "confidential_auto",
                        "organization_id": str(current_user.organization_id)
                    }
                )
            except Exception as backup_error:
                # Log backup error but don't fail the upload
                logger.warning(f"Backup failed for confidential document {document.id}: {backup_error}")

        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail="Document upload failed")


@router.post("/upload-and-analyze", response_model=dict)
async def upload_and_analyze_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    analysis_type: str = Form("full"),
    deal_id: str = Form(None),
    is_confidential: bool = Form(False),
    current_user: User = Depends(deps.check_permission("documents:upload")),
) -> Any:
    """
    Upload a document file and immediately perform AI analysis
    """
    from app.services.integrated_ai_service import integrated_ai_service
    from app.schemas.document_analysis import DocumentAnalysisRequest
    from app.crud.crud_document_analysis import crud_document_analysis

    # Validate file type and size
    if file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    # Convert string form data to appropriate types
    deal_uuid = None
    if deal_id and deal_id.strip():
        try:
            deal_uuid = UUID(deal_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deal_id format")

    try:
        # Read file content
        file_content = await file.read()

        # Create document record first
        document_data = DocumentCreate(
            title=title,
            filename=file.filename,
            file_size=file.size,
            file_extension=Path(file.filename).suffix.lower(),
            document_type=document_type,
            deal_id=deal_uuid,
            is_confidential=is_confidential,
            status="processing"  # Set to processing immediately
        )

        document = crud_document.create_with_organization(
            db=db,
            obj_in=document_data,
            organization_id=current_user.organization_id,
            created_by_id=current_user.id
        )

        # Perform AI analysis with file content
        analysis_request = DocumentAnalysisRequest(
            document_id=document.id,
            analysis_type=analysis_type,
            priority="high"  # High priority for immediate analysis
        )

        # Notify about analysis start
        from app.services.realtime_notifications import realtime_notifications
        await realtime_notifications.notify_document_analysis_started(
            str(document.id), analysis_type, estimated_duration=30
        )

        # Use integrated AI service for analysis
        analysis_result = await integrated_ai_service.analyze_document_with_file(
            analysis_request, file_content, file.filename
        )

        # Notify about analysis completion
        await realtime_notifications.notify_document_analysis_completed(
            str(document.id),
            {
                "overall_risk_score": analysis_result.overall_risk_score,
                "risk_level": analysis_result.risk_level,
                "confidence_score": analysis_result.confidence_score,
                "critical_issues": analysis_result.critical_issues,
                "compliance_flags": analysis_result.compliance_flags,
                "key_findings": analysis_result.key_findings
            },
            float(analysis_result.processing_time)
        )

        # Store analysis results in database (simplified for this endpoint)
        analysis_data = {
            "analysis_type": analysis_type,
            "overall_risk_score": analysis_result.overall_risk_score,
            "confidence_score": analysis_result.confidence_score,
            "risk_level": analysis_result.risk_level,
            "summary": analysis_result.summary,
            "key_findings": analysis_result.key_findings,
            "model_version": analysis_result.model_version,
            "analysis_status": analysis_result.status
        }

        # Update document with analysis summary
        document.ai_analysis = {
            "summary": analysis_result.summary,
            "risk_score": float(analysis_result.overall_risk_score),
            "confidence": float(analysis_result.confidence_score),
            "analysis_date": analysis_result.analysis_date.isoformat()
        }
        document.status = "analyzed" if analysis_result.status == "completed" else "analysis_failed"
        document.risk_score = str(int(float(analysis_result.overall_risk_score)))
        document.key_findings = analysis_result.key_findings
        document.compliance_status = "compliant" if not analysis_result.compliance_flags else "review_required"

        db.add(document)
        db.commit()

        return {
            "message": "Document uploaded and analyzed successfully",
            "document_id": document.id,
            "analysis_id": analysis_result.analysis_id,
            "upload_summary": {
                "filename": file.filename,
                "file_size": file.size,
                "document_type": document_type
            },
            "analysis_summary": {
                "overall_risk_score": analysis_result.overall_risk_score,
                "risk_level": analysis_result.risk_level,
                "confidence_score": analysis_result.confidence_score,
                "critical_issues_count": len(analysis_result.critical_issues),
                "compliance_flags_count": len(analysis_result.compliance_flags),
                "model_version": analysis_result.model_version,
                "processing_time": analysis_result.processing_time
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document upload and analysis failed: {str(e)}"
        )


@router.post("/secure-upload", response_model=dict)
async def secure_upload_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    deal_id: str = Form(None),
    is_confidential: bool = Form(False),
    perform_security_scan: bool = Form(True),
    extract_metadata: bool = Form(True),
    current_user: User = Depends(deps.check_permission("documents:upload")),
) -> Any:
    """
    Secure document upload with comprehensive processing and security scanning
    """
    from app.services.document_processor import document_processor

    # Validate file type and size
    if file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    # Convert string form data to appropriate types
    deal_uuid = None
    if deal_id and deal_id.strip():
        try:
            deal_uuid = UUID(deal_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deal_id format")

    try:
        # Read file content
        file_content = await file.read()

        # Perform security validation if requested
        security_report = None
        if perform_security_scan:
            security_report = document_processor.validate_file_security(file_content, file.filename)

            if not security_report["is_safe"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Security threats detected: {', '.join(security_report['threats_detected'])}"
                )

        # Process document and extract text
        file_info, extracted_text = await document_processor.process_document(file_content, file.filename)

        if not file_info["extraction_successful"]:
            raise HTTPException(
                status_code=400,
                detail=f"Document processing failed: {file_info.get('extraction_error', 'Unknown error')}"
            )

        # Get document statistics
        text_stats = document_processor.get_document_stats(extracted_text)

        # Create document record
        document_data = DocumentCreate(
            title=title,
            filename=file.filename,
            file_size=file.size,
            file_extension=Path(file.filename).suffix.lower(),
            document_type=document_type,
            deal_id=deal_uuid,
            is_confidential=is_confidential,
            status="processed"
        )

        document = crud_document.create_with_organization(
            db=db,
            obj_in=document_data,
            organization_id=current_user.organization_id,
            created_by_id=current_user.id
        )

        # Store processing metadata
        processing_metadata = {
            "file_info": file_info,
            "text_stats": text_stats,
            "security_report": security_report,
            "extracted_text_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        }

        # Update document with processing results
        document.ai_analysis = {
            "processing_metadata": processing_metadata,
            "text_extracted": True,
            "word_count": text_stats.get("word_count", 0),
            "readability_score": text_stats.get("readability_score", 0),
            "processed_at": datetime.utcnow().isoformat()
        }

        db.add(document)
        db.commit()

        return {
            "message": "Document uploaded and processed successfully",
            "document_id": document.id,
            "processing_summary": {
                "filename": file.filename,
                "file_size": file.size,
                "document_type": document_type,
                "text_extracted": file_info["extraction_successful"],
                "word_count": text_stats.get("word_count", 0),
                "readability_score": text_stats.get("readability_score", 0),
                "security_scan_passed": security_report["is_safe"] if security_report else True
            },
            "file_analysis": {
                "mime_type": file_info.get("mime_type"),
                "text_length": file_info.get("text_length", 0),
                "extraction_method": file_info.get("document_type"),
                "complexity": text_stats.get("text_complexity", "unknown")
            },
            "security_report": security_report if perform_security_scan else None,
            "next_steps": [
                "Document is ready for AI analysis",
                "Use /analyze endpoint to perform risk assessment",
                "Review extracted content in document details"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        # Clean up document if processing fails
        if 'document' in locals():
            document.status = "processing_failed"
            db.add(document)
            db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )


@router.post("/batch-upload", response_model=dict)
async def batch_upload_documents(
    *,
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(...),
    deal_id: str = Form(None),
    document_type: str = Form("general"),
    is_confidential: bool = Form(False),
    auto_analyze: bool = Form(False),
    current_user: User = Depends(deps.check_permission("documents:upload")),
) -> Any:
    """
    Upload multiple documents in batch with processing
    """
    from app.services.document_processor import document_processor
    from app.services.integrated_ai_service import integrated_ai_service
    from app.schemas.document_analysis import DocumentAnalysisRequest

    if len(files) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch upload")

    # Convert deal_id if provided
    deal_uuid = None
    if deal_id and deal_id.strip():
        try:
            deal_uuid = UUID(deal_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deal_id format")

    results = []
    successful_uploads = 0
    failed_uploads = 0

    for file in files:
        try:
            # Validate individual file
            if file.size > 50 * 1024 * 1024:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "File too large (max 50MB)"
                })
                failed_uploads += 1
                continue

            # Read and process file
            file_content = await file.read()

            # Security scan
            security_report = document_processor.validate_file_security(file_content, file.filename)
            if not security_report["is_safe"]:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": f"Security threats: {', '.join(security_report['threats_detected'])}"
                })
                failed_uploads += 1
                continue

            # Process document
            file_info, extracted_text = await document_processor.process_document(file_content, file.filename)

            if not file_info["extraction_successful"]:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": f"Text extraction failed: {file_info.get('extraction_error', 'Unknown error')}"
                })
                failed_uploads += 1
                continue

            # Create document record
            document_data = DocumentCreate(
                title=file.filename,
                filename=file.filename,
                file_size=file.size,
                file_extension=Path(file.filename).suffix.lower(),
                document_type=document_type,
                deal_id=deal_uuid,
                is_confidential=is_confidential,
                status="processed"
            )

            document = crud_document.create_with_organization(
                db=db,
                obj_in=document_data,
                organization_id=current_user.organization_id,
                created_by_id=current_user.id
            )

            # Perform AI analysis if requested
            analysis_summary = None
            if auto_analyze:
                try:
                    analysis_request = DocumentAnalysisRequest(
                        document_id=document.id,
                        analysis_type="full",
                        priority="medium"
                    )

                    analysis_result = await integrated_ai_service.analyze_document_with_file(
                        analysis_request, file_content, file.filename
                    )

                    analysis_summary = {
                        "risk_score": float(analysis_result.overall_risk_score),
                        "risk_level": analysis_result.risk_level,
                        "confidence": float(analysis_result.confidence_score)
                    }

                    # Update document status
                    document.status = "analyzed"
                    document.risk_score = str(int(float(analysis_result.overall_risk_score)))

                except Exception as e:
                    logger.warning(f"Auto-analysis failed for {file.filename}: {str(e)}")
                    analysis_summary = {"error": str(e)}

            db.add(document)
            db.commit()

            results.append({
                "filename": file.filename,
                "status": "success",
                "document_id": str(document.id),
                "file_size": file.size,
                "word_count": file_info.get("word_count", 0),
                "analysis_summary": analysis_summary
            })
            successful_uploads += 1

        except Exception as e:
            logger.error(f"Batch upload failed for {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
            failed_uploads += 1

    return {
        "message": f"Batch upload completed: {successful_uploads} successful, {failed_uploads} failed",
        "summary": {
            "total_files": len(files),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "auto_analysis_enabled": auto_analyze
        },
        "results": results,
        "next_steps": [
            "Review individual file results",
            "Analyze uploaded documents if not done automatically",
            "Check failed uploads and retry if needed"
        ]
    }


@router.get("/processing/status", response_model=dict)
def get_processing_status(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get document processing status and capabilities
    """
    from app.services.document_processor import document_processor

    # Get document counts by status
    doc_query = db.query(crud_document.model).filter(
        crud_document.model.organization_id == current_user.organization_id
    )

    status_counts = {}
    total_documents = 0

    for status in ["uploaded", "processing", "processed", "analyzed", "failed"]:
        count = doc_query.filter(crud_document.model.status == status).count()
        status_counts[status] = count
        total_documents += count

    # Get processing capabilities
    supported_formats = list(document_processor.SUPPORTED_FORMATS.keys())

    return {
        "processing_status": {
            "total_documents": total_documents,
            "status_breakdown": status_counts,
            "processing_queue_size": status_counts.get("processing", 0)
        },
        "capabilities": {
            "supported_formats": supported_formats,
            "max_file_size": "50MB",
            "ocr_enabled": True,
            "security_scanning": True,
            "batch_processing": True,
            "auto_analysis": True
        },
        "processing_features": {
            "text_extraction": {
                "pdf": "Advanced with metadata extraction",
                "docx": "Full document structure",
                "xlsx": "Data and formulas",
                "pptx": "Slides and content",
                "images": "OCR with preprocessing"
            },
            "security_features": [
                "File signature validation",
                "Malware pattern detection",
                "Size limit enforcement",
                "Content structure analysis"
            ],
            "analysis_features": [
                "Document statistics",
                "Readability scoring",
                "Content complexity analysis",
                "Metadata extraction"
            ]
        },
        "recent_activity": {
            "last_24_hours": {
                "uploads": doc_query.filter(
                    crud_document.model.created_at >= datetime.utcnow() - timedelta(days=1)
                ).count(),
                "processed": doc_query.filter(
                    crud_document.model.status.in_(["processed", "analyzed"]),
                    crud_document.model.updated_at >= datetime.utcnow() - timedelta(days=1)
                ).count()
            }
        }
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def read_document(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get document by ID
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check confidentiality access
    if document.is_confidential and current_user.role not in ["admin", "manager", "vp"]:
        raise HTTPException(status_code=403, detail="Access denied to confidential document")
    
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    document_in: DocumentUpdate,
    current_user: User = Depends(deps.check_permission("documents:edit")),
) -> Any:
    """
    Update document
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    document = crud_document.update(db=db, db_obj=document, obj_in=document_in)
    return document


@router.delete("/{document_id}")
def delete_document(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    current_user: User = Depends(deps.check_permission("documents:delete")),
) -> Any:
    """
    Delete document
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete file from S3 if it exists
    try:
        if document.file_path and not document.file_path.startswith("/uploads/"):
            # This is an S3 key, delete from S3
            s3_storage.delete_file(document.file_path)
    except Exception as e:
        logger.warning(f"Failed to delete S3 file for document {document_id}: {e}")

    document = crud_document.remove(db=db, id=document_id)
    return {"message": "Document deleted successfully"}


@router.get("/{document_id}/download")
async def download_document(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    use_cdn: bool = Query(True, description="Use CDN for download"),
    expiration_hours: int = Query(24, description="URL expiration in hours"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download document with CDN support and secure URLs
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Update download count
        crud_document.increment_download_count(db, document_id)

        # Generate secure download URL
        if use_cdn and cdn_service.is_enabled():
            # Use CDN with signed URL for secure access
            download_url = cdn_service.generate_signed_url(
                document.file_path,
                expiration_hours=expiration_hours
            )
        else:
            # Use S3 presigned URL
            download_url = s3_storage.generate_presigned_url(
                document.file_path,
                expiration=expiration_hours * 3600  # Convert to seconds
            )

        # Get file metadata
        file_metadata = s3_storage.get_file_metadata(document.file_path)

        return {
            "download_url": download_url,
            "filename": document.filename,
            "file_size": document.file_size,
            "content_type": document.file_type,
            "expires_in_hours": expiration_hours,
            "cdn_enabled": use_cdn and cdn_service.is_enabled(),
            "metadata": {
                "title": document.title,
                "document_type": document.document_type,
                "is_confidential": document.is_confidential,
                "last_modified": file_metadata.get("last_modified"),
                "download_count": document.download_count + 1
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Download preparation failed")


@router.post("/{document_id}/analyze")
async def analyze_document(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    analysis_type: str = "full",
    priority: str = "medium",
    current_user: User = Depends(deps.check_permission("documents:analyze")),
) -> Any:
    """
    Trigger comprehensive AI analysis of document using real AI integration
    """
    from app.services.integrated_ai_service import integrated_ai_service
    from app.schemas.document_analysis import DocumentAnalysisRequest
    from app.crud.crud_document_analysis import crud_document_analysis

    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update document status to processing
    document.status = "processing"
    db.add(document)
    db.commit()

    try:
        # Prepare document information for AI analysis
        document_info = {
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "file_size": document.file_size,
            "file_extension": document.file_extension,
            "document_type": document.document_type,
            "is_confidential": document.is_confidential,
            "created_at": document.created_at,
            "content": ""  # Would be loaded from file storage in production
        }

        # Create analysis request
        analysis_request = DocumentAnalysisRequest(
            document_id=document_id,
            analysis_type=analysis_type,
            priority=priority
        )

        # Perform AI analysis using integrated service
        analysis_result = await integrated_ai_service.analyze_document(analysis_request, document_info)

        # Store analysis results in database
        analysis_data = {
            "analysis_type": analysis_type,
            "overall_risk_score": analysis_result.overall_risk_score,
            "confidence_score": analysis_result.confidence_score,
            "risk_level": analysis_result.risk_level,
            "summary": analysis_result.summary,
            "key_findings": analysis_result.key_findings,
            "extracted_entities": analysis_result.extracted_entities,
            "financial_figures": [fig.dict() for fig in analysis_result.financial_figures],
            "key_dates": [date.dict() for date in analysis_result.key_dates],
            "parties_involved": analysis_result.parties_involved,
            "risk_categories": [cat.dict() for cat in analysis_result.risk_categories],
            "critical_issues": [issue.dict() for issue in analysis_result.critical_issues],
            "anomalies": [anomaly.dict() for anomaly in analysis_result.anomalies],
            "compliance_flags": [flag.dict() for flag in analysis_result.compliance_flags],
            "document_quality_score": analysis_result.document_quality_score,
            "completeness_score": analysis_result.completeness_score,
            "processing_time_seconds": analysis_result.processing_time,
            "model_version": analysis_result.model_version,
            "analysis_status": "completed"
        }

        # Store detailed analysis
        crud_document_analysis.create_analysis(
            db=db,
            document_id=document_id,
            analysis_type=analysis_type,
            analysis_results=analysis_data,
            organization_id=current_user.organization_id,
            created_by_id=current_user.id
        )

        # Update document with analysis summary
        document.ai_analysis = {
            "summary": analysis_result.summary,
            "risk_score": float(analysis_result.overall_risk_score),
            "confidence": float(analysis_result.confidence_score),
            "analysis_date": analysis_result.analysis_date.isoformat()
        }
        document.status = "analyzed"
        document.risk_score = str(int(float(analysis_result.overall_risk_score)))
        document.key_findings = analysis_result.key_findings
        document.compliance_status = "compliant" if not analysis_result.compliance_flags else "review_required"

        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "message": "Document analysis completed successfully",
            "analysis_id": analysis_result.analysis_id,
            "analysis_summary": {
                "overall_risk_score": analysis_result.overall_risk_score,
                "risk_level": analysis_result.risk_level,
                "confidence_score": analysis_result.confidence_score,
                "critical_issues_count": len(analysis_result.critical_issues),
                "compliance_flags_count": len(analysis_result.compliance_flags)
            }
        }

    except Exception as e:
        # Update document status to failed
        document.status = "analysis_failed"
        db.add(document)
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {str(e)}"
        )


@router.get("/{document_id}/analysis", response_model=dict)
def get_document_analysis(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    analysis_type: str = Query(None, description="Filter by analysis type"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI analysis results for a document
    """
    from app.crud.crud_document_analysis import crud_document_analysis

    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Get analysis results
    if analysis_type:
        analysis = crud_document_analysis.get_latest_analysis(
            db=db, document_id=document_id, analysis_type=analysis_type
        )
    else:
        analyses = crud_document_analysis.get_by_document(db=db, document_id=document_id)
        analysis = analyses[0] if analyses else None

    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for this document")

    return {
        "analysis_id": analysis.id,
        "document_id": analysis.document_id,
        "analysis_type": analysis.analysis_type,
        "analysis_date": analysis.analysis_date,
        "overall_risk_score": analysis.overall_risk_score,
        "confidence_score": analysis.confidence_score,
        "risk_level": analysis.risk_level,
        "summary": analysis.summary,
        "key_findings": analysis.key_findings,
        "extracted_entities": analysis.extracted_entities,
        "financial_figures": analysis.financial_figures,
        "key_dates": analysis.key_dates,
        "parties_involved": analysis.parties_involved,
        "risk_categories": analysis.risk_categories,
        "critical_issues": analysis.critical_issues,
        "anomalies": analysis.anomalies,
        "compliance_flags": analysis.compliance_flags,
        "document_quality_score": analysis.document_quality_score,
        "completeness_score": analysis.completeness_score,
        "processing_time": analysis.processing_time_seconds
    }


@router.post("/risk-assessment", response_model=dict)
async def create_risk_assessment(
    *,
    db: Session = Depends(get_db),
    assessment_name: str,
    assessment_type: str = "deal",
    deal_id: UUID = None,
    document_ids: List[UUID] = [],
    current_user: User = Depends(deps.check_permission("documents:analyze")),
) -> Any:
    """
    Create comprehensive risk assessment for multiple documents
    """
    from app.services.integrated_ai_service import integrated_ai_service
    from app.schemas.document_analysis import RiskAssessmentRequest
    from app.crud.crud_document_analysis import crud_risk_assessment

    # Validate document access
    documents_info = []
    for doc_id in document_ids:
        document = crud_document.get(db=db, id=doc_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

        if document.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        documents_info.append({
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "file_size": document.file_size,
            "file_extension": document.file_extension,
            "document_type": document.document_type,
            "is_confidential": document.is_confidential,
            "created_at": document.created_at
        })

    # Create assessment request
    assessment_request = RiskAssessmentRequest(
        assessment_name=assessment_name,
        assessment_type=assessment_type,
        deal_id=deal_id,
        document_ids=document_ids
    )

    try:
        # Perform risk assessment using integrated service
        assessment_result = await integrated_ai_service.assess_risk(assessment_request, documents_info)

        # Store assessment results
        assessment_data = {
            "assessment_name": assessment_name,
            "assessment_type": assessment_type,
            "deal_id": deal_id,
            "document_ids": document_ids,
            "overall_risk_score": assessment_result.overall_risk_score,
            "risk_level": assessment_result.risk_level,
            "confidence_level": assessment_result.confidence_level,
            "risk_categories": [cat.dict() for cat in assessment_result.risk_categories],
            "critical_issues": [issue.dict() for issue in assessment_result.critical_issues],
            "missing_documents": [doc.dict() for doc in assessment_result.missing_documents],
            "compliance_status": assessment_result.compliance_status,
            "assessment_completeness": assessment_result.assessment_completeness,
            "data_quality_score": assessment_result.data_quality_score
        }

        assessment = crud_risk_assessment.create_assessment(
            db=db,
            assessment_data=assessment_data,
            organization_id=current_user.organization_id,
            created_by_id=current_user.id
        )

        return {
            "message": "Risk assessment completed successfully",
            "assessment_id": assessment.id,
            "assessment_summary": {
                "overall_risk_score": assessment_result.overall_risk_score,
                "risk_level": assessment_result.risk_level,
                "confidence_level": assessment_result.confidence_level,
                "critical_issues_count": len(assessment_result.critical_issues),
                "missing_documents_count": len(assessment_result.missing_documents),
                "documents_analyzed": len(document_ids)
            },
            "recommendations": assessment_result.recommendations[:3]  # Top 3 recommendations
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk assessment failed: {str(e)}"
        )


@router.get("/risk-assessments", response_model=List[dict])
def get_risk_assessments(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    assessment_type: str = Query(None, description="Filter by assessment type"),
    risk_level: str = Query(None, description="Filter by risk level"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get risk assessments for the organization
    """
    from app.crud.crud_document_analysis import crud_risk_assessment

    assessments = crud_risk_assessment.get_by_organization(
        db=db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        assessment_type=assessment_type,
        risk_level=risk_level
    )

    return [
        {
            "assessment_id": assessment.id,
            "assessment_name": assessment.assessment_name,
            "assessment_type": assessment.assessment_type,
            "assessment_date": assessment.assessment_date,
            "overall_risk_score": assessment.overall_risk_score,
            "risk_level": assessment.risk_level,
            "confidence_level": assessment.confidence_level,
            "deal_id": assessment.deal_id,
            "document_count": len(assessment.document_ids) if assessment.document_ids else 0,
            "critical_issues_count": len(assessment.critical_issues) if assessment.critical_issues else 0
        }
        for assessment in assessments
    ]


@router.get("/{document_id}/categorize", response_model=dict)
async def categorize_document(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Automatically categorize document using AI
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Simple categorization based on document metadata
    filename = document.filename.lower()
    title = document.title.lower()
    doc_type = (document.document_type or "").lower()

    text_to_analyze = f"{filename} {title} {doc_type}"

    # Category scoring
    categories = {
        "financial": ["financial", "audit", "statement", "budget", "forecast", "revenue", "income"],
        "legal": ["contract", "agreement", "legal", "terms", "conditions", "compliance", "law"],
        "operational": ["operational", "process", "procedure", "manual", "workflow", "operations"],
        "marketing": ["marketing", "sales", "presentation", "pitch", "proposal", "campaign"],
        "hr": ["employee", "hr", "human resources", "personnel", "payroll", "benefits"],
        "technical": ["technical", "specification", "architecture", "design", "development", "system"]
    }

    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text_to_analyze)
        if score > 0:
            category_scores[category] = score

    if category_scores:
        predicted_category = max(category_scores, key=category_scores.get)
        confidence = min(category_scores[predicted_category] * 20, 95)  # Scale to percentage

        # Get alternative categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [
            {"category": cat, "confidence": min(score * 15, 85)}
            for cat, score in sorted_categories[1:3]
        ]
    else:
        predicted_category = "general"
        confidence = 60
        alternatives = []

    return {
        "document_id": document_id,
        "predicted_category": predicted_category,
        "confidence": confidence,
        "alternative_categories": alternatives,
        "reasoning": f"Categorized based on filename and title analysis",
        "keywords_matched": [kw for kw in categories.get(predicted_category, []) if kw in text_to_analyze]
    }


@router.get("/analytics/statistics", response_model=dict)
def get_document_analytics(
    *,
    db: Session = Depends(get_db),
    date_from: datetime = Query(None, description="Start date for analytics"),
    date_to: datetime = Query(None, description="End date for analytics"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get document analytics and statistics
    """
    from app.crud.crud_document_analysis import crud_document_analysis

    # Get analysis statistics
    analysis_stats = crud_document_analysis.get_analysis_statistics(
        db=db,
        organization_id=current_user.organization_id,
        date_from=date_from,
        date_to=date_to
    )

    # Get document statistics
    doc_query = db.query(crud_document.model).filter(
        crud_document.model.organization_id == current_user.organization_id
    )

    if date_from:
        doc_query = doc_query.filter(crud_document.model.created_at >= date_from)
    if date_to:
        doc_query = doc_query.filter(crud_document.model.created_at <= date_to)

    documents = doc_query.all()

    # Calculate document statistics
    total_documents = len(documents)
    analyzed_documents = len([d for d in documents if d.status == "analyzed"])
    pending_analysis = len([d for d in documents if d.status in ["uploaded", "processing"]])

    # Document type distribution
    doc_type_dist = {}
    status_dist = {}

    for doc in documents:
        doc_type = doc.document_type or "unknown"
        doc_type_dist[doc_type] = doc_type_dist.get(doc_type, 0) + 1

        status = doc.status or "unknown"
        status_dist[status] = status_dist.get(status, 0) + 1

    return {
        "document_statistics": {
            "total_documents": total_documents,
            "analyzed_documents": analyzed_documents,
            "pending_analysis": pending_analysis,
            "analysis_completion_rate": (analyzed_documents / total_documents * 100) if total_documents > 0 else 0,
            "document_type_distribution": doc_type_dist,
            "status_distribution": status_dist
        },
        "analysis_statistics": analysis_stats,
        "period": {
            "from": date_from.isoformat() if date_from else None,
            "to": date_to.isoformat() if date_to else None
        }
    }


@router.get("/high-risk", response_model=List[dict])
def get_high_risk_documents(
    *,
    db: Session = Depends(get_db),
    risk_threshold: float = Query(70.0, ge=0, le=100, description="Risk score threshold"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get high-risk documents requiring attention
    """
    from app.crud.crud_document_analysis import crud_document_analysis

    high_risk_analyses = crud_document_analysis.get_high_risk_analyses(
        db=db,
        organization_id=current_user.organization_id,
        risk_threshold=risk_threshold,
        limit=limit
    )

    results = []
    for analysis in high_risk_analyses:
        document = crud_document.get(db=db, id=analysis.document_id)
        if document:
            results.append({
                "document_id": document.id,
                "document_title": document.title,
                "document_type": document.document_type,
                "risk_score": analysis.overall_risk_score,
                "risk_level": analysis.risk_level,
                "confidence_score": analysis.confidence_score,
                "analysis_date": analysis.analysis_date,
                "critical_issues_count": len(analysis.critical_issues) if analysis.critical_issues else 0,
                "compliance_flags_count": len(analysis.compliance_flags) if analysis.compliance_flags else 0,
                "summary": analysis.summary
            })

    return results


@router.post("/{document_id}/backup")
async def backup_document(
    *,
    db: Session = Depends(get_db),
    document_id: UUID,
    current_user: User = Depends(deps.check_permission("documents:backup")),
) -> Any:
    """
    Create manual backup of a document
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if user has access to this document's organization
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        backup_result = backup_service.backup_file(
            document.file_path,
            metadata={
                "document_id": str(document.id),
                "document_title": document.title,
                "backup_type": "manual",
                "requested_by": str(current_user.id),
                "organization_id": str(current_user.organization_id)
            }
        )

        return {
            "message": "Document backed up successfully",
            "backup_details": backup_result
        }

    except Exception as e:
        logger.error(f"Manual backup failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Backup failed")


@router.post("/backup/organization")
async def backup_organization_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("documents:backup")),
) -> Any:
    """
    Create backup of all organization documents
    """
    try:
        backup_result = backup_service.schedule_automated_backup(
            str(current_user.organization_id)
        )

        return {
            "message": "Organization backup completed successfully",
            "backup_details": backup_result
        }

    except Exception as e:
        logger.error(f"Organization backup failed for {current_user.organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Organization backup failed")


@router.get("/backup/status")
async def get_backup_status(
    *,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get backup status and statistics
    """
    try:
        backup_status = backup_service.get_backup_status(
            organization_id=str(current_user.organization_id)
        )

        return backup_status

    except Exception as e:
        logger.error(f"Failed to get backup status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get backup status")


@router.get("/cdn/status")
async def get_cdn_status(
    *,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get CDN status and configuration
    """
    try:
        if not cdn_service.is_enabled():
            return {
                "cdn_enabled": False,
                "message": "CDN not configured"
            }

        # Get distribution config
        distribution_config = cdn_service.get_distribution_config()

        # Get cache statistics for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)

        try:
            cache_stats = cdn_service.get_cache_statistics(start_time, end_time)
        except Exception:
            cache_stats = {"error": "Unable to retrieve cache statistics"}

        return {
            "cdn_enabled": True,
            "distribution_config": distribution_config,
            "cache_statistics": cache_stats,
            "edge_locations": cdn_service.get_edge_locations()
        }

    except Exception as e:
        logger.error(f"Failed to get CDN status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get CDN status")


@router.get("/{document_id}/processing-status")
async def get_document_processing_status(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("documents:read")),
) -> Any:
    """
    Get document processing status and results
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check organization access
    if document.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    processing_info = {
        "document_id": str(document.id),
        "processing_status": document.processing_status,
        "metadata": document.metadata or {},
        "text_analysis": document.text_analysis or {},
        "search_keywords": document.search_keywords or [],
        "artifacts": {
            "thumbnail": {
                "available": bool(document.thumbnail_path),
                "path": document.thumbnail_path
            },
            "extracted_text": {
                "available": bool(document.extracted_text_path),
                "path": document.extracted_text_path
            },
            "search_index": {
                "available": bool(document.search_index_path),
                "path": document.search_index_path
            }
        }
    }

    return {"message": "Processing status retrieved", "data": processing_info}


@router.get("/{document_id}/thumbnail")
async def get_document_thumbnail(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("documents:read")),
) -> Any:
    """
    Get document thumbnail URL
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check organization access
    if document.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not document.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not available")

    try:
        # Generate presigned URL for thumbnail
        thumbnail_url = s3_storage.generate_presigned_url(
            document.thumbnail_path,
            expiration=3600  # 1 hour
        )

        return {
            "message": "Thumbnail URL generated",
            "thumbnail_url": thumbnail_url,
            "expires_in": 3600
        }

    except Exception as e:
        logger.error(f"Failed to generate thumbnail URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate thumbnail URL")


@router.get("/{document_id}/extracted-text")
async def get_document_extracted_text(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("documents:read")),
) -> Any:
    """
    Get extracted text content from document
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check organization access
    if document.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not document.extracted_text_path:
        raise HTTPException(status_code=404, detail="Extracted text not available")

    try:
        # Download extracted text from S3
        text_content = s3_storage.download_file_content(document.extracted_text_path)

        return {
            "message": "Extracted text retrieved",
            "text_content": text_content.decode('utf-8'),
            "character_count": len(text_content),
            "word_count": len(text_content.decode('utf-8').split())
        }

    except Exception as e:
        logger.error(f"Failed to retrieve extracted text: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve extracted text")


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("documents:upload")),
) -> Any:
    """
    Reprocess document through the processing pipeline
    """
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check organization access
    if document.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # Update processing status
        crud_document.update(db=db, db_obj=document, obj_in={"processing_status": "processing"})

        # Download original file from S3
        file_content = s3_storage.download_file_content(document.file_path)

        # Create a mock UploadFile object for processing
        from io import BytesIO
        from fastapi import UploadFile

        file_obj = UploadFile(
            file=BytesIO(file_content),
            filename=document.filename,
            headers={"content-type": document.file_type}
        )

        # Process through pipeline
        processing_result = await document_processor.process_document_pipeline(
            file=file_obj,
            document_id=str(document.id),
            organization_id=str(current_user.organization_id)
        )

        # Update document with new processing results
        update_data = {
            "processing_status": "completed",
            "metadata": processing_result.get("metadata", {}),
            "text_analysis": processing_result.get("text_analysis", {}),
            "search_keywords": processing_result.get("search_index", {}).get("keywords", []),
            "thumbnail_path": processing_result.get("thumbnail", {}).get("s3_key"),
            "extracted_text_path": processing_result.get("artifacts", {}).get("extracted_text", {}).get("s3_key"),
            "search_index_path": processing_result.get("artifacts", {}).get("search_index", {}).get("s3_key")
        }

        document = crud_document.update(db=db, db_obj=document, obj_in=update_data)

        return {
            "message": "Document reprocessed successfully",
            "processing_result": processing_result
        }

    except Exception as e:
        logger.error(f"Document reprocessing failed: {e}")
        # Update status to failed
        crud_document.update(db=db, db_obj=document, obj_in={"processing_status": "failed"})
        raise HTTPException(status_code=500, detail="Document reprocessing failed")


@router.get("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    search_type: str = Query("content", description="Search type: content, metadata, keywords"),
    document_type: str = Query(None, description="Filter by document type"),
    date_from: datetime = Query(None, description="Filter from date"),
    date_to: datetime = Query(None, description="Filter to date"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search documents using processing pipeline data
    """
    try:
        # Base query for organization documents
        doc_query = db.query(crud_document.model).filter(
            crud_document.model.organization_id == current_user.organization_id
        )

        # Apply filters
        if document_type:
            doc_query = doc_query.filter(crud_document.model.document_type == document_type)

        if date_from:
            doc_query = doc_query.filter(crud_document.model.created_at >= date_from)

        if date_to:
            doc_query = doc_query.filter(crud_document.model.created_at <= date_to)

        # Search based on type
        search_results = []
        query_lower = query.lower()

        if search_type == "content":
            # Search in extracted text (would require full-text search in production)
            documents = doc_query.filter(
                crud_document.model.extracted_text_path.isnot(None)
            ).all()

            for doc in documents:
                # Simple text matching (in production, use full-text search)
                if (query_lower in doc.title.lower() or
                    query_lower in doc.filename.lower() or
                    (doc.metadata and any(query_lower in str(v).lower() for v in doc.metadata.values()))):

                    search_results.append({
                        "document": doc,
                        "match_type": "content",
                        "relevance_score": 0.8
                    })

        elif search_type == "keywords":
            # Search in extracted keywords
            documents = doc_query.filter(
                crud_document.model.search_keywords.isnot(None)
            ).all()

            for doc in documents:
                if doc.search_keywords:
                    keyword_matches = [kw for kw in doc.search_keywords if query_lower in kw.lower()]
                    if keyword_matches:
                        search_results.append({
                            "document": doc,
                            "match_type": "keywords",
                            "matched_keywords": keyword_matches,
                            "relevance_score": min(len(keyword_matches) * 0.2, 1.0)
                        })

        elif search_type == "metadata":
            # Search in document metadata
            documents = doc_query.filter(
                crud_document.model.metadata.isnot(None)
            ).all()

            for doc in documents:
                if doc.metadata:
                    metadata_matches = []
                    for key, value in doc.metadata.items():
                        if query_lower in str(value).lower():
                            metadata_matches.append(f"{key}: {value}")

                    if metadata_matches:
                        search_results.append({
                            "document": doc,
                            "match_type": "metadata",
                            "matched_metadata": metadata_matches,
                            "relevance_score": min(len(metadata_matches) * 0.3, 1.0)
                        })

        else:
            # Combined search across all types
            documents = doc_query.all()

            for doc in documents:
                matches = []
                score = 0.0

                # Title and filename matching
                if query_lower in doc.title.lower():
                    matches.append("title")
                    score += 0.4

                if query_lower in doc.filename.lower():
                    matches.append("filename")
                    score += 0.3

                # Keyword matching
                if doc.search_keywords:
                    keyword_matches = [kw for kw in doc.search_keywords if query_lower in kw.lower()]
                    if keyword_matches:
                        matches.append("keywords")
                        score += min(len(keyword_matches) * 0.1, 0.3)

                # Metadata matching
                if doc.metadata:
                    for value in doc.metadata.values():
                        if query_lower in str(value).lower():
                            matches.append("metadata")
                            score += 0.2
                            break

                if matches:
                    search_results.append({
                        "document": doc,
                        "match_type": "combined",
                        "match_areas": matches,
                        "relevance_score": min(score, 1.0)
                    })

        # Sort by relevance score and limit results
        search_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        search_results = search_results[:limit]

        # Format response
        formatted_results = []
        for result in search_results:
            doc = result["document"]
            formatted_result = {
                "document_id": str(doc.id),
                "title": doc.title,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "file_size": doc.file_size,
                "created_at": doc.created_at,
                "processing_status": doc.processing_status,
                "match_type": result["match_type"],
                "relevance_score": result["relevance_score"],
                "thumbnail_available": bool(doc.thumbnail_path),
                "text_analysis_available": bool(doc.text_analysis)
            }

            # Add match-specific data
            if "matched_keywords" in result:
                formatted_result["matched_keywords"] = result["matched_keywords"]

            if "matched_metadata" in result:
                formatted_result["matched_metadata"] = result["matched_metadata"]

            if "match_areas" in result:
                formatted_result["match_areas"] = result["match_areas"]

            formatted_results.append(formatted_result)

        return {
            "message": "Search completed",
            "query": query,
            "search_type": search_type,
            "total_results": len(formatted_results),
            "results": formatted_results,
            "search_metadata": {
                "execution_time_ms": 50,  # Placeholder
                "filters_applied": {
                    "document_type": document_type,
                    "date_from": date_from.isoformat() if date_from else None,
                    "date_to": date_to.isoformat() if date_to else None
                }
            }
        }

    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail="Document search failed")


@router.get("/processing/analytics")
async def get_processing_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get processing analytics and insights for the organization
    """
    try:
        # Get document processing statistics
        doc_query = db.query(crud_document.model).filter(
            crud_document.model.organization_id == current_user.organization_id
        )

        total_documents = doc_query.count()

        # Processing status breakdown
        status_counts = {}
        for status in ["pending", "processing", "completed", "failed"]:
            count = doc_query.filter(crud_document.model.processing_status == status).count()
            status_counts[status] = count

        # Document type analysis
        type_analysis = {}
        documents_with_analysis = doc_query.filter(
            crud_document.model.text_analysis.isnot(None)
        ).all()

        for doc in documents_with_analysis:
            doc_type = doc.document_type or "unknown"
            if doc_type not in type_analysis:
                type_analysis[doc_type] = {
                    "count": 0,
                    "avg_word_count": 0,
                    "avg_readability": 0,
                    "total_entities": 0
                }

            type_analysis[doc_type]["count"] += 1

            if doc.text_analysis:
                word_count = doc.text_analysis.get("word_count", 0)
                readability = doc.text_analysis.get("readability_score", 0)
                entities = len(doc.text_analysis.get("entities", []))

                type_analysis[doc_type]["avg_word_count"] += word_count
                type_analysis[doc_type]["avg_readability"] += readability
                type_analysis[doc_type]["total_entities"] += entities

        # Calculate averages
        for doc_type, stats in type_analysis.items():
            if stats["count"] > 0:
                stats["avg_word_count"] = stats["avg_word_count"] // stats["count"]
                stats["avg_readability"] = stats["avg_readability"] / stats["count"]
                stats["avg_entities_per_doc"] = stats["total_entities"] / stats["count"]

        # Processing performance metrics
        recent_docs = doc_query.filter(
            crud_document.model.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all()

        processing_times = []
        success_rate = 0

        for doc in recent_docs:
            if doc.processing_status == "completed":
                success_rate += 1
                # Estimate processing time (would be tracked in production)
                processing_times.append(2.5)  # Placeholder

        success_rate = (success_rate / len(recent_docs) * 100) if recent_docs else 0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

        return {
            "message": "Processing analytics retrieved",
            "analytics": {
                "overview": {
                    "total_documents": total_documents,
                    "processing_status_breakdown": status_counts,
                    "success_rate_7_days": round(success_rate, 2),
                    "avg_processing_time_seconds": round(avg_processing_time, 2)
                },
                "document_type_analysis": type_analysis,
                "processing_capabilities": {
                    "thumbnail_generation": {
                        "enabled": True,
                        "supported_formats": ["pdf", "jpg", "png", "gif", "bmp"]
                    },
                    "text_extraction": {
                        "enabled": True,
                        "supported_formats": ["pdf", "docx", "xlsx", "pptx", "txt"]
                    },
                    "nlp_analysis": {
                        "enabled": True,
                        "features": ["entity_extraction", "readability_analysis", "keyword_extraction"]
                    },
                    "virus_scanning": {
                        "enabled": True,
                        "pattern_detection": True
                    }
                },
                "storage_metrics": {
                    "total_artifacts": sum(1 for doc in documents_with_analysis if doc.thumbnail_path),
                    "thumbnails_generated": sum(1 for doc in documents_with_analysis if doc.thumbnail_path),
                    "text_extractions": sum(1 for doc in documents_with_analysis if doc.extracted_text_path),
                    "search_indices": sum(1 for doc in documents_with_analysis if doc.search_index_path)
                }
            }
        }

    except Exception as e:
        logger.error(f"Failed to get processing analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing analytics")


@router.post("/cdn/invalidate")
async def invalidate_cdn_cache(
    *,
    file_keys: List[str],
    current_user: User = Depends(deps.check_permission("documents:admin")),
) -> Any:
    """
    Invalidate CDN cache for specific files
    """
    try:
        if not cdn_service.is_enabled():
            raise HTTPException(status_code=400, detail="CDN not configured")

        invalidation_result = cdn_service.invalidate_cache(file_keys)

        return {
            "message": "Cache invalidation initiated",
            "invalidation_details": invalidation_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CDN cache invalidation failed: {e}")
        raise HTTPException(status_code=500, detail="Cache invalidation failed")
