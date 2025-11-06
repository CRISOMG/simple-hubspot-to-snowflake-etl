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
