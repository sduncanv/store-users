from Classes.Users import Users
from Tools.Utils.Helpers import exception_decorator


@exception_decorator
def users(event, context):

    users_class = Users()

    methods = {
        "POST": users_class.create_user,
        "GET": users_class.get_user,
        "PUT": users_class.update_user,
    }

    executed = methods.get(event['httpMethod'])
    return executed(event)


@exception_decorator
def authenticate_user(event, context):

    users_class = Users()

    methods = {
        "POST": users_class.authenticate_user
    }

    executed = methods.get(event['httpMethod'])
    return executed(event)


@exception_decorator
def login(event, context):

    users_class = Users()

    methods = {
        "POST": users_class.login
    }

    executed = methods.get(event['httpMethod'])
    return executed(event)
