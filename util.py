import os
import json


class CFObject:
    zone_id = os.getenv("ZONE_ID")
    api_token = os.getenv("API_TOKEN")
    records = json.loads(os.getenv("RECORDS"))

    # URL to check
    url = "http://{}".format(next(iter(records)))

    # Cloudflare API endpoint for updating a DNS record
    api_url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}"