# Конфиг для юзербота
import os
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")

# Группы для мониторинга
groups = [
    "shveinoeproizvodstvokirgiziia",
    "katalog_s",
    "textiles2022",
    "texmartkg",
    "proizvodsto_odejda_optom",
]

DB_USER = os.environ.get("DB_USER")  # без дефолта
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
