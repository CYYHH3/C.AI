import os, requests, time, json


# Webshare Proxy
proxies = {
    "http": os.environ["WEBSHARE_PROXY"],
    "https": os.environ["WEBSHARE_PROXY"]
}


# Yes, Captcha! class
class yesCaptcha:
    def __init__(self):
        self.clientKey = os.environ["YESCAPTCHA_CLIENTKEY"]
        self.createTask_API = "https://api.yescaptcha.com/createTask"
        self.getTask_API = "https://api.yescaptcha.com/getTaskResult"

        self.solved_captchas_count = 0
        self.max_solved_captchas = 3

    def createTask(self, task):
        if self.solved_captchas_count >= self.max_solved_captchas:
            raise ValueError("Reached maximum number of solved captchas.")
        
        task_info = {
            "clientKey": self.clientKey,
            "task": task,
            "softID": 60167
        }

        self.solved_captchas_count += 1

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


# Bot-Hosting.net class
class botHosting:
    def __init__(self, proxies = {}, headers = {}, cookies = {}):
        self.Bot_Hosting_token = os.environ["BOT_HOSTING_TOKEN"]

        self.login_URL = "https://bot-hosting.net/login"
        self.earnCoins_URL = "https://bot-hosting.net/panel/earn"

        self.freeCoinsStatus_API = "https://bot-hosting.net/api/freeCoinsStatus"
        self.earnCoins_API = "https://bot-hosting.net/api/freeCoins"
        self.me_API = "https://bot-hosting.net/api/me"

        self.hCaptcha_siteKey = "21335a07-5b97-4a79-b1e9-b197dc35017a"

        self.proxies = proxies
        self.headers = headers
        self.cookies = cookies

        self.coinsClaimed_local = 0
        self.coinsOwned = None
        self.claimable = None
        self.coinsClaimed = None
        self.captcha = None

        if proxies != {} and headers != {} and cookies != {}:
            self.getCoinsOwned()
            self.getFreeCoinsStatus()
    
    def getCoinsOwned(self):
        self.coinsOwned = requests.get(self.me_API, headers=self.headers, cookies=self.cookies, proxies=self.proxies).json().get("coins")
        return self.coinsOwned

    def getFreeCoinsStatus(self):
        freeCoinsStatus = requests.get(self.freeCoinsStatus_API, headers=self.headers, cookies=self.cookies, proxies=self.proxies).json()
        self.claimable = freeCoinsStatus.get("claimable")
        self.coinsClaimed = freeCoinsStatus.get("coinsClaimed")
        self.captcha = freeCoinsStatus.get("captcha")
        return freeCoinsStatus
    
    def earnCoins(self, h_captcha_response):
        requests.post(self.earnCoins_API, headers=self.headers, cookies=self.cookies, proxies=self.proxies, json=h_captcha_response).json()
        self.coinsClaimed_local += 1
        self.getFreeCoinsStatus()


########## Start main program ##########


# Create Yes, Captcha! object
yesCaptcha = yesCaptcha()

# Create dummy botHosting object
botHost = botHosting()


# 创建 Yes, Captcha! Cloudflare 5秒盾 任务
print("Bypassing Cloudflare protection...")

cf_task_info = {
    "type": "CloudFlareTaskS3",
    "websiteURL": botHost.login_URL,
    "proxy": proxies["https"],
}
cf_task = yesCaptcha.createTask(cf_task_info)

# 获取 Yes, Captcha! Cloudflare 5秒盾 任务结果
for i in range(30):
    time.sleep(3)
    print("Bypassing Cloudflare protection...")
    cf_task_result = yesCaptcha.getTaskResult(cf_task.get("taskId"))
    if cf_task_result.get('status') == 'processing':
        continue
    elif cf_task_result.get('status') == 'ready':
        break
    else:
        raise Exception(cf_task_result)

# 提取结果 & 更新 headers 和 cookies
headers = cf_task_result.get("solution").get("request_headers")
del headers["Accept-Encoding"]
headers.update({"authorization": botHost.Bot_Hosting_token})
cookies = cf_task_result.get("solution").get("cookies")

# Create real botHosting object
botHosting = botHosting(proxies, headers, cookies)


# Display account info
print()
print(f"Coins owned: {botHosting.coinsOwned}")
print(f"Claimable: {botHosting.claimable}")
print()

if botHosting.coinsOwned == None and botHosting.claimable == None and botHosting.coinsClaimed == None:
    print("Failed to get data. Exiting...")
    exit()


# Claim free coins if available
if botHosting.claimable:
    while botHosting.claimable:
        time.sleep(10)
        h_captcha_response = {}

        if botHosting.captcha:
            print("Solving hCaptcha...")

            try:
                # 创建 Yes, Captcha! hCaptcha 任务
                task_info = {
                    "type": "HCaptchaTaskProxyless",
                    "websiteURL": botHosting.earnCoins_URL,
                    "websiteKey": botHosting.hCaptcha_siteKey,
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
            except ValueError as e:
                print(e)
                break
        
        print(f"Claiming coin {botHosting.coinsClaimed_local + 1}...")
        botHosting.earnCoins(h_captcha_response)
else:
    print("No free coins available.")


# Display account info
print()
print(f"Coins claimed: {botHosting.coinsClaimed}/10")
print(f"Coins owned: {botHosting.getCoinsOwned()}")
print(f"Yes, Captcha! 账户余额: {yesCaptcha.getBalance()}")



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
                        "value": botHosting.coinsOwned
                    },
                    {
                        "name": "Yes, Captcha! 账户余额",
                        "value": yesCaptcha.getBalance()
                    }
                ]
            }
        ]
    }
    f.write(json.dumps(discord_webhook_msg))