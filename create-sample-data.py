#!/usr/bin/env python3
"""
Sample Data Generator for DealVerse OS
Creates realistic deals, clients, and documents for testing
"""

import requests
import json
import random
from datetime import datetime, timedelta


# Sample data templates
COMPANIES = [
    "TechFlow Solutions", "DataVault Inc", "CloudSync Corp", "InnovateLabs",
    "FinanceForward", "HealthTech Dynamics", "EcoEnergy Systems", "RetailNext",
    "LogisticsPro", "MediaStream Co", "CyberShield Security", "AgriTech Innovations",
    "UrbanDev Properties", "BioMed Research", "AutoTech Motors", "EduPlatform Inc"
]

INDUSTRIES = [
    "Technology", "Healthcare", "Financial Services", "Energy", "Retail",
    "Manufacturing", "Real Estate", "Biotechnology", "Automotive", "Education"
]

DEAL_TYPES = ["M&A", "IPO", "Private Equity", "Debt Financing", "Strategic Investment"]

DEAL_STAGES = ["prospecting", "pitch", "negotiation", "due_diligence", "closing"]

CLIENT_TYPES = ["prospect", "active", "inactive"]

FIRST_NAMES = ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "Robert", "Jennifer", "William", "Jessica"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]


def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": "admin@dealverse.com",
        "password": "changethis"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login/json",
        json=login_data
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None


def create_client(token, client_data):
    """Create a client"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        "http://localhost:8000/api/v1/clients",
        json=client_data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to create client: {response.status_code}")
        return None


def create_deal(token, deal_data):
    """Create a deal"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        "http://localhost:8000/api/v1/deals",
        json=deal_data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to create deal: {response.status_code}")
        return None


def generate_sample_clients(token, count=10):
    """Generate sample clients"""
    print(f"📊 Creating {count} sample clients...")
    clients = []
    
    for i in range(count):
        company = random.choice(COMPANIES)
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        industry = random.choice(INDUSTRIES)
        
        client_data = {
            "name": f"{first_name} {last_name}",
            "company": company,
            "title": random.choice(["CEO", "CFO", "VP Finance", "Director", "Manager"]),
            "email": f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '')}.com",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "industry": industry,
            "company_size": random.choice(["startup", "small", "medium", "large", "enterprise"]),
            "annual_revenue": random.choice(["<$1M", "$1M-$10M", "$10M-$100M", "$100M-$1B", ">$1B"]),
            "client_type": random.choice(CLIENT_TYPES),
            "relationship_status": random.choice(["cold", "warm", "hot"]),
            "source": random.choice(["referral", "website", "event", "cold_outreach", "linkedin"]),
            "notes": f"Potential client in {industry} sector. Initial contact made.",
            "tags": [industry.lower(), "potential", "q4-2024"]
        }
        
        client = create_client(token, client_data)
        if client:
            clients.append(client)
            print(f"✅ Created client: {client_data['name']} at {client_data['company']}")
    
    return clients


def generate_sample_deals(token, clients, count=8):
    """Generate sample deals"""
    print(f"📊 Creating {count} sample deals...")
    deals = []
    
    for i in range(count):
        company = random.choice(COMPANIES)
        deal_type = random.choice(DEAL_TYPES)
        stage = random.choice(DEAL_STAGES)
        
        # Random deal value between $1M and $500M
        deal_value = random.randint(1000000, 500000000)
        
        # Random client (if available)
        client_id = random.choice(clients)["id"] if clients and random.choice([True, False]) else None
        
        deal_data = {
            "title": f"{company} {deal_type}",
            "description": f"{deal_type} transaction for {company} in the {random.choice(INDUSTRIES)} sector.",
            "deal_type": deal_type,
            "deal_value": deal_value,
            "currency": "USD",
            "fee_percentage": round(random.uniform(1.0, 3.5), 2),
            "stage": stage,
            "status": "active",
            "probability": str(random.randint(20, 95)),
            "expected_close_date": (datetime.now() + timedelta(days=random.randint(30, 180))).date().isoformat(),
            "target_company": company,
            "target_industry": random.choice(INDUSTRIES),
            "target_location": random.choice(["New York, NY", "San Francisco, CA", "Chicago, IL", "Boston, MA", "Austin, TX"]),
            "target_revenue": random.randint(10000000, 1000000000),
            "target_employees": random.choice(["50-100", "100-500", "500-1000", "1000-5000", "5000+"]),
            "lead_banker": random.choice([f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}" for _ in range(5)]),
            "ai_score": str(random.randint(60, 95)),
            "notes": f"Promising {deal_type} opportunity with strong fundamentals.",
            "client_id": client_id,
            "tags": [deal_type.lower().replace(" ", "_"), stage, "2024"],
            "risk_factors": random.sample([
                "Market volatility", "Regulatory changes", "Competition", 
                "Economic downturn", "Technology disruption"
            ], random.randint(1, 3)),
            "opportunities": random.sample([
                "Market expansion", "Cost synergies", "Technology integration",
                "Brand strengthening", "Operational efficiency"
            ], random.randint(1, 3))
        }
        
        deal = create_deal(token, deal_data)
        if deal:
            deals.append(deal)
            print(f"✅ Created deal: {deal_data['title']} (${deal_value:,})")
    
    return deals


def main():
    """Main function to generate sample data"""
    print("🚀 DealVerse OS Sample Data Generator")
    print("=" * 50)
    
    # Get authentication token
    print("🔐 Authenticating...")
    token = get_auth_token()
    if not token:
        print("❌ Authentication failed. Make sure the backend is running.")
        return
    
    print("✅ Authentication successful")
    
    # Generate sample clients
    clients = generate_sample_clients(token, count=12)
    
    # Generate sample deals
    deals = generate_sample_deals(token, clients, count=10)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Sample Data Generation Complete")
    print("=" * 50)
    print(f"✅ Created {len(clients)} clients")
    print(f"✅ Created {len(deals)} deals")
    
    total_deal_value = sum(deal.get("deal_value", 0) for deal in deals)
    print(f"💰 Total pipeline value: ${total_deal_value:,}")
    
    print("\n🎯 Next Steps:")
    print("1. Refresh your dashboard to see the new data")
    print("2. Explore the deals in Prospect AI module")
    print("3. Check client relationships")
    print("4. Review deal analytics")
    
    print("\n🌐 Access your dashboard: http://localhost:3000/dashboard")


if __name__ == "__main__":
    main()
