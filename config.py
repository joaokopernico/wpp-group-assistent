from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Eleven Labs Configuration
ELEVEN_LABS_API_KEY = os.getenv('ELEVEN_LABS_API_KEY')
ELEVEN_LABS_VOICE_ID = os.getenv('ELEVEN_LABS_VOICE_ID')

# Other Configurations
ALLOWED_INSTANCE_IDS = os.getenv('ALLOWED_INSTANCE_IDS')  # Array de IDs permitidos
ALLOWED_CHATS = os.getenv('ALLOWED_CHATS')  # Array de chats permitidos
ALLOWED_ADMIN = os.getenv('ALLOWED_ADMIN')   # Array de administradores permitidos
ALLOWED_SEND_MESSAGE = os.getenv('ALLOWED_SEND_MESSAGE')   # Array de administradores permitidos
