from Classes.Users import Users
from Tools.Utils.Helpers import exception_decorator


@exception_decorator
def users(event, context):

    users_class = Users()

    methods = {
        "POST": users_class.create_user
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
