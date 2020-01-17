from django.conf.urls import url

from fondo_api.views.loan import LoanView, LoanDetailView, LoanAppsView
from fondo_api.views.user import UserView, UserDetailView, UserActivateView
from fondo_api.views.activity import ActivityDetailView, ActivityYearView, ActivityYearDetailView
from fondo_api.views.alexa import AlexaView
from fondo_api.views.auth import AuthView
from fondo_api.views.notification import NotificationView

urlpatterns = [
    url( r'^api/authorize/?$', AuthView.as_view(), name='view_auth' ),

    url( r'^api/loan/?$', LoanView.as_view(), name='view_loan' ),
    url( r'^api/loan/(?P<id>[0-9]+)$', LoanDetailView.as_view(), name='view_loan_detail' ),
    url( r'^api/loan/(?P<id>[0-9]+)/(?P<app>[a-zA-Z]+)$', LoanAppsView.as_view(), name='view_loan_apps' ),

    url( r'^api/user/?$', UserView.as_view(), name='view_user' ),
    url( r'^api/user/(?P<id>-?[0-9]+)$', UserDetailView.as_view(), name='view_user_detail' ),
    url( r'^api/user/activate/(?P<id>[0-9]+)$', UserActivateView.as_view(), name='view_user_activate' ),

    url( r'^api/activity/(?P<id>[0-9]+)/?$', ActivityDetailView.as_view(), name='view_activity_detail' ),
    url( r'^api/activity/year/?$', ActivityYearView.as_view(), name='view_activity_year'),
    url( r'^api/activity/year/(?P<id_year>[0-9]+)$', ActivityYearDetailView.as_view(), name='view_activity_year_detail' ),

    url( r'^api/alexa/?$', AlexaView.as_view(), name='view_alexa' ),

    url( r'^api/notification/(?P<operation>[a-zA-Z]+)/?$', NotificationView.as_view(), name='view_notification' ),
]
