from faker import Faker
import random
import requests
import json
import time
from logmagix import Logger,LogLevel
import re

log = Logger(prefix="Tempmail", level=LogLevel.DEBUG,github_repository="https://github.com/rilspratama/Meshchan.git")

def sleepy_time():
    log.error("Server respone too many requests")
    time.sleep(60)

headers = {
  'Content-Type': "application/json"
}


def get_domains():
    response = requests.get("https://api.mail.tm/domains")
    while True:
        if response.status_code == 200:
            data = response.json()
            data_list_dm = data.get("hydra:member", "No domains availabel")
            domains = []
            for dm in data_list_dm:
                domains.append(dm.get("domain"))
            return domains
        elif response.status_code == 429:
            sleepy_time()
        else:
            log.error(f"Error >>> {response.status_code}")
            return None

def create_email(address,password):
    payload = json.dumps({
        "address": address,
        "password": password
    })
    response = requests.post("https://api.mail.tm/accounts", headers=headers,data=payload)
    while True:
        if response.status_code == 201:
            data = response.json()
            address = data.get("address")
            log.info(f"Email created ID >>> {address}")
            return address
        elif response.status_code == 429:
            sleepy_time()
        else:
            log.error(f"Error >>> {response.status_code}")
            return None
        
        
        
def get_token(email,password):
    payload = json.dumps({
        "address": email,
        "password": password
    })
    response = requests.post("https://api.mail.tm/token", data=payload,headers=headers)
    while True:
        if response.status_code == 200:
            data = response.json()
            log.info(f"Token successfully retrieved.")
            return data.get("token")
        elif response.status_code == 429:
            sleepy_time()
        else:
            log.error(f"Error >>> {response.status_code}")
            return None


def get_latest_message(access_token):
    _headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.mail.tm/messages", headers=_headers)
    while True:
        if response.status_code == 200:
            data = response.json()
            messages = data.get("hydra:member")
            messages = messages[0]
            return messages.get("id")
        elif response.status_code == 429:
            sleepy_time()
        else:
            log.error(f"Error >>> {response.status_code}")
            return None


def get_message(access_token,id):
    _headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"https://api.mail.tm/messages/{id}", headers=_headers)
    while True:
        if response.status_code == 200:
            data = response.json()
            messages = data.get("text")
            return messages
        elif response.status_code == 429:
            sleepy_time()
        else:
            log.error(f"Error >>> {response.status_code}")
            return None


def get_otp(text):
    otp_match = re.search(r'\b[0-9]{4}\b', text)
    if otp_match:
        return otp_match.group()