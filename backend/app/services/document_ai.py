"""
AI services for document analysis and risk assessment
"""
import random
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from app.schemas.document_analysis import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    DocumentCategorizationRequest,
    DocumentCategorizationResponse,
    DocumentComparisonRequest,
    DocumentComparisonResponse,
    ExtractedEntity,
    ExtractedClause,
    FinancialFigure,
    KeyDate,
    RiskCategory,
    CriticalIssue,
    Anomaly,
    ComplianceFlag,
    MissingDocument,
    DocumentDifference
)

logger = logging.getLogger(__name__)


class DocumentAIService:
    """AI service for document analysis and risk assessment"""
    
    def __init__(self):
        self.model_version = "2.0.0"
        self.supported_file_types = [
            "pdf", "docx", "doc", "txt", "xlsx", "xls", "pptx", "ppt"
        ]
        
        # Risk scoring thresholds
        self.risk_thresholds = {
            "low": 30,
            "medium": 60,
            "high": 80,
            "critical": 100
        }
        
        # Document type patterns for categorization
        self.document_patterns = {
            "financial": ["financial", "audit", "statement", "budget", "forecast", "revenue"],
            "legal": ["contract", "agreement", "legal", "terms", "conditions", "compliance"],
            "operational": ["operational", "process", "procedure", "manual", "workflow"],
            "marketing": ["marketing", "sales", "presentation", "pitch", "proposal"],
            "hr": ["employee", "hr", "human resources", "personnel", "payroll"],
            "technical": ["technical", "specification", "architecture", "design", "development"]
        }
    
    async def analyze_document(self, request: DocumentAnalysisRequest, document_info: Dict[str, Any]) -> DocumentAnalysisResponse:
        """
        Perform comprehensive AI analysis of a document
        
        In production, this would:
        1. Extract text from document using OCR/text extraction
        2. Apply NLP models for entity extraction
        3. Run risk assessment algorithms
        4. Perform compliance checking
        5. Generate structured analysis results
        
        For now, we'll use sophisticated mock logic based on document metadata
        """
        start_time = time.time()
        
        try:
            # Simulate document processing based on file type and size
            processing_delay = self._calculate_processing_time(document_info)
            await self._simulate_processing(processing_delay)
            
            # Perform analysis based on document type and content
            analysis_results = self._perform_document_analysis(request, document_info)
            
            processing_time = Decimal(str(time.time() - start_time))
            
            return DocumentAnalysisResponse(
                analysis_id=document_info.get("id"),
                document_id=request.document_id,
                analysis_type=request.analysis_type,
                status="completed",
                processing_time=processing_time,
                analysis_date=datetime.utcnow(),
                model_version=self.model_version,
                **analysis_results
            )
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise
    
    def _calculate_processing_time(self, document_info: Dict[str, Any]) -> float:
        """Calculate realistic processing time based on document characteristics"""
        base_time = 2.0  # Base 2 seconds
        
        # Add time based on file size (simulate OCR/text extraction)
        file_size = document_info.get("file_size", 1024 * 1024)  # Default 1MB
        size_factor = min(file_size / (1024 * 1024), 10)  # Max 10MB consideration
        
        # Add time based on file type complexity
        file_extension = document_info.get("file_extension", "pdf").lower()
        type_multipliers = {
            "pdf": 1.5,
            "docx": 1.2,
            "doc": 1.3,
            "xlsx": 2.0,
            "xls": 2.2,
            "pptx": 1.8,
            "txt": 0.5
        }
        
        type_multiplier = type_multipliers.get(file_extension, 1.0)
        
        return base_time + (size_factor * 0.5) * type_multiplier
    
    async def _simulate_processing(self, delay: float):
        """Simulate processing delay"""
        # In a real implementation, this would be actual processing time
        # For testing, we'll use a minimal delay
        await asyncio.sleep(min(delay, 0.1))  # Cap at 100ms for testing
    
    def _perform_document_analysis(self, request: DocumentAnalysisRequest, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the actual document analysis"""
        
        # Determine document category for context-aware analysis
        document_category = self._categorize_document(document_info)
        
        # Generate analysis results based on document type and analysis type
        if request.analysis_type == "full":
            return self._full_analysis(document_info, document_category)
        elif request.analysis_type == "risk_only":
            return self._risk_only_analysis(document_info, document_category)
        elif request.analysis_type == "financial_only":
            return self._financial_only_analysis(document_info, document_category)
        elif request.analysis_type == "legal_only":
            return self._legal_only_analysis(document_info, document_category)
        else:
            return self._compliance_only_analysis(document_info, document_category)
    
    def _categorize_document(self, document_info: Dict[str, Any]) -> str:
        """Categorize document based on filename and metadata"""
        filename = document_info.get("filename", "").lower()
        title = document_info.get("title", "").lower()
        doc_type = document_info.get("document_type", "").lower()
        
        text_to_analyze = f"{filename} {title} {doc_type}"
        
        # Score each category
        category_scores = {}
        for category, keywords in self.document_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            if score > 0:
                category_scores[category] = score
        
        # Return highest scoring category or default
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return "general"
    
    def _full_analysis(self, document_info: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Perform comprehensive document analysis"""
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(document_info, category)
        risk_level = self._determine_risk_level(risk_score)
        
        # Generate analysis components
        summary = self._generate_summary(document_info, category, risk_score)
        key_findings = self._generate_key_findings(document_info, category)
        extracted_entities = self._extract_entities(document_info, category)
        extracted_clauses = self._extract_clauses(document_info, category)
        financial_figures = self._extract_financial_figures(document_info, category)
        key_dates = self._extract_key_dates(document_info, category)
        parties_involved = self._extract_parties(document_info, category)
        
        # Risk assessment
        risk_categories = self._assess_risk_categories(document_info, category)
        critical_issues = self._identify_critical_issues(document_info, category, risk_score)
        anomalies = self._detect_anomalies(document_info, category)
        compliance_flags = self._check_compliance(document_info, category)
        
        # Quality metrics
        quality_scores = self._assess_document_quality(document_info)
        
        return {
            "overall_risk_score": risk_score,
            "confidence_score": Decimal(str(random.uniform(75, 95))),
            "risk_level": risk_level,
            "summary": summary,
            "key_findings": key_findings,
            "extracted_entities": extracted_entities,
            "extracted_clauses": extracted_clauses,
            "financial_figures": financial_figures,
            "key_dates": key_dates,
            "parties_involved": parties_involved,
            "risk_categories": risk_categories,
            "critical_issues": critical_issues,
            "anomalies": anomalies,
            "compliance_flags": compliance_flags,
            **quality_scores
        }
    
    def _calculate_risk_score(self, document_info: Dict[str, Any], category: str) -> Decimal:
        """Calculate overall risk score for document"""
        base_score = 40  # Base risk score
        
        # Category-specific risk adjustments
        category_risk_multipliers = {
            "financial": 1.3,
            "legal": 1.5,
            "operational": 1.0,
            "marketing": 0.8,
            "hr": 1.1,
            "technical": 0.9,
            "general": 1.0
        }
        
        multiplier = category_risk_multipliers.get(category, 1.0)
        
        # Document characteristics that affect risk
        if document_info.get("is_confidential", False):
            base_score += 15
        
        # File age (older files might have outdated information)
        created_at = document_info.get("created_at")
        if created_at:
            # Simulate age-based risk (older = potentially higher risk)
            age_days = (datetime.utcnow() - created_at).days if isinstance(created_at, datetime) else 0
            if age_days > 365:
                base_score += 10
            elif age_days > 180:
                base_score += 5
        
        # File size (very large or very small files might indicate issues)
        file_size = document_info.get("file_size", 1024 * 1024)
        if file_size < 10 * 1024:  # Very small files
            base_score += 5
        elif file_size > 50 * 1024 * 1024:  # Very large files
            base_score += 8
        
        # Apply category multiplier and add randomness
        final_score = base_score * multiplier + random.uniform(-10, 10)
        
        return Decimal(str(max(0, min(100, final_score))))
    
    def _determine_risk_level(self, risk_score: Decimal) -> str:
        """Determine risk level based on score"""
        score = float(risk_score)
        
        if score >= self.risk_thresholds["critical"]:
            return "critical"
        elif score >= self.risk_thresholds["high"]:
            return "high"
        elif score >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _generate_summary(self, document_info: Dict[str, Any], category: str, risk_score: Decimal) -> str:
        """Generate document analysis summary"""
        doc_name = document_info.get("title", "Document")
        risk_level = self._determine_risk_level(risk_score)
        
        category_summaries = {
            "financial": f"Financial document '{doc_name}' analyzed with {risk_level} risk level. Key financial metrics and compliance requirements reviewed.",
            "legal": f"Legal document '{doc_name}' shows {risk_level} risk profile. Contract terms and legal obligations assessed for potential issues.",
            "operational": f"Operational document '{doc_name}' evaluated with {risk_level} risk rating. Process flows and operational requirements analyzed.",
            "marketing": f"Marketing document '{doc_name}' reviewed with {risk_level} risk assessment. Content compliance and brand guidelines checked.",
            "hr": f"HR document '{doc_name}' analyzed showing {risk_level} risk level. Employment terms and regulatory compliance verified.",
            "technical": f"Technical document '{doc_name}' assessed with {risk_level} risk profile. Technical specifications and requirements reviewed."
        }
        
        return category_summaries.get(category, 
            f"Document '{doc_name}' comprehensively analyzed with {risk_level} overall risk level. "
            f"Multiple analysis dimensions considered including content quality, compliance, and potential issues.")
    
    def _generate_key_findings(self, document_info: Dict[str, Any], category: str) -> List[str]:
        """Generate key findings based on document analysis"""
        findings = []
        
        # Category-specific findings
        category_findings = {
            "financial": [
                "Revenue projections appear realistic based on historical data",
                "Cash flow analysis shows positive trends",
                "Audit trail documentation is comprehensive",
                "Financial controls are adequately documented"
            ],
            "legal": [
                "Contract terms are clearly defined and enforceable",
                "Liability clauses provide adequate protection",
                "Termination conditions are standard for industry",
                "Intellectual property rights are properly addressed"
            ],
            "operational": [
                "Process workflows are well-documented",
                "Quality control measures are in place",
                "Resource allocation appears appropriate",
                "Risk mitigation strategies are defined"
            ],
            "marketing": [
                "Brand messaging is consistent with guidelines",
                "Target audience is clearly defined",
                "Compliance with advertising regulations verified",
                "Market positioning strategy is sound"
            ]
        }
        
        # Get category-specific findings
        base_findings = category_findings.get(category, [
            "Document structure is well-organized",
            "Content appears complete and comprehensive",
            "No major inconsistencies detected",
            "Standard formatting and presentation"
        ])
        
        # Select random subset of findings
        findings.extend(random.sample(base_findings, min(3, len(base_findings))))
        
        # Add risk-based findings
        risk_score = float(self._calculate_risk_score(document_info, category))
        if risk_score > 70:
            findings.append("Several high-risk elements identified requiring attention")
        elif risk_score > 50:
            findings.append("Moderate risk factors present, monitoring recommended")
        else:
            findings.append("Low risk profile with minimal concerns identified")
        
        return findings
    
    def _extract_entities(self, document_info: Dict[str, Any], category: str) -> Dict[str, List[ExtractedEntity]]:
        """Extract entities from document"""
        entities = {
            "persons": [],
            "companies": [],
            "dates": [],
            "amounts": [],
            "locations": []
        }
        
        # Generate mock entities based on category
        if category == "financial":
            entities["companies"].extend([
                ExtractedEntity(entity_type="company", entity_value="ABC Corporation", confidence=Decimal("0.95")),
                ExtractedEntity(entity_type="company", entity_value="XYZ Holdings", confidence=Decimal("0.88"))
            ])
            entities["amounts"].extend([
                ExtractedEntity(entity_type="amount", entity_value="$2,500,000", confidence=Decimal("0.92")),
                ExtractedEntity(entity_type="amount", entity_value="$150,000", confidence=Decimal("0.87"))
            ])
        
        elif category == "legal":
            entities["persons"].extend([
                ExtractedEntity(entity_type="person", entity_value="John Smith", confidence=Decimal("0.91")),
                ExtractedEntity(entity_type="person", entity_value="Sarah Johnson", confidence=Decimal("0.89"))
            ])
            entities["dates"].extend([
                ExtractedEntity(entity_type="date", entity_value="2024-12-31", confidence=Decimal("0.96")),
                ExtractedEntity(entity_type="date", entity_value="2025-06-30", confidence=Decimal("0.93"))
            ])
        
        # Add common entities for all categories
        entities["locations"].append(
            ExtractedEntity(entity_type="location", entity_value="New York, NY", confidence=Decimal("0.85"))
        )
        
        return entities
    
    def _extract_clauses(self, document_info: Dict[str, Any], category: str) -> List[ExtractedClause]:
        """Extract important clauses from document"""
        clauses = []
        
        if category == "legal":
            clauses.extend([
                ExtractedClause(
                    clause_type="termination",
                    clause_text="Either party may terminate this agreement with 30 days written notice",
                    importance="high",
                    risk_level="medium",
                    recommendations=["Consider extending notice period to 60 days"]
                ),
                ExtractedClause(
                    clause_type="liability",
                    clause_text="Liability shall be limited to the amount paid under this agreement",
                    importance="critical",
                    risk_level="low",
                    recommendations=["Standard liability limitation clause"]
                )
            ])
        
        elif category == "financial":
            clauses.extend([
                ExtractedClause(
                    clause_type="payment",
                    clause_text="Payment terms are net 30 days from invoice date",
                    importance="high",
                    risk_level="low",
                    recommendations=["Standard payment terms"]
                )
            ])
        
        return clauses
    
    def _extract_financial_figures(self, document_info: Dict[str, Any], category: str) -> List[FinancialFigure]:
        """Extract financial figures from document"""
        figures = []
        
        if category in ["financial", "legal"]:
            figures.extend([
                FinancialFigure(
                    metric="revenue",
                    value=Decimal("2500000"),
                    currency="USD",
                    period="FY 2023",
                    confidence=Decimal("0.92")
                ),
                FinancialFigure(
                    metric="ebitda",
                    value=Decimal("450000"),
                    currency="USD",
                    period="FY 2023",
                    confidence=Decimal("0.88")
                )
            ])
        
        return figures
    
    def _extract_key_dates(self, document_info: Dict[str, Any], category: str) -> List[KeyDate]:
        """Extract important dates from document"""
        dates = []
        
        # Generate relevant dates based on category
        if category == "legal":
            dates.extend([
                KeyDate(
                    event="contract_expiry",
                    date="2024-12-31",
                    importance="critical",
                    description="Contract expiration date"
                ),
                KeyDate(
                    event="review_date",
                    date="2024-06-30",
                    importance="medium",
                    description="Mid-term contract review"
                )
            ])
        
        elif category == "financial":
            dates.extend([
                KeyDate(
                    event="payment_due",
                    date="2024-03-15",
                    importance="high",
                    description="Quarterly payment due date"
                )
            ])
        
        return dates
    
    def _extract_parties(self, document_info: Dict[str, Any], category: str) -> List[str]:
        """Extract parties involved in document"""
        parties = ["Primary Organization"]
        
        # Add category-specific parties
        if category == "legal":
            parties.extend(["Counterparty Corp", "Legal Counsel LLC"])
        elif category == "financial":
            parties.extend(["Auditing Firm", "Financial Advisor"])
        elif category == "operational":
            parties.extend(["Service Provider", "Vendor Company"])
        
        return parties
    
    def _assess_risk_categories(self, document_info: Dict[str, Any], category: str) -> List[RiskCategory]:
        """Assess risk across different categories"""
        risk_categories = []
        
        # Financial risk
        financial_score = random.uniform(20, 80)
        risk_categories.append(RiskCategory(
            category="financial",
            score=Decimal(str(financial_score)),
            level=self._determine_risk_level(Decimal(str(financial_score))),
            findings=["Cash flow projections appear realistic", "Revenue assumptions are conservative"],
            recommendations=["Monitor quarterly performance against projections"]
        ))
        
        # Legal risk
        legal_score = random.uniform(15, 75)
        risk_categories.append(RiskCategory(
            category="legal",
            score=Decimal(str(legal_score)),
            level=self._determine_risk_level(Decimal(str(legal_score))),
            findings=["Contract terms are standard", "Liability clauses provide adequate protection"],
            recommendations=["Review termination clauses with legal counsel"]
        ))
        
        # Operational risk
        operational_score = random.uniform(25, 70)
        risk_categories.append(RiskCategory(
            category="operational",
            score=Decimal(str(operational_score)),
            level=self._determine_risk_level(Decimal(str(operational_score))),
            findings=["Process documentation is comprehensive", "Resource allocation appears adequate"],
            recommendations=["Implement regular process reviews"]
        ))
        
        return risk_categories
    
    def _identify_critical_issues(self, document_info: Dict[str, Any], category: str, risk_score: Decimal) -> List[CriticalIssue]:
        """Identify critical issues requiring attention"""
        issues = []
        
        # Generate issues based on risk score
        if float(risk_score) > 70:
            if category == "legal":
                issues.append(CriticalIssue(
                    issue_type="legal_risk",
                    severity="high",
                    description="Termination clause may be too restrictive",
                    impact="Could limit flexibility in contract management",
                    mitigation="Negotiate more balanced termination terms",
                    timeline="Before contract execution"
                ))
            
            elif category == "financial":
                issues.append(CriticalIssue(
                    issue_type="financial_concern",
                    severity="medium",
                    description="Revenue projections appear aggressive",
                    impact="May lead to missed targets and covenant breaches",
                    mitigation="Develop conservative scenario planning",
                    timeline="Next quarterly review"
                ))
        
        return issues
    
    def _detect_anomalies(self, document_info: Dict[str, Any], category: str) -> List[Anomaly]:
        """Detect anomalies in document"""
        anomalies = []
        
        # Simulate anomaly detection
        if random.random() < 0.3:  # 30% chance of anomaly
            anomalies.append(Anomaly(
                anomaly_type="data_inconsistency",
                description="Date format inconsistency detected in multiple sections",
                severity="low",
                confidence=Decimal("0.75")
            ))
        
        return anomalies
    
    def _check_compliance(self, document_info: Dict[str, Any], category: str) -> List[ComplianceFlag]:
        """Check compliance requirements"""
        flags = []
        
        # Category-specific compliance checks
        if category == "financial":
            if random.random() < 0.2:  # 20% chance of compliance flag
                flags.append(ComplianceFlag(
                    regulation="SOX",
                    issue_type="requirement",
                    description="Financial controls documentation may need enhancement",
                    severity="medium",
                    recommendation="Review internal controls documentation"
                ))
        
        elif category == "legal":
            if random.random() < 0.15:  # 15% chance of compliance flag
                flags.append(ComplianceFlag(
                    regulation="GDPR",
                    issue_type="risk",
                    description="Data processing clauses may need GDPR compliance review",
                    severity="medium",
                    recommendation="Ensure data processing terms comply with GDPR"
                ))
        
        return flags
    
    def _assess_document_quality(self, document_info: Dict[str, Any]) -> Dict[str, Decimal]:
        """Assess document quality metrics"""
        
        # Base quality scores
        base_quality = 75
        base_completeness = 80
        base_readability = 85
        
        # Adjust based on file characteristics
        file_size = document_info.get("file_size", 1024 * 1024)
        
        # Very small files might be incomplete
        if file_size < 50 * 1024:  # Less than 50KB
            base_completeness -= 15
            base_quality -= 10
        
        # Very large files might be hard to read
        elif file_size > 10 * 1024 * 1024:  # More than 10MB
            base_readability -= 10
        
        # Add some randomness
        quality_variance = random.uniform(-10, 10)
        completeness_variance = random.uniform(-8, 8)
        readability_variance = random.uniform(-5, 5)
        
        return {
            "document_quality_score": Decimal(str(max(0, min(100, base_quality + quality_variance)))),
            "completeness_score": Decimal(str(max(0, min(100, base_completeness + completeness_variance)))),
            "readability_score": Decimal(str(max(0, min(100, base_readability + readability_variance))))
        }
    
    def _risk_only_analysis(self, document_info: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Perform risk-focused analysis"""
        risk_score = self._calculate_risk_score(document_info, category)
        risk_level = self._determine_risk_level(risk_score)
        
        return {
            "overall_risk_score": risk_score,
            "confidence_score": Decimal(str(random.uniform(80, 95))),
            "risk_level": risk_level,
            "summary": f"Risk-focused analysis completed with {risk_level} overall risk level",
            "key_findings": ["Risk assessment completed", "Key risk factors identified"],
            "extracted_entities": {},
            "extracted_clauses": [],
            "financial_figures": [],
            "key_dates": [],
            "parties_involved": [],
            "risk_categories": self._assess_risk_categories(document_info, category),
            "critical_issues": self._identify_critical_issues(document_info, category, risk_score),
            "anomalies": [],
            "compliance_flags": [],
            "document_quality_score": Decimal("75"),
            "completeness_score": Decimal("80"),
            "readability_score": Decimal("85")
        }
    
    def _financial_only_analysis(self, document_info: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Perform financial-focused analysis"""
        return {
            "overall_risk_score": Decimal("45"),
            "confidence_score": Decimal(str(random.uniform(85, 95))),
            "risk_level": "medium",
            "summary": "Financial analysis completed focusing on monetary values and financial metrics",
            "key_findings": ["Financial data extracted", "Revenue projections analyzed"],
            "extracted_entities": {"amounts": [
                ExtractedEntity(entity_type="amount", entity_value="$1,250,000", confidence=Decimal("0.94"))
            ]},
            "extracted_clauses": [],
            "financial_figures": self._extract_financial_figures(document_info, "financial"),
            "key_dates": [],
            "parties_involved": [],
            "risk_categories": [self._assess_risk_categories(document_info, category)[0]],  # Financial risk only
            "critical_issues": [],
            "anomalies": [],
            "compliance_flags": [],
            "document_quality_score": Decimal("80"),
            "completeness_score": Decimal("85"),
            "readability_score": Decimal("80")
        }
    
    def _legal_only_analysis(self, document_info: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Perform legal-focused analysis"""
        return {
            "overall_risk_score": Decimal("55"),
            "confidence_score": Decimal(str(random.uniform(80, 90))),
            "risk_level": "medium",
            "summary": "Legal analysis completed focusing on contract terms and legal obligations",
            "key_findings": ["Legal clauses analyzed", "Contract terms reviewed"],
            "extracted_entities": {},
            "extracted_clauses": self._extract_clauses(document_info, "legal"),
            "financial_figures": [],
            "key_dates": self._extract_key_dates(document_info, "legal"),
            "parties_involved": self._extract_parties(document_info, "legal"),
            "risk_categories": [self._assess_risk_categories(document_info, category)[1]],  # Legal risk only
            "critical_issues": [],
            "anomalies": [],
            "compliance_flags": self._check_compliance(document_info, "legal"),
            "document_quality_score": Decimal("85"),
            "completeness_score": Decimal("90"),
            "readability_score": Decimal("75")
        }
    
    def _compliance_only_analysis(self, document_info: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Perform compliance-focused analysis"""
        return {
            "overall_risk_score": Decimal("35"),
            "confidence_score": Decimal(str(random.uniform(75, 90))),
            "risk_level": "low",
            "summary": "Compliance analysis completed focusing on regulatory requirements",
            "key_findings": ["Compliance requirements reviewed", "Regulatory standards checked"],
            "extracted_entities": {},
            "extracted_clauses": [],
            "financial_figures": [],
            "key_dates": [],
            "parties_involved": [],
            "risk_categories": [],
            "critical_issues": [],
            "anomalies": [],
            "compliance_flags": self._check_compliance(document_info, category),
            "document_quality_score": Decimal("80"),
            "completeness_score": Decimal("85"),
            "readability_score": Decimal("80")
        }


    async def assess_risk(self, request: RiskAssessmentRequest, documents_info: List[Dict[str, Any]]) -> RiskAssessmentResponse:
        """Perform comprehensive risk assessment for multiple documents"""

        # Analyze each document and aggregate results
        document_analyses = []
        for doc_info in documents_info:
            analysis_request = DocumentAnalysisRequest(
                document_id=doc_info["id"],
                analysis_type="risk_only"
            )
            analysis = await self.analyze_document(analysis_request, doc_info)
            document_analyses.append(analysis)

        # Aggregate risk assessment
        overall_risk_score = self._calculate_aggregate_risk_score(document_analyses)
        risk_level = self._determine_risk_level(overall_risk_score)

        # Generate comprehensive assessment
        risk_categories = self._aggregate_risk_categories(document_analyses)
        critical_issues = self._aggregate_critical_issues(document_analyses)
        missing_documents = self._identify_missing_documents(request.assessment_type)
        compliance_status = self._assess_overall_compliance(document_analyses)

        return RiskAssessmentResponse(
            assessment_id=request.deal_id or uuid.uuid4(),
            assessment_name=request.assessment_name,
            assessment_type=request.assessment_type,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            confidence_level=Decimal(str(random.uniform(75, 90))),
            risk_categories=risk_categories,
            critical_issues=critical_issues,
            medium_issues=[],
            low_issues=[],
            recommendations=self._generate_risk_recommendations(risk_level, critical_issues),
            action_items=[],
            missing_documents=missing_documents,
            information_gaps=[],
            compliance_status=compliance_status,
            regulatory_issues=[],
            required_actions=[],
            assessment_date=datetime.utcnow(),
            assessment_completeness=Decimal(str(random.uniform(80, 95))),
            data_quality_score=Decimal(str(random.uniform(75, 90)))
        )

    def _calculate_aggregate_risk_score(self, analyses: List[DocumentAnalysisResponse]) -> Decimal:
        """Calculate aggregate risk score from multiple document analyses"""
        if not analyses:
            return Decimal("50")

        # Weight documents by importance (can be enhanced with document-specific weights)
        total_score = sum(float(analysis.overall_risk_score) for analysis in analyses)
        average_score = total_score / len(analyses)

        # Add complexity factor for multiple documents
        complexity_factor = min(len(analyses) * 2, 10)  # Max 10 point increase

        final_score = average_score + complexity_factor
        return Decimal(str(max(0, min(100, final_score))))

    def _aggregate_risk_categories(self, analyses: List[DocumentAnalysisResponse]) -> List[RiskCategory]:
        """Aggregate risk categories from multiple analyses"""
        category_scores = {}
        category_findings = {}

        for analysis in analyses:
            for risk_cat in analysis.risk_categories:
                cat_name = risk_cat.category
                if cat_name not in category_scores:
                    category_scores[cat_name] = []
                    category_findings[cat_name] = []

                category_scores[cat_name].append(float(risk_cat.score))
                category_findings[cat_name].extend(risk_cat.findings)

        # Calculate average scores and aggregate findings
        aggregated_categories = []
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            aggregated_categories.append(RiskCategory(
                category=category,
                score=Decimal(str(avg_score)),
                level=self._determine_risk_level(Decimal(str(avg_score))),
                findings=list(set(category_findings[category]))[:5],  # Unique findings, max 5
                recommendations=[f"Monitor {category} risk factors closely"]
            ))

        return aggregated_categories

    def _aggregate_critical_issues(self, analyses: List[DocumentAnalysisResponse]) -> List[CriticalIssue]:
        """Aggregate critical issues from multiple analyses"""
        all_issues = []
        for analysis in analyses:
            all_issues.extend(analysis.critical_issues)

        # Remove duplicates and prioritize by severity
        unique_issues = []
        seen_descriptions = set()

        for issue in sorted(all_issues, key=lambda x: {"critical": 3, "high": 2, "medium": 1}.get(x.severity, 0), reverse=True):
            if issue.description not in seen_descriptions:
                unique_issues.append(issue)
                seen_descriptions.add(issue.description)

        return unique_issues[:10]  # Return top 10 critical issues

    def _identify_missing_documents(self, assessment_type: str) -> List[MissingDocument]:
        """Identify missing documents based on assessment type"""
        missing_docs = []

        if assessment_type == "deal":
            missing_docs.extend([
                MissingDocument(
                    document_type="Financial Statements",
                    importance="critical",
                    deadline="Before closing",
                    impact_if_missing="Cannot complete financial due diligence"
                ),
                MissingDocument(
                    document_type="Legal Opinions",
                    importance="high",
                    deadline="2 weeks before closing",
                    impact_if_missing="Legal risks may not be properly assessed"
                )
            ])

        return missing_docs

    def _assess_overall_compliance(self, analyses: List[DocumentAnalysisResponse]) -> str:
        """Assess overall compliance status"""
        compliance_flags = []
        for analysis in analyses:
            compliance_flags.extend(analysis.compliance_flags)

        if not compliance_flags:
            return "compliant"

        # Check severity of compliance issues
        high_severity_count = sum(1 for flag in compliance_flags if flag.severity in ["high", "critical"])

        if high_severity_count > 0:
            return "non_compliant"
        else:
            return "review_required"

    def _generate_risk_recommendations(self, risk_level: str, critical_issues: List[CriticalIssue]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        if risk_level == "critical":
            recommendations.extend([
                "Immediate executive review required",
                "Consider deal restructuring or termination",
                "Engage specialized risk consultants"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Detailed risk mitigation plan required",
                "Additional due diligence recommended",
                "Consider deal term adjustments"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Monitor identified risks closely",
                "Implement standard risk controls",
                "Regular risk assessment updates"
            ])
        else:
            recommendations.extend([
                "Maintain current risk monitoring",
                "Standard due diligence procedures sufficient"
            ])

        # Add issue-specific recommendations
        for issue in critical_issues[:3]:  # Top 3 issues
            if issue.mitigation:
                recommendations.append(issue.mitigation)

        return recommendations[:5]  # Return top 5 recommendations


# Import asyncio and uuid for async operations
import asyncio
import uuid

# Create service instance
document_ai_service = DocumentAIService()
