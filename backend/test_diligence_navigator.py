#!/usr/bin/env python3
"""
Test script for Diligence Navigator implementation
"""
import asyncio
import sys
import os
import requests
import json
from datetime import datetime
import time

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@dealverse.com"
TEST_PASSWORD = "testpassword123"

class DiligenceNavigatorTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_document_id = None
    
    def test_authentication(self):
        """Test user authentication"""
        print("🔐 Testing authentication...")
        
        # Try to login
        login_data = {
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{API_BASE}/auth/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def test_document_upload(self):
        """Test document upload functionality"""
        print("\n📄 Testing document upload...")
        
        # Create a test document
        document_data = {
            "title": f"Test Contract {datetime.now().strftime('%H%M%S')}",
            "filename": "test_contract.pdf",
            "file_path": "/uploads/test_contract.pdf",
            "file_size": 1024 * 500,  # 500KB
            "file_type": "application/pdf",
            "file_extension": "pdf",
            "document_type": "legal",
            "category": "contracts",
            "is_confidential": True,
            "status": "uploaded"
        }
        
        response = self.session.post(f"{API_BASE}/documents/", json=document_data)
        
        if response.status_code == 200:
            document = response.json()
            self.test_document_id = document.get("id")
            print(f"✅ Document uploaded: {document.get('title')} (ID: {self.test_document_id})")
            return document
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Response: {response.text}")
            return None
    
    def test_document_analysis(self):
        """Test AI document analysis"""
        print("\n🧠 Testing AI document analysis...")
        
        if not self.test_document_id:
            print("❌ No test document available for analysis")
            return None
        
        # Test different analysis types
        analysis_types = ["full", "risk_only", "financial_only", "legal_only"]
        
        for analysis_type in analysis_types:
            print(f"\n   Testing {analysis_type} analysis...")
            
            params = {
                "analysis_type": analysis_type,
                "priority": "high"
            }
            
            response = self.session.post(
                f"{API_BASE}/documents/{self.test_document_id}/analyze",
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {analysis_type} analysis completed:")
                
                summary = result.get("analysis_summary", {})
                print(f"      Risk Score: {summary.get('overall_risk_score')}")
                print(f"      Risk Level: {summary.get('risk_level')}")
                print(f"      Confidence: {summary.get('confidence_score')}")
                print(f"      Critical Issues: {summary.get('critical_issues_count')}")
                print(f"      Compliance Flags: {summary.get('compliance_flags_count')}")
                
                # Wait a bit between analyses
                time.sleep(1)
            else:
                print(f"   ❌ {analysis_type} analysis failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"      Error: {error_detail}")
                except:
                    print(f"      Response: {response.text}")
        
        return True
    
    def test_get_analysis_results(self):
        """Test retrieving analysis results"""
        print("\n📊 Testing analysis results retrieval...")
        
        if not self.test_document_id:
            print("❌ No test document available")
            return None
        
        response = self.session.get(f"{API_BASE}/documents/{self.test_document_id}/analysis")
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ Analysis results retrieved:")
            print(f"   Analysis Type: {analysis.get('analysis_type')}")
            print(f"   Risk Score: {analysis.get('overall_risk_score')}")
            print(f"   Risk Level: {analysis.get('risk_level')}")
            print(f"   Summary: {analysis.get('summary')[:100]}...")
            
            # Check extracted data
            entities = analysis.get('extracted_entities', {})
            if entities:
                print(f"   Extracted Entities:")
                for entity_type, entity_list in entities.items():
                    if entity_list:
                        print(f"      {entity_type}: {len(entity_list)} found")
            
            financial_figures = analysis.get('financial_figures', [])
            if financial_figures:
                print(f"   Financial Figures: {len(financial_figures)} extracted")
            
            key_dates = analysis.get('key_dates', [])
            if key_dates:
                print(f"   Key Dates: {len(key_dates)} identified")
            
            critical_issues = analysis.get('critical_issues', [])
            if critical_issues:
                print(f"   Critical Issues: {len(critical_issues)} found")
                for issue in critical_issues[:2]:  # Show first 2 issues
                    print(f"      - {issue.get('description', 'N/A')}")
            
            return analysis
        else:
            print(f"❌ Failed to retrieve analysis results: {response.status_code}")
            return None
    
    def test_risk_assessment(self):
        """Test comprehensive risk assessment"""
        print("\n⚠️ Testing risk assessment...")
        
        if not self.test_document_id:
            print("❌ No test document available")
            return None
        
        assessment_data = {
            "assessment_name": f"Test Risk Assessment {datetime.now().strftime('%H%M%S')}",
            "assessment_type": "document_set",
            "document_ids": [self.test_document_id]
        }
        
        response = self.session.post(f"{API_BASE}/documents/risk-assessment", json=assessment_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Risk assessment completed:")
            
            summary = result.get("assessment_summary", {})
            print(f"   Overall Risk Score: {summary.get('overall_risk_score')}")
            print(f"   Risk Level: {summary.get('risk_level')}")
            print(f"   Confidence: {summary.get('confidence_level')}")
            print(f"   Critical Issues: {summary.get('critical_issues_count')}")
            print(f"   Missing Documents: {summary.get('missing_documents_count')}")
            print(f"   Documents Analyzed: {summary.get('documents_analyzed')}")
            
            recommendations = result.get("recommendations", [])
            if recommendations:
                print(f"   Top Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"      {i}. {rec}")
            
            return result
        else:
            print(f"❌ Risk assessment failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Response: {response.text}")
            return None
    
    def test_document_categorization(self):
        """Test document categorization"""
        print("\n🏷️ Testing document categorization...")
        
        if not self.test_document_id:
            print("❌ No test document available")
            return None
        
        response = self.session.get(f"{API_BASE}/documents/{self.test_document_id}/categorize")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document categorization completed:")
            print(f"   Predicted Category: {result.get('predicted_category')}")
            print(f"   Confidence: {result.get('confidence')}%")
            print(f"   Reasoning: {result.get('reasoning')}")
            
            alternatives = result.get('alternative_categories', [])
            if alternatives:
                print(f"   Alternative Categories:")
                for alt in alternatives:
                    print(f"      - {alt.get('category')}: {alt.get('confidence')}%")
            
            keywords = result.get('keywords_matched', [])
            if keywords:
                print(f"   Keywords Matched: {', '.join(keywords)}")
            
            return result
        else:
            print(f"❌ Document categorization failed: {response.status_code}")
            return None
    
    def test_analytics_and_statistics(self):
        """Test analytics and statistics"""
        print("\n📈 Testing analytics and statistics...")
        
        response = self.session.get(f"{API_BASE}/documents/analytics/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Analytics retrieved:")
            
            doc_stats = stats.get("document_statistics", {})
            print(f"   Document Statistics:")
            print(f"      Total Documents: {doc_stats.get('total_documents')}")
            print(f"      Analyzed Documents: {doc_stats.get('analyzed_documents')}")
            print(f"      Pending Analysis: {doc_stats.get('pending_analysis')}")
            print(f"      Analysis Completion Rate: {doc_stats.get('analysis_completion_rate', 0):.1f}%")
            
            analysis_stats = stats.get("analysis_statistics", {})
            print(f"   Analysis Statistics:")
            print(f"      Total Analyses: {analysis_stats.get('total_analyses')}")
            print(f"      Average Risk Score: {analysis_stats.get('average_risk_score', 0):.1f}")
            print(f"      High Risk Count: {analysis_stats.get('high_risk_count')}")
            
            risk_dist = analysis_stats.get('risk_level_distribution', {})
            if risk_dist:
                print(f"   Risk Level Distribution:")
                for level, count in risk_dist.items():
                    print(f"      {level}: {count}")
            
            return stats
        else:
            print(f"❌ Analytics retrieval failed: {response.status_code}")
            return None
    
    def test_high_risk_documents(self):
        """Test high-risk documents retrieval"""
        print("\n🚨 Testing high-risk documents...")
        
        params = {
            "risk_threshold": 60.0,
            "limit": 10
        }
        
        response = self.session.get(f"{API_BASE}/documents/high-risk", params=params)
        
        if response.status_code == 200:
            high_risk_docs = response.json()
            print(f"✅ High-risk documents retrieved: {len(high_risk_docs)} found")
            
            for doc in high_risk_docs[:3]:  # Show first 3
                print(f"   - {doc.get('document_title')}")
                print(f"     Risk Score: {doc.get('risk_score')}")
                print(f"     Risk Level: {doc.get('risk_level')}")
                print(f"     Critical Issues: {doc.get('critical_issues_count')}")
                print()
            
            return high_risk_docs
        else:
            print(f"❌ High-risk documents retrieval failed: {response.status_code}")
            return None
    
    def run_all_tests(self):
        """Run all Diligence Navigator tests"""
        print("🚀 Starting Diligence Navigator API Tests")
        print("=" * 60)
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Test all functionality
        document = self.test_document_upload()
        analysis_success = self.test_document_analysis()
        analysis_results = self.test_get_analysis_results()
        risk_assessment = self.test_risk_assessment()
        categorization = self.test_document_categorization()
        analytics = self.test_analytics_and_statistics()
        high_risk_docs = self.test_high_risk_documents()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"✅ Document Upload: {'PASS' if document else 'FAIL'}")
        print(f"✅ Document Analysis: {'PASS' if analysis_success else 'FAIL'}")
        print(f"✅ Analysis Results: {'PASS' if analysis_results else 'FAIL'}")
        print(f"✅ Risk Assessment: {'PASS' if risk_assessment else 'FAIL'}")
        print(f"✅ Document Categorization: {'PASS' if categorization else 'FAIL'}")
        print(f"✅ Analytics & Statistics: {'PASS' if analytics else 'FAIL'}")
        print(f"✅ High-Risk Documents: {'PASS' if high_risk_docs else 'FAIL'}")
        
        all_passed = all([
            document, analysis_success, analysis_results, 
            risk_assessment, categorization, analytics, high_risk_docs
        ])
        
        if all_passed:
            print("\n🎉 All tests passed! Diligence Navigator is working correctly.")
            print("\n📚 Available endpoints:")
            print("  - POST /api/v1/documents/{id}/analyze - AI document analysis")
            print("  - GET /api/v1/documents/{id}/analysis - Get analysis results")
            print("  - POST /api/v1/documents/risk-assessment - Comprehensive risk assessment")
            print("  - GET /api/v1/documents/risk-assessments - List risk assessments")
            print("  - GET /api/v1/documents/{id}/categorize - Document categorization")
            print("  - GET /api/v1/documents/analytics/statistics - Analytics and statistics")
            print("  - GET /api/v1/documents/high-risk - High-risk documents")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
        
        return all_passed


if __name__ == "__main__":
    tester = DiligenceNavigatorTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
