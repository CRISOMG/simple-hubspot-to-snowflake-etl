import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del .env

HUBSPOT_KEY = os.getenv("HUBSPOT_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {HUBSPOT_KEY}"}

# Endpoint para Deals
deals_url = "https://api.hubapi.com/crm/v3/objects/deals"
# Endpoint para Contacts (Leads)
leads_url = "https://api.hubapi.com/crm/v3/objects/contacts"

# Parámetros para pedir solo las propiedades que te interesan
params = {
    "properties": "dealname,amount,dealstage,createdate,email,firstname,lastname,hs_lead_status",
    "associations": "company,contact",
}


def extract_data():
    print("Iniciando extracción...")
    # Extraer Deals
    deals_response = requests.get(deals_url, headers=headers, params=params)
    deals_response.raise_for_status()
    deals_data = deals_response.json()["results"]

    # Extraer Leads (Contacts)
    leads_response = requests.get(leads_url, headers=headers, params=params)
    leads_response.raise_for_status()

    leads_data = leads_response.json()["results"]

    print(f"Se extrajeron {len(deals_data)} deals y {len(leads_data)} leads.")
    return deals_data, leads_data
