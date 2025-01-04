import requests
import time 
import json
import os
from logmagix import Logger,LogLevel,Home
import logging
from fake_useragent import UserAgent
import uuid
import random
import threading

home_screen = Home(text="IVY",align="center", adinfo1="The developers are not responsible for any misuse or potential account violations.",adinfo2="Automation Node Extension",credits="Developed by Rils")
log = Logger(prefix="BOT", level=LogLevel.DEBUG,github_repository="https://github.com/rilspratama/Meshchan.git")
ua = UserAgent(platforms=["desktop"])

stop_event = threading.Event()


def get_turnstile_token():
    params = {
        "url":"https://app.meshchain.ai/",
        "sitekey":"0x4AAAAAAA0e4lkIb7ZRG1LE"
    }
    headers = {"X-API-Key":"adcfe085cb6065d543660d32bf34bac5"}
    while True:
        response = requests.get(f"https://turnshit.biz.id/turnstile", params=params,headers=headers)
        if response.status_code == 200 and response.json().get("status") == "success":
            logging.info("Turnstile token retrieved successfully.")
            return response.json().get("result")
        else:
            logging.error("Turnstile token failed to take, try again...")



def add_account_to_cache(email, access_token, refresh_token, uid_node):
    try:
        if os.path.exists('accounts_cache.json') and os.path.getsize('accounts_cache.json') > 0:
            with open('accounts_cache.json', 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        
        existing_account = next((item for item in data if item['email'] == email), None)
        
        if existing_account:
            existing_account.update({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "uid_node": uid_node
            })
        else:
            data_new = {
                "email": email,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "uid_node": uid_node
            }
            data.append(data_new)
        
        with open("accounts_cache.json", "w") as file:
            json.dump(data, file, indent=4)
    
    except Exception as e:
        print(f"Error adding account to cache: {e}")


def check_account_cache(email):
    try:
        with open("accounts_cache.json", "r") as file:
            data = json.load(file)
        
        for items in data:
            if items["email"] == email:
                return True
        
        return False
    
    except FileNotFoundError:
        return False
    except json.JSONDecodeError:
        return False


def update_account_access_token(email,access_token):
    with open("accounts_cache.json","r") as ffile:
        data = json.load(ffile)
    for items in data:
        if items["email"] == email:
            items["access_token"] = access_token
            break
    with open("accounts_cache.json","w") as file:
        json.dump(data,file,indent=4)


def update_account_refresh_token(email,refresh_token):
    with open("accounts_cache.json","r") as ffile:
        data = json.load(ffile)
    for items in data:
        if items["email"] == email:
            items["refresh_token"] = refresh_token
            break
    with open("accounts_cache.json","w") as file:
        json.dump(data,file,indent=4)


def get_access_token_from_cache(email):
    with open("accounts_cache.json", "r") as file:
        data = json.load(file)
    
    for account in data:
        if account["email"] == email:
            return account["access_token"]


def get_refresh_token_from_cache(email):
    with open("accounts_cache.json", "r") as file:
        data = json.load(file)
    
    for account in data:
        if account["email"] == email:
            return account["refresh_token"]

def get_uid_node_from_cache(email):
    with open("accounts_cache.json", "r") as file:
        data = json.load(file)
    
    for account in data:
        if account["email"] == email:
            return account["uid_node"]


def login(res,email,password,headers):
    headers["origin"] = "https://app.meshchain.ai"
    headers["referer"] = "https://app.meshchain.ai"
    payload = json.dumps({
        "email": email,
        "password": password,
        "captcha_token": get_turnstile_token()
    })
    try:
        log.info(f"[{email}]First log-in....")
        response = res.post("https://api.meshchain.ai/meshmain/auth/email-signin", data=payload,headers=headers)
        if response.status_code == 201:
            data = response.json()
            return data.get("access_token"), data.get("refresh_token")
        else:
            return None
    except Exception as e:
        log.critical(f"[{email}]Exception >>> {e}")


def renew_refresh_token(res,refresh_token,headers,email):
    headers["origin"] = "https://app.meshchain.ai"
    headers["referer"] = "https://app.meshchain.ai"
    payload = json.dumps({
      "refresh_token": refresh_token
    })
    try:
        log.info(f"[{email}]Refreshing token...")
        response = res.post("https://api.meshchain.ai/meshmain/auth/refresh-token", data=payload,headers=headers)
        if response.status_code == 201:
            data = response.json()
            log.success(f"[{email}]Refresh token success")
            return data.get("access_token"), data.get("refresh_token")
        else:
            log.error(f"[{email}]Refresh token failed, need to login again.")
            return None
    except Exception as e:
        log.critical(f"[{email}]Exception >>> {e}")


def nodes(res,headers,access_token,email):
    headers["authorization"] = f"Bearer {access_token}"
    headers["origin"] = "https://app.meshchain.ai"
    headers["referer"] = "https://app.meshchain.ai"
    params = {
        "page":1,
        "limit":100
    }
    try:
        log.info(f"[{email}]Checking nodes...")
        response = res.get("https://api.meshchain.ai/meshmain/nodes",headers=headers,params=params)
        data = response.json()
        if response.status_code == 200:
            if not data.get("total_count") == 0:
                for devices in data.get("devices"):
                    if devices.get("type") == "browser" and devices.get("name"):
                        return devices.get("unique_id")
                    else:
                        log.info(f"[{email}]Nodes not found!")
                        return False
            else:
                log.info(f"[{email}]Nodes not found!")
                return False
        else:
            log.critical(f"[{email}]Failed checking node >>> {response.status_code}")
    except Exception as e:
        log.critical(f"[{email}]Error checking nodes[Exception] >>> {e}")




def generate_random_string():
    return str(uuid.uuid4()).replace('-', '')

def create_node_extension(res,headers,access_token,email):
    headers["authorization"] = f"Bearer {access_token}"
    headers["origin"] = "chrome-extension://lobckpihghfknleknppdjnnncpcfpcgh"
    payload = json.dumps({
      "unique_id": generate_random_string(),
      "node_type": "browser",
      "name": "Extension"
    })
    try:
        log.info(f"[{email}]Creating node extension...")
        response = res.post("https://api.meshchain.ai/meshmain/nodes/link",data=payload,headers=headers)
        data = response.json()
        if response.status_code == 201:
            log.info(f"[{email}]Creating node success.")
            return data.get("unique_id")
        else:
            log.critical(f"[{email}]Failed to creting node >>> {res.status_code}")
    except Exception as e:
        log.critical(f"[{email}]Failed to creating node[Exception]>>> {e}")


def start_node(res,headers,access_token,uid_node,email):
    headers["authorization"] = f"Bearer {access_token}"
    headers["origin"] = "chrome-extension://lobckpihghfknleknppdjnnncpcfpcgh"
    payload = json.dumps({
      "unique_id": uid_node
    })
    try:
        log.info("Starting node...")
        response = res.post("https://api.meshchain.ai/meshmain/rewards/start",headers=headers,data=payload)
        if response.status_code == 201:
            log.success(f"[{email}]Start node success.")
        else:
            log.info(f"[{email}]Start node failed >>> {response.status_code}")
    except Exception as e:
        log.critical(f"[{email}]Failed start node[Exception] >>> {e}")


def claim_node_points(res,headers,access_token,uid_node,email):
    payload = json.dumps({
      "unique_id": uid_node
    })
    headers["authorization"] = f"Bearer {access_token}"
    headers["origin"] = "chrome-extension://lobckpihghfknleknppdjnnncpcfpcgh"
    try:
        log.info(f"[{email}]Cumming reward points..")
        respone = res.post("https://api.meshchain.ai/meshmain/rewards/claim",headers=headers,data=payload)
        data = respone.json()
        if respone.status_code == 201:
            log.success(f"[{email}]Claim rewards point success >>> {data.get('total_reward')}")
        else:
            log.error(f"[{email}]Claim failed >>> {respone.status_code}")
    except Exception as e:
        log.critical(f"[{email}]Failed claim reward[Exception] >>> {e}")
        

def estimate_node(res,headers,access_token,uid_node,email):
    payload = json.dumps({
      "unique_id": uid_node
    })
    headers["authorization"] = f"Bearer {access_token}"
    headers["origin"] = "chrome-extension://lobckpihghfknleknppdjnnncpcfpcgh"
    try:
        response = res.post("https://api.meshchain.ai/meshmain/rewards/estimate",headers=headers,data=payload)
        data = response.json()
        if response.status_code == 201:
            log.success(f"[{email}]Ping success poinst >>> {data.get('value')}")
            if data.get("filled") == True:
                claim_node_points(res,headers,access_token,uid_node,email)
        elif response.status_code == 401:
            log.error(f"[{email}]Token expired.")
            return 123
        elif response.status_code == 400:
            log.error("Node not started.")
            return 234
        else:
            log.critical(f"[{email}]Error from server >>> {response.status_code}")
    except Exception as e:
        log.critical(f"[{email}]Failed to estimate node. >>> {e}")

def user_profile(res,headers,access_token,email):
    headers["authorization"] = f"Bearer {access_token}"
    try:
        log.info(f"[{email}]Getting user profile...")
        response = res.get("https://api.meshchain.ai/meshmain/user/profile", headers=headers)
        data = response.json()
        if response.status_code == 200:
            log.success(f"[{email}]Login success >>> {data.get('name')}")
        elif response.status_code == 401:
            log.error("Failed to login access token expired.")
            return 123
        else:
            log.critical(f"Failedt to logn from server >>> {response.status_code}")
    except Exception as e:
        log.critical(f"Failed to login[Exception] >>> {e}")

def process_account(email,password,proxy_selected):
    headers = {
      'User-Agent': ua.random,
      'Accept': "application/json, text/plain, */*",
      'accept-language': "en-US,en;q=0.9",
      'priority': "u=1, i",
      'Content-Type': "application/json"
    }
    res = requests.Session()
    pproxies = {
        "http": proxy_selected,
        "https": proxy_selected
    }
    log.info(proxy_selected)
    res.proxies.update(pproxies)
    test_net = res.get("https://ipinfo.io/json")
    data = test_net.json()
    log.info(f"Using IP >>> {data.get('ip')}")
    log.info(f"Detail >> {data.get('city')}|{data.get('region')}|{data.get('country')}|{data.get('hostname', 'Hostname not found')}")
    if check_account_cache(email):
        access_token = get_access_token_from_cache(email)
        get_node_uid = get_uid_node_from_cache(email)
        if user_profile(res,headers,access_token,email) == 123:
            refresh_token = get_refresh_token_from_cache(email)
            access_token,refresh_token = renew_refresh_token(res,refresh_token,headers,email)
            if access_token == None:
                access_token,refresh_token = login(res,email,password,headers)
            update_account_access_token(email,access_token)
            update_account_refresh_token(email,refresh_token)
        while not stop_event.is_set():
            access_token = get_access_token_from_cache(email)
            get_node_uid = get_uid_node_from_cache(email)
            ping = estimate_node(res,headers,access_token,get_node_uid,email)
            if ping == 123:
                refresh_token = get_refresh_token_from_cache(email)
                access_token,refresh_token = renew_refresh_token(res,refresh_token,headers,email)
                if access_token and refresh_token == None:
                    access_token,refresh_token = login(res,email,password,headers)
                update_account_access_token(email,access_token)
                update_account_refresh_token(email,refresh_token)
            elif ping == 234:
                start_node(res,headers,access_token,get_node_uid,email)
            else:
                pass
            time.sleep(3)
    else:
        access_token,refresh_token = login(res,email,password,headers)
        uid_nodes = nodes(res,headers,access_token,email)
        if uid_nodes == False:
            uid_nodes = create_node_extension(res,headers,access_token,email)
        else:
            add_account_to_cache(email,access_token,refresh_token,uid_nodes)
        add_account_to_cache(email,access_token,refresh_token,uid_nodes)
        if user_profile(res,headers,access_token,email) == 1:
            refresh_token = get_refresh_token_from_cache(email)
            access_token,refresh_token = renew_refresh_token(res,refresh_token,headers,email)
            update_account_access_token(email,access_token)
            update_account_refresh_token(email,refresh_token)
        while not stop_event.is_set():
            access_token = get_access_token_from_cache(email)
            get_node_uid = get_uid_node_from_cache(email)
            ping = estimate_node(res,headers,access_token,get_node_uid,email)
            if ping == 123:
                refresh_token = get_refresh_token_from_cache(email)
                access_token,refresh_token = renew_refresh_token(res,refresh_token,headers,email)
                update_account_access_token(email,access_token)
                update_account_refresh_token(email,refresh_token)
            elif ping == 234:
                start_node(res,headers,access_token,get_node_uid,email)
            else:
                pass
            time.sleep(3)





def get_proxy_list(proxy_file_path):
    try:
        with open(proxy_file_path, "r") as f:
            proxy_list = [line.strip() for line in f.readlines()]
            return proxy_list
    except FileNotFoundError:
        log.critical("Proxy file not found.")
    
def main():
    home_screen.display()
    account_path = input("Enter accounts file path (exemple: accounts.txt) >>> ")
    use_proxy = input("Do you want to use a proxy? (y/n) >>> ")
    
    if use_proxy.lower() == "y":
        proxy_file_name = input("Enter the name of the proxy file (example: proxy.txt) >>> ")
        try:
            with open(account_path, "r") as f:
                proxy_list = get_proxy_list(proxy_file_name)
                account_list = f.readlines()
                for account in account_list:
                    account = account.split("|")
                    email = account[0]
                    password = account[1].strip()
                    threads = []
                    proxy_selected = random.choice(proxy_list)
                    t = threading.Thread(target=process_account, args=(email,password,proxy_selected))
                    threads.append(t)
                    t.start()
        except FileNotFoundError:
            log.error("Accounts file not found.")
        except Exception as e:
            log.error(f"Exception >>> {e}")
    elif use_proxy.lower() == "n":
        try:
            with open(account_path, "r") as f:
                account_list = f.readlines()
                for account in account_list:
                    account = account.split("|")
                    email = account[0]
                    password = account[1].strip()
                    threads = []
                    proxy_selected = None
                    t = threading.Thread(target=process_account, args=(email,password,proxy_selected))
                    threads.append(t)
                    t.start()
        except FileNotFoundError:
            log.critical("Accounts file not found.")
        except Exception as e:
            log.critical(f"Exception >>> {e}")
    
    else:
        log.critical("Invalid selection!")
    
    try:
        log.info("Press CTRL + C to stop all workers.")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        log.info("CTRL + C detected! Stop all workers...")
        stop_event.set()



































































































































































































































































































































































































































































































































































































































































































if __name__ == "__main__":
    main()
