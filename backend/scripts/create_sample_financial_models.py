#!/usr/bin/env python3
"""
Script to create sample financial models for testing the Valuation Hub
"""
import sys
import os
import json
from datetime import datetime, timedelta
from uuid import uuid4

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db, engine
from app.models.financial_model import FinancialModel
from app.models.user import User
from app.models.organization import Organization
from app.models.deal import Deal

# Sample financial model data
SAMPLE_MODELS = [
    {
        "name": "TechFlow Industries - DCF Model",
        "description": "Discounted Cash Flow valuation model for TechFlow Industries acquisition",
        "model_type": "DCF",
        "status": "approved",
        "approval_status": "approved",
        "version": 3,
        "enterprise_value": "$2,100,000,000",
        "equity_value": "$1,950,000,000",
        "share_price": "$45.50",
        "valuation_multiple": "12.5x",
        "is_shared": True,
        "access_level": "deal_team",
        "tags": ["acquisition", "saas", "high-growth"],
        "model_data": {
            "revenue_projections": {
                "2024": 180000000,
                "2025": 234000000,
                "2026": 304200000,
                "2027": 395460000,
                "2028": 514098000
            },
            "ebitda_margins": {
                "2024": 0.18,
                "2025": 0.22,
                "2026": 0.25,
                "2027": 0.28,
                "2028": 0.30
            },
            "capex_as_percent_revenue": 0.03,
            "working_capital_change": 0.02,
            "tax_rate": 0.25,
            "terminal_growth_rate": 0.025,
            "wacc": 0.095
        },
        "assumptions": {
            "revenue_growth_rates": [0.30, 0.30, 0.30, 0.30],
            "ebitda_margin_expansion": "Gradual improvement from operational leverage",
            "discount_rate": 0.095,
            "terminal_value_method": "Gordon Growth Model",
            "key_risks": ["Market competition", "Customer concentration", "Technology disruption"]
        },
        "base_case": {
            "enterprise_value": 2100000000,
            "equity_value": 1950000000,
            "irr": 0.183,
            "multiple": 12.5
        },
        "upside_case": {
            "enterprise_value": 2520000000,
            "equity_value": 2370000000,
            "irr": 0.225,
            "multiple": 15.0
        },
        "downside_case": {
            "enterprise_value": 1680000000,
            "equity_value": 1530000000,
            "irr": 0.142,
            "multiple": 10.0
        }
    },
    {
        "name": "GreenEnergy - Comparable Analysis",
        "description": "Trading and transaction multiples analysis for renewable energy sector",
        "model_type": "Comps",
        "status": "review",
        "approval_status": "pending",
        "version": 2,
        "enterprise_value": "$1,800,000,000",
        "equity_value": "$1,650,000,000",
        "share_price": "$38.25",
        "valuation_multiple": "10.8x",
        "is_shared": True,
        "access_level": "deal_team",
        "tags": ["renewable", "energy", "growth"],
        "model_data": {
            "trading_multiples": {
                "ev_revenue_2024": 8.5,
                "ev_revenue_2025": 6.8,
                "ev_ebitda_2024": 12.2,
                "ev_ebitda_2025": 9.8,
                "pe_ratio_2024": 18.5,
                "pe_ratio_2025": 14.2
            },
            "transaction_multiples": {
                "ev_revenue_median": 9.2,
                "ev_ebitda_median": 13.5,
                "premium_to_trading": 0.15
            },
            "peer_companies": [
                {"name": "SolarTech Corp", "ev_revenue": 8.2, "ev_ebitda": 11.8},
                {"name": "WindPower Inc", "ev_revenue": 9.1, "ev_ebitda": 13.2},
                {"name": "CleanEnergy Solutions", "ev_revenue": 8.8, "ev_ebitda": 12.5}
            ]
        },
        "assumptions": {
            "peer_selection_criteria": "Pure-play renewable energy companies with >$500M revenue",
            "multiple_methodology": "Median of trading and transaction multiples",
            "adjustments": ["Size premium", "Liquidity discount", "Control premium"]
        }
    },
    {
        "name": "HealthTech - LBO Analysis",
        "description": "Leveraged buyout model for healthcare technology platform",
        "model_type": "LBO",
        "status": "draft",
        "approval_status": "pending",
        "version": 1,
        "enterprise_value": "$950,000,000",
        "equity_value": "$285,000,000",
        "share_price": "$28.50",
        "valuation_multiple": "8.5x",
        "is_shared": False,
        "access_level": "private",
        "tags": ["healthcare", "lbo", "technology"],
        "model_data": {
            "purchase_price": 950000000,
            "debt_financing": {
                "senior_debt": 475000000,
                "subordinated_debt": 190000000,
                "total_debt": 665000000
            },
            "equity_contribution": 285000000,
            "debt_to_ebitda": 5.2,
            "exit_assumptions": {
                "exit_year": 5,
                "exit_multiple": 10.0,
                "debt_paydown": 285000000
            }
        },
        "assumptions": {
            "leverage_ratio": "5.2x EBITDA at entry",
            "debt_structure": "70% debt, 30% equity",
            "operational_improvements": "15% EBITDA margin expansion over 5 years",
            "exit_strategy": "Strategic sale to larger healthcare platform"
        }
    },
    {
        "name": "RetailTech - Sum of Parts",
        "description": "Sum-of-the-parts valuation for diversified retail technology company",
        "model_type": "Sum_of_Parts",
        "status": "active",
        "approval_status": "approved",
        "version": 2,
        "enterprise_value": "$3,200,000,000",
        "equity_value": "$2,950,000,000",
        "share_price": "$52.75",
        "valuation_multiple": "14.2x",
        "is_shared": True,
        "access_level": "organization",
        "tags": ["retail", "technology", "diversified"],
        "model_data": {
            "business_segments": {
                "e_commerce_platform": {
                    "revenue": 800000000,
                    "ebitda": 160000000,
                    "multiple": 12.0,
                    "value": 1920000000
                },
                "payment_processing": {
                    "revenue": 400000000,
                    "ebitda": 120000000,
                    "multiple": 15.0,
                    "value": 1800000000
                },
                "logistics_network": {
                    "revenue": 300000000,
                    "ebitda": 45000000,
                    "multiple": 8.0,
                    "value": 360000000
                }
            },
            "corporate_adjustments": {
                "net_debt": -250000000,
                "minority_interests": -30000000,
                "excess_cash": 100000000
            }
        },
        "assumptions": {
            "segment_multiples": "Based on pure-play comparable companies",
            "synergies": "No synergies assumed in standalone valuations",
            "corporate_costs": "Allocated proportionally to segments"
        }
    }
]

def create_sample_financial_models():
    """Create sample financial models in the database"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get the first organization, user, and deal for testing
        organization = db.query(Organization).first()
        user = db.query(User).first()
        deal = db.query(Deal).first()
        
        if not organization or not user or not deal:
            print("❌ No organization, user, or deal found. Please run the database initialization script first.")
            return False
        
        print(f"📊 Creating sample financial models for organization: {organization.name}")
        print(f"👤 Using user: {user.email}")
        print(f"🤝 Using deal: {deal.title}")
        
        # Create sample financial models
        created_count = 0
        for model_data in SAMPLE_MODELS:
            # Check if model already exists
            existing_model = db.query(FinancialModel).filter(
                FinancialModel.name == model_data["name"],
                FinancialModel.organization_id == organization.id
            ).first()
            
            if existing_model:
                print(f"⏭️  Financial model already exists: {model_data['name']}")
                continue
            
            # Create financial model
            financial_model = FinancialModel(
                name=model_data["name"],
                description=model_data["description"],
                model_type=model_data["model_type"],
                status=model_data["status"],
                approval_status=model_data["approval_status"],
                version=model_data["version"],
                is_current=True,
                model_data=model_data["model_data"],
                assumptions=model_data["assumptions"],
                inputs=model_data.get("inputs", {}),
                outputs=model_data.get("outputs", {}),
                base_case=model_data.get("base_case", {}),
                upside_case=model_data.get("upside_case", {}),
                downside_case=model_data.get("downside_case", {}),
                sensitivity_analysis=model_data.get("sensitivity_analysis", {}),
                enterprise_value=model_data.get("enterprise_value"),
                equity_value=model_data.get("equity_value"),
                share_price=model_data.get("share_price"),
                valuation_multiple=model_data.get("valuation_multiple"),
                is_shared=model_data.get("is_shared", False),
                access_level=model_data.get("access_level", "deal_team"),
                collaborators=model_data.get("collaborators", []),
                tags=model_data.get("tags", []),
                notes=model_data.get("notes"),
                organization_id=organization.id,
                deal_id=deal.id,
                created_by_id=user.id
            )
            
            db.add(financial_model)
            created_count += 1
            print(f"✅ Created financial model: {model_data['name']}")
        
        db.commit()
        print(f"\n🎉 Successfully created {created_count} sample financial models!")
        print(f"📊 Total financial models in database: {db.query(FinancialModel).count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample financial models: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_financial_models():
    """List all financial models in the database"""
    db = next(get_db())
    
    try:
        models = db.query(FinancialModel).all()
        print(f"\n📋 Financial Models in database ({len(models)} total):")
        print("-" * 80)
        
        for model in models:
            print(f"📊 {model.name}")
            print(f"   Type: {model.model_type} | Status: {model.status} | Version: v{model.version}")
            print(f"   Value: {model.enterprise_value or 'N/A'} | Created: {model.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing financial models: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 DealVerse OS - Sample Financial Models Creator")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_financial_models()
    else:
        success = create_sample_financial_models()
        if success:
            print("\n📋 Listing created financial models:")
            list_financial_models()
        else:
            print("\n❌ Failed to create sample financial models")
            sys.exit(1)
