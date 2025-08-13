import os
import sys
import time
import json
import logging
import signal
import schedule
import requests

DEBUG = bool(os.environ["DEBUG"])
CONFIG_FILE_PATH = str(os.environ["CONFIG_FILE_PATH"])
CHECK_INTERVAL = int(os.environ["CHECK_INTERVAL"])

# https://developers.cloudflare.com/api/
BASE_API_URL = "https://api.cloudflare.com/client/v4"
IP_TRACE_URL_1 = "https://1.1.1.1/cdn-cgi/trace"
IP_TRACE_URL_2 = "https://1.0.0.1/cdn-cgi/trace"

stop_running = False
last_public_ip = ""


def load_config():
    try:
        with open(CONFIG_PATH, "r") as file:
            config = json.load(file)

        logging.info("Successfully loaded config.")
        return config
    except:
        logging.error("Failed to load config!")
        return None


def fetch_public_ip():
    ip = None

    try:
        response = requests.get(IP_TRACE_URL_1)
        ip_line = next(line for line in response.text.split(
            "\n") if line.startswith("ip="))
        ip = ip_line.split("=")[1]
        logging.info(f"Fetched public IP: {ip}")
    except:
        logging.warning(
            "Failed to fetch public IP over primary endpoint! Trying secondary endpoint...")

        try:
            response = requests.get(IP_TRACE_URL_2)
            ip_line = next(line for line in response.text.split(
                "\n") if line.startswith("ip="))
            ip = ip_line.split("=")[1]
            logging.info(f"Fetched public IP: {ip}")
        except:
            logging.error("Failed to fetch public IP over secondary endpoint!")

    return ip


def call_cloudflare_api(endpoint, method, token, data=None):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        if data:
            response = requests.request(
                method=method,
                url=BASE_API_URL + endpoint,
                headers=headers,
                json=data
            )
        else:
            response = requests.request(
                method=method,
                url=BASE_API_URL + endpoint,
                headers=headers
            )

        if response.ok:
            logging.debug(
                f"Good response while requesting endpoint '{endpoint}'.")
            return response.json()
        else:
            logging.error(
                f"Bad response while requesting endpoint '{endpoint}': {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error while requesting endpoint '{endpoint}': {e}")
        return None


def run_update():
    try:
        logging.info("Starting updating...")
        config = load_config()
        public_ip = fetch_public_ip()

        if not config or not public_ip:
            return

        if public_ip == last_public_ip:
            logging.info("Skipped updating because public IP has not changed.")
            return

        token = config["api_token"]

        for zone in config["zones"]:
            zone_id = zone["zone_id"]
            zone_info = call_cloudflare_api(f"/zones/{zone_id}", "GET", token)

            if zone_info is None or zone_info["result"]["name"] is None:
                logging.warning(f"Zone with ID '{zone_id}' was not found!")
                continue

            zone_name = zone_info["result"]["name"]
            zone_records = call_cloudflare_api(
                f"/zones/{zone_id}/dns_records?per_page=100", "GET", token)

            if zone_records is None:
                logging.warning(
                    f"Records for zone '{zone_name}' were not found!")
                continue

            zone_records = zone_records["result"]

            for subdomain in zone["subdomains"]:
                subdomain_name = subdomain["name"] if subdomain["name"] else zone_name
                subdomain_type = subdomain["type"]
                subdomain_content = subdomain["content"].replace(
                    "<PUBLIC_IP>", public_ip)
                subdomain_proxied = subdomain["proxied"] if "proxied" in subdomain.keys(
                ) else None

                subdomain_record = next(
                    (record for record in zone_records if record["name"] == subdomain_name and record["type"] == subdomain_type), None)

                if not subdomain_record:
                    logging.warning(
                        f"Record for subdomain '{subdomain_name}' with type '{subdomain_type}' was not found!")
                    continue

                subdomain_record_id = subdomain_record["id"]

                if subdomain_content != subdomain_record["content"]:
                    data = {
                        "name": subdomain_name,
                        "type": subdomain_type,
                        "content": subdomain_content
                    }

                    if subdomain_proxied:
                        data["proxied"] = subdomain_proxied

                    # response = call_cloudflare_api(f"/zones/{zone_id}/dns_records/{subdomain_record_id}", "PATCH", token, data)

                    print(data)
                    response = {"success": True}

                    if response and response["success"]:
                        logging.info(
                            f"Successfully updated record '{subdomain_name}' of type '{subdomain_type}' in zone '{zone_name}'.")
                    else:
                        logging.warning(
                            f"Failed to update record '{subdomain_name}' of type '{subdomain_type}' in zone '{zone_name}'!")
                else:
                    logging.info(
                        f"Skipped record '{subdomain_name}' of type '{subdomain_type}' in zone '{zone_name}'.")

        last_public_ip = public_ip
        logging.info("Done with updating.")
    except Exception as e:
        logging.error(f"Error while updating: {e}")


def handle_stop(signum, frame):
    global stop_running

    stop_running = True
    logging.info(f"Received signal {signum}. Stopping gracefully...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

    run_update()

    signal.signal(signal.SIGINT, handle_stop)  # CTRL + C
    signal.signal(signal.SIGTERM, handle_stop)  # Docker stop

    schedule.every(CHECK_INTERVAL).minutes.do(run_update)

    while not stop_running:
        schedule.run_pending()
        time.sleep(1)

    logging.info("Stopped.")
    sys.exit(0)
