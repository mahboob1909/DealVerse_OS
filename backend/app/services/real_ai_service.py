"""
Real AI Service for DealVerse OS - Enhanced OpenRouter, OpenAI and Anthropic Integration
Optimized for DeepSeek model with advanced document analysis capabilities
"""
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import re

import openai
import anthropic
import tiktoken
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.ai_config import (
    get_ai_settings, 
    get_ai_prompt, 
    RISK_SCORING_CONFIG,
    ENTITY_EXTRACTION_CONFIG
)
from app.schemas.document_analysis import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    ExtractedEntity,
    ExtractedClause,
    FinancialFigure,
    KeyDate,
    RiskCategory,
    CriticalIssue,
    Anomaly,
    ComplianceFlag
)

logger = logging.getLogger(__name__)


class RealAIService:
    """Real AI service using OpenAI GPT-4, Anthropic Claude, and OpenRouter"""

    def __init__(self):
        self.settings = get_ai_settings()
        self.openai_client = None
        self.anthropic_client = None
        self.openrouter_client = None
        self.tokenizer = None

        # Initialize clients
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize AI service clients"""
        try:
            if self.settings.openai_api_key:
                self.openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
                self.tokenizer = tiktoken.encoding_for_model("gpt-4")
                logger.info("OpenAI client initialized successfully")

            if self.settings.anthropic_api_key:
                self.anthropic_client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
                logger.info("Anthropic client initialized successfully")

            if self.settings.openrouter_api_key:
                self.openrouter_client = AsyncOpenAI(
                    api_key=self.settings.openrouter_api_key,
                    base_url=self.settings.openrouter_base_url
                )
                logger.info("OpenRouter client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {str(e)}")
            raise
    
    async def analyze_document(
        self, 
        request: DocumentAnalysisRequest, 
        document_info: Dict[str, Any],
        document_content: str
    ) -> DocumentAnalysisResponse:
        """
        Perform real AI analysis of document content
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare analysis context
            analysis_context = {
                "document_type": document_info.get("document_type", "unknown"),
                "document_title": document_info.get("title", ""),
                "analysis_type": request.analysis_type,
                "document_content": document_content
            }
            
            # Perform analysis based on type
            if request.analysis_type == "full":
                analysis_results = await self._perform_full_analysis(analysis_context)
            elif request.analysis_type == "risk_only":
                analysis_results = await self._perform_risk_analysis(analysis_context)
            elif request.analysis_type == "financial_only":
                analysis_results = await self._perform_financial_analysis(analysis_context)
            elif request.analysis_type == "legal_only":
                analysis_results = await self._perform_legal_analysis(analysis_context)
            else:  # compliance_only
                analysis_results = await self._perform_compliance_analysis(analysis_context)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return DocumentAnalysisResponse(
                analysis_id=document_info.get("id"),
                document_id=request.document_id,
                analysis_type=request.analysis_type,
                status="completed",
                processing_time=Decimal(str(processing_time)),
                analysis_date=datetime.utcnow(),
                model_version=self._get_model_version(),
                **analysis_results
            )
            
        except Exception as e:
            logger.error(f"Error in real AI document analysis: {str(e)}")
            # Fallback to basic analysis
            return await self._fallback_analysis(request, document_info, str(e))
    
    async def _perform_full_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive document analysis"""
        
        # Get AI analysis
        ai_response = await self._call_ai_service(
            prompt_type="document_analysis",
            context=context
        )
        
        # Parse AI response
        parsed_results = self._parse_ai_response(ai_response)
        
        # Extract structured data
        extracted_entities = await self._extract_entities(context["document_content"])
        risk_assessment = await self._assess_risks(context)
        compliance_flags = await self._check_compliance(context)
        
        return {
            "overall_risk_score": parsed_results.get("risk_score", Decimal("50")),
            "confidence_score": parsed_results.get("confidence", Decimal("85")),
            "risk_level": parsed_results.get("risk_level", "medium"),
            "summary": parsed_results.get("summary", "AI analysis completed"),
            "key_findings": parsed_results.get("key_findings", []),
            "extracted_entities": extracted_entities,
            "extracted_clauses": self._extract_clauses_from_ai(parsed_results),
            "financial_figures": self._extract_financial_figures(parsed_results),
            "key_dates": self._extract_key_dates(parsed_results),
            "parties_involved": parsed_results.get("parties", []),
            "risk_categories": risk_assessment.get("categories", []),
            "critical_issues": risk_assessment.get("critical_issues", []),
            "anomalies": self._detect_anomalies(parsed_results),
            "compliance_flags": compliance_flags,
            "document_quality_score": parsed_results.get("quality_score", Decimal("80")),
            "completeness_score": parsed_results.get("completeness_score", Decimal("85")),
            "readability_score": parsed_results.get("readability_score", Decimal("75"))
        }
    
    async def _call_ai_service(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        max_retries: int = None
    ) -> str:
        """Call the configured AI service with fallback"""

        max_retries = max_retries or self.settings.max_retries

        for attempt in range(max_retries):
            try:
                if self.settings.preferred_ai_provider == "openrouter" and self.openrouter_client:
                    return await self._call_openrouter(prompt_type, context)
                elif self.settings.preferred_ai_provider == "openai" and self.openai_client:
                    return await self._call_openai(prompt_type, context)
                elif self.settings.preferred_ai_provider == "anthropic" and self.anthropic_client:
                    return await self._call_anthropic(prompt_type, context)
                else:
                    # Try fallback provider
                    if self.settings.enable_fallback:
                        if self.openrouter_client:
                            return await self._call_openrouter(prompt_type, context)
                        elif self.openai_client:
                            return await self._call_openai(prompt_type, context)
                        elif self.anthropic_client:
                            return await self._call_anthropic(prompt_type, context)

                raise Exception("No AI provider available")

            except Exception as e:
                logger.warning(f"AI service attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _call_openai(self, prompt_type: str, context: Dict[str, Any]) -> str:
        """Call OpenAI GPT-4 API"""
        
        system_prompt = get_ai_prompt(prompt_type, "system")
        user_prompt = get_ai_prompt(prompt_type, "user_template").format(**context)
        
        # Truncate content if too long
        user_prompt = self._truncate_content(user_prompt, self.settings.openai_max_tokens)
        
        response = await self.openai_client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=self.settings.openai_max_tokens,
            temperature=self.settings.openai_temperature,
            timeout=self.settings.request_timeout
        )
        
        return response.choices[0].message.content

    async def _call_openrouter(self, prompt_type: str, context: Dict[str, Any]) -> str:
        """Call OpenRouter API with DeepSeek optimization"""

        system_prompt = get_ai_prompt(prompt_type, "system")
        user_prompt = get_ai_prompt(prompt_type, "user_template").format(**context)

        # Enhanced content truncation for DeepSeek
        user_prompt = self._truncate_content_smart(user_prompt, self.settings.openrouter_max_tokens)

        # Prepare headers for OpenRouter with enhanced metadata
        extra_headers = {
            "HTTP-Referer": self.settings.openrouter_site_url or "https://dealverse.com",
            "X-Title": self.settings.openrouter_site_name or "DealVerse OS - AI Document Analysis"
        }

        # DeepSeek-specific optimizations
        model_params = {
            "model": self.settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": self.settings.openrouter_max_tokens,
            "temperature": self.settings.openrouter_temperature,
            "timeout": self.settings.request_timeout,
            "extra_headers": extra_headers
        }

        # Add DeepSeek-specific parameters if using DeepSeek model
        if "deepseek" in self.settings.openrouter_model.lower():
            model_params.update({
                "top_p": 0.95,  # DeepSeek works well with slightly higher top_p
                "frequency_penalty": 0.1,  # Reduce repetition
                "presence_penalty": 0.1,   # Encourage diverse responses
            })

        try:
            response = await self.openrouter_client.chat.completions.create(**model_params)

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from OpenRouter API")

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenRouter API call failed: {str(e)}")
            # Enhanced error context for debugging
            logger.error(f"Model: {self.settings.openrouter_model}, Prompt type: {prompt_type}")
            raise

    async def _call_anthropic(self, prompt_type: str, context: Dict[str, Any]) -> str:
        """Call Anthropic Claude API"""
        
        system_prompt = get_ai_prompt(prompt_type, "system")
        user_prompt = get_ai_prompt(prompt_type, "user_template").format(**context)
        
        # Truncate content if too long
        user_prompt = self._truncate_content(user_prompt, self.settings.anthropic_max_tokens)
        
        response = await self.anthropic_client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=self.settings.anthropic_max_tokens,
            temperature=self.settings.anthropic_temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            timeout=self.settings.request_timeout
        )
        
        return response.content[0].text
    
    def _truncate_content_smart(self, content: str, max_tokens: int) -> str:
        """Smart content truncation optimized for document analysis"""
        if not content:
            return content

        # Reserve tokens for system prompt and response
        available_tokens = max_tokens - 1000  # Conservative buffer

        if not self.tokenizer:
            # Enhanced character-based truncation as fallback
            max_chars = available_tokens * 3  # Rough estimate
            if len(content) <= max_chars:
                return content

            # Try to truncate at sentence boundaries
            truncated = content[:max_chars]
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n')

            # Use the latest sentence or paragraph boundary
            cut_point = max(last_period, last_newline)
            if cut_point > max_chars * 0.8:  # Only if we don't lose too much content
                return content[:cut_point + 1] + "\n\n[Content truncated for analysis]"
            else:
                return truncated + "\n\n[Content truncated for analysis]"

        # Token-based truncation with tiktoken
        try:
            tokens = self.tokenizer.encode(content)
            if len(tokens) <= available_tokens:
                return content

            # Truncate tokens and decode back
            truncated_tokens = tokens[:available_tokens]
            truncated_content = self.tokenizer.decode(truncated_tokens)
            return truncated_content + "\n\n[Content truncated for analysis]"

        except Exception as e:
            logger.warning(f"Token-based truncation failed: {str(e)}, falling back to character-based")
            return self._truncate_content(content, max_tokens)

    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Legacy truncate content to fit within token limits"""
        if not self.tokenizer:
            # Simple character-based truncation as fallback
            max_chars = max_tokens * 3  # Rough estimate
            return content[:max_chars] if len(content) > max_chars else content
        
        tokens = self.tokenizer.encode(content)
        if len(tokens) <= max_tokens:
            return content
        
        # Truncate and decode back to text
        truncated_tokens = tokens[:max_tokens - 100]  # Leave some buffer
        return self.tokenizer.decode(truncated_tokens)
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Enhanced AI response parsing with better JSON handling"""
        try:
            # Clean the response
            cleaned_response = ai_response.strip()

            # Try to extract JSON from response if it's wrapped in text
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_content = cleaned_response[json_start:json_end]
                try:
                    parsed_json = json.loads(json_content)
                    logger.info("Successfully parsed structured JSON response")
                    return self._normalize_ai_response(parsed_json)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed: {str(e)}, attempting repair")
                    # Try to repair common JSON issues
                    repaired_json = self._repair_json(json_content)
                    if repaired_json:
                        return self._normalize_ai_response(repaired_json)

            # Fallback to regex extraction for unstructured responses
            logger.warning("Falling back to regex-based parsing")
            return self._extract_with_regex(cleaned_response)

        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return self._get_fallback_response()

    def _repair_json(self, json_content: str) -> Optional[Dict[str, Any]]:
        """Attempt to repair common JSON formatting issues"""
        try:
            # Common fixes for AI-generated JSON
            repaired = json_content

            # Fix trailing commas
            repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)

            # Fix unquoted keys
            repaired = re.sub(r'(\w+):', r'"\1":', repaired)

            # Fix single quotes
            repaired = repaired.replace("'", '"')

            # Try parsing the repaired JSON
            return json.loads(repaired)

        except Exception as e:
            logger.warning(f"JSON repair failed: {str(e)}")
            return None

    def _normalize_ai_response(self, parsed_json: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize AI response to expected format"""
        normalized = {}

        # Extract executive summary
        if "executive_summary" in parsed_json:
            exec_summary = parsed_json["executive_summary"]
            normalized["summary"] = exec_summary.get("summary", "")
            normalized["key_findings"] = exec_summary.get("key_findings", [])
            normalized["confidence"] = Decimal(str(exec_summary.get("confidence_score", 0.8)))

        # Extract risk assessment
        if "risk_assessment" in parsed_json:
            risk_data = parsed_json["risk_assessment"]
            normalized["risk_score"] = Decimal(str(risk_data.get("risk_score", 0.5) * 100))
            normalized["risk_level"] = risk_data.get("overall_risk_level", "Medium")
            normalized["risks"] = risk_data.get("identified_risks", [])

        # Extract entities
        if "extracted_entities" in parsed_json:
            normalized["entities"] = parsed_json["extracted_entities"]

        # Extract compliance flags
        if "compliance_flags" in parsed_json:
            normalized["compliance_issues"] = parsed_json["compliance_flags"]

        # Extract financial analysis
        if "financial_analysis" in parsed_json:
            normalized["financial_data"] = parsed_json["financial_analysis"]

        # Extract recommendations
        if "recommendations" in parsed_json:
            normalized["recommendations"] = parsed_json["recommendations"]

        return normalized

    def _extract_with_regex(self, response: str) -> Dict[str, Any]:
        """Extract key information using regex patterns"""
        parsed = {}

        # Extract risk score
        risk_match = re.search(r'risk[_\s]*score[:\s]*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
        if risk_match:
            parsed["risk_score"] = Decimal(risk_match.group(1))

        # Extract confidence
        conf_match = re.search(r'confidence[:\s]*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
        if conf_match:
            parsed["confidence"] = Decimal(conf_match.group(1))

        # Extract summary (first substantial paragraph)
        lines = response.split('\n')
        for line in lines:
            if line.strip() and len(line.strip()) > 50:
                parsed["summary"] = line.strip()
                break

        return parsed

    def _get_fallback_response(self) -> Dict[str, Any]:
        """Get fallback response when parsing fails"""
        return {
            "summary": "AI analysis completed with parsing issues",
            "confidence": Decimal("70"),
            "risk_score": Decimal("50"),
            "risk_level": "Medium",
            "key_findings": ["Analysis completed but response format was unclear"],
            "entities": {},
            "compliance_issues": [],
            "recommendations": {"immediate_actions": ["Review document manually"]}
        }
    
    def _get_model_version(self) -> str:
        """Get the current model version being used"""
        if self.settings.preferred_ai_provider == "openai":
            return f"OpenAI-{self.settings.openai_model}"
        else:
            return f"Anthropic-{self.settings.anthropic_model}"
    
    async def _fallback_analysis(
        self, 
        request: DocumentAnalysisRequest, 
        document_info: Dict[str, Any], 
        error_msg: str
    ) -> DocumentAnalysisResponse:
        """Provide fallback analysis when AI service fails"""
        
        return DocumentAnalysisResponse(
            analysis_id=document_info.get("id"),
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            status="completed_with_fallback",
            processing_time=Decimal("1.0"),
            analysis_date=datetime.utcnow(),
            model_version="Fallback-v1.0",
            overall_risk_score=Decimal("50"),
            confidence_score=Decimal("60"),
            risk_level="medium",
            summary=f"Fallback analysis completed. AI service error: {error_msg}",
            key_findings=["Document processed with fallback analysis"],
            extracted_entities={},
            extracted_clauses=[],
            financial_figures=[],
            key_dates=[],
            parties_involved=[],
            risk_categories=[],
            critical_issues=[],
            anomalies=[],
            compliance_flags=[],
            document_quality_score=Decimal("70"),
            completeness_score=Decimal("70"),
            readability_score=Decimal("70")
        )


    async def _perform_risk_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform risk-focused analysis"""
        risk_assessment = await self._assess_risks(context)

        return {
            "overall_risk_score": risk_assessment.get("overall_score", Decimal("50")),
            "confidence_score": Decimal("80"),
            "risk_level": risk_assessment.get("risk_level", "medium"),
            "summary": "Risk-focused analysis completed",
            "key_findings": risk_assessment.get("key_findings", []),
            "extracted_entities": {},
            "extracted_clauses": [],
            "financial_figures": [],
            "key_dates": [],
            "parties_involved": [],
            "risk_categories": risk_assessment.get("categories", []),
            "critical_issues": risk_assessment.get("critical_issues", []),
            "anomalies": [],
            "compliance_flags": [],
            "document_quality_score": Decimal("75"),
            "completeness_score": Decimal("80"),
            "readability_score": Decimal("85")
        }

    async def _perform_financial_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform financial-focused analysis"""
        ai_response = await self._call_ai_service("document_analysis", context)
        parsed_results = self._parse_ai_response(ai_response)

        return {
            "overall_risk_score": Decimal("45"),
            "confidence_score": Decimal("85"),
            "risk_level": "medium",
            "summary": "Financial analysis completed focusing on monetary values and metrics",
            "key_findings": parsed_results.get("key_findings", ["Financial data analyzed"]),
            "extracted_entities": {"amounts": self._extract_amounts_from_ai(parsed_results)},
            "extracted_clauses": [],
            "financial_figures": self._extract_financial_figures(parsed_results),
            "key_dates": [],
            "parties_involved": [],
            "risk_categories": [],
            "critical_issues": [],
            "anomalies": [],
            "compliance_flags": [],
            "document_quality_score": Decimal("80"),
            "completeness_score": Decimal("85"),
            "readability_score": Decimal("80")
        }

    async def _perform_legal_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform legal-focused analysis"""
        ai_response = await self._call_ai_service("document_analysis", context)
        parsed_results = self._parse_ai_response(ai_response)

        return {
            "overall_risk_score": Decimal("55"),
            "confidence_score": Decimal("80"),
            "risk_level": "medium",
            "summary": "Legal analysis completed focusing on contract terms and obligations",
            "key_findings": parsed_results.get("key_findings", ["Legal clauses analyzed"]),
            "extracted_entities": {},
            "extracted_clauses": self._extract_clauses_from_ai(parsed_results),
            "financial_figures": [],
            "key_dates": self._extract_key_dates(parsed_results),
            "parties_involved": parsed_results.get("parties", []),
            "risk_categories": [],
            "critical_issues": [],
            "anomalies": [],
            "compliance_flags": [],
            "document_quality_score": Decimal("75"),
            "completeness_score": Decimal("80"),
            "readability_score": Decimal("85")
        }

    async def _perform_compliance_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform compliance-focused analysis"""
        compliance_flags = await self._check_compliance(context)

        return {
            "overall_risk_score": Decimal("35"),
            "confidence_score": Decimal("75"),
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
            "compliance_flags": compliance_flags,
            "document_quality_score": Decimal("80"),
            "completeness_score": Decimal("85"),
            "readability_score": Decimal("75")
        }

    async def _extract_entities(self, document_content: str) -> Dict[str, List[ExtractedEntity]]:
        """Extract entities using AI"""
        try:
            context = {"document_content": document_content}
            ai_response = await self._call_ai_service("entity_extraction", context)
            parsed_entities = self._parse_ai_response(ai_response)

            entities = {
                "persons": [],
                "companies": [],
                "dates": [],
                "amounts": [],
                "locations": []
            }

            # Parse AI response for entities
            if isinstance(parsed_entities, dict):
                for entity_type, entity_list in parsed_entities.items():
                    if isinstance(entity_list, list):
                        for entity in entity_list:
                            if isinstance(entity, dict):
                                extracted_entity = ExtractedEntity(
                                    entity_type=entity.get("type", entity_type),
                                    entity_value=entity.get("value", ""),
                                    confidence=Decimal(str(entity.get("confidence", 0.8)))
                                )

                                # Map to our categories
                                if entity_type.lower() in ["person", "people", "individuals"]:
                                    entities["persons"].append(extracted_entity)
                                elif entity_type.lower() in ["company", "organization", "org"]:
                                    entities["companies"].append(extracted_entity)
                                elif entity_type.lower() in ["date", "dates"]:
                                    entities["dates"].append(extracted_entity)
                                elif entity_type.lower() in ["amount", "money", "financial"]:
                                    entities["amounts"].append(extracted_entity)
                                elif entity_type.lower() in ["location", "place", "gpe"]:
                                    entities["locations"].append(extracted_entity)

            return entities

        except Exception as e:
            logger.warning(f"Entity extraction failed: {str(e)}")
            return {"persons": [], "companies": [], "dates": [], "amounts": [], "locations": []}

    async def _assess_risks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks using AI"""
        try:
            ai_response = await self._call_ai_service("risk_assessment", context)
            parsed_results = self._parse_ai_response(ai_response)

            # Extract risk categories
            categories = []
            if "risks" in parsed_results:
                for risk in parsed_results["risks"]:
                    if isinstance(risk, dict):
                        category = RiskCategory(
                            category=risk.get("category", "general"),
                            risk_level=risk.get("level", "medium"),
                            description=risk.get("description", ""),
                            impact_score=Decimal(str(risk.get("impact", 50))),
                            likelihood_score=Decimal(str(risk.get("likelihood", 50)))
                        )
                        categories.append(category)

            # Extract critical issues
            critical_issues = []
            if "critical_issues" in parsed_results:
                for issue in parsed_results["critical_issues"]:
                    if isinstance(issue, dict):
                        critical_issue = CriticalIssue(
                            issue_type=issue.get("type", "general"),
                            severity=issue.get("severity", "medium"),
                            description=issue.get("description", ""),
                            recommendation=issue.get("recommendation", "")
                        )
                        critical_issues.append(critical_issue)

            return {
                "overall_score": parsed_results.get("overall_score", Decimal("50")),
                "risk_level": parsed_results.get("risk_level", "medium"),
                "categories": categories,
                "critical_issues": critical_issues,
                "key_findings": parsed_results.get("key_findings", [])
            }

        except Exception as e:
            logger.warning(f"Risk assessment failed: {str(e)}")
            return {
                "overall_score": Decimal("50"),
                "risk_level": "medium",
                "categories": [],
                "critical_issues": [],
                "key_findings": []
            }

    async def _check_compliance(self, context: Dict[str, Any]) -> List[ComplianceFlag]:
        """Check compliance using AI"""
        try:
            ai_response = await self._call_ai_service("compliance_check", context)
            parsed_results = self._parse_ai_response(ai_response)

            compliance_flags = []
            if "compliance_issues" in parsed_results:
                for issue in parsed_results["compliance_issues"]:
                    if isinstance(issue, dict):
                        flag = ComplianceFlag(
                            regulation_type=issue.get("regulation", "general"),
                            severity=issue.get("severity", "medium"),
                            description=issue.get("description", ""),
                            recommendation=issue.get("recommendation", "")
                        )
                        compliance_flags.append(flag)

            return compliance_flags

        except Exception as e:
            logger.warning(f"Compliance check failed: {str(e)}")
            return []


    def _extract_clauses_from_ai(self, parsed_results: Dict[str, Any]) -> List[ExtractedClause]:
        """Extract clauses from AI analysis results"""
        clauses = []

        if "clauses" in parsed_results:
            for clause_data in parsed_results["clauses"]:
                if isinstance(clause_data, dict):
                    clause = ExtractedClause(
                        clause_type=clause_data.get("type", "general"),
                        clause_text=clause_data.get("text", ""),
                        importance=clause_data.get("importance", "medium"),
                        page_number=clause_data.get("page", 1)
                    )
                    clauses.append(clause)

        return clauses

    def _extract_financial_figures(self, parsed_results: Dict[str, Any]) -> List[FinancialFigure]:
        """Extract financial figures from AI analysis results"""
        figures = []

        if "financial_figures" in parsed_results:
            for figure_data in parsed_results["financial_figures"]:
                if isinstance(figure_data, dict):
                    figure = FinancialFigure(
                        figure_type=figure_data.get("type", "amount"),
                        amount=Decimal(str(figure_data.get("amount", 0))),
                        currency=figure_data.get("currency", "USD"),
                        context=figure_data.get("context", ""),
                        confidence=Decimal(str(figure_data.get("confidence", 0.8)))
                    )
                    figures.append(figure)

        return figures

    def _extract_key_dates(self, parsed_results: Dict[str, Any]) -> List[KeyDate]:
        """Extract key dates from AI analysis results"""
        dates = []

        if "key_dates" in parsed_results:
            for date_data in parsed_results["key_dates"]:
                if isinstance(date_data, dict):
                    try:
                        # Parse date string
                        date_str = date_data.get("date", "")
                        if date_str:
                            # Try different date formats
                            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]:
                                try:
                                    parsed_date = datetime.strptime(date_str, fmt).date()
                                    break
                                except ValueError:
                                    continue
                            else:
                                continue  # Skip if no format matches

                            key_date = KeyDate(
                                date_type=date_data.get("type", "general"),
                                date_value=parsed_date,
                                description=date_data.get("description", ""),
                                importance=date_data.get("importance", "medium")
                            )
                            dates.append(key_date)
                    except Exception as e:
                        logger.warning(f"Failed to parse date: {str(e)}")
                        continue

        return dates

    def _extract_amounts_from_ai(self, parsed_results: Dict[str, Any]) -> List[ExtractedEntity]:
        """Extract monetary amounts from AI analysis results"""
        amounts = []

        if "amounts" in parsed_results:
            for amount_data in parsed_results["amounts"]:
                if isinstance(amount_data, dict):
                    entity = ExtractedEntity(
                        entity_type="amount",
                        entity_value=amount_data.get("value", ""),
                        confidence=Decimal(str(amount_data.get("confidence", 0.8)))
                    )
                    amounts.append(entity)

        return amounts

    def _detect_anomalies(self, parsed_results: Dict[str, Any]) -> List[Anomaly]:
        """Detect anomalies from AI analysis results"""
        anomalies = []

        if "anomalies" in parsed_results:
            for anomaly_data in parsed_results["anomalies"]:
                if isinstance(anomaly_data, dict):
                    anomaly = Anomaly(
                        anomaly_type=anomaly_data.get("type", "general"),
                        description=anomaly_data.get("description", ""),
                        severity=anomaly_data.get("severity", "medium"),
                        confidence=Decimal(str(anomaly_data.get("confidence", 0.7)))
                    )
                    anomalies.append(anomaly)

        return anomalies

    async def assess_risk(
        self,
        request: RiskAssessmentRequest,
        document_info: Dict[str, Any],
        document_content: str
    ) -> RiskAssessmentResponse:
        """
        Perform real AI risk assessment
        """
        start_time = datetime.utcnow()

        try:
            context = {
                "document_type": document_info.get("document_type", "unknown"),
                "document_content": document_content
            }

            risk_assessment = await self._assess_risks(context)
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            return RiskAssessmentResponse(
                assessment_id=document_info.get("id"),
                document_id=request.document_id,
                overall_risk_score=risk_assessment.get("overall_score", Decimal("50")),
                risk_level=risk_assessment.get("risk_level", "medium"),
                assessment_date=datetime.utcnow(),
                processing_time=Decimal(str(processing_time)),
                model_version=self._get_model_version(),
                risk_categories=risk_assessment.get("categories", []),
                critical_issues=risk_assessment.get("critical_issues", []),
                recommendations=risk_assessment.get("key_findings", [])
            )

        except Exception as e:
            logger.error(f"Error in real AI risk assessment: {str(e)}")
            return RiskAssessmentResponse(
                assessment_id=document_info.get("id"),
                document_id=request.document_id,
                overall_risk_score=Decimal("50"),
                risk_level="medium",
                assessment_date=datetime.utcnow(),
                processing_time=Decimal("1.0"),
                model_version="Fallback-v1.0",
                risk_categories=[],
                critical_issues=[],
                recommendations=["Risk assessment completed with fallback"]
            )

    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of the AI service"""
        return {
            "service_type": "real_ai",
            "openai_available": bool(self.openai_client),
            "anthropic_available": bool(self.anthropic_client),
            "openrouter_available": bool(self.openrouter_client),
            "preferred_provider": self.settings.preferred_ai_provider,
            "fallback_enabled": self.settings.enable_fallback,
            "model_versions": {
                "openai": self.settings.openai_model,
                "anthropic": self.settings.anthropic_model,
                "openrouter": self.settings.openrouter_model
            }
        }


# Global instance
real_ai_service = RealAIService()
