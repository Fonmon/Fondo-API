from ..models import NotificationSubscriptions, UserProfile

def save_subscription(user_id, subscription):
    user = UserProfile.objects.get(id = user_id)
    NotificationSubscriptions.objects.create(
        user = user,
        subscription = subscription
    )

def unregister_subscription(user_id, subscription):
    try:
        NotificationSubscriptions.objects.get(
            user_id = user_id,
            subscription__endpoint = subscription['endpoint']
        ).delete()
    except NotificationSubscriptions.DoesNotExist:
        return 404
    return 200

def remove_all_subscriptions(user_id):
    NotificationSubscriptions.objects.filter(user_id = user_id).delete()

def send_notification():
    pass