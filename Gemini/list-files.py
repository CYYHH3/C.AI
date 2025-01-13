# https://ai.google.dev/api/files?hl=zh-cn#rest-resource:-files

import google.generativeai as genai

print("Files:")
for f in genai.list_files():
    print("  ", f.name)