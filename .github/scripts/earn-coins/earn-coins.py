import os, requests, time, json


# Set up variables
# Webshare Proxy
proxies = {
    "http": os.environ["WEBSHARE_PROXY"],
    "https": os.environ["WEBSHARE_PROXY"]
}

# Yes, Captcha!
clientKey = os.environ["YESCAPTCHA_CLIENTKEY"]
createTask_API = "https://api.yescaptcha.com/createTask"
getTask_API = "https://api.yescaptcha.com/getTaskResult"

# Bot-Hosting.net
Bot_Hosting_token = os.environ["BOT_HOSTING_TOKEN"]
websiteKey = "21335a07-5b97-4a79-b1e9-b197dc35017a"
login_URL = "https://bot-hosting.net/login"
earnCoins_URL = "https://bot-hosting.net/panel/earn"
freeCoinStatus_API = "https://bot-hosting.net/api/freeCoinsStatus"
earnCoins_API = "https://bot-hosting.net/api/freeCoins"
me_API = "https://bot-hosting.net/api/me"
# End of variables


# Yes, Captcha! class
class yesCaptcha:
    def __init__(self, clientKey, createTask_API, getTask_API):
        self.clientKey = clientKey
        self.createTask_API = createTask_API
        self.getTask_API = getTask_API

    def createTask(self, task):
        task_info = {
            "clientKey": self.clientKey,
            "task": task,
            "softID": 60167
        }
        return requests.post(self.createTask_API, json=task_info).json()

    def getTaskResult(self, taskId):
        result_info = {
            "clientKey": self.clientKey,
            "taskId": taskId
        }
        return requests.post(self.getTask_API, json=result_info).json()
    
    def getBalance(self):
        balance_info = {
            "clientKey": self.clientKey
        }
        return requests.post("https://api.yescaptcha.com/getBalance", json=balance_info).json().get("balance")


# Create Yes, Captcha! object
yesCaptcha = yesCaptcha(clientKey, createTask_API, getTask_API)


print("Solving captcha...")


# 创建 Yes, Captcha! 任务
task_info = {
    "type": "CloudFlareTaskS2",
    "websiteURL": login_URL,
    "proxy": proxies["https"],
}
task = yesCaptcha.createTask(task_info)


# 获取任务结果
for i in range(30):
    time.sleep(3)
    print("Solving captcha...")
    result = yesCaptcha.getTaskResult(task.get("taskId"))
    if result.get('status') == 'processing':
        continue
    elif result.get('status') == 'ready':
        break
    else:
        raise Exception(result)


# 提取结果
solution = result.get("solution")
headers = {"user-agent": solution.get("request_headers").get("user-agent")}
headers.update({"authorization": Bot_Hosting_token})
cookies = solution.get("cookies")


# Earn coins if possible
getFreeCoinsStatus = lambda: requests.get(freeCoinStatus_API, headers=headers, cookies=cookies, proxies=proxies).json()
myCoins = lambda: requests.get(me_API, headers=headers, cookies=cookies, proxies=proxies).json().get("coins")

coinsOwned = myCoins()
freeCoinsStatus = getFreeCoinsStatus()
claimable = freeCoinsStatus.get("claimable")
coinsClaimed = freeCoinsStatus.get("coinsClaimed")
captcha = freeCoinsStatus.get("captcha")

if claimable and coinsClaimed == 10:
    coinsClaimed = 0

print()
print(f"Coins owned: {coinsOwned}")
print(f"Claimable: {claimable}")
print(f"Coins claimed: {coinsClaimed}/10")
print()

captcha_count = 0

if claimable and coinsClaimed < 10:
    while claimable and coinsClaimed < 10:
        time.sleep(10)
        h_captcha_response = {}

        if captcha and captcha_count < 2:
            print("Solving hCaptcha...")

            # 创建 Yes, Captcha! 任务
            task_info = {
                "type": "HCaptchaTaskProxyless",
                "websiteURL": earnCoins_URL,
                "websiteKey": websiteKey,
            }
            task = yesCaptcha.createTask(task_info)

            # 获取任务结果
            for i in range(30):
                time.sleep(3)
                print("Solving hCaptcha...")
                result = yesCaptcha.getTaskResult(task.get("taskId"))
                if result.get('status') == 'processing':
                    continue
                elif result.get('status') == 'ready':
                    break
                else:
                    raise Exception(result)
            
            # 提取结果
            solution = result.get("solution")
            h_captcha_response = {"hCaptchaResponse": solution.get("gRecaptchaResponse")}

            captcha_count += 1
        elif captcha and captcha_count >= 2:
            break
        print(f"Claiming {coinsClaimed + 1}/10 coins...")
        requests.post(earnCoins_API, headers=headers, cookies=cookies, proxies=proxies, json=h_captcha_response)

        freeCoinsStatus = getFreeCoinsStatus()
        claimable = freeCoinsStatus.get("claimable")
        coinsClaimed = freeCoinsStatus.get("coinsClaimed")
        captcha = freeCoinsStatus.get("captcha")
else:
    print("No free coins available.")


# Get and store data
coinsOwned = myCoins()
yesCaptcha_balance = yesCaptcha.getBalance()

print()
print(f"Coins owned: {coinsOwned}")
print(f"Yes, Captcha! 账户余额: {yesCaptcha_balance}")

with open("discord-webhook-msg.json", "w") as f:
    discord_webhook_msg = {
        "embeds": [
            {
                "title": "Bot-Hosting.net Earn Coins",
                "description": "Cron job done.",
                "color": 5793266,
                "fields": [
                    {
                        "name": "Coins Owned",
                        "value": coinsOwned
                    },
                    {
                        "name": "Yes, Captcha! 账户余额",
                        "value": yesCaptcha_balance
                    }
                ]
            }
        ]
    }
    f.write(json.dumps(discord_webhook_msg))