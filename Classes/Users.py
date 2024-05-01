import os
from sqlalchemy import select, insert
from hashlib import sha256
import json
# import hashlib

from Tools.Database.Conn import Database
from Tools.Utils.Helpers import get_input_data
from Tools.Classes.AwsCognito import AwsCognito
from Tools.Classes.BasicTools import BasicTools
from Tools.Classes.CustomError import CustomError
from Models.AuthenticatedUsers import AuthenticatedUsersModel
from Models.Users import UserModel


class Users:

    def __init__(self) -> None:
        self.user_pool = os.getenv('USER_POOL')
        self.client_id = os.getenv('CLIENT_ID')
        self.cognito = AwsCognito()
        self.db = Database()
        self.tools = BasicTools()

    def create_user(self, event) -> dict:

        input_data = get_input_data(event)

        username = input_data.get('username', '')
        password = input_data.get('password', '')
        email = input_data.get('email', '')
        name = input_data.get('name', '')
        first_lastname = input_data.get('first_lastname', '')

        values = [
            self.tools.params('username', str, username),
            self.tools.params('password', str, password),
            self.tools.params('email', str, email),
            self.tools.params('name', str, name),
            self.tools.params('first_lastname', str, first_lastname)
        ]

        is_valid = self.tools.validate_input_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['data'][0])

        input_data.update({'client_id': self.client_id})

        result = self.cognito.create_user(input_data)
        print(f'{result} --> 1')

        # result = {}
        # result['statusCode'] = 200
        status_code = result['statusCode']

        if status_code == 200:

            password = sha256(bytes(str(password), "utf-8")).hexdigest()
            # ew = hashlib.sha256(bytes(password, "utf-8")).hexdigest()

            statement = insert(UserModel).values(
                username=username,
                password=password,
                email=email,
                name=name,
                first_lastname=first_lastname
            )
            result_statement = self.db.insert_statement(statement)

            result_statement.update({"message": "User was created."})
            data = result_statement

        else:
            data = result['body']
            data = json.loads(data)['message']

            raise CustomError(data)

        print(f'{status_code} --> status_code')
        return {
            'statusCode': status_code, 'data': data
        }

    def authenticate_user(self, event) -> dict:

        data = get_input_data(event)

        username = data.get('username', '')
        code = data.get('code', '')

        values = [
            self.tools.params('username', str, username),
            self.tools.params('code', str, code)
        ]

        is_valid = self.tools.validate_input_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['data'][0])

        data.update({'client_id': self.client_id})

        user_id = self.get_user_id(username)

        if not user_id:
            raise CustomError(
                f'The specified username ({username}) does not exist.'
            )

        print(f'{data} --> sasasasaasa')
        result = self.cognito.authenticate_user(data=data)
        print(f'{result} --> 1')

        # result = {}
        # result['statusCode'] = 200
        status_code = result['statusCode']

        if status_code == 200:
            self.insert_authenticated_user({
                'user_id': user_id['user_id'],
                'code': code
            })
            data = "User was confirmed."

        else:
            data = result['message']

        return {
            'statusCode': status_code, 'data': data
        }

    def get_user_id(self, username: str):

        statement = select(UserModel).filter_by(
            username=username,
            active=1
        )

        result_statement = self.db.select_statement(statement)
        print(f'{result_statement} ---> result_statement')

        if result_statement:
            return result_statement[0]

        return result_statement

    def insert_authenticated_user(self, data):

        print(f'{data} -----------')

        statement = insert(AuthenticatedUsersModel).values(
            user_id=data['user_id'],
            code=data['code'],
            is_authenticated=1
        )
        print(f'{statement} ...')

        res = self.db.insert_statement(statement)

        print(f'{res} ...')
        print(type(res))
