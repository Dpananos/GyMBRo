import os
import datetime
import pytest
import psycopg2
from gymbro.connect import SqlConnection


def test_conect():

    con = SqlConnection.from_env(file_path=".test.env")
    assert con.host == os.environ["DB_HOST"]
    assert con.port == os.environ["DB_PORT"]
    assert con.database == os.environ["DB_NAME"]
    assert con.user == os.environ["DB_USER"]
    assert con.password == os.environ["DB_PASSWORD"]