import os
import datetime
import pytest
import psycopg2
from gymbro.connect import SqlConnection


def test_conect():

    con = SqlConnection.from_env(file_path=".test.env")
    assert con.host == os.environ["POSTGRES_HOST"]
    assert con.port == os.environ["POSTGRES_PORT"]
    assert con.database == os.environ["POSTGRES_DB"]
    assert con.user == os.environ["POSTGRES_USER"]
    assert con.password == os.environ["POSTGRES_PASSWORD"]