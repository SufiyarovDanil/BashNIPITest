"""
Данный модуль содержит необходимые для для приложения переменные среды.

"""

import os

from dotenv import load_dotenv


load_dotenv()

DB_HOST: str = os.environ.get('DB_HOST')
DB_PORT: str = os.environ.get('DB_PORT')
DB_USER: str = os.environ.get('DB_USER')
DB_PASS: str = os.environ.get('DB_PASS')
DB_NAME: str = os.environ.get('DB_NAME')

DB_TEST_HOST: str = os.environ.get('DB_TEST_HOST')
DB_TEST_PORT: str = os.environ.get('DB_TEST_PORT')
DB_TEST_USER: str = os.environ.get('DB_TEST_USER')
DB_TEST_PASS: str = os.environ.get('DB_TEST_PASS')
DB_TEST_NAME: str = os.environ.get('DB_TEST_NAME')
