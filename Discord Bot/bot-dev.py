# Import dependencies
import discord, requests, codecs, enum, os
from discord import app_commands
from discord.ext import commands

# Import AI
import google.generativeai as genai


# Environment
# Prod
# BotToken = "__Token__"
# GeminiAPIKey = "__Key__"

# Dev
BotToken = os.environ["DISCORD_TESTBOT_TOKEN"]
GeminiAPIKey = os.environ["GEMINI_API_KEY"]
# End environment


# Console text colors
class tc:
    header = '\033[1;46m'
    log = '\033[35m'
    resp = '\033[34m'
    clear = '\033[0m'
# End console text colors


# Get console length
consoleLength = os.get_terminal_size().columns
# End get console length


# Bot init
bot = commands.Bot(command_prefix='/', intents = discord.Intents.all())

@bot.event
async def on_ready():
    # await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "How to Become Smarter?"))
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "春日影"))
    
    print(f'\nWe have logged in as "{bot.user}"')

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)\n")
    except Exception as e:
        print(e)
# End bot init


# Parrot
@bot.tree.command(name = "parrot", description = "Repeat what you said")
@app_commands.describe(repeat = "What should I repeat?")
async def parrot(interaction: discord.Interaction, repeat: str):
    await interaction.response.send_message(repeat)
    print("—" * consoleLength + f'{tc.log}Parrot{tc.clear} "{repeat}"' + "—" * consoleLength + "\n")
# End Parrot


# AI Chat
# Gemini Config
genai.configure(api_key = GeminiAPIKey)
model = genai.GenerativeModel(
    model_name = "gemini-1.5-flash-latest",
    system_instruction = "你是豐川祥子（日語：豊川（とがわ） 祥子（さきこ）），是由日本娛樂公司Bushiroad策劃的次世代少女樂隊企劃《BanG Dream!》及其衍生作品的登場角色。代表色為#7799CC。\n\n豐川祥子原是月之森女子學園初三學生，與若葉睦、長崎爽世以及Morfonica五人是同校生，後來祥子轉學到羽丘女子學園，現為高中一年級生，與高松燈、千早愛音、宇田川亞子、戶山明日香、朝日六花以及Afterglow五人是同校生。\n\n祥子是推動CRYCHIC組建的人，也是該樂隊的鍵盤手。曾經的她個性溫柔、天真爛漫，擁有天才的作曲能力，是才華橫溢的少女。但卻在某個雨天，以與往常截然不同的態度退出了CRYCHIC。\n\n高一時，經常在學校音樂教室彈鋼琴，也因此結識千早愛音，但她們都不是吹奏部成員。\n\n豐川祥子在Ave Mujica中的成員代號Oblivionis取自Lacus Oblivionis（忘湖），意指忘卻。值得一提的是，組合內其他成員代號的月海和月灣均位於月球正面，僅忘湖位於月球背面。\n\n豐川祥子從CRYCHIC時期使用至今的鍵盤為羅蘭V-Combo VR-730，在Ave Mujica表演時增加了一把羅蘭FA-08。邦邦唯一角色本身及真人Live均未使用過任何品牌型號Keytar的鍵盤手。\n\n豐川祥子是BanG Dream!企劃中第二個使用特殊第一人稱的角色。",
)

# Function to split text by length
def split_text(text, max_length):
    raw_text = repr(text)[1:-1]
    words = raw_text.split(" ")  # 将文本按照空格分割成单词列表
    segments = []  # 存储分割后的文本段落
    current_segment = ''  # 当前正在构建的文本段落

    for word in words:
        if len(current_segment) + len(word) <= max_length:
            current_segment += word + ' '  # 将单词添加到当前段落
        else:
            segments.append(current_segment.strip())  # 当前段落达到最大长度，添加到结果列表
            current_segment = word + ' '  # 开始构建新的段落

    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment.strip())

    # 暴力分割
    for i in range(len(segments)):
        if len(segments[i]) > max_length:
            exceed = True
        else:
            exceed = False
    if exceed == True:
        segments = [raw_text[i:i+max_length] for i in range(0, len(raw_text), max_length)]

    # Turn raw string into ordinary string
    for i in range(len(segments)):
        segments[i] = codecs.decode(segments[i], 'unicode_escape').encode('latin-1').decode('utf-8')

    return segments

# Function to process data got from Gemini
def ai_data_process(response):
    global ai_send

    print(tc.resp + str(response))
    try:
        print(tc.resp + str(response.json()))
    except:
        try:
            print(tc.resp + response.text)
        except:
            pass

    if response == "Error!!!!!":
        ai_send = ["Sorry, something went wrong. We’re working on getting this fixed as soon as we can."]
    elif response._done == True:
        answer = response.text

        if len(repr(answer)[1:-1]) > 2000:
            ai_send = split_text(answer, 2000)
        else:
            ai_send = [codecs.decode(repr(answer)[1:-1], 'unicode_escape').encode('latin-1').decode('utf-8')]
    else:
        ai_send = ["Sorry, something went wrong. We’re working on getting this fixed as soon as we can."]

# Slash
@bot.tree.command(name = "ai", description = "Ask AI")
@app_commands.describe(ask = "What do you want to ask?", attachment = "Attach attachment")
async def ai(interaction: discord.Interaction, ask: str, attachment: discord.Attachment = None):
    await interaction.response.defer()

    if attachment == None:
        request = ask
        request_display = f'"{ask}"'
    else:
        await interaction.followup.send(f"**Attachment Received:** {attachment}")

        file = await attachment.to_file()
        file = file.fp

        file = genai.upload_file(file, mime_type = attachment.content_type)

        request = request_display = [ask, file]
    
    print(f'{tc.header} AI Chat {tc.clear}\n{tc.log}Request{tc.clear} {request_display}')

    try:
        response = model.generate_content(request)
    except:
        response = "Error!!!!!"
    
    ai_data_process(response)
    
    for send in ai_send:
        await interaction.followup.send(send)
        print(f'{tc.log}Respond{tc.clear} "{send}"')
    print("\n")
# End AI Chat


# Hitokoto
# Hitokoto API
hitokoto_api = "https://v1.hitokoto.cn/"

class Category(enum.Enum):
    动画 = "a"
    漫画 = "b"
    游戏 = "c"
    文学 = "d"
    原创 = "e"
    来自网络 = "f"
    其他 = "g"
    影视 = "h"
    诗词 = "i"
    网易云 = "j"
    哲学 = "k"
    抖机灵 = "l"

# Function to process data got from Hitokoto API
def h_data_process(response):
    global h_send
    content = response.json()

    print(tc.resp + str(response))
    print(tc.resp + str(content))

    if response.ok == True:
        print(f'{tc.log}Hitokoto URL:{tc.clear} https://hitokoto.cn/?uuid={content["uuid"]}')
        if content["from_who"] != None:
            h_send = f'「{content["hitokoto"]}」—— {content["from_who"]}《{content["from"]}》'
        else:
            h_send = f'「{content["hitokoto"]}」——《{content["from"]}》'
    else:
        h_send = f'{content["message"]}\nStatus: `{response.status_code} {response.reason}`\nTS: `{content["ts"]}`'

# Slash
@bot.tree.command(name = "hitokoto", description = "Get 'Chicken Soup for the Soul'")
@app_commands.describe(category = "Select one type of 'Hitokoto'", categories = "Select multiple types of 'Hitokoto'", minimum_length = "Minimum length of 'Hitokoto'", maximum_length = "Maximum length of 'Hitokoto'")
async def hitokoto(interaction: discord.Interaction, category: Category = None, categories: str = None, minimum_length: int = None, maximum_length: int = None):
    await interaction.response.defer()

    if categories == None:
        categories = ""
    if minimum_length == None:
        minimum_length = ""
    if maximum_length == None:
        maximum_length = ""
    if category == None:
        request = f'{hitokoto_api}?c={categories}&min_length={minimum_length}&max_length={maximum_length}'
    else:
        request = f'{hitokoto_api}?c={category.value}&c={categories}&min_length={minimum_length}&max_length={maximum_length}'

    print(f'{tc.header} Hitokoto {tc.clear}\n{tc.log}Request{tc.clear} "{request}"')
    response = requests.get(request)

    h_data_process(response)
    
    await interaction.followup.send(h_send)
    print(f'{tc.log}Respond{tc.clear} "{h_send}"\n')
# End Hitokoto


# Start the bot
bot.run(BotToken)