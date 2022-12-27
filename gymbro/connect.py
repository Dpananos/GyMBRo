import psycopg2
from dotenv import dotenv_values
from dataclasses import dataclass


@dataclass
class SqlConnection:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

    @classmethod
    def from_env(cls, file_path=None):

        if not file_path:
            file_path = ".env"

        config = dotenv_values(file_path)

        return cls(
            host=config["DB_HOST"],
            port=config["DB_PORT"],
            database=config["DB_NAME"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
        )


class SqlTable:
    # TODO:  Clean this up by adding column names to the table class and editing the insert method to use them.
    def __init__(self, connection, name):

        self.connection = connection
        self.name = name

    def last_observation(self):

        with self.connection.cursor() as cur:
            cur.execute(
                'SELECT "id" FROM {} order by created_at desc LIMIT 1'.format(self.name)
            )
            last_obs = cur.fetchone()

            if last_obs:
                return last_obs[0]
            else:
                return None

    def query(self, query, fetchall=True):

        with self.connection.cursor() as cur:
            cur.execute(query)

            # When testing this class, I write and delete an observation from the test db
            # In order to remove that observation, i need to execute a query but doing `fetchall` on a drop command
            # results in a psycopg2.ProgrammingError: no results to fetch
            # So I added the `fetchall` argument to the query method to allow me to execute a query without fetching all results
            if fetchall:
                return cur.fetchall()
            else:
                return self

    def insert(self, query, values):

        with self.connection.cursor() as cur:
            cur.execute(query, values)
