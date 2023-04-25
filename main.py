import requests
import logging
import os
from dotenv import load_dotenv
import telegram
import asyncio
from util import CFObject


def get_current_ip():
    # Retrieve the current public IP address
    response = requests.get("https://api.ipify.org")
    if response.status_code == 200:
        return response.text.strip()
    else:
        return None


def update_dns_record(ip, record_name):
    # Update the DNS record with the new IP address
    url = cfObj.api_url.format(cfObj.zone_id, cfObj.records[record_name])
    headers = {
        "Authorization": "Bearer {}".format(cfObj.api_token),
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


async def send_notification(message):
    bot = telegram.Bot(token=os.getenv("TELEGRAM_API_KEY"))
    await bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)


def runLogic():
    # Check the domain status
    if not check_domain_status(cfObj.url):
        # If the domain is not responding, update the DNS record
        ip = get_current_ip()

        # if this is true find a new api to get ip
        if ip == None:
            logging.critical("Could not retrieve current IP address")
            asyncio.run(send_notification("CRITICAL: Could not retrieve current IP address."))
            return
        
        for record_name in cfObj.records:
            update_dns_record(ip, record_name)

        logging.warning(f"Updated DNS record with new IP address: {ip}")
        asyncio.run(send_notification(f"WARNING: Updated DNS record with new IP address: {ip}"))
    else:
        logging.info("Domain is responding correctly")


def load():
    # Load environment variables from .env file
    load_dotenv(os.getcwd() + '/.env')
    
    # add logging
    logging.basicConfig(filename='CloudflareIPUpdater.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    # load github vars
    global cfObj
    cfObj = CFObject()

    # windows has issues
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    # load all vars
    load()
    
    try:
        runLogic()
    except Exception as e:
        logging.exception("Exception")
        asyncio.run(send_notification(f"EXCEPTION: {str(e)}"))


if __name__ == "__main__":
    main()