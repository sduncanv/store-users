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
            'username': "user_prueba_3",
            'password': "User_prueba_2",
            'user_id': 2,
            'created_at': "2024-04-29 11:59:08",
            'email': "correonuevo171201@gmail.com",
        }

        result = self.cognito.create_user(data)

        return response_format(
            result['statusCode'],
            'OK' if result['statusCode'] else 'Error',
            result['data']
        )
