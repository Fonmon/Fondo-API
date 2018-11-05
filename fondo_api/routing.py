from channels.routing import ChannelNameRouter, ProtocolTypeRouter
from .tasks.consumers import NotificationTaskConsumer

application = ProtocolTypeRouter({
    'channel': ChannelNameRouter({
        'notification-task': NotificationTaskConsumer,
    })
})