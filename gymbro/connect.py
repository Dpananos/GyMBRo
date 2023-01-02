import psycopg2
from dotenv import dotenv_values
from dataclasses import dataclass
import os

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

        if file_path:
            config = dotenv_values(file_path)
        else:
            config = os.environ


        return cls(
            host=config["POSTGRES_HOST"],
            port=config["POSTGRES_PORT"],
            database=config["POSTGRES_DB"],
            user=config["POSTGRES_USER"],
            password=config["POSTGRES_PASSWORD"],
        )