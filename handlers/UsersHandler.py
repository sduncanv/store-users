from Classes.Users import Users


def users(event, context):

    users_class = Users()

    methods = {
        "POST": users_class.create_user
    }

    executed = methods.get(event['httpMethod'])
    return executed(event)
