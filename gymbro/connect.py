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