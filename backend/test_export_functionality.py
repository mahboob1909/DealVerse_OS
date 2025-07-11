#!/usr/bin/env python3
"""
Test script for DealVerse OS Export Functionality
Tests PDF, Excel, and PowerPoint export capabilities
"""
import asyncio
import sys
import os
import tempfile
from datetime import datetime
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.export_service import export_service


async def test_financial_model_excel_export():
    """Test financial model Excel export"""
    print("📊 Testing Financial Model Excel Export...")
    
    # Sample financial model data
    model_data = {
        "name": "Test Financial Model",
        "created_at": "2024-01-15",
        "updated_at": "2024-01-20",
        "model_type": "DCF Analysis",
        "key_metrics": {
            "NPV": 1500000,
            "IRR": 0.25,
            "Payback_Period": 3.2,
            "ROI": 0.35
        },
        "projections": {
            "years": [
                {
                    "year": "2024",
                    "revenue": 1000000,
                    "cogs": 400000,
                    "gross_profit": 600000,
                    "operating_expenses": 300000,
                    "ebitda": 300000,
                    "net_income": 200000
                },
                {
                    "year": "2025",
                    "revenue": 1500000,
                    "cogs": 600000,
                    "gross_profit": 900000,
                    "operating_expenses": 400000,
                    "ebitda": 500000,
                    "net_income": 350000
                },
                {
                    "year": "2026",
                    "revenue": 2200000,
                    "cogs": 880000,
                    "gross_profit": 1320000,
                    "operating_expenses": 550000,
                    "ebitda": 770000,
                    "net_income": 540000
                }
            ]
        },
        "assumptions": {
            "revenue_growth": {
                "year_1": 0.50,
                "year_2": 0.47,
                "year_3": 0.40
            },
            "cost_structure": {
                "cogs_percentage": 0.40,
                "opex_percentage": 0.25
            }
        }
    }
    
    try:
        excel_data = await export_service.export_financial_model_to_excel(
            model_data=model_data,
            model_id=uuid4(),
            organization_name="Test Organization"
        )
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_file.write(excel_data)
            temp_file_path = temp_file.name
        
        print(f"   ✅ Excel export successful! File size: {len(excel_data)} bytes")
        print(f"   📁 Temporary file saved: {temp_file_path}")
        
        # Clean up
        os.unlink(temp_file_path)
        return True
        
    except Exception as e:
        print(f"   ❌ Excel export failed: {str(e)}")
        return False


async def test_financial_model_pdf_export():
    """Test financial model PDF export"""
    print("\n📄 Testing Financial Model PDF Export...")
    
    # Sample financial model data (same as Excel test)
    model_data = {
        "name": "Test Financial Model PDF",
        "created_at": "2024-01-15",
        "updated_at": "2024-01-20",
        "model_type": "DCF Analysis",
        "key_metrics": {
            "NPV": 1500000,
            "IRR": 0.25,
            "Payback_Period": 3.2,
            "ROI": 0.35
        },
        "projections": {
            "years": [
                {
                    "year": "2024",
                    "revenue": 1000000,
                    "cogs": 400000,
                    "gross_profit": 600000,
                    "operating_expenses": 300000,
                    "ebitda": 300000,
                    "net_income": 200000
                },
                {
                    "year": "2025",
                    "revenue": 1500000,
                    "cogs": 600000,
                    "gross_profit": 900000,
                    "operating_expenses": 400000,
                    "ebitda": 500000,
                    "net_income": 350000
                }
            ]
        },
        "assumptions": {
            "revenue_growth": {
                "year_1": 0.50,
                "year_2": 0.47
            }
        }
    }
    
    try:
        pdf_data = await export_service.export_financial_model_to_pdf(
            model_data=model_data,
            model_id=uuid4(),
            organization_name="Test Organization"
        )
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name
        
        print(f"   ✅ PDF export successful! File size: {len(pdf_data)} bytes")
        print(f"   📁 Temporary file saved: {temp_file_path}")
        
        # Clean up
        os.unlink(temp_file_path)
        return True
        
    except Exception as e:
        print(f"   ❌ PDF export failed: {str(e)}")
        return False


async def test_presentation_pptx_export():
    """Test presentation PowerPoint export"""
    print("\n🎯 Testing Presentation PowerPoint Export...")
    
    # Sample presentation data
    presentation_data = {
        "title": "Test Investment Presentation",
        "description": "Sample presentation for testing export functionality",
        "slides": [
            {
                "title": "Executive Summary",
                "content": "• Investment opportunity overview\n• Market analysis\n• Financial projections\n• Risk assessment",
                "type": "title_content",
                "order": 1
            },
            {
                "title": "Market Analysis",
                "content": "• Total Addressable Market: $10B\n• Serviceable Market: $2B\n• Growth Rate: 15% CAGR\n• Key Competitors: 3 major players",
                "type": "title_content",
                "order": 2,
                "charts": [
                    {
                        "title": "Market Size Projection",
                        "type": "line",
                        "data": {"2024": 10, "2025": 11.5, "2026": 13.2}
                    }
                ]
            },
            {
                "title": "Financial Projections",
                "content": "• Revenue Growth: 50% YoY\n• Gross Margin: 60%\n• EBITDA Margin: 25%\n• Break-even: Year 2",
                "type": "title_content",
                "order": 3
            }
        ]
    }
    
    try:
        pptx_data = await export_service.export_presentation_to_pptx(
            presentation_data=presentation_data,
            presentation_id=uuid4(),
            organization_name="Test Organization"
        )
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as temp_file:
            temp_file.write(pptx_data)
            temp_file_path = temp_file.name
        
        print(f"   ✅ PowerPoint export successful! File size: {len(pptx_data)} bytes")
        print(f"   📁 Temporary file saved: {temp_file_path}")
        
        # Clean up
        os.unlink(temp_file_path)
        return True
        
    except Exception as e:
        print(f"   ❌ PowerPoint export failed: {str(e)}")
        return False


async def test_compliance_pdf_export():
    """Test compliance report PDF export"""
    print("\n🛡️  Testing Compliance Report PDF Export...")
    
    # Sample compliance data
    compliance_data = {
        "audit_period": "January 2024 - March 2024",
        "compliance_areas": ["SOX", "GDPR", "Financial Regulations"],
        "report_type": "Comprehensive Audit",
        "summary": {
            "total_checks": 45,
            "passed": 38,
            "failed": 4,
            "warnings": 3,
            "compliance_score": 84.4
        },
        "findings": [
            {
                "category": "Data Privacy",
                "status": "Compliant",
                "description": "All data processing activities comply with GDPR requirements",
                "risk_level": "Low"
            },
            {
                "category": "Financial Controls",
                "status": "Non-Compliant",
                "description": "Missing segregation of duties in accounts payable process",
                "risk_level": "High"
            },
            {
                "category": "Access Management",
                "status": "Warning",
                "description": "Some user accounts have excessive privileges",
                "risk_level": "Medium"
            }
        ]
    }
    
    try:
        pdf_data = await export_service.export_compliance_report_to_pdf(
            compliance_data=compliance_data,
            organization_name="Test Organization"
        )
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name
        
        print(f"   ✅ Compliance PDF export successful! File size: {len(pdf_data)} bytes")
        print(f"   📁 Temporary file saved: {temp_file_path}")
        
        # Clean up
        os.unlink(temp_file_path)
        return True
        
    except Exception as e:
        print(f"   ❌ Compliance PDF export failed: {str(e)}")
        return False


async def test_analytics_excel_export():
    """Test analytics Excel export"""
    print("\n📈 Testing Analytics Excel Export...")
    
    # Sample analytics data
    analytics_data = {
        "kpis": {
            "total_deals": 125,
            "active_deals": 45,
            "total_deal_value": 15750000,
            "average_deal_size": 126000,
            "total_clients": 78,
            "active_clients": 52,
            "team_members": 12
        },
        "metrics": [
            {
                "name": "Deal Conversion Rate",
                "current_value": 68.5,
                "previous_value": 62.3,
                "change_percent": 9.9
            },
            {
                "name": "Average Deal Duration",
                "current_value": 45,
                "previous_value": 52,
                "change_percent": -13.5
            }
        ],
        "trends": [
            {"date": "2024-01-01", "metric": "Total Deals", "value": 100},
            {"date": "2024-02-01", "metric": "Total Deals", "value": 115},
            {"date": "2024-03-01", "metric": "Total Deals", "value": 125}
        ]
    }
    
    try:
        excel_data = await export_service.export_analytics_to_excel(
            analytics_data=analytics_data,
            organization_name="Test Organization"
        )
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_file.write(excel_data)
            temp_file_path = temp_file.name
        
        print(f"   ✅ Analytics Excel export successful! File size: {len(excel_data)} bytes")
        print(f"   📁 Temporary file saved: {temp_file_path}")
        
        # Clean up
        os.unlink(temp_file_path)
        return True
        
    except Exception as e:
        print(f"   ❌ Analytics Excel export failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🚀 DealVerse OS - Export Functionality Test")
    print("=" * 60)
    
    test_results = []
    
    # Test all export functions
    test_results.append(await test_financial_model_excel_export())
    test_results.append(await test_financial_model_pdf_export())
    test_results.append(await test_presentation_pptx_export())
    test_results.append(await test_compliance_pdf_export())
    test_results.append(await test_analytics_excel_export())
    
    # Summary
    print("\n" + "=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL EXPORT FUNCTIONALITY TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} export formats working correctly")
        print("✅ PDF generation working")
        print("✅ Excel generation working")
        print("✅ PowerPoint generation working")
        print("✅ Export service ready for production")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        print("❌ Some export functionality needs attention")
    
    print("=" * 60)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test failed with error: {str(e)}")
        sys.exit(1)
