import os

TOKEN = os.environ.get(
    "TOKEN",
    default='your_token'
)
BASE_URL = 'https://api.exchangeratesapi.io/latest?base='
DB_NAME = 'db.p'
BASE_RATE = 'USD'
