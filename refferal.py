import requests
from fake_useragent import UserAgent
from faker import Faker
import time
import string
import json
import random
from tempmail import *
from logmagix import Logger,Home,LogLevel





home_screen = Home(text="IVY",align="center", adinfo1="The developers are not responsible for any misuse or potential account violations.",adinfo2="Automation refferal meshchan",credits="Developed by Rils")
log = Logger(prefix="BOT", level=LogLevel.DEBUG,github_repository="https://github.com/rilspratama/Meshchan.git")

ua = UserAgent(platforms=["desktop"])
fake = Faker()


def generate_random_name():
    return fake.name()

def generate_email(uname,domain):
    return f"{uname}@{domain}"
    

def generate_password(length=12):
    if length < 6: 
        length = 6
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choices(characters, k=length))
    return password

def get_turnstile_token():
    params = {
        "url":"https://app.meshchain.ai/",
        "sitekey":"0x4AAAAAAA0e4lkIb7ZRG1LE"
    }
    global api_key
    headers = {
        "X-API-Key": api_key
    }
    while True:
        response = requests.get(f"https://turnshit.biz.id/turnstile", params=params,headers=headers)
        if response.status_code == 200 and response.json().get("status") == "success":
            log.success("Turnstile token retrieved successfully.")
            return response.json().get("result")
        else:
            log.error("Turnstile token failed to take, try again...")



def refferal(res,fname,email,password,reffcode,headers):
    payload = json.dumps({
        "full_name": fname,
        "email": email,
        "password": password,
        "referral_code": reffcode,
        "captcha_token": get_turnstile_token()
    })
    try:
        response = res.post("https://api.meshchain.ai/meshmain/auth/email-signup",data=payload,headers=headers)
        if response.status_code == 201:
            log.success(f"Registred success USERID >>> {response.json().get('user_id')}")
        else:
            log.critical(f"Registration failed >> {response.status_code}")
    except Exception as e:
        log.critical(f"Exception >>> {e}")


def login(res,email,password,headers):
    payload = json.dumps({
        "email": email,
        "password": password,
        "captcha_token": get_turnstile_token()
    })
    try:
        response = res.post("https://api.meshchain.ai/meshmain/auth/email-signin", data=payload,headers=headers)
        if response.status_code == 201:
            data = response.json()
            return data.get("access_token")
        else:
            return None
    except Exception as e:
        log.critical(f"Exception >>> {e}")

def verify_email(res,email,otp,headers):
    payload = json.dumps({
        "email": email,
        "code": otp,
        "captcha_token": get_turnstile_token() 
    })
    try:
        response = res.post("https://api.meshchain.ai/meshmain/auth/verify-email", data=payload,headers=headers)
        if response.status_code == 201:
            log.success("Email verified successfully")
        else:
            log.error(f"Error respone >> {response.status_code}")
            log.error(f"{response.json()}")
    except Exception as e:
        log.critical(f"Exception >>> {e}")


def claim_bnb(res,headers):
    payload = json.dumps({
        "mission_id":"EMAIL_VERIFICATION"
    })
    try:
        response = res.post("https://api.meshchain.ai/meshmain/mission/claim", headers=headers, data=payload)
        if response.status_code == 201:
            log.success("Claim success")
        else:
            log.error(f"Error respone >> {response.status_code}")
    except Exception as e:
        log.critical(f"Exception >>> {e}")

def process_refferal(res,reffcode,headers,account_filepath):
    log.info("Starting the registration process")
    name = generate_random_name()
    domains = get_domains()
    random_domain = random.choice(domains)
    username = f"{fake.user_name()}{random.randint(100,9999)}"
    email = f"{generate_email(username,random_domain)}"
    password = generate_password()
    log.info(f"Using email >>> {email}")
    log.info("Registration  email.")
    create_email(email,password)
    time.sleep(5)
    log.info("Creating account to platform...")
    refferal(res,name,email,password,reffcode,headers)
    log.info("Register account success.")
    log.info("Logging in to account...")
    access_token = login(res,email,password,headers)
    log.info("Login success!!!")
    log.info("Verifying account...")
    log.info("Logging in email...")
    email_ac = get_token(email,password)
    id_email = get_latest_message(email_ac)
    text_email = get_message(email_ac,id_email)
    otp = get_otp(text_email)
    headers["Authorization"] = f"Bearer {access_token}"
    verify_email(res,email,otp,headers)
    log.info("Email verification successful")
    log.info("Claiming 0.005 BNB Task")
    claim_bnb(res,headers)
    with open(account_filepath, "a") as f:
        f.write(f"{email}|{password}\n")




def main():
    home_screen.display()
    reffcode = input("Enter refferal code >>> ")
    global api_key
    api_key = input("Enter api key turnshit(get on @ivy_solver_bot) >>> ")
    numbers_of_refferal = int(input("Numbers of refferal >>>"))
    aaccount_file_path = input("Enter the name of the account file (example: accounts.txt) >>> ")
    use_proxy = input("Do you want to use a proxy? (y/n) >>> ")
    if use_proxy.lower() == "y":
        proxy_file_name = input("Enter the name of the proxy file (example: proxy.txt) >>> ")
        try:
            with open(proxy_file_name, "r") as f:
                proxy_list = [line.strip() for line in f.readlines()]
                for _ in range(numbers_of_refferal):
                    print("="*50)
                    try:
                        proxy_selected = random.choice(proxy_list)
                        res = requests.Session()
                        proxies = {
                                "http": proxy_selected,
                                "https": proxy_selected
                            }
                        res = requests.Session()
                        res.proxies.update(proxies)
                        test_net = res.get("https://ipinfo.io/json")
                        data = test_net.json()
                        log.info(f"Using IP >>> {data.get('ip')}")
                        log.info(f"Detail >> {data.get('city')}|{data.get('region')}|{data.get('country')}|{data.get('hostname', 'Hostname not found')}")
                        headers = {
                              'User-Agent': ua.random,
                              'Accept': "application/json, text/plain, */*",
                              'Content-Type': "application/json",
                              'accept-language': "en-US,en;q=0.9",
                              'origin': "https://app.meshchain.ai",
                              'priority': "u=1, i",
                              'referer': "https://app.meshchain.ai/"
                        }
                        process_refferal(res,reffcode,headers,aaccount_file_path)
                    except Exception as e:
                        log.error(f"Exception >>> {e}")
        except FileNotFoundError:
            log.critical("Proxy file not found!")
    
    elif use_proxy.lower() == "n":
        for _ in range(numbers_of_refferal):
            print("="*50)
            try:
                res = requests.Session()
                test_net = res.get("https://ipinfo.io/json")
                data = test_net.json()
                log.info(f"Using IP >>> {data.get('ip')}")
                log.info(f"Detail >> {data.get('city')}|{data.get('region')}|{data.get('country')}|{data.get('hostname', 'Hostname not found')}")
                headers = {
                      'User-Agent': ua.random,
                      'Accept': "application/json, text/plain, */*",
                      'Content-Type': "application/json",
                      'accept-language': "en-US,en;q=0.9",
                      'origin': "https://app.meshchain.ai",
                      'priority': "u=1, i",
                      'referer': "https://app.meshchain.ai/"
                }
                process_refferal(res,reffcode,headers,aaccount_file_path)
            except Exception as e:
                log.error(f"Exception >>> {e}")
    else:
        log.critical("Invalid selection!")
        

if __name__ == "__main__":
    main()