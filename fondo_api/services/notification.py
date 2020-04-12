import json
from django.utils.timezone import make_aware

from fondo_api.celery.tasks import send_notification
from fondo_api.models import NotificationSubscriptions, UserProfile, SchedulerTask

class NotificationService:

    def save_subscription(self, user_id, subscription):
        user = UserProfile.objects.get(id=user_id)
        notifications = NotificationSubscriptions.objects.filter(subscription__endpoint=subscription['endpoint'])
        if len(notifications) == 0:
            NotificationSubscriptions.objects.create(
                user = user,
                subscription = subscription
            )

    def unregister_subscription(self, user_id, subscription):
        try:
            NotificationSubscriptions.objects.get(
                user_id = user_id,
                subscription__endpoint = subscription['endpoint']
            ).delete()
        except NotificationSubscriptions.DoesNotExist:
            return 404
        return 200

    def remove_all_subscriptions(self, user_id):
        NotificationSubscriptions.objects.filter(user_id=user_id).delete()

    def send_notification(self, user_ids, message, target, run_async = True):
        notification_subscriptions = NotificationSubscriptions.objects.filter(user_id__in=user_ids)
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
            send_notification.delay({'type': 'send_notification', 'content': content})
        else:
            send_notification({'type': 'send_notification', 'content': content})

    def schedule_notification(self, run_date, payload, repeat=0):
        tasks = SchedulerTask.objects.filter(payload__owner_id = payload["owner_id"], 
										payload__type = payload["type"],
										run_date__year = run_date.year,
										run_date__month = run_date.month,
										run_date__day = run_date.day,
										processed = False)
        if len(tasks) == 0:
            run_date = make_aware(run_date)
            SchedulerTask.objects.create(
                type = 0,
                run_date = run_date,
                payload = payload,
                repeat = repeat
            )

    def remove_sch_notitfications(self, notification_type, owner_id):
        SchedulerTask.objects.filter(payload__owner_id = owner_id,
                                payload__type = notification_type).delete()