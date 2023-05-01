from dotenv import dotenv_values
from dataclasses import dataclass
import os
import sqlalchemy

@dataclass
class SqlConnection:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        return self.connect_sqlalchemy()

    def connect_sqlalchemy(self):
        return sqlalchemy.create_engine(
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )

    @classmethod
    def from_env(cls, file_path=None):

        if not file_path:
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