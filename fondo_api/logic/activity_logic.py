from datetime import date
from ..models import ActivityYear, Activity
from django.db import IntegrityError
from ..serializers import ActivityYearSerializer, ActivityGeneralSerializer

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
    activities = Activity.objects.filter(year_id = id_year)
    serializer = ActivityGeneralSerializer(activities, many=True)
    return serializer.data