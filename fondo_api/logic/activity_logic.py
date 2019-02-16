import logging
from datetime import date
from django.db import IntegrityError, transaction
from django.db.models import Q

from fondo_api.models import ActivityYear, Activity, ActivityUser, UserProfile
from fondo_api.serializers import ActivityYearSerializer, ActivityGeneralSerializer, ActivityDetailSerializer

logger = logging.getLogger(__name__)

def create_year():
    year = date.today().year
    try:
        years = ActivityYear.objects.filter(~Q(year = year)).order_by('-year')
        if len(years) > 0:
            last_year = years[0]
            last_year.enable = False
            last_year.save()
        ActivityYear.objects.create(year = year)
    except IntegrityError:
        return False
    return True

def get_years():
    years = ActivityYear.objects.all().order_by('-year')
    serializer = ActivityYearSerializer(years,many=True)
    return serializer.data

def get_activities(id_year):
    activities = Activity.objects.filter(year_id = id_year).order_by('-date')
    serializer = ActivityGeneralSerializer(activities, many=True)
    return serializer.data

@transaction.atomic
def create_activity(data, id_year):
    activity = Activity()
    activity.name = data['name']
    activity.value = int(data['value'])
    activity.year_id = id_year
    activity.date = data['date']
    activity.save()
    add_users(activity)

def add_users(activity):
    users = UserProfile.objects.filter(is_active = True).order_by('id')
    for user in users:
        activity_user = ActivityUser()
        activity_user.user = user
        activity_user.activity = activity
        activity_user.save()

def get_activity(id):
    try:
        activity = Activity.objects.get(id = id)
        serializer = ActivityDetailSerializer(activity)
        return serializer.data
    except Activity.DoesNotExist:
        return None

def remove_activity(id):
    activity = Activity.objects.filter(id = id).delete()

def patch_activity(patch, id, data):
    try:
        if patch == 'activity':
            update_activity(id,data)
        else:
            update_activity_user(id, data)
    except:
        return None
    return get_activity(id)

def update_activity(id, data):
    try:
        activity = Activity.objects.get(id = id)
        activity.name = data['name']
        activity.date = data['date']
        activity.value = data['value']
        activity.save()
    except Activity.DoesNotExist:
        raise

def update_activity_user(id, data):
    try:
        activity_user_id = data['id']
        activity_user = ActivityUser.objects.get(activity_id = id, id = activity_user_id)
        activity_user.state = data['state']
        activity_user.save()
    except ActivityUser.DoesNotExist:
        raise