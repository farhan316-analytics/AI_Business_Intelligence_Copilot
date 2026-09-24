import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()

print("ENV FILE FOUND:", env_path)

load_dotenv(env_path)

key = os.getenv("OPENAI_API_KEY")

if key:
    print("OPENAI_API_KEY FOUND: YES")
    print("KEY START:", key[:7])
else:
    print("OPENAI_API_KEY FOUND: NO")