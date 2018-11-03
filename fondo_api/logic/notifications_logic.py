from ..models import NotificationSubscriptions, UserProfile

def save_subscription(user_id, subscription):
    try:
        user = UserProfile.objects.get(id = user_id)
        NotificationSubscriptions.objects.create(
            user = user,
            subscription = subscription
        )
    except UserProfile.DoesNotExist:
        return 404
    except Exception as ex:
        print(ex)
        return 500
    return 200

def unregister_subscription(user_id, subscription):
    try:
        NotificationSubscriptions.objects.get(
            user_id = user_id,
            subscription__endpoint = subscription['endpoint']
        ).delete()
    except NotificationSubscriptions.DoesNotExist:
        return 404
    return 200