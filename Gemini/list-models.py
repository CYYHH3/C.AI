# https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=python&hl=zh-cn#list_models

import google.generativeai as genai

for m in genai.list_models():
    print(m.name)