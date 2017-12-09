from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^api/loan/(?P<pk>[0-9]+)$',
        views.get_loans,
        name='get_loans'
    ),
    url(
        r'^api/loan/$',
        views.post_loan,
        name='post_loan'
    ),
    url(
        r'^api/user/$',
        views.get_post_user,
        name='get_post_user'
    )
]