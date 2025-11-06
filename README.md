# 🚀 Simple HubSpot-to-Snowflake ETL

This project is a simple ETL (Extract, Transform, Load) process that demonstrates how to:

1.  Populate a HubSpot developer sandbox with realistic sample data (Companies, Contacts, and both B2B/B2C Deals).
2.  Extract this data using the HubSpot REST API.
3.  Transform the data with Pandas.
4.  Load the cleaned data into `DEALS` and `LEADS` tables in Snowflake.
5.  Analyze the results in Snowflake to measure the ratio of B2B vs. B2C deals.

-----

## 🔧 1. Configuration

This is the most important section. The project will not run without these environment variables.

### A. `.env` File

First, create your local environment file by copying the example:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in the following variables.

### B. HubSpot Configuration

You will need a **Private App Access Token**.

1.  **Create a Developer Sandbox:**

      * Go to the [HubSpot Developer](https://developers.hubspot.com/get-started) page and sign up for a free developer account. This will give you an isolated sandbox (testing environment).

2.  **Create a Private App:**

      * Inside your **new HubSpot sandbox**, navigate to **Settings** (⚙️ icon) \> **Integrations** \> **Private Apps**.
      * Click "Create a new private app" and give it a name (e.g., "Snowflake\_ETL\_App").

3.  **Set Scopes (Critical Step):**

      * Go to the **"Scopes"** tab for your new app. This is the most common point of failure.
      * You **must** grant the following permissions for the `seed.py` (write) and `etl.py` (read) scripts to work:
          * `crm.objects.companies.write`
          * `crm.objects.contacts.write`
          * `crm.objects.deals.write`
          * `crm.objects.companies.read`
          * `crm.objects.contacts.read`
          * `crm.objects.deals.read`

4.  **Get Your Access Token:**

      * After saving the scopes, go to the **"Auth"** tab.
      * Click "Show token" and copy the generated **Access Token**.

5.  **Update `.env`:**

      * Paste this token into the `HUBSPOT_API_KEY` variable in your `.env` file.

### C. Snowflake Configuration

This project uses the [Snowflake Connector for Python](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector) to connect.

1.  Log in to your Snowflake account.
2.  Find your account details. You will need your:
      * **User/Password**: Your login credentials.
      * **Account Identifier**: The first part of your Snowflake URL.
      * **Warehouse, Database, and Schema**: The compute resource and data locations you want to use.
3.  **Update `.env`:**
      * Fill in the following variables in your `.env` file based on your account:
          * `SNOW_USER=USERNAME`
          * `SNOW_PASSWORD=YourPassword`
          * `SNOW_ACCOUNT=XXXXX-XXXXXX`
          * `SNOW_WAREHOUSE=COMPUTE_WH`
          * `SNOW_DATABASE=SNOWFLAKE_LEARNING_DB`
          * `SNOW_SCHEMA=PUBLIC`

-----

## ⚙️ 2. Python Environment Setup

You must install the project dependencies in a virtual environment.

1.  **Create the virtual environment:**

    ```bash
    python3 -m venv venv
    ```

2.  **Activate the environment:**

      * On macOS / Linux:
        ```bash
        source venv/bin/activate
        ```
      * On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

3.  **Install all required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

-----

## ▶️ 3. Run the Scripts

You must run these scripts in order.

### Step 1: Populate HubSpot (Seeding)

This script will populate your HubSpot sandbox with realistic test data (5 Companies, 15 Contacts, and 15 Deals). It randomly creates B2B deals (associated with a company) and B2C deals (associated only with a contact).

```bash
python3 suite/seed.py
```

### Step 2: Run the ETL

This script connects to the HubSpot API, extracts the data you just created, transforms it with Pandas (capturing the `associated_company_id`), and loads it into `DEALS` and `LEADS` tables in Snowflake.

```bash
python3 suite/etl.py
```

-----

## 📊 4. Analyze in Snowflake

If the ETL was successful, you will have two new tables (`DEALS` and `LEADS`) in the database and schema you specified.

1.  Navigate to your database and schema in the Snowflake UI.
2.  Open a new [SQL Worksheet](https://docs.snowflake.com/en/user-guide/ui-snowsight-worksheets-gs).
3.  Run the following query to verify the B2B vs. B2C data:

> **Note:** The `write_pandas` tool automatically uppercases column names. Your query must use `ASSOCIATED_COMPANY_ID` (all caps).

```sql
SELECT
    COUNT(CASE WHEN ASSOCIATED_COMPANY_ID IS NOT NULL THEN 1 END) AS total_deals_b2b,
    COUNT(CASE WHEN ASSOCIATED_COMPANY_ID IS NULL THEN 1 END)     AS total_deals_b2c,
    COUNT(*) AS total_deals
FROM
    DEALS;
```

## 🏁 Conclusion

This is a simple example of an ETL process with the intention of measuring B2B vs. B2C Deals in Marketing Operations by analyzing CRM association data.