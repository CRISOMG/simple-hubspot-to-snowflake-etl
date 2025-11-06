# Importa estos al inicio de tu etl.py
from typing import List, Tuple, Optional, TypedDict, Generic, TypeVar

# --- Plantillas de Tipo para la API de HubSpot ---

# 1. Define un "Tipo Genérico" que puede ser cualquier objeto (Deal, Contact, etc.)
T = TypeVar("T")


# 2. Define la "envoltura" de la API.
#    Usa Generic[T] para decir que 'results' será una lista del tipo 'T'
class HubSpotApiResponse(TypedDict, Generic[T]):
    results: List[T]
    # Aquí también iría 'paging', si lo estuvieras usando


# Un solo resultado de asociación (ej. un ID de compañía)
class HubSpotAssociationResult(TypedDict):
    id: str
    type: str


# Un grupo de asociaciones (ej. la lista de compañías)
class HubSpotAssociationGroup(TypedDict):
    results: List[HubSpotAssociationResult]


# El objeto 'associations' (que puede tener compañías o no)
class HubSpotAssociations(TypedDict):
    companies: Optional[HubSpotAssociationGroup]
    contacts: Optional[HubSpotAssociationGroup]


# Las propiedades que pides para los Deals
class HubSpotDealProperties(TypedDict):
    dealname: Optional[str]
    amount: Optional[str]  # La API devuelve números como strings
    dealstage: Optional[str]
    createdate: Optional[str]


# Las propiedades que pides para los Contacts
class HubSpotContactProperties(TypedDict):
    email: Optional[str]
    firstname: Optional[str]
    lastname: Optional[str]
    hs_lead_status: Optional[str]
    createdate: Optional[str]


# Finalmente, el objeto completo de Deal (un item de la lista 'results')
class HubSpotDealObject(TypedDict):
    id: str
    properties: HubSpotDealProperties
    associations: Optional[HubSpotAssociations]
    createdAt: str
    updatedAt: str
    archived: bool


# Y el objeto completo de Contact (un item de la lista 'results')
class HubSpotContactObject(TypedDict):
    id: str
    properties: HubSpotContactProperties
    associations: Optional[
        HubSpotAssociations
    ]  # Los contactos también pueden tener asoc.
    createdAt: str
    updatedAt: str
    archived: bool
