import os
import datetime
import pytest
import psycopg2
from gymbro.connect import SqlConnection, SqlTable


def test_conect():

    con = SqlConnection.from_env(file_path=".test.env")
    assert con.host == os.environ["DB_HOST"]
    assert con.port == os.environ["DB_PORT"]
    assert con.database == os.environ["DB_NAME"]
    assert con.user == os.environ["DB_USER"]
    assert con.password == os.environ["DB_PASSWORD"]


class TestSqlTable:
    def test_sql_table(self):

        with SqlConnection.from_env(file_path=".test.env").connect() as con:

            table = SqlTable("fact_tweets", con)
            assert table.query(
                'SELECT "id" FROM fact_tweets order by created_at desc LIMIT 1'
            ) == [(1568020944689692672,)]

            test_insert_data = (
                987654321,
                datetime.datetime(
                    1999, 12, 31, 11, 59, 0, tzinfo=datetime.timezone.utc
                ),
                297549322,
                "test tweet",
            )

            table.insert(
                "INSERT INTO fact_tweets (id, created_at, author_id, text) VALUES (%s, %s, %s, %s)",
                test_insert_data,
            )

            con.commit()

            assert table.query(
                'SELECT "text" FROM fact_tweets where id = 987654321'
            ) == [("test tweet",)]

            table.query("delete from fact_tweets where id = 987654321", fetchall=False)

            assert (
                table.query('SELECT "text" FROM fact_tweets where id = 987654321') == []
            )

    def test_last_observation(self):

        with SqlConnection.from_env(file_path=".test.env").connect() as con:

            table = SqlTable("fact_tweets", con)
            assert table.last_observation() == (1568020944689692672,)
