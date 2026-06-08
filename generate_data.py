import json
import random
import os

# Set seed for reproducibility
random.seed(42)

countries = ["India", "Brazil", "Nigeria", "Indonesia"]
sectors = ["Manufacturing", "Retail", "Logistics", "Technology"]

# Sample names, cities, streets for generating realistic values
data_pool = {
    "India": {
        "owners": ["Rajesh Kumar", "Amit Patel", "Priya Sharma", "Vikram Singh", "Sneha Reddy", "Arjun Mehta", "Sanjay Dutt", "Deepika Padukone", "Anil Kapoor", "Rohan Gupta"],
        "cities": ["Mumbai", "Bangalore", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata"],
        "streets": ["MG Road", "Link Road", "Station Road", "Jubilee Hills", "Whitefield", "Koramangala"],
        "biz_names": ["AeroTech", "Bharat", "Chola", "Dravida", "Elite", "Ganga", "Hind", "Indus", "Jyoti", "Kalyan"],
    },
    "Brazil": {
        "owners": ["Lucas Silva", "Gabriel Santos", "Julia Costa", "Mateus Oliveira", "Ana Souza", "Bruno Lima", "Carla Pereira", "Diego Alves", "Felipe Melo", "Beatriz Rocha"],
        "cities": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Salvador", "Brasília", "Curitiba", "Fortaleza"],
        "streets": ["Avenida Paulista", "Rua Augusta", "Avenida Atlântica", "Rua das Flores", "Rua Bahia"],
        "biz_names": ["Alfa", "Brasil", "Cruzeiro", "Delta", "Estrela", "Fluminense", "Gaucho", "Horizonte", "Ipanema", "Jardim"],
    },
    "Nigeria": {
        "owners": ["Chinelo Okeke", "Babajide Adebayo", "Emeka Obi", "Ngozi Uzor", "Ibrahim Musa", "Tunde Folawiyo", "Chioma Nnaji", "Abubakar Shehu", "Funmi Balogun", "Olumide Bakare"],
        "cities": ["Lagos", "Abuja", "Port Harcourt", "Ibadan", "Kano", "Enugu", "Benin City"],
        "streets": ["Alausa Way", "Bode Thomas St", "Herbert Macaulay Way", "Garki Ave", "Wuse Road"],
        "biz_names": ["Afri", "Benue", "Calabar", "Duma", "Eko", "Futa", "Gbagada", "Hausa", "Ibadan", "Jesa"],
    },
    "Indonesia": {
        "owners": ["Adi Wijaya", "Siti Rahma", "Budi Santoso", "Dewi Lestari", "Agung Wibowo", "Rian Hidayat", "Indah Permata", "Joko Widodo", "Rudi Hartono", "Sri Mulyani"],
        "cities": ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Makassar", "Yogyakarta"],
        "streets": ["Jalan Sudirman", "Jalan Thamrin", "Jalan Gajah Mada", "Jalan Dago", "Jalan Malioboro"],
        "biz_names": ["Agung", "Bumi", "Cipta", "Dunia", "Eka", "Fajar", "Garuda", "Harapan", "Indo", "Jaya"],
    }
}

biz_suffixes = {
    "Manufacturing": ["Industries", "Manufacturing", "Factory", "Productions", "Systems"],
    "Retail": ["Traders", "Retailers", "Mart", "Stores", "Supermarket"],
    "Logistics": ["Logistics", "Transport", "Express", "Carriers", "Shipping"],
    "Technology": ["Tech Solutions", "Software", "Digital", "Technologies", "Labs"]
}

# Generate 4 fraud profiles to be reused in fraud cases and applications (for fraud ring simulation)
blacklisted_phones = [
    "+91 98765 43210",
    "+55 11 98765-4321",
    "+234 803 111 2222",
    "+62 812-3456-7890"
]

blacklisted_addresses = [
    "123 Fraud Lane, Mumbai, India",
    "Avenida Paulista 1000, São Paulo, Brazil",
    "45 Alausa Way, Ikeja, Lagos, Nigeria",
    "Sudirman Kav 21, Jakarta, Indonesia"
]

fraud_reasons = [
    "Identity theft / Stolen credentials",
    "Forged bank statements & financial history",
    "Defaulted on multiple identity-theft loans",
    "Straw company setup / Shell corporation"
]

# Generate fraud_cases collection (should have these 4 blacklisted details, plus a couple of others)
fraud_cases = []
for i in range(4):
    fraud_cases.append({
        "case_id": f"FC{i+1:03d}",
        "reason": fraud_reasons[i],
        "phone": blacklisted_phones[i],
        "address": blacklisted_addresses[i]
    })
# Add 2 more historical fraud cases to make it 6 total
fraud_cases.append({
    "case_id": "FC005",
    "reason": "Suspicious business registration mismatch",
    "phone": "+91 91234 56789",
    "address": "456 Fake St, Bangalore, India"
})
fraud_cases.append({
    "case_id": "FC006",
    "reason": "Multiple simultaneous applications under different names",
    "phone": "+55 21 91234-5678",
    "address": "Rua Copacabana 500, Rio de Janeiro, Brazil"
})

# Generate 100 applications, businesses, and loan_history
applications = []
businesses = []
loan_history = []

# Keep track of generated names to avoid duplicates
generated_names = set()

# Helper to generate unique business name
def gen_business_name(country, sector):
    pool = data_pool[country]["biz_names"]
    suffixes = biz_suffixes[sector]
    while True:
        base = random.choice(pool)
        suffix = random.choice(suffixes)
        country_suffix = "Pvt Ltd" if country == "India" else "Ltda" if country == "Brazil" else "Ltd" if country == "Nigeria" else "PT"
        name = f"{base} {suffix} {country_suffix}"
        if name not in generated_names:
            generated_names.add(name)
            return name

# Generate 100 records
for idx in range(100):
    app_id = f"APP{idx+1:03d}"
    
    # Even distribution of countries and sectors
    country = countries[idx % 4]
    sector = sectors[(idx // 4) % 4]
    
    business_name = gen_business_name(country, sector)
    owner_name = random.choice(data_pool[country]["owners"])
    years_in_business = random.randint(1, 15)
    
    # 10% fraud cases (indexes 0, 10, 20, 30, 40, 50, 60, 70, 80, 90)
    is_fraud = (idx % 10 == 0)
    
    phone = ""
    address = ""
    
    if is_fraud:
        # Reuse blacklisted phones/addresses
        blacklist_idx = (idx // 10) % 4
        phone = blacklisted_phones[blacklist_idx]
        address = blacklisted_addresses[blacklist_idx]
        decision = "Rejected"
        business_status = "Unable to Verify"
        repayment_risk = "High"
    else:
        # Generate normal phone and address
        city = random.choice(data_pool[country]["cities"])
        street = random.choice(data_pool[country]["streets"])
        building_num = random.randint(10, 999)
        
        if country == "India":
            phone = f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}"
            address = f"{building_num}, {street}, {city}, India"
        elif country == "Brazil":
            phone = f"+55 11 9{random.randint(7000, 9999)}-{random.randint(1000, 9999)}"
            address = f"{street} {building_num}, {city}, Brazil"
        elif country == "Nigeria":
            phone = f"+234 803 {random.randint(100, 999)} {random.randint(1000, 9999)}"
            address = f"{building_num} {street}, {city}, Nigeria"
        elif country == "Indonesia":
            phone = f"+62 812-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            address = f"{street} No. {building_num}, {city}, Indonesia"
            
        # Distribute decisions: ~60% Approved, ~20% Rejected, ~20% Manual Review
        r = random.random()
        if r < 0.60:
            decision = "Approved"
            business_status = "Verified"
            repayment_risk = "Low"
        elif r < 0.80:
            decision = "Rejected"
            business_status = "Unable to Verify"
            repayment_risk = "High"
        else:
            decision = "Manual Review"
            business_status = "Partially Verified"
            repayment_risk = "Medium"

    loan_amount = random.randint(50, 2000) * 1000  # $50,000 to $2,000,000
    revenue = loan_amount * random.uniform(1.2, 5.0)
    existing_debt = loan_amount * random.uniform(0.0, 0.6)
    email = f"info@{business_name.lower().replace(' ', '')}.com"
    website = f"www.{business_name.lower().replace(' ', '')}.com"
    
    # Construct application document
    app_doc = {
        "application_id": app_id,
        "business_name": business_name,
        "owner_name": owner_name,
        "country": country,
        "industry": sector,
        "years_in_business": years_in_business,
        "loan_amount": int(loan_amount),
        "revenue": int(revenue),
        "existing_debt": int(existing_debt),
        "address": address,
        "phone": phone,
        "email": email,
        "website": website,
        "decision": decision
    }
    applications.append(app_doc)
    
    # Construct business document
    # If years_in_business > 3 and not fraud, they may have a previous loan
    prev_loans = []
    if years_in_business > 3 and not is_fraud:
        prev_loan_dec = "Approved" if decision == "Approved" else random.choice(["Approved", "Rejected"])
        prev_loans.append({
            "loan_id": f"L{idx+100:03d}",
            "amount": int(loan_amount * 0.7),
            "decision": prev_loan_dec
        })
        
    biz_doc = {
        "business_name": business_name,
        "owner_name": owner_name,
        "country": country,
        "years_in_business": years_in_business,
        "status": business_status,
        "previous_loans": prev_loans
    }
    businesses.append(biz_doc)
    
    # Construct loan history document
    prev_loan_history = []
    for l in prev_loans:
        status = "Completed" if l["decision"] == "Approved" and random.random() > 0.1 else "Defaulted" if l["decision"] == "Approved" else "N/A"
        prev_loan_history.append({
            "loan_id": l["loan_id"],
            "amount": l["amount"],
            "decision": l["decision"],
            "repayment_status": status
        })
        
    history_doc = {
        "business_name": business_name,
        "previous_loans": prev_loan_history
    }
    loan_history.append(history_doc)

# Save files
workspace_dir = "c:/Users/smgal/Documents/hw"
with open(os.path.join(workspace_dir, "applications.json"), "w", encoding="utf-8") as f:
    json.dump(applications, f, indent=2)

with open(os.path.join(workspace_dir, "fraud_cases.json"), "w", encoding="utf-8") as f:
    json.dump(fraud_cases, f, indent=2)

with open(os.path.join(workspace_dir, "businesses.json"), "w", encoding="utf-8") as f:
    json.dump(businesses, f, indent=2)

with open(os.path.join(workspace_dir, "loan_history.json"), "w", encoding="utf-8") as f:
    json.dump(loan_history, f, indent=2)

print("Generated and saved 100 records for each collection successfully!")
