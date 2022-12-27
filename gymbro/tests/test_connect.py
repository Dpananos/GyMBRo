import os
from gymbro.connect import SqlConnection


def test_connect():

    conn = SqlConnection.from_env(file_path=".test.env")

    assert conn.host == os.environ["DB_HOST"]
    assert conn.port == os.environ["DB_PORT"]
    assert conn.database == os.environ["DB_NAME"]
    assert conn.user == os.environ["DB_USER"]
    assert conn.password == os.environ["DB_PASSWORD"]

