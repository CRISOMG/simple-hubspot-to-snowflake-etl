import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del .env

HUBSPOT_KEY = os.getenv("HUBSPOT_API_KEY")
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


import pandas as pd


def transform_data(deals_data, leads_data):
    print("Iniciando transformación...")

    # 1. Transformar Deals
    deals_list = []
    for deal in deals_data:
        props = deal["properties"]

        # --- NUEVA LÓGICA DE TRANSFORMACIÓN ---
        assoc_company_id = None
        # Verificamos si la asociación a 'companies' existe
        if "associations" in deal and "companies" in deal["associations"]:
            try:
                # Extraer el primer ID de compañía asociada
                assoc_company_id = deal["associations"]["companies"]["results"][0]["id"]
            except (KeyError, IndexError, TypeError):
                assoc_company_id = None  # No se encontró asociación
        # -------------------------------------

        deals_list.append(
            {
                "deal_id": deal["id"],
                "deal_name": props.get("dealname"),
                "amount": props.get("amount"),
                "stage": props.get("dealstage"),
                "created_at": props.get("createdate"),
                "associated_company_id": assoc_company_id,  # <-- NUEVA COLUMNA
            }
        )

    df_deals = pd.DataFrame(deals_list)

    # Transformaciones básicas:
    df_deals["amount"] = pd.to_numeric(df_deals["amount"]).fillna(0)  # Rellenar nulos
    df_deals["created_at"] = pd.to_datetime(df_deals["created_at"])  # Convertir a fecha

    # 2. Transformar Leads
    leads_list = []
    for lead in leads_data:
        props = lead["properties"]
        leads_list.append(
            {
                "lead_id": lead["id"],
                "email": props.get("email"),
                "first_name": props.get("firstname"),
                "last_name": props.get("lastname"),
                "status": props.get("hs_lead_status"),
                "created_at": props.get("createdate"),
            }
        )
    df_leads = pd.DataFrame(leads_list)

    # Transformaciones básicas:
    df_leads["created_at"] = pd.to_datetime(df_leads["created_at"])
    df_leads["status"] = df_leads["status"].fillna("UNKNOWN")  # Rellenar nulos

    print("Transformación completa.")
    return df_deals, df_leads


from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector


def load_data(df_deals, df_leads):
    print("Iniciando carga a Snowflake...")

    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOW_USER"),
            password=os.getenv("SNOW_PASSWORD"),
            account=os.getenv("SNOW_ACCOUNT"),
            warehouse=os.getenv("SNOW_WAREHOUSE"),
            database=os.getenv("SNOW_DATABASE"),
            schema=os.getenv("SNOW_SCHEMA"),
            role=os.getenv("SNOW_ROLE"),
        )

        print("Conexión a Snowflake exitosa.")

        # Cargar Deals
        # 'if_exists='replace'' borra la tabla y la crea de nuevo.
        # Es simple y perfecto para esta prueba.
        write_pandas(
            conn,
            df_deals,
            "DEALS",  # Nombre de la tabla en Snowflake
            auto_create_table=True,  # Crea la tabla si no existe
            overwrite=True,
            use_logical_type=True,
        )

        # Cargar Leads
        write_pandas(
            conn,
            df_leads,
            "LEADS",  # Nombre de la tabla en Snowflake
            auto_create_table=True,
            overwrite=True,
            use_logical_type=True,
        )

        print("Carga a Snowflake completada.")

    except Exception as e:
        print(f"Error cargando a Snowflake: {e}")
    finally:
        if "conn" in locals():
            conn.close()


# --- Script principal para ejecutar todo ---
if __name__ == "__main__":
    raw_deals, raw_leads = extract_data()
    clean_deals, clean_leads = transform_data(raw_deals, raw_leads)
    load_data(clean_deals, clean_leads)
