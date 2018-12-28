import json
from django.urls import reverse
from django.test.client import encode_multipart
from rest_framework import status
from datetime import date

from fondo_api.tests.abstract_test import AbstractTest
from fondo_api.models import *

view_get_post_years = 'view_get_post_years'
view_get_post_activities = 'view_get_post_activities'
view_get_patch_delete_activity = 'view_get_patch_delete_activity'

class ActivityViewTest(AbstractTest):
    def setUp(self):
        self.create_user()
        self.token = self.get_token('mail_for_tests@mail.com','password')

        self.activity_json = {
            "name": "New Activity for tests",
            "value": 30000,
            "date": "2020-11-7"
        }

    def test_get_years_empty(self):
        response = self.client.get(
			reverse(view_get_post_years),
			**self.get_auth_header(self.token)
		)

        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)

    def test_get_years(self):
        ActivityYear.objects.create(year=2020)
        ActivityYear.objects.create(year=2021)
        response = self.client.get(
			reverse(view_get_post_years),
			**self.get_auth_header(self.token)
		)

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)
        self.assertEqual(response.data[0]['year'],2021)
        self.assertEqual(response.data[1]['year'],2020)

    def test_create_year(self):
        response = self.client.post(
			reverse(view_get_post_years),
			**self.get_auth_header(self.token)
		)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        
        year = date.today().year
        activity_years = ActivityYear.objects.all()
        self.assertEqual(len(activity_years),1)
        self.assertEqual(activity_years[0].year, year)

        response = self.client.post(
			reverse(view_get_post_years),
			**self.get_auth_header(self.token)
		)
        self.assertEqual(response.status_code,status.HTTP_304_NOT_MODIFIED)

    def test_get_activities(self):
        activity_year_2020 = ActivityYear.objects.create(year=2020)
        activity_year_2021 = ActivityYear.objects.create(year=2021)

        Activity.objects.create(
            id=1,
            name="Test Activity 1",
            value=1000,
            date='2020-1-1',
            year = activity_year_2020
        )

        Activity.objects.create(
            id=2,
            name="Test Activity 2",
            value=1000,
            date='2021-1-1',
            year = activity_year_2021
        )

        response = self.client.get(
			reverse(view_get_post_activities,kwargs={'id_year':activity_year_2020.id}),
			**self.get_auth_header(self.token)
		)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['id'],1)
        self.assertEqual(response.data[0]['name'],'Test Activity 1')

    def test_create_activity(self):
        activity_year_2020 = ActivityYear.objects.create(year=2020)
        response = self.client.post(
			reverse(view_get_post_activities,kwargs={'id_year':activity_year_2020.id}),
            data=self.activity_json,
			**self.get_auth_header(self.token)
		)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        
        activities = Activity.objects.all()
        self.assertEqual(len(activities),1)
        self.assertEqual(activities[0].name,'New Activity for tests')
        self.assertEqual(activities[0].value,30000)
        self.assertEqual(activities[0].date.year,2020)
        self.assertEqual(activities[0].date.month,11)
        self.assertEqual(activities[0].date.day,7)
        self.assertEqual(activities[0].year_id,activity_year_2020.id)
        self.assertEqual(activities[0].users.count(),1)

    def test_get_activity_not_found(self):
        response = self.client.get(
            reverse(view_get_patch_delete_activity,kwargs={'id':12}),
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_activity(self):
        activity_year_2020 = ActivityYear.objects.create(year=2020)
        self.client.post(
			reverse(view_get_post_activities,kwargs={'id_year':activity_year_2020.id}),
            data=self.activity_json,
			**self.get_auth_header(self.token)
		)

        activity_id = Activity.objects.all()[0].id
        response = self.client.get(
            reverse(view_get_patch_delete_activity,kwargs={'id':activity_id}),
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'],activity_id)
        self.assertEqual(response.data['name'],'New Activity for tests')
        self.assertEqual(response.data['value'],30000)
        self.assertEqual(response.data['date'],'2020-11-07')
        self.assertEqual(len(response.data['users']),1)
        self.assertIsNotNone(response.data['users'][0]['id'])
        self.assertEqual(response.data['users'][0]['state'],0)

    def test_delete_activity(self):
        activity_year_2020 = ActivityYear.objects.create(year=2020)
        Activity.objects.create(
            id=1,
            name="Test Activity 1",
            value=1000,
            date='2020-1-1',
            year = activity_year_2020
        )
        response = self.client.delete(
            reverse(view_get_patch_delete_activity,kwargs={'id':1}),
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Activity.objects.all().count(),0)

    def test_update_activity(self):
        activity_year_2020 = ActivityYear.objects.create(year=2020)
        Activity.objects.create(
            id=1,
            name="Test Activity 1",
            value=1000,
            date='2020-1-1',
            year = activity_year_2020
        )
        response = self.client.patch(
            reverse(view_get_patch_delete_activity,kwargs={'id':1}),
            data=json.dumps(self.activity_json),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'],1)
        self.assertEqual(response.data['name'],'New Activity for tests')
        self.assertEqual(response.data['value'],30000)
        self.assertEqual(response.data['date'],'2020-11-07')
        self.assertEqual(response.data['users'],[])

        response = self.client.patch(
            reverse(view_get_patch_delete_activity,kwargs={'id':2}),
            data=json.dumps(self.activity_json),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_activity_user(self):
        activity_year_2020 = ActivityYear.objects.create(year=2020)
        self.client.post(
			reverse(view_get_post_activities,kwargs={'id_year':activity_year_2020.id}),
            data=self.activity_json,
			**self.get_auth_header(self.token)
		)

        activity_id = Activity.objects.all()[0].id
        activity_user_id = ActivityUser.objects.filter(activity_id = activity_id)[0].id
        patch_user = {
            "id": activity_user_id,
            "state": 2
        }
        response = self.client.patch(
            '%s?patch=user' % reverse(view_get_patch_delete_activity,kwargs={'id':activity_id}),
            data=json.dumps(patch_user),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'],activity_id)
        self.assertEqual(response.data['name'],'New Activity for tests')
        self.assertEqual(response.data['value'],30000)
        self.assertEqual(response.data['date'],'2020-11-07')
        self.assertEqual(len(response.data['users']),1)
        self.assertIsNotNone(response.data['users'][0]['id'])
        self.assertEqual(response.data['users'][0]['state'],2)

        response = self.client.patch(
            '%s?patch=user' % reverse(view_get_patch_delete_activity,kwargs={'id':123}),
            data=json.dumps(patch_user),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_activity_bad_request(self):
        response = self.client.patch(
            '%s?patch=invalid' % reverse(view_get_patch_delete_activity,kwargs={'id':1}),
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)