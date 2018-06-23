from datetime import date
from ..models import ActivityYear, Activity, ActivityUser, UserProfile
from django.db import IntegrityError, transaction
from ..serializers import ActivityYearSerializer, ActivityGeneralSerializer, ActivityDetailSerializer

def create_year():
    year = date.today().year
    try:
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
    try:
        activity.save()
        add_users(activity)
    except IntegrityError:
        return False
    return True

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