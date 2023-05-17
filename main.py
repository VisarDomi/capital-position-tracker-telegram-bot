import time
import requests
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
import os

############ logging ###############

def pprint(data):
    return json.dumps(data, indent=4)

logger = logging.getLogger("MyLogger")
logger.setLevel(logging.ERROR)

if not os.path.exists('logs'):
    os.makedirs('logs')
handler = TimedRotatingFileHandler("./logs/app.log", when="midnight", interval=1)
handler.suffix = "%Y%m%d"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

########### loading from .env #######
load_dotenv()  # take environment variables from .env.

telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
capital_api_key = os.getenv('CAPITAL_API_KEY')
capital_login = os.getenv('CAPITAL_LOGIN')
capital_password = os.getenv('CAPITAL_PASSWORD')

############ telegram ###########

telegram_api_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'

def send_message(text):
    while True:
        response = requests.post(
            telegram_api_url,
            data={'chat_id': telegram_chat_id, 'text': text}
        )

        if response.status_code == 200:
            logger.info("send_message")
            break

        elif response.status_code == 429:
            retry_after = response.json()['parameters']['retry_after']
            logger.warning(f"Rate limit hit, retrying after {retry_after} seconds...")
            time.sleep(retry_after)

        else:
            logger.error(f"Failed to send message: {response.content}")
            break

def send_update(previous_positions, current_positions, cst_token, security_token):
    previous_dealIds = {pos['position']['dealId']: pos for pos in previous_positions['positions']}
    current_dealIds = {pos['position']['dealId']: pos for pos in current_positions['positions']}

    for dealId, position in previous_dealIds.items():
        if dealId not in current_dealIds:
            logger.info("send_update closed")
            message = f"""
            {position['position']['direction']} order closed:
            Trading: {position['market']['instrumentName']}
            """
            logger.info("send_position")
            send_message(message)

    for dealId, position in current_dealIds.items():
        if dealId not in previous_dealIds:
            logger.info("send_update opened")
            position_details = get_position_details(dealId, cst_token, security_token)
            if position_details:
                message = f"""
                {position_details['position']['direction']} order opened:
                Trading: {position_details['market']['instrumentName']}
                Position price: {position_details['position']['level']}
                """
                logger.info("send_position")
                send_message(message)

########## capital ##############

capital_base_url = "https://api-capital.backend-capital.com/api/v1"
POLLING_TIME = 1


capital_positions_url = f"{capital_base_url}/positions"
capital_session_url = f"{capital_base_url}/session"


def get_session():
    headers = {
        "X-CAP-API-KEY": capital_api_key,
        "Content-Type": "application/json"
    }

    body = {
        "identifier": capital_login,
        "password": capital_password,
        "encryptedPassword": False
    }

    response = requests.post(capital_session_url, json=body, headers=headers)

    if response.status_code == 200:
        cst_token = response.headers.get("CST")
        security_token = response.headers.get("X-SECURITY-TOKEN")
        logger.info(f"CST: {cst_token}")
        logger.info(f"X-SECURITY-TOKEN: {security_token}")
        return cst_token, security_token
    else:
        logger.error(f"get_session Request failed with status code {response.status_code}")
        return None

def get_positions(cst_token, security_token):
    headers = {
        "X-SECURITY-TOKEN": security_token,
        "CST": cst_token
    }

    response = requests.get(capital_positions_url, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        logger.info(f"get_positions json response: {pprint(json_response)}")
        return json_response
    else:
        logger.error(f"get_positions Request failed with status code {response.status_code}")
        return None

def get_position_details(dealId, cst_token, security_token):
    deal_url = f"{capital_positions_url}/{dealId}"

    headers = {
        "X-SECURITY-TOKEN": security_token,
        "CST": cst_token
    }

    response = requests.get(deal_url, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        logger.info(f"get_position_details json response: {pprint(json_response)}")
        return json_response
    else:
        logger.error(f"get_position_details Request failed with status code {response.status_code}")
        return None

####### main functions #########

def poll_capital(seconds=60):
    session = get_session()
    if session is None:
        logger.error("Failed to get session, stopping execution.")
        return
    cst_token, security_token = session

    previous_positions = get_positions(cst_token, security_token)
    if previous_positions is None:
        logger.error("Failed to get previous positions, stopping execution.")
        return

    while True:
        current_positions = get_positions(cst_token, security_token)
        if current_positions is None:
            logger.error("Failed to get current positions, stopping execution.")
            return

        send_update(previous_positions, current_positions, cst_token, security_token)

        previous_positions = current_positions

        logger.info(f"sleeping for {seconds} seconds...")
        time.sleep(seconds)

if __name__ == "__main__":
    poll_capital(seconds=POLLING_TIME)
