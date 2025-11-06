import requests
import os
import time
from dotenv import load_dotenv
from faker import Faker
import random
import json


def get_industries():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, "industries.json")

        with open(json_path, "r") as f:
            valid_industries = json.load(f)

        print(f"Se cargaron {len(valid_industries)} industrias desde industries.json")

        return valid_industries
    except FileNotFoundError:
        print(
            "ERROR: No se encontró el archivo 'industries.json'. Usando lista de fallback."
        )
        valid_industries = ["COMPUTER_SOFTWARE", "BANKING"]


industries = get_industries()
# --- Configuración ---
load_dotenv()
API_KEY = os.getenv("HUBSPOT_API_KEY")
if not API_KEY:
    raise EnvironmentError("No se encontró HUBSPOT_API_KEY en el archivo .env")

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Endpoints de la API V3
COMPANIES_URL = "https://api.hubapi.com/crm/v3/objects/companies"
CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
DEALS_URL = "https://api.hubapi.com/crm/v3/objects/deals"

# Instancia de Faker
faker = Faker()

# Listas para guardar los IDs creados
company_ids = []
contact_ids = []

# --- 1. Crear Compañías ---
print("--- Iniciando creación de Compañías ---")
for _ in range(5):
    properties = {
        "name": faker.company(),
        "industry": faker.random_element(elements=industries),
        "domain": faker.domain_name(),
        "city": faker.city(),
        "country": faker.country(),
    }
    payload = {"properties": properties}

    try:
        r = requests.post(COMPANIES_URL, headers=HEADERS, json=payload)
        r.raise_for_status()  # Lanza error si la API falla

        company_id = r.json()["id"]
        company_ids.append(company_id)
        print(f"Compañía creada con ID: {company_id}")

    except requests.exceptions.HTTPError as e:
        print(f"Error creando compañía: {e.response.text}")

    time.sleep(0.4)  # Pausa para no saturar el rate limit de la API

# --- 2. Crear Contactos (y asociarlos a Compañías) ---
print("\n--- Iniciando creación de Contactos ---")
for company_id in company_ids:
    for _ in range(3):  # 3 contactos por compañía
        properties = {
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "email": faker.unique.email(),
            "phone": faker.phone_number(),
            # ¡Esta es la propiedad clave para que sean "Leads"!
            "hs_lead_status": faker.random_element(
                elements=("NEW", "OPEN", "IN_PROGRESS", "UNQUALIFIED")
            ),
        }

        # Payload de asociación (Tipo ID 2 = Contacto a Compañía)
        association = {
            "to": {"id": company_id},
            "types": [
                {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 1}
            ],
        }

        payload = {"properties": properties, "associations": [association]}

        try:
            r = requests.post(CONTACTS_URL, headers=HEADERS, json=payload)
            r.raise_for_status()

            contact_id = r.json()["id"]
            # Guardamos el contact_id Y a qué compañía pertenece para el paso 3
            contact_ids.append({"contact_id": contact_id, "company_id": company_id})
            print(
                f"  Contacto creado con ID: {contact_id} (Asociado a Compañía {company_id})"
            )

        except requests.exceptions.HTTPError as e:
            print(f"Error creando contacto: {e.response.text}")

        time.sleep(0.4)

# --- 3. Crear Deals (y asociarlos a Compañías y Contactos) ---
print("\n--- Iniciando creación de Deals (B2B y B2C) ---")
for item in contact_ids:
    contact_id = item["contact_id"]
    company_id = item["company_id"]

    # --- NUEVA LÓGICA DE DECISIÓN ---
    # Decidimos aleatoriamente si será B2B o B2C
    deal_type = random.choice(["B2B", "B2C"])

    properties = {
        # Añadimos el tipo al nombre para verlo fácil en la UI de HubSpot
        "dealname": f"Deal ({deal_type}) - {faker.bs()}",
        "amount": faker.random_int(min=5000, max=100000),
        "dealstage": "appointmentscheduled",
        "pipeline": "default",
    }

    # Asociación 1: Deal a Contacto (Siempre presente)
    assoc_contact = {
        "to": {"id": contact_id},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}],
    }

    # Lista de asociaciones
    associations = [assoc_contact]

    log_message = f"    Deal (B2C) creado... (Asociado a Contacto {contact_id})"

    # Asociación 2: Deal a Compañía (SOLO si es B2B)
    if deal_type == "B2B":
        assoc_company = {
            "to": {"id": company_id},
            "types": [
                {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}
            ],
        }
        associations.append(assoc_company)
        log_message = f"    Deal (B2B) creado... (Asociado a Contacto {contact_id} y Compañía {company_id})"

    # El payload ahora usa la lista de asociaciones condicional
    payload = {"properties": properties, "associations": associations}

    try:
        r = requests.post(DEALS_URL, headers=HEADERS, json=payload)
        r.raise_for_status()

        deal_id = r.json()["id"]
        # Usamos un log más claro
        print(log_message.replace("...", f"con ID: {deal_id}"))

    except requests.exceptions.HTTPError as e:
        print(f"Error creando deal: {e.response.text}")

    time.sleep(0.4)

print("\n--- Proceso de 'seeding' completado ---")
print(f"Total Compañías creadas: {len(company_ids)}")
print(f"Total Contactos (Leads) creados: {len(contact_ids)}")
print(f"Total Deals creados: {len(contact_ids)}")
