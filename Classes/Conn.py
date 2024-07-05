import os
from typing import Union
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

# ENGINE = 'mysql+pymysql'
ENGINE = 'postgresql+psycopg2'


class Database:

    def __init__(self):

        self.db = os.getenv('DB_NAME')
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')

    def create_engine_method(self):

        text = f'{ENGINE}://{self.user}:{self.password}@{self.host}/{self.db}'
        print(f'{text} ---> connUser')

        return create_engine(
            f'{ENGINE}://{self.user}:{self.password}@{self.host}/{self.db}'
        )

    def select_statement(self, statement):
        """
        This function opens a connection to the database, executes the query
        to select and closes the connection.

        Returns a database object.
        """

        engine = self.create_engine_method()

        with engine.connect() as connection:
            consult = connection.execute(statement)
            connection.commit()
            connection.close()

        return self.formate_result(consult)

    def formate_result(self, result) -> Union[dict, list]:

        results_as_dicts = []

        for row in result:
            res = dict(row._mapping)
            for key, value in res.items():
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                    res[key] = value
            results_as_dicts.append(res)

        return results_as_dicts

    def insert_statement(self, statement):
        """
        This function opens a connection to the database, executes the query
        to insert and closes the connection.

        Returns a database object.
        """

        engine = self.create_engine_method()

        with engine.connect() as connection:
            consult = connection.execute(statement)
            connection.commit()
            connection.close()

        consult = consult.inserted_primary_key._asdict()
        return consult

    def update_statement(self, statement):
        """
        This function opens a connection to the database, executes the query
        to updated and closes the connection.

        Returns a database object.
        """

        engine = self.create_engine_method()

        with engine.connect() as connection:
            consult = connection.execute(statement)
            connection.commit()
            connection.close()

        result = consult.last_updated_params()

        return result
