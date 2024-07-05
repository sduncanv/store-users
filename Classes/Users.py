import os
from sqlalchemy import select, insert, update
from hashlib import sha256

# from Tools.Database.Conn import Database
from Users.Classes.Conn import Database
from Tools.Utils.Helpers import get_input_data
from Tools.Classes.AwsCognito import AwsCognito
from Tools.Classes.BasicTools import BasicTools
from Tools.Classes.CustomError import CustomError
from Tools.Utils.QueryTools import get_model_columns, exclude_columns
from Users.Models.AuthenticatedUsers import AuthenticatedUsersModel
from Users.Models.Users import UserModel


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

        # Validate if the username exist
        user_exists = self.get_user_info({'username': username})

        if user_exists['data']:
            raise CustomError('El username ya está registrado.')

        input_data.update({'client_id': self.client_id})
        result = self.cognito.create_user(input_data)

        status_code = result['statusCode']

        if status_code == 200:

            password = sha256(bytes(str(password), "utf-8")).hexdigest()

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
            raise CustomError(result['data'])

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
            raise CustomError(is_valid['data'][0])

        data.update({'client_id': self.client_id})

        # Validate if the username exist
        user_id = self.get_user_info({'username': username})

        if user_id['statusCode'] == 404:
            raise CustomError('The specified user does not exist.')

        result = self.cognito.authenticate_user(data=data)

        status_code = result['statusCode']

        if status_code == 200:
            self.insert_authenticated_user({
                'user_id': user_id['data']['user_id'],
                'code': code
            })
            data = "User was confirmed."

        else:
            data = result['data']

        return {'statusCode': status_code, 'data': data}

    def get_user_info(self, kwargs: dict):

        conditions = {'active': 1}

        for key, value in kwargs.items():
            conditions.update({key: value})

        statement = select(UserModel).filter_by(**conditions)

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
            get_attributes=True
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
            raise CustomError(is_valid['data'][0])

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
            raise CustomError(is_valid['data'][0])

        user_info = self.get_user_info({'username': username})

        if not user_info['data']:
            raise CustomError('El usuario no existe.')

        response = self.cognito.get_token_by_user({
            'username': username,
            'password': password,
            'client_id': os.getenv('CLIENT_ID')
        })

        status_code = response['statusCode']
        data = response['data']

        if status_code != 200:
            raise CustomError(data)

        return {'statusCode': status_code, 'data': data}
