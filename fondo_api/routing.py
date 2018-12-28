from channels.routing import ChannelNameRouter, ProtocolTypeRouter

from fondo_api.tasks.consumers import NotificationTaskConsumer

application = ProtocolTypeRouter({
    'channel': ChannelNameRouter({
        'notification-task': NotificationTaskConsumer,
    })
})