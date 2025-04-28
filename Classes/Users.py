import os
import hmac
import hashlib
import base64
from sqlalchemy import select, insert, update, or_
from hashlib import sha256

from Tools.Database.Conn import Database
from Tools.Utils.Helpers import get_input_data
from Tools.Classes.AwsCognito import AwsCognito
from Tools.Classes.BasicTools import BasicTools
from Tools.Classes.CustomError import CustomError
from Tools.Utils.QueryTools import get_model_columns, exclude_columns
from Users.Models.AuthenticatedUsers import AuthenticatedUsersModel
from Users.Models.Users import UserModel


def get_secret_hash(username: str, client_id: str, client_secret: str) -> str:
    message = username + client_id
    dig = hmac.new(
        client_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()


class Users:

    def __init__(self) -> None:

        self.client_id = os.getenv('CLIENT_ID')
        self.secret_hash = os.getenv('SECRET_HASH')
        self.cognito = AwsCognito()
        self.db = Database(
            db=os.getenv('DATABASE_NAME'),
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD')
        )
        self.tools = BasicTools()

    def create_user(self, event) -> dict:

        input_data = get_input_data(event)

        username = input_data.get('username', '')
        password = input_data.get('password', '')
        email = input_data.get('email', '')
        phone_number = input_data.get('phone_number', '')

        values = [
            self.tools.params('username', str, username),
            self.tools.params('password', str, password),
            self.tools.params('email', str, email),
            self.tools.params('phone_number', str, phone_number)
        ]

        is_valid = self.tools.validate_input_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0])

        # Validate if the username exist
        user_exists = self.get_user_info({
            'email': email, 'username': username
        })

        if user_exists['statusCode'] == 200:
            raise CustomError('Username or email already exists.')

        secret_hash = get_secret_hash(
            username, self.client_id, self.secret_hash
        )

        input_data.update({
            'client_id': self.client_id,
            'secret_hash': secret_hash
        })

        result = self.cognito.create_user(input_data)
        status_code = result['statusCode']

        if status_code == 200:

            password = sha256(bytes(str(password), "utf-8")).hexdigest()

            statement = insert(UserModel).values(
                username=username,
                password=password,
                email=email,
                phone_number=phone_number,
            )

            result_statement = self.db.insert_statement(statement)
            result_statement.update({"message": "User was created."})
            data = result_statement

        else:
            raise CustomError(
                message=result['data'], status_code=result['statusCode']
            )

        return {'statusCode': status_code, 'data': data}

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
            raise CustomError(is_valid['errors'][0])

        secret_hash = get_secret_hash(
            username, self.client_id, self.secret_hash
        )

        data.update({
            'client_id': self.client_id, 'secret_hash': secret_hash
        })

        # Validate if the username exist
        user_id = self.get_user_info({'username': username})

        if user_id['statusCode'] == 404:
            raise CustomError('The specified user does not exist.')

        autenticated = self.db.select_statement(
            select(AuthenticatedUsersModel).where(
                AuthenticatedUsersModel.user_id == user_id['data']['user_id'],
                AuthenticatedUsersModel.is_authenticated == 1
            )
        )

        if autenticated:
            raise CustomError('The user is already authenticated.')

        result = self.cognito.authenticate_user(data=data)

        status_code = result['statusCode']

        if status_code == 200:
            self.insert_authenticated_user({
                'user_id': user_id['data']['user_id'], 'code': code
            })
            data = "User was confirmed."

        else:
            data = result['data']

        return {'statusCode': status_code, 'data': data}

    def get_user_info(self, kwargs: dict):

        conditions = []

        for key, value in kwargs.items():
            conditions.append(getattr(UserModel, key) == value)

        statement = select(UserModel).where(
            UserModel.active == 1, or_(*conditions)
        )

        result_statement = self.db.select_statement(statement)

        if result_statement:
            status_code = 200
            result = result_statement[0]

        else:
            status_code = 404
            result = []

        return {'statusCode': status_code, 'data': result}

    def insert_authenticated_user(self, data):

        statement = insert(AuthenticatedUsersModel).values(
            user_id=data['user_id'],
            code=data['code'],
            is_authenticated=1
        )

        self.db.insert_statement(statement)

    def get_user(self, event):

        input_data = get_input_data(event)
        conditions = {'active': 1}

        for key, value in input_data.items():
            conditions.update({key: value})

        statement = select(
            *exclude_columns(UserModel, ['password'])
        ).filter_by(**conditions)

        result_statement = self.db.select_statement(statement)

        status_code = 200
        if not result_statement:
            status_code = 404

        return {'statusCode': status_code, 'data': result_statement}

    def update_user(self, event):

        input_data = get_input_data(event)
        user_id = input_data.pop('user_id')

        model_columns = get_model_columns(
            UserModel, exclude_primary_key=True,
            return_attributes=True
        )

        list_validation = []

        for column, value in input_data.items():

            if column in model_columns.keys():
                _type = model_columns[column]['type']

                list_validation.append(
                    self.tools.params(column, _type, value)
                )

        is_valid = self.tools.validate_input_data(list_validation)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0])

        user_info = self.get_user_info({'user_id': user_id})

        if not user_info['data']:
            raise CustomError('El usuario no existe.')

        statement = update(UserModel).where(
            UserModel.user_id == user_id,
            UserModel.active == 1
        ).values(**input_data)

        statement_result = self.db.update_statement(statement)

        if statement_result:
            status_code = 200
            data = 'The user was updated.'

        else:
            status_code = 400
            data = "The user wasn't updated"

        return {'statusCode': status_code, 'data': data}

    def login(self, event):

        data = get_input_data(event)

        username = data.get('username', '')
        password = data.get('password', '')

        values = [
            self.tools.params('username', str, username),
            self.tools.params('password', str, password)
        ]

        is_valid = self.tools.validate_input_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0])

        user_info = self.get_user_info({'username': username})

        if not user_info['data']:
            raise CustomError('El usuario no existe.')

        secret_hash = get_secret_hash(
            username, self.client_id, self.secret_hash
        )

        response = self.cognito.get_token_by_user({
            'username': username,
            'password': password,
            'secret_hash': secret_hash,
            'client_id': self.client_id
        })

        data = response['data']

        if response['statusCode'] == 400:
            raise CustomError(
                message=data, status_code=response['statusCode']
            )

        if response.get('data', '').get('AccessToken', ''):
            status_code = 200

        return {'statusCode': status_code, 'data': data}
