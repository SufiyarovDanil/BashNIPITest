"""
Cодержит необходимые для для приложения переменные среды.

"""

import os


DB_HOST: str = os.environ.get('DB_HOST')
DB_PORT: str = os.environ.get('DB_PORT')
DB_USER: str = os.environ.get('DB_USER')
DB_PASS: str = os.environ.get('DB_PASS')
DB_NAME: str = os.environ.get('DB_NAME')
