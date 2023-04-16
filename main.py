import requests
import logging
import json
import os
from dotenv import load_dotenv


def get_current_ip():
    # Retrieve the current public IP address
    response = requests.get("https://api.ipify.org")
    if response.status_code == 200:
        return response.text.strip()
    else:
        return None


def update_dns_record(ip, record_name, API_URL, API_TOKEN, ZONE_ID, RECORDS):
    # Update the DNS record with the new IP address
    url = API_URL.format(ZONE_ID, RECORDS[record_name])
    headers = {
        "Authorization": "Bearer {}".format(API_TOKEN),
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": record_name,
        "content": ip,
        "ttl": 120,
        "proxied": True
    }
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


def check_domain_status(URL):
    # Check whether the domain is properly responding
    response = requests.get(URL)
    return response.ok


def load_vars():
    # Cloudflare API credentials
    ZONE_ID = os.getenv("ZONE_ID")
    API_TOKEN = os.getenv("API_TOKEN")
    RECORDS = json.loads(os.getenv("RECORDS"))

    # URL to check
    URL = "http://{}".format(next(iter(RECORDS)))

    # Cloudflare API endpoint for updating a DNS record
    API_URL = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}"
    return ZONE_ID, API_TOKEN, RECORDS, URL, API_URL


def main():
    # Load environment variables from .env file
    load_dotenv(os.getcwd() + "/.env")
    # add logging
    logging.basicConfig(filename='CloudflareIPUpdater.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    ZONE_ID, API_TOKEN, RECORDS, URL, API_URL = load_vars()

    # Check the domain status
    if not check_domain_status(URL):
        # If the domain is not responding, update the DNS record
        ip = get_current_ip()

        # if this is true find a new api to get ip
        if ip == None:
            logging.critical("Could not retrieve current IP address")
            return
        
        for record_name in RECORDS:
            update_dns_record(ip, record_name, API_URL, API_TOKEN, ZONE_ID, RECORDS)

        logging.warning("Updated DNS record with new IP address: {}".format(ip))
    else:
        logging.info("Domain is responding correctly")


if __name__ == "__main__":
    main()
