import os
from contextlib import contextmanager

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv()


@contextmanager
def get_connection():
    database_url = os.getenv("DATABASE_URL")
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        yield conn
