import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Access the environment variables
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_POOL_RECYCLE = int(os.getenv('SQLALCHEMY_POOL_RECYCLE', 40))
TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_KEY_SECRET = os.getenv('TWITTER_CONSUMER_KEY_SECRET')
SMS_SEVENIO_KEY = os.getenv('SMS_SEVENIO_KEY')
CQ9_AGENT_KEY_REMOTE_PROD = os.getenv('CQ9_AGENT_KEY_REMOTE_PROD')
CQ9_AGENT_KEY_REMOTE_STAGE = os.getenv('CQ9_AGENT_KEY_REMOTE_STAGE')
CQ9_AGENT_KEY_LOCAL = os.getenv('CQ9_AGENT_KEY_LOCAL')
CQ9_AGENT_KEY = os.getenv('CQ9_AGENT_KEY')
CQ9_KEY = os.getenv('CQ9_KEY')
BANK_ADDRESS = os.getenv('BANK_ADDRESS')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
BSNSCAN_API_KEY = os.getenv('BSNSCAN_API_KEY')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CLIENT_KEY = os.getenv('DISCORD_CLIENT_KEY')
# STATIC_ROOT = os.getenv('STATIC_ROOT')
# TWO_DIGIT_CURRENCIES = os.getenv('TWO_DIGIT_CURRENCIES')
#
# # If TWO_DIGIT_CURRENCIES is not None, split it by comma
# if TWO_DIGIT_CURRENCIES is  not None:
#     TWO_DIGIT_CURRENCIES = TWO_DIGIT_CURRENCIES.split(',')

SQLALCHEMY_ENGINE_OPTIONS = {
    # 'pool': QueuePool(creator),
    # 'pool_size': 10,
    'pool_recycle': 40
    # 'pool_pre_ping': True
}
# SQLALCHEMY_BINDS = Engine(sqlite:///example.db)


TWO_DIGIT_CURRENCIES = ['USD', 'EUR', 'USDT']
