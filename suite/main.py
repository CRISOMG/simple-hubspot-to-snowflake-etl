from extract import extract_data
from transform import transform_data
from load import load_data

if __name__ == "__main__":
    raw_deals, raw_leads = extract_data()
    clean_deals, clean_leads = transform_data(raw_deals, raw_leads)
    load_data(clean_deals, clean_leads)
