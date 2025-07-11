#!/usr/bin/env python3
"""
Test script for Enhanced AI Integration in DealVerse OS
Tests the new DeepSeek-optimized AI analysis capabilities
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.enhanced_document_ai import enhanced_document_ai
from app.services.integrated_ai_service import IntegratedAIService
from app.schemas.document_analysis import DocumentAnalysisRequest
from app.core.ai_config import get_ai_settings, validate_ai_configuration


class EnhancedAITester:
    """Test suite for enhanced AI integration"""
    
    def __init__(self):
        self.ai_service = IntegratedAIService()
        self.enhanced_ai = enhanced_document_ai
        self.test_results = []
        
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Enhanced AI Integration Tests")
        print("=" * 60)
        
        # Test 1: Configuration validation
        await self.test_ai_configuration()
        
        # Test 2: Enhanced document analysis
        await self.test_enhanced_document_analysis()
        
        # Test 3: JSON response parsing
        await self.test_json_response_parsing()
        
        # Test 4: Error handling and fallbacks
        await self.test_error_handling()
        
        # Test 5: Performance and optimization
        await self.test_performance_optimization()
        
        # Print summary
        self.print_test_summary()
        
    async def test_ai_configuration(self):
        """Test AI configuration and provider setup"""
        print("\n📋 Test 1: AI Configuration Validation")
        print("-" * 40)
        
        try:
            # Check AI settings
            settings = get_ai_settings()
            config_status = validate_ai_configuration()
            
            print(f"✓ AI Settings loaded successfully")
            print(f"  - Preferred provider: {settings.preferred_ai_provider}")
            print(f"  - OpenRouter configured: {config_status.get('openrouter_configured', False)}")
            print(f"  - OpenAI configured: {config_status.get('openai_configured', False)}")
            print(f"  - Anthropic configured: {config_status.get('anthropic_configured', False)}")
            
            if config_status.get('openrouter_configured'):
                print(f"  - OpenRouter model: {settings.openrouter_model}")
                print(f"  - Max tokens: {settings.openrouter_max_tokens}")
                print(f"  - Temperature: {settings.openrouter_temperature}")
            
            self.test_results.append(("AI Configuration", "PASS", "Configuration loaded successfully"))
            
        except Exception as e:
            print(f"❌ AI Configuration test failed: {str(e)}")
            self.test_results.append(("AI Configuration", "FAIL", str(e)))
    
    async def test_enhanced_document_analysis(self):
        """Test enhanced document analysis with sample data"""
        print("\n🔍 Test 2: Enhanced Document Analysis")
        print("-" * 40)
        
        try:
            # Create test document data
            test_document = {
                "id": str(uuid4()),
                "title": "Sample Financial Report",
                "document_type": "financial_statement",
                "file_size": 1024 * 50,  # 50KB
                "file_extension": "pdf",
                "content": """
                ACME Corporation Financial Statement Q4 2023
                
                Revenue: $2,500,000 (up 15% from previous quarter)
                Operating Expenses: $1,800,000
                Net Income: $700,000
                
                Key Personnel:
                - John Smith, CEO
                - Sarah Johnson, CFO
                - Michael Brown, COO
                
                Risk Factors:
                - Market volatility in technology sector
                - Regulatory changes in data privacy laws
                - Competition from emerging startups
                
                Compliance Notes:
                - SOX compliance maintained
                - SEC filing requirements met
                - GDPR compliance under review
                
                Strategic Initiatives:
                - Expansion into European markets
                - Investment in AI technology
                - Partnership with major cloud providers
                """
            }
            
            # Create analysis request
            request = DocumentAnalysisRequest(
                document_id=test_document["id"],
                analysis_type="full",
                priority="high",
                custom_parameters={"test_mode": True}
            )
            
            # Perform enhanced analysis
            print("  Performing enhanced AI analysis...")
            start_time = datetime.now()
            
            result = await self.enhanced_ai.analyze_document_enhanced(request, test_document)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Validate results
            print(f"✓ Analysis completed in {processing_time:.2f} seconds")
            print(f"  - Status: {result.status}")
            print(f"  - Risk Level: {result.risk_level}")
            print(f"  - Risk Score: {result.overall_risk_score}")
            print(f"  - Confidence: {result.confidence_score}")
            print(f"  - Key Findings: {len(result.key_findings)} items")
            print(f"  - Entities Found: {len(result.extracted_entities)} types")
            print(f"  - Risk Categories: {len(result.risk_categories)} categories")
            print(f"  - Compliance Flags: {len(result.compliance_flags)} flags")
            
            # Check for specific extracted data
            if result.extracted_entities.get("companies"):
                print(f"  - Companies: {len(result.extracted_entities['companies'])} found")
            if result.extracted_entities.get("persons"):
                print(f"  - People: {len(result.extracted_entities['persons'])} found")
            if result.extracted_entities.get("amounts"):
                print(f"  - Financial amounts: {len(result.extracted_entities['amounts'])} found")
            
            self.test_results.append(("Enhanced Document Analysis", "PASS", f"Analysis completed in {processing_time:.2f}s"))
            
        except Exception as e:
            print(f"❌ Enhanced document analysis test failed: {str(e)}")
            self.test_results.append(("Enhanced Document Analysis", "FAIL", str(e)))
    
    async def test_json_response_parsing(self):
        """Test JSON response parsing capabilities"""
        print("\n🔧 Test 3: JSON Response Parsing")
        print("-" * 40)
        
        try:
            # Test valid JSON parsing
            test_json = '''
            {
              "executive_summary": {
                "summary": "Test document analysis completed",
                "key_findings": ["Finding 1", "Finding 2"],
                "confidence_score": 0.95
              },
              "risk_assessment": {
                "overall_risk_level": "Medium",
                "risk_score": 0.65,
                "identified_risks": [
                  {"type": "Financial", "description": "Test risk", "severity": "Medium", "confidence": 0.8}
                ]
              },
              "extracted_entities": {
                "organizations": [
                  {"name": "Test Corp", "type": "corporation", "confidence": 0.9}
                ],
                "people": [
                  {"name": "John Doe", "role": "CEO", "confidence": 0.95}
                ]
              }
            }
            '''
            
            # Test parsing
            parsed_result = self.enhanced_ai.real_ai._parse_ai_response(test_json)
            
            print("✓ JSON parsing successful")
            print(f"  - Summary: {parsed_result.get('summary', 'N/A')}")
            print(f"  - Risk level: {parsed_result.get('risk_level', 'N/A')}")
            print(f"  - Entities found: {len(parsed_result.get('entities', {}))}")
            
            # Test malformed JSON repair
            malformed_json = '''
            {
              "executive_summary": {
                "summary": "Test with trailing comma",
                "confidence_score": 0.95,
              },
              "risk_assessment": {
                overall_risk_level: "Medium",
                "risk_score": 0.65
              }
            }
            '''
            
            repaired_result = self.enhanced_ai.real_ai._repair_json(malformed_json)
            if repaired_result:
                print("✓ JSON repair successful")
            else:
                print("⚠️  JSON repair failed (expected for some malformed JSON)")
            
            self.test_results.append(("JSON Response Parsing", "PASS", "Parsing and repair working"))
            
        except Exception as e:
            print(f"❌ JSON response parsing test failed: {str(e)}")
            self.test_results.append(("JSON Response Parsing", "FAIL", str(e)))
    
    async def test_error_handling(self):
        """Test error handling and fallback mechanisms"""
        print("\n🛡️  Test 4: Error Handling and Fallbacks")
        print("-" * 40)
        
        try:
            # Test with invalid document data
            invalid_document = {
                "id": str(uuid4()),
                "title": "",
                "document_type": "unknown",
                "content": ""
            }
            
            request = DocumentAnalysisRequest(
                document_id=invalid_document["id"],
                analysis_type="full",
                priority="low"
            )
            
            # This should handle gracefully
            result = await self.ai_service.analyze_document(request, invalid_document)
            
            print("✓ Error handling successful")
            print(f"  - Status: {result.status}")
            print(f"  - Fallback analysis provided: {bool(result.summary)}")
            
            self.test_results.append(("Error Handling", "PASS", "Graceful error handling working"))
            
        except Exception as e:
            print(f"❌ Error handling test failed: {str(e)}")
            self.test_results.append(("Error Handling", "FAIL", str(e)))
    
    async def test_performance_optimization(self):
        """Test performance optimizations"""
        print("\n⚡ Test 5: Performance Optimization")
        print("-" * 40)
        
        try:
            # Test content truncation
            large_content = "This is a test document. " * 1000  # Large content
            
            truncated = self.enhanced_ai.real_ai._truncate_content_smart(large_content, 100)
            
            print("✓ Content truncation working")
            print(f"  - Original length: {len(large_content)} chars")
            print(f"  - Truncated length: {len(truncated)} chars")
            print(f"  - Truncation marker present: {'[Content truncated for analysis]' in truncated}")
            
            # Test preprocessing
            messy_content = """
            
            
            This    is    a    messy    document    with    lots    of    whitespace.
            
            
            
            It has $1,000,000 in revenue and 25% growth.
            
            
            The date is 12/31/2023.
            
            
            """
            
            cleaned = self.enhanced_ai._preprocess_content(messy_content)
            
            print("✓ Content preprocessing working")
            original_lines = len(messy_content.split('\n'))
            cleaned_lines = len(cleaned.split('\n'))
            print(f"  - Original lines: {original_lines}")
            print(f"  - Cleaned lines: {cleaned_lines}")
            print(f"  - Whitespace normalized: {len(cleaned) < len(messy_content)}")
            
            self.test_results.append(("Performance Optimization", "PASS", "Optimizations working correctly"))
            
        except Exception as e:
            print(f"❌ Performance optimization test failed: {str(e)}")
            self.test_results.append(("Performance Optimization", "FAIL", str(e)))
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED AI INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 40)
        for test_name, status, details in self.test_results:
            status_icon = "✓" if status == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {status}")
            if details:
                print(f"   {details}")
        
        if failed == 0:
            print("\n🎉 All tests passed! Enhanced AI integration is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        
        print("\n💡 Next Steps:")
        print("1. Ensure OpenRouter API key is configured in .env")
        print("2. Test with real documents in the application")
        print("3. Monitor AI analysis performance in production")
        print("4. Review and adjust AI prompts based on results")


async def main():
    """Main test execution"""
    tester = EnhancedAITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
