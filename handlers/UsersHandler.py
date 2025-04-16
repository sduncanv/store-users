from Users.Classes.Users import Users
from Tools.Utils.Helpers import exception_decorator


@exception_decorator
def users(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.create_user,
        "GET": users_class.get_user,
        "PUT": users_class.update_user,
    }

    return functions[method](event)


@exception_decorator
def authenticate_user(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.authenticate_user
    }

    return functions[method](event)


@exception_decorator
def login(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.login
    }

    return functions[method](event)
