from django.conf.urls import url
from .views.loan_view import LoanView
from .views.user_view import UserView
from .views.activity_view import ActivityView
from .views.alexa_view import AlexaView
from .views.auth_view import AuthView
from .views.notification_view import NotificationView

urlpatterns = [
    url( r'^api/authorize/?$', AuthView.as_view(), name='view_auth' ),

    url( r'^api/loan/(?P<id>[0-9]+)/(?P<app>[a-zA-Z]+)$', LoanView.view_loan_apps, name='view_loan_apps' ),
    url( r'^api/loan/(?P<id>[0-9]+)$', LoanView.view_get_update_loan, name='view_get_update_loan' ),
    url( r'^api/loan/?$', LoanView.view_get_post_loans, name='view_get_post_loans' ),

    url( r'^api/user/?$', UserView.view_get_post_users, name='view_get_post_users' ),
    url( r'^api/user/(?P<id>-?[0-9]+)$', UserView.view_get_update_delete_user, name='view_get_update_delete_user' ),
    url( r'^api/user/activate/(?P<id>[0-9]+)$', UserView.view_activate_user, name='view_activate_user' ),
    url( r'^api/user/logout/?$', UserView.view_logout, name='view_logout' ),

    url( r'^api/activity/year/?$', ActivityView.view_get_post_years, name='view_get_post_years'),
    url( r'^api/activity/year/(?P<id_year>[0-9]+)$', ActivityView.view_get_post_activities, name='view_get_post_activities'),
    url( r'^api/activity/(?P<id>[0-9]+)/?$', ActivityView.view_get_patch_delete_activity, name='view_get_patch_delete_activity'),

    url( r'^api/alexa/?$', AlexaView.as_view(), name='view_alexa'),

    url( r'^api/notification/subscribe/?$', NotificationView.view_notification_subscribe, name='view_notification_subscribe'),
    url( r'^api/notification/unsubscribe/?$', NotificationView.view_notification_unsubscribe, name='view_notification_unsubscribe'),
]