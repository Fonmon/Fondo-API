import json
import fondo_api.scheduler.tasks as tasks
from fondo_api.models import NotificationSubscriptions, UserProfile

def save_subscription(user_id, subscription):
    user = UserProfile.objects.get(id = user_id)
    notifications = NotificationSubscriptions.objects.filter(subscription__endpoint = subscription['endpoint'])
    if len(notifications) == 0:
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

def remove_invalid_subscriptions(subscriptions):
    for subscription in subscriptions:
        NotificationSubscriptions.objects.filter( subscription__endpoint = subscription['endpoint'] ).delete()

def send_notification(user_ids, message, target, run_async = True):
    notification_subscriptions = NotificationSubscriptions.objects.filter(user_id__in = user_ids)
    if len(notification_subscriptions) == 0:
        return
    subscriptions = []
    for notification_subscription in notification_subscriptions:
        subscription = notification_subscription.subscription
        subscription['keys'] = subscription['keys'].replace("'", '"')
        subscription['keys'] = json.loads(subscription['keys'])
        subscriptions.append(subscription)

    content = {
        'subscriptions': subscriptions,
        'message': {
            'body': message,
            'target': target
        }
    }
    if run_async:
        tasks.send_notification.delay({'type': 'send_notification', 'content': content})
    else:
        tasks.send_notification({'type': 'send_notification', 'content': content})