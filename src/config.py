import os

from dotenv import load_dotenv

load_dotenv()

aws_cli_profile = os.environ.get("AWS_PROFILE", "default")
