import os
import json
from dotenv import load_dotenv


class CFObject:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv(os.getcwd() + '/.env')

        self.zone_id = os.getenv("ZONE_ID")
        self.api_token = os.getenv("API_TOKEN")
        self.records = json.loads(os.getenv("RECORDS"))

        # URL to check if website is still up
        self.url = "http://{}".format(next(iter(self.records)))

        # Cloudflare API endpoint for updating a DNS record
        self.api_url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}"


class TelegramObject:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv(os.getcwd() + '/.env')

        self.token = os.getenv("TELEGRAM_API_KEY")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")