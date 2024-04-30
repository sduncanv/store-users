import os

from Tools.Database.Conn import Database
from Tools.Classes.AwsCognito import AwsCognito
from Tools.Utils.Helpers import response_format


class Users:

    def __init__(self) -> None:
        self.user_pool = os.getenv('USER_POOL')
        self.client_id = os.getenv('CLIENT_ID')
        self.cognito = AwsCognito()
        self.db = Database()

    def create_user(self, event) -> dict:

        data = {
            'client_id': self.client_id,
            'username': "user_prueba_7",
            'password': "User_prueba_2",
            'user_id': 2,
            'created_at': "2024-04-29 11:59:08",
            # 'email': "correonuevo171201@gmail.com",
            'email': "samuelduncanv@gmail.com",
        }

        result = self.cognito.create_user(data)
        print(f'{result} --> 1')

        if result['statusCode'] == 200:
            status_code = result['statusCode']
            data = "User was created."

        else:
            status_code = result['statusCode']
            data = result['message']

        return response_format(
            status_code,
            'Ok' if status_code == 200 else 'Error',
            data
        )

    def authenticate_user(self, event) -> dict:

        data = {
            'client_id': self.client_id,
            'username': "user_prueba_7",
            'code': "291409"
        }

        result = self.cognito.authenticate_user(data=data)

        print(f'{result} --> 1')

        if result['statusCode'] == 200:
            status_code = result['statusCode']
            data = "User was confirmed."

        else:
            status_code = result['statusCode']
            data = result['message']

        return response_format(
            status_code,
            'Ok' if status_code == 200 else 'Error',
            data
        )
