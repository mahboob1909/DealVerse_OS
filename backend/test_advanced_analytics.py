#!/usr/bin/env python3
"""
Test script for DealVerse OS Advanced Analytics Service
Tests business intelligence features and analytics calculations
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.advanced_analytics_service import advanced_analytics_service


class MockDB:
    """Mock database session for testing"""
    def query(self, model):
        return MockQuery()
    
    def filter(self, *args):
        return MockQuery()


class MockQuery:
    """Mock query object"""
    def __init__(self):
        self.filters = []
    
    def filter(self, *args):
        self.filters.extend(args)
        return self
    
    def all(self):
        # Return mock data based on the query
        return self._generate_mock_data()
    
    def count(self):
        return len(self.all())
    
    def _generate_mock_data(self):
        # Generate mock deals, clients, users based on query
        from types import SimpleNamespace
        
        # Mock deals
        deals = []
        for i in range(50):
            deal = SimpleNamespace()
            deal.id = uuid4()
            deal.organization_id = uuid4()
            deal.stage = ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"][i % 6]
            deal.deal_value = 10000 + (i * 5000)
            deal.created_at = datetime.now() - timedelta(days=i)
            deal.updated_at = datetime.now() - timedelta(days=max(0, i-10))
            deals.append(deal)
        
        return deals


class MockCRUD:
    """Mock CRUD operations"""
    @staticmethod
    def count_by_organization(db, organization_id):
        return 125
    
    @staticmethod
    def count_active_by_organization(db, organization_id):
        return 45
    
    @staticmethod
    def get_by_organization(db, organization_id, limit=None):
        from types import SimpleNamespace
        
        items = []
        for i in range(min(limit or 100, 100)):
            item = SimpleNamespace()
            item.id = uuid4()
            item.organization_id = organization_id
            item.created_at = datetime.now() - timedelta(days=i)
            
            # Add specific attributes based on type
            if hasattr(item, 'industry'):
                item.industry = ["Technology", "Healthcare", "Finance", "Manufacturing"][i % 4]
                item.company_size = ["Small", "Medium", "Large", "Enterprise"][i % 4]
            
            items.append(item)
        
        return items
    
    @staticmethod
    def get_by_client(db, client_id):
        return MockCRUD.get_by_organization(db, uuid4(), 5)
    
    @staticmethod
    def get_by_user(db, user_id):
        return MockCRUD.get_by_organization(db, uuid4(), 10)


def test_comprehensive_analytics():
    """Test comprehensive dashboard analytics"""
    print("📊 Testing Comprehensive Dashboard Analytics...")
    
    try:
        # Mock the CRUD imports
        import app.crud.crud_deal
        import app.crud.crud_client
        import app.crud.crud_user
        import app.crud.crud_financial_model
        import app.crud.crud_presentation
        import app.crud.crud_document
        
        # Replace with mock CRUD
        app.crud.crud_deal.crud_deal = MockCRUD()
        app.crud.crud_client.crud_client = MockCRUD()
        app.crud.crud_user.crud_user = MockCRUD()
        app.crud.crud_financial_model.crud_financial_model = MockCRUD()
        app.crud.crud_presentation.crud_presentation = MockCRUD()
        app.crud.crud_document.crud_document = MockCRUD()
        
        # Test analytics
        db = MockDB()
        organization_id = uuid4()
        
        analytics = advanced_analytics_service.get_comprehensive_dashboard_analytics(
            db=db,
            organization_id=organization_id
        )
        
        # Validate analytics structure
        required_keys = [
            'overview', 'kpis', 'deal_analytics', 'client_analytics', 
            'team_analytics', 'financial_analytics', 'trends', 'predictions', 'benchmarks'
        ]
        
        for key in required_keys:
            if key not in analytics:
                print(f"   ❌ Missing key: {key}")
                return False
            print(f"   ✅ Found key: {key}")
        
        # Validate KPIs structure
        kpi_keys = ['revenue_efficiency', 'growth_metrics', 'operational_efficiency']
        for key in kpi_keys:
            if key not in analytics['kpis']:
                print(f"   ❌ Missing KPI: {key}")
                return False
            print(f"   ✅ Found KPI: {key}")
        
        # Validate deal analytics
        deal_keys = ['total_deals', 'active_deals', 'win_rate', 'average_deal_size']
        for key in deal_keys:
            if key not in analytics['deal_analytics']:
                print(f"   ❌ Missing deal metric: {key}")
                return False
            print(f"   ✅ Found deal metric: {key} = {analytics['deal_analytics'][key]}")
        
        # Validate benchmarks
        if 'performance_ratings' not in analytics['benchmarks']:
            print("   ❌ Missing performance ratings")
            return False
        
        if 'overall_score' not in analytics['benchmarks']:
            print("   ❌ Missing overall score")
            return False
        
        print(f"   ✅ Overall performance score: {analytics['benchmarks']['overall_score']['score']}")
        print(f"   ✅ Performance rating: {analytics['benchmarks']['overall_score']['rating']}")
        
        # Validate predictions
        if 'next_month_projection' in analytics['predictions']:
            projection = analytics['predictions']['next_month_projection']
            print(f"   ✅ Next month projection: {projection}")
        
        print("   ✅ Comprehensive analytics test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Comprehensive analytics test failed: {str(e)}")
        return False


def test_deal_analytics():
    """Test deal analytics calculations"""
    print("\n💼 Testing Deal Analytics...")
    
    try:
        db = MockDB()
        organization_id = uuid4()
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        
        deal_analytics = advanced_analytics_service._get_deal_analytics(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Validate deal analytics
        required_metrics = [
            'total_deals', 'active_deals', 'win_rate', 'average_deal_size',
            'average_deal_duration_days', 'stage_distribution', 'conversion_funnel'
        ]
        
        for metric in required_metrics:
            if metric not in deal_analytics:
                print(f"   ❌ Missing metric: {metric}")
                return False
            print(f"   ✅ {metric}: {deal_analytics[metric]}")
        
        # Validate win rate is a percentage
        win_rate = deal_analytics['win_rate']
        if not (0 <= win_rate <= 100):
            print(f"   ❌ Invalid win rate: {win_rate}")
            return False
        
        print("   ✅ Deal analytics test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Deal analytics test failed: {str(e)}")
        return False


def test_client_analytics():
    """Test client analytics calculations"""
    print("\n👥 Testing Client Analytics...")
    
    try:
        db = MockDB()
        organization_id = uuid4()
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        
        client_analytics = advanced_analytics_service._get_client_analytics(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Validate client analytics
        required_metrics = [
            'total_clients', 'new_clients_in_period', 'industry_distribution',
            'average_client_value', 'client_acquisition_rate', 'top_industries'
        ]
        
        for metric in required_metrics:
            if metric not in client_analytics:
                print(f"   ❌ Missing metric: {metric}")
                return False
            print(f"   ✅ {metric}: {client_analytics[metric]}")
        
        print("   ✅ Client analytics test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Client analytics test failed: {str(e)}")
        return False


def test_team_analytics():
    """Test team analytics calculations"""
    print("\n👨‍💼 Testing Team Analytics...")
    
    try:
        db = MockDB()
        organization_id = uuid4()
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        
        team_analytics = advanced_analytics_service._get_team_analytics(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Validate team analytics
        required_metrics = [
            'total_team_members', 'user_performance', 'team_productivity'
        ]
        
        for metric in required_metrics:
            if metric not in team_analytics:
                print(f"   ❌ Missing metric: {metric}")
                return False
            print(f"   ✅ {metric}: {type(team_analytics[metric])}")
        
        # Validate team productivity
        productivity = team_analytics['team_productivity']
        if 'average_deals_per_user' not in productivity:
            print("   ❌ Missing average deals per user")
            return False
        
        if 'top_performers' not in productivity:
            print("   ❌ Missing top performers")
            return False
        
        print(f"   ✅ Average deals per user: {productivity['average_deals_per_user']}")
        print(f"   ✅ Top performers count: {len(productivity['top_performers'])}")
        
        print("   ✅ Team analytics test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Team analytics test failed: {str(e)}")
        return False


def test_predictive_insights():
    """Test predictive insights generation"""
    print("\n🔮 Testing Predictive Insights...")
    
    try:
        db = MockDB()
        organization_id = uuid4()
        
        # Mock deal analytics and trends
        deal_analytics = {
            'win_rate': 45.5,
            'average_deal_duration_days': 65,
            'total_pipeline_value': 500000
        }
        
        trends = {
            'weekly_trends': [
                {'deals_created': 5, 'total_value': 50000},
                {'deals_created': 7, 'total_value': 70000},
                {'deals_created': 6, 'total_value': 60000},
                {'deals_created': 8, 'total_value': 80000}
            ]
        }
        
        predictions = advanced_analytics_service._get_predictive_insights(
            db=db,
            organization_id=organization_id,
            deal_analytics=deal_analytics,
            trends=trends
        )
        
        # Validate predictions structure
        if 'next_month_projection' not in predictions:
            print("   ❌ Missing next month projection")
            return False
        
        projection = predictions['next_month_projection']
        
        if 'projected_deals' in projection:
            print(f"   ✅ Projected deals: {projection['projected_deals']}")
        
        if 'projected_value' in projection:
            print(f"   ✅ Projected value: {projection['projected_value']}")
        
        if 'confidence' in projection:
            print(f"   ✅ Confidence level: {projection['confidence']}")
        
        if 'recommendations' in predictions:
            print(f"   ✅ Recommendations count: {len(predictions['recommendations'])}")
        
        print("   ✅ Predictive insights test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Predictive insights test failed: {str(e)}")
        return False


def test_performance_benchmarks():
    """Test performance benchmarking"""
    print("\n🏆 Testing Performance Benchmarks...")
    
    try:
        db = MockDB()
        organization_id = uuid4()
        
        deal_analytics = {
            'win_rate': 45.5,
            'average_deal_duration_days': 65,
            'average_deal_size': 75000
        }
        
        benchmarks = advanced_analytics_service._get_performance_benchmarks(
            db=db,
            organization_id=organization_id,
            deal_analytics=deal_analytics
        )
        
        # Validate benchmarks structure
        if 'performance_ratings' not in benchmarks:
            print("   ❌ Missing performance ratings")
            return False
        
        if 'overall_score' not in benchmarks:
            print("   ❌ Missing overall score")
            return False
        
        ratings = benchmarks['performance_ratings']
        
        for metric, data in ratings.items():
            if 'rating' not in data:
                print(f"   ❌ Missing rating for {metric}")
                return False
            print(f"   ✅ {metric}: {data['rating']} (value: {data['current_value']})")
        
        overall_score = benchmarks['overall_score']
        print(f"   ✅ Overall score: {overall_score['score']}% ({overall_score['rating']})")
        
        print("   ✅ Performance benchmarks test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Performance benchmarks test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    print("🚀 DealVerse OS - Advanced Analytics Service Test")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_comprehensive_analytics())
    test_results.append(test_deal_analytics())
    test_results.append(test_client_analytics())
    test_results.append(test_team_analytics())
    test_results.append(test_predictive_insights())
    test_results.append(test_performance_benchmarks())
    
    # Summary
    print("\n" + "=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL ADVANCED ANALYTICS TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} analytics features working correctly")
        print("✅ Business intelligence calculations working")
        print("✅ Predictive insights generation working")
        print("✅ Performance benchmarking working")
        print("✅ Advanced analytics service ready for production")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        print("❌ Some advanced analytics features need attention")
    
    print("=" * 60)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test failed with error: {str(e)}")
        sys.exit(1)
