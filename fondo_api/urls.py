from django.conf.urls import url
from . import views

urlpatterns = [
    url( r'^api/loan/(?P<id>[0-9]+)$', views.view_update_loan, name='view_update_loan' ),
    url( r'^api/loan/?$', views.view_get_post_loans, name='view_get_post_loans' ),
    url( r'^api/user/$', views.view_get_post_users, name='view_get_post_users' ),
    url( r'^api/user/(?P<id>-?[0-9]+)$', views.view_get_update_delete_user, name='view_get_update_delete_user' )
]