import os
from dotenv import load_dotenv

load_dotenv()

App_name = os.getenv("APP_NAME")
Environment = os.getenv("ENVIRONMENT")
Debug = os.getenv("Debug","False").lower()in ("true", "1", "t")

print(f"Running {App_name} in {Environment} mode. Debug is {Debug}.")