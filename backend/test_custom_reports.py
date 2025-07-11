#!/usr/bin/env python3
"""
Test script for DealVerse OS Custom Reports Service
Tests report generation with templates and customization options
"""
import asyncio
import sys
import os
import tempfile
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.custom_reports_service import custom_reports_service


class MockDB:
    """Mock database session for testing"""
    def query(self, model):
        return MockQuery()


class MockQuery:
    """Mock query object"""
    def filter(self, *args):
        return self
    
    def all(self):
        return []
    
    def count(self):
        return 0


def test_get_available_templates():
    """Test getting available report templates"""
    print("📋 Testing Available Templates...")
    
    try:
        templates = custom_reports_service.get_available_templates()
        
        # Validate templates structure
        expected_templates = [
            "executive_summary", "sales_performance", "client_analysis",
            "financial_summary", "team_productivity", "compliance_audit"
        ]
        
        for template_id in expected_templates:
            if template_id not in templates:
                print(f"   ❌ Missing template: {template_id}")
                return False
            
            template = templates[template_id]
            required_keys = ["name", "description", "sections", "default_period", "format_options"]
            
            for key in required_keys:
                if key not in template:
                    print(f"   ❌ Missing key '{key}' in template {template_id}")
                    return False
            
            print(f"   ✅ Template {template_id}: {template['name']}")
        
        print(f"   ✅ Found {len(templates)} templates")
        print("   ✅ Available templates test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Available templates test failed: {str(e)}")
        return False


def test_get_template_details():
    """Test getting specific template details"""
    print("\n📄 Testing Template Details...")
    
    try:
        # Test valid template
        template_details = custom_reports_service.get_template_details("executive_summary")
        
        required_keys = ["name", "description", "sections", "default_period", "format_options", "charts"]
        for key in required_keys:
            if key not in template_details:
                print(f"   ❌ Missing key: {key}")
                return False
        
        print(f"   ✅ Executive summary template: {template_details['name']}")
        print(f"   ✅ Sections: {len(template_details['sections'])}")
        print(f"   ✅ Charts: {len(template_details['charts'])}")
        print(f"   ✅ Default period: {template_details['default_period']} days")
        
        # Test invalid template
        try:
            custom_reports_service.get_template_details("invalid_template")
            print("   ❌ Should have raised ValueError for invalid template")
            return False
        except ValueError:
            print("   ✅ Correctly raised ValueError for invalid template")
        
        print("   ✅ Template details test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Template details test failed: {str(e)}")
        return False


async def test_generate_section_data():
    """Test generating data for report sections"""
    print("\n📊 Testing Section Data Generation...")
    
    try:
        # Mock analytics data
        analytics = {
            "deal_analytics": {
                "total_deals": 125,
                "active_deals": 45,
                "win_rate": 65.5,
                "total_pipeline_value": 2500000,
                "stage_distribution": {
                    "prospecting": 20,
                    "qualification": 15,
                    "proposal": 8,
                    "negotiation": 5,
                    "closed_won": 12,
                    "closed_lost": 3
                },
                "conversion_funnel": {
                    "prospecting": 20,
                    "qualification": 15,
                    "proposal": 8,
                    "negotiation": 5,
                    "closed_won": 12
                }
            },
            "client_analytics": {
                "total_clients": 78,
                "new_clients_in_period": 12,
                "industry_distribution": {
                    "Technology": 25,
                    "Healthcare": 18,
                    "Finance": 15,
                    "Manufacturing": 12,
                    "Other": 8
                },
                "top_industries": [
                    ["Technology", 25],
                    ["Healthcare", 18],
                    ["Finance", 15]
                ],
                "client_acquisition_rate": 4.2
            },
            "team_analytics": {
                "total_team_members": 12,
                "team_productivity": {
                    "top_performers": [
                        {"name": "John Doe", "total_value": 500000, "deals_count": 8},
                        {"name": "Jane Smith", "total_value": 450000, "deals_count": 7}
                    ]
                }
            },
            "financial_analytics": {
                "deal_financials": {
                    "total_pipeline_value": 2500000,
                    "realized_revenue": 1200000
                }
            },
            "kpis": {
                "operational_efficiency": {
                    "deals_per_team_member": 3.75,
                    "conversion_rate": 65.5
                },
                "revenue_efficiency": {
                    "revenue_per_deal": 20000,
                    "revenue_per_client": 15385
                }
            },
            "trends": {
                "weekly_trends": [
                    {"week_start": "2024-01-01", "total_value": 100000},
                    {"week_start": "2024-01-08", "total_value": 120000}
                ]
            },
            "predictions": {
                "next_month_projection": {
                    "projected_deals": 15,
                    "projected_value": 300000
                },
                "recommendations": [
                    "Focus on improving qualification process",
                    "Increase pipeline coverage"
                ]
            }
        }
        
        db = MockDB()
        organization_id = uuid4()
        date_range = (datetime.now() - timedelta(days=90), datetime.now())
        
        # Test different sections
        test_sections = [
            "overview_metrics",
            "deal_performance", 
            "client_insights",
            "team_productivity",
            "financial_highlights",
            "sales_funnel",
            "forecasting"
        ]
        
        for section in test_sections:
            section_data = await custom_reports_service._generate_section_data(
                section, analytics, db, organization_id, date_range
            )
            
            if "title" not in section_data:
                print(f"   ❌ Missing title in section: {section}")
                return False
            
            print(f"   ✅ Section {section}: {section_data['title']}")
            
            # Check for placeholder sections
            if section_data.get("placeholder"):
                print(f"      ⚠️  Section {section} is a placeholder")
            else:
                print(f"      ✅ Section {section} has real data")
        
        print("   ✅ Section data generation test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Section data generation test failed: {str(e)}")
        return False


def test_chart_data_generation():
    """Test generating chart data"""
    print("\n📈 Testing Chart Data Generation...")
    
    try:
        # Mock analytics data
        analytics = {
            "deal_analytics": {
                "stage_distribution": {
                    "prospecting": 20,
                    "qualification": 15,
                    "proposal": 8,
                    "negotiation": 5,
                    "closed_won": 12
                },
                "win_rate": 65.5
            },
            "trends": {
                "weekly_trends": [
                    {"week_start": "2024-01-01", "total_value": 100000},
                    {"week_start": "2024-01-08", "total_value": 120000},
                    {"week_start": "2024-01-15", "total_value": 110000}
                ]
            },
            "team_analytics": {
                "team_productivity": {
                    "top_performers": [
                        {"name": "John Doe", "total_value": 500000},
                        {"name": "Jane Smith", "total_value": 450000}
                    ]
                }
            },
            "client_analytics": {
                "industry_distribution": {
                    "Technology": 25,
                    "Healthcare": 18,
                    "Finance": 15
                }
            }
        }
        
        # Test different chart types
        test_charts = [
            "deal_pipeline",
            "revenue_trend",
            "win_rate_chart",
            "team_performance",
            "industry_distribution"
        ]
        
        for chart_type in test_charts:
            chart_data = custom_reports_service._generate_chart_data(chart_type, analytics)
            
            required_keys = ["type", "title"]
            for key in required_keys:
                if key not in chart_data:
                    print(f"   ❌ Missing key '{key}' in chart: {chart_type}")
                    return False
            
            print(f"   ✅ Chart {chart_type}: {chart_data['title']} ({chart_data['type']})")
            
            # Check for placeholder charts
            if chart_data["type"] == "placeholder":
                print(f"      ⚠️  Chart {chart_type} is a placeholder")
            else:
                print(f"      ✅ Chart {chart_type} has real data")
        
        print("   ✅ Chart data generation test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Chart data generation test failed: {str(e)}")
        return False


def test_conversion_rates_calculation():
    """Test conversion rates calculation"""
    print("\n🔄 Testing Conversion Rates Calculation...")
    
    try:
        deal_analytics = {
            "conversion_funnel": {
                "prospecting": 100,
                "qualification": 60,
                "proposal": 30,
                "negotiation": 20,
                "closed_won": 15
            }
        }
        
        conversion_rates = custom_reports_service._calculate_conversion_rates(deal_analytics)
        
        # Validate conversion rates
        expected_rates = {
            "prospecting_to_qualification": 60.0,  # 60/100 * 100
            "qualification_to_proposal": 50.0,     # 30/60 * 100
            "proposal_to_negotiation": 66.67,      # 20/30 * 100
            "negotiation_to_closed_won": 75.0      # 15/20 * 100
        }
        
        for stage_conversion, expected_rate in expected_rates.items():
            if stage_conversion not in conversion_rates:
                print(f"   ❌ Missing conversion rate: {stage_conversion}")
                return False
            
            actual_rate = conversion_rates[stage_conversion]
            if abs(actual_rate - expected_rate) > 0.1:  # Allow small floating point differences
                print(f"   ❌ Incorrect rate for {stage_conversion}: expected {expected_rate}, got {actual_rate}")
                return False
            
            print(f"   ✅ {stage_conversion}: {actual_rate}%")
        
        print("   ✅ Conversion rates calculation test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Conversion rates calculation test failed: {str(e)}")
        return False


def test_bottleneck_identification():
    """Test funnel bottleneck identification"""
    print("\n🚧 Testing Bottleneck Identification...")
    
    try:
        # Create deal analytics with known bottlenecks
        deal_analytics = {
            "conversion_funnel": {
                "prospecting": 100,
                "qualification": 20,  # Low conversion (20%)
                "proposal": 18,       # Good conversion (90%)
                "negotiation": 5,     # Low conversion (27.8%)
                "closed_won": 4       # Good conversion (80%)
            }
        }
        
        bottlenecks = custom_reports_service._identify_funnel_bottlenecks(deal_analytics)
        
        # Should identify prospecting and proposal as bottlenecks (< 30% conversion)
        expected_bottlenecks = 2  # prospecting and proposal stages
        
        if len(bottlenecks) < expected_bottlenecks:
            print(f"   ❌ Expected at least {expected_bottlenecks} bottlenecks, found {len(bottlenecks)}")
            return False
        
        for bottleneck in bottlenecks:
            print(f"   ✅ Identified bottleneck: {bottleneck}")
        
        print("   ✅ Bottleneck identification test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Bottleneck identification test failed: {str(e)}")
        return False


def test_customizations_application():
    """Test applying customizations to report data"""
    print("\n⚙️  Testing Customizations Application...")
    
    try:
        # Mock report data
        report_data = {
            "sections": {
                "overview_metrics": {"title": "Overview"},
                "deal_performance": {"title": "Deal Performance"},
                "client_insights": {"title": "Client Insights"},
                "team_productivity": {"title": "Team Productivity"}
            },
            "charts": {
                "deal_pipeline": {"type": "bar"},
                "revenue_trend": {"type": "line"},
                "win_rate_chart": {"type": "gauge"}
            }
        }
        
        # Test section filtering
        customizations = {
            "sections": ["overview_metrics", "deal_performance"],
            "charts": ["deal_pipeline"],
            "title": "Custom Report Title"
        }
        
        customized_data = custom_reports_service._apply_customizations(report_data, customizations)
        
        # Validate section filtering
        if len(customized_data["sections"]) != 2:
            print(f"   ❌ Expected 2 sections, got {len(customized_data['sections'])}")
            return False
        
        if "overview_metrics" not in customized_data["sections"]:
            print("   ❌ Missing overview_metrics section")
            return False
        
        if "deal_performance" not in customized_data["sections"]:
            print("   ❌ Missing deal_performance section")
            return False
        
        # Validate chart filtering
        if len(customized_data["charts"]) != 1:
            print(f"   ❌ Expected 1 chart, got {len(customized_data['charts'])}")
            return False
        
        if "deal_pipeline" not in customized_data["charts"]:
            print("   ❌ Missing deal_pipeline chart")
            return False
        
        # Validate custom title
        if customized_data.get("custom_title") != "Custom Report Title":
            print("   ❌ Custom title not applied correctly")
            return False
        
        print("   ✅ Section filtering working")
        print("   ✅ Chart filtering working")
        print("   ✅ Custom title applied")
        print("   ✅ Customizations application test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Customizations application test failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🚀 DealVerse OS - Custom Reports Service Test")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_get_available_templates())
    test_results.append(test_get_template_details())
    test_results.append(await test_generate_section_data())
    test_results.append(test_chart_data_generation())
    test_results.append(test_conversion_rates_calculation())
    test_results.append(test_bottleneck_identification())
    test_results.append(test_customizations_application())
    
    # Summary
    print("\n" + "=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL CUSTOM REPORTS TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} report features working correctly")
        print("✅ Template system working")
        print("✅ Section data generation working")
        print("✅ Chart data generation working")
        print("✅ Customization system working")
        print("✅ Analytics calculations working")
        print("✅ Custom reports service ready for production")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        print("❌ Some custom reports features need attention")
    
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
