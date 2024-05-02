import os
from sqlalchemy import select, insert, update
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
from Tools.Utils.QueryTools import get_model_columns


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

        # if not user_id:
        #     raise CustomError(
        #         f'The specified username ({username}) does not exist.'
        #     )

        print(f'{data} --> sasasasaasa')
        result = self.cognito.authenticate_user(data=data)
        print(f'{result} --> 1')

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

    def get_user_id(self, **kwargs):

        conditions = {'active': 1}

        for key, value in kwargs.items():
            conditions.update({key: value})

        statement = select(UserModel).filter_by(**conditions)

        result_statement = self.db.select_statement(statement)

        if result_statement:
            return result_statement[0]

        raise CustomError(
            'The specified user does not exist.'
        )

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

    def get_user(self, event):

        input_data = get_input_data(event)

        user_id = input_data.get('user_id', '')

        conditions = {'active': 1}

        if user_id:
            conditions.update({'user_id': user_id})

        statement = select(
            *self.exclude_columns(UserModel, ['password'])
        ).filter_by(**conditions)

        result_statement = self.db.select_statement(statement)

        return {'statusCode': 200, 'data': result_statement}

    def exclude_columns(
        self, model, excluded: list, primary_key=False
    ) -> list:

        if excluded is None:
            excluded = []

        columns = []

        for column in model.__table__.columns:

            if primary_key and column.primary_key:
                excluded.append(column.key)

            if column.key not in excluded:
                columns.append(column)

        return columns

    def update_user(self, event):

        input_data = get_input_data(event)
        user_id = input_data['user_id']

        model_columns = get_model_columns(
            UserModel, exclude_primary_key=True,
            get_attributes=True
        )
        print(f'{model_columns} ---> model_columns')
        list_validation = []

        # keys_to_deleted = []
        for column, value in input_data.items():

            # if column in ['user_id', 'active']:
            #     keys_to_deleted.append(str(column))

            if column in model_columns.keys():
                _type = model_columns[column]['type']

                list_validation.append(
                    self.tools.params(column, _type, value)
                )

        # for key in keys_to_deleted:
        #     if key in input_data:
        #         del input_data[key]
        # print(f'{input_data} ---> input_data')

        print(f'{list_validation} ---> list_validation')

        is_valid = self.tools.validate_input_data(list_validation)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['data'][0])

        self.get_user_id(**{
            'user_id': user_id
        })

        statement = update(UserModel).where(
            UserModel.user_id == user_id,
            UserModel.active == 1
        ).values(**input_data)

        statement_result = self.db.update_statement(statement)

        print(statement_result)

        if statement_result:
            status_code = 200
            data = 'The user was updated.'

        else:
            status_code = 400
            data = "The user wasn't updated"

        return {'statusCode': status_code, 'data': data}

    def delete_user(self, event):

        pass
