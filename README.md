# simple-hubspot-to-snowflake-etl


### HubSpot Developer Sadbox Configuration

Create a [Developer Sabox Account](https://offers.hubspot.com/free-cms-developer-sandbox). For more account details see [getting-started/account-types](https://developers.hubspot.com/docs/getting-started/account-types).


# Filling .env.example

### HubSpot Credentials Configuration

Create a [HubSpot Private App](https://developers.hubspot.com/docs/apps/legacy-apps/private-apps/overview), In order to [Make API calls with your app’s access token](https://developers.hubspot.com/docs/apps/legacy-apps/private-apps/overview#make-api-calls-with-your-app%E2%80%99s-access-token)
  and get **HUBSPOT_ACCESS_TOKEN** enviroment variable selecting your hubspot private app from `Sidebar Tab "Developer" > Legacy Apps > "Your Private App Name"` or `Header Setting Icon > Integrations > Connected Apps >  "Your Private App Name"` in Tab `Auth` copy the **Access Token**.

### Snowflake Credentials Configuration

We use [Snowflake Connector for Python](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector) and the [the-default-authenticator](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect#connecting-using-the-default-authenticator), For login credentials navigate to `Sidebar Account Details Pop-up > Connect a tool to Snowflake` then you`ll see a modal with account data to configure your snow enviroment variables in the .env.example.

# Prepare Python enviroment

Run `python3 -m venv venv` and `source venv/bin/activate` to create and load a virtual enviroment for python.

Run `pip install - r requirements.txt` after load python venv for install dependencies.

# Run Scripts

Run `python3 seed.py` for populate your hubspot cms with example data of Contact, Companies and Deals. Keep in mind the detail of random Contact assosiations with Companies in order to create B2B or B2C Deals.

Run `python3 etl.py` for connect to hubspot api rest, get Contacts and Deals, transform data with pandas and load to snowflake with snowflake-python-connector.

# Analytics in Snowflake

Create a [SQL Worksheet](https://docs.snowflake.com/en/user-guide/ui-snowsight-worksheets-gs) in SNOWFLAKE_LEARNING_DB database over PUBLIC schema and write:

```
SELECT
    COUNT(CASE WHEN DEALS."associated_company_id" IS NOT NULL THEN 1 END) AS total_deals_b2b,
    COUNT(CASE WHEN DEALS."associated_company_id" IS NULL THEN 1 END)     AS total_deals_b2c,
    COUNT(*) AS total_deals
FROM
    DEALS;
```
