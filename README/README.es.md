# 🚀 Simple HubSpot-to-Snowflake ETL

Este proyecto es un simple proceso ETL (Extracción, Transformación y Carga) que demuestra cómo:

1.  Poblar un *sandbox* de HubSpot con datos de muestra (Compañías, Contactos y Deals B2B/B2C).
2.  Extraer estos datos usando la API REST de HubSpot.
3.  Transformar los datos con Pandas.
4.  Cargar los datos limpios en tablas (`DEALS`, `LEADS`) dentro de Snowflake.
5.  Analizar el resultado en Snowflake para medir la proporción de negociaciones B2B vs. B2C.

-----

## 🔧 1. Configuración de Credenciales

Este es el paso más importante. El proyecto no funcionará sin estas variables de entorno.

### A. Archivo `.env`

Primero, crea tu propio archivo de entorno a partir del ejemplo:

```bash
cp .env.example .env
```

Ahora, abre el archivo `.env` y rellena las siguientes variables.

### B. HubSpot

Necesitarás un **Token de Acceso de una Aplicación Privada (Private App)**.

1.  **Crea un Sandbox de Desarrollador:** Ve a [HubSpot Developer](https://developers.hubspot.com/get-started) y crea una cuenta gratuita. Esto te dará un *sandbox* (entorno de pruebas) aislado.
2.  **Crea una App Privada:**
      * Dentro de tu *sandbox* de HubSpot, ve a **Configuración** (icono ⚙️) \> **Integraciones** \> **Aplicaciones Privadas**.
      * Crea una nueva app (ej. "ETL para Snowflake").
      * Ve a la pestaña **"Scopes" (Permisos)**. Esto es **crítico**. Otorga los siguientes permisos a tu app para que los scripts `seed.py` y `etl.py` puedan funcionar:
          * `crm.objects.companies.write`
          * `crm.objects.companies.read`
          * `crm.objects.contacts.write`
          * `crm.objects.contacts.read`
          * `crm.objects.deals.write`
          * `crm.objects.deals.read`
3.  **Obtén el Token:** Tras crear la app, te mostrará un **Token de Acceso**.
4.  **Actualiza `.env`:** Copia este token y pégalo en la variable `HUBSPOT_API_KEY` de tu archivo `.env`.

### C. Snowflake

El script usará el [Conector de Python para Snowflake](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector) para conectarse.

1.  Inicia sesión en tu cuenta de Snowflake.
2.  Encuentra los detalles de tu cuenta (normalmente en la esquina inferior izquierda).
3.  **Actualiza `.env`:** Rellena las siguientes variables:
      * `SNOW_USER`: Tu nombre de usuario de Snowflake (ej. `CRISOMG`).
      * `SNOW_PASSWORD`: Tu contraseña.
      * `SNOW_ACCOUNT`: Tu identificador de cuenta (ej. `RXXDNZQ-RH92607`).
      * `SNOW_WAREHOUSE`: El *warehouse* que usará el script (ej. `COMPUTE_WH`).
      * `SNOW_DATABASE`: La base de datos donde se crearán las tablas (ej. `SNOWFLAKE_LEARNING_DB`).
      * `SNOW_SCHEMA`: El esquema donde se crearán las tablas (ej. `PUBLIC`).

-----

## ⚙️ 2. Entorno de Python

Necesitarás un entorno virtual para instalar las dependencias del proyecto.

1.  **Crea el entorno virtual:**

    ```bash
    python3 -m venv venv
    ```

2.  **Activa el entorno:**

      * En macOS / Linux:
        ```bash
        source venv/bin/activate
        ```
      * En Windows:
        ```bash
        .\venv\Scripts\activate
        ```

3.  **Instala las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

-----

## ▶️ 3. Ejecutar los Scripts

Asegúrate de ejecutar los scripts en este orden.

### Paso 1: Poblar HubSpot (Seeding)

Este script llenará tu *sandbox* de HubSpot con datos de prueba realistas (5 Compañías, 15 Contactos y 15 Deals). Crea aleatoriamente Deals B2B (asociados a una compañía) y B2C (asociados solo a un contacto).

```bash
python3 seed.py
```

### Paso 2: Ejecutar el ETL

Este script se conectará a la API de HubSpot, extraerá los datos que acabas de crear, los transformará con Pandas (notando cuáles Deals tienen un `associated_company_id` y cuáles no) y los cargará en Snowflake.

```bash
python3 etl.py
```

-----

## 📊 4. Analizar en Snowflake

Si el ETL fue exitoso, tendrás dos nuevas tablas en Snowflake: `DEALS` y `LEADS`.

1.  Ve a tu base de datos y esquema en Snowflake (los que definiste en `.env`).
2.  Crea una nueva "SQL Worksheet".
3.  Ejecuta la siguiente consulta para verificar tu objetivo:

<!-- end list -->

```sql
SELECT
    COUNT(CASE WHEN ASSOCIATED_COMPANY_ID IS NOT NULL THEN 1 END) AS total_deals_b2b,
    COUNT(CASE WHEN ASSOCIATED_COMPANY_ID IS NULL THEN 1 END)     AS total_deals_b2c,
    COUNT(*) AS total_deals
FROM
    DEALS;
```