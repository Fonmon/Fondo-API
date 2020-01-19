import datetime
from django.test import TestCase

from fondo_api.services.utils.date import days360

class DateUtilsTest(TestCase):
    def test_case_nasd(self):
        self.assertEqual(days360(datetime.date(2018,3,28), datetime.date(2019,3,27)), 359)
        self.assertEqual(days360(datetime.date(2018,2,28), datetime.date(2018,3,28)), 28)
        self.assertEqual(days360(datetime.date(2018,4,29), datetime.date(2018,5,31)), 32)
        self.assertEqual(days360(datetime.date(2018,4,30), datetime.date(2018,5,31)), 30)
        self.assertEqual(days360(datetime.date(2018,2,27), datetime.date(2018,5,31)), 94)
        self.assertEqual(days360(datetime.date(2018,2,28), datetime.date(2018,3,31)), 30)
        self.assertEqual(days360(datetime.date(2018,3,29), datetime.date(2018,5,31)), 62)
        self.assertEqual(days360(datetime.date(2018,5,31), datetime.date(2018,3,29)), 62)
        self.assertEqual(days360(datetime.date(2018,3,10), datetime.date(2018,3,31)), 21)
        self.assertEqual(days360(datetime.date(2012,2,29), datetime.date(2013,2,28)), 358)
        self.assertEqual(days360(datetime.date(2016,1,1), datetime.date(2016,12,31)), 360)
        self.assertEqual(days360(datetime.date(2012,2,29), datetime.date(2016,2,29)), 1439)

    def test_case_european(self):
        self.assertEqual(days360(datetime.date(2018,3,28), datetime.date(2019,3,27), True), 359)
        self.assertEqual(days360(datetime.date(2018,2,28), datetime.date(2018,3,28), True), 30)
        self.assertEqual(days360(datetime.date(2018,4,29), datetime.date(2018,5,31), True), 31)
        self.assertEqual(days360(datetime.date(2018,4,30), datetime.date(2018,5,31), True), 30)
        self.assertEqual(days360(datetime.date(2018,2,27), datetime.date(2018,5,31), True), 93)
        self.assertEqual(days360(datetime.date(2018,2,28), datetime.date(2018,3,31), True), 32)
        self.assertEqual(days360(datetime.date(2018,3,29), datetime.date(2018,5,31), True), 61)
        self.assertEqual(days360(datetime.date(2018,5,31), datetime.date(2018,3,29), True), 61)
        self.assertEqual(days360(datetime.date(2018,3,10), datetime.date(2018,3,31), True), 20)
        self.assertEqual(days360(datetime.date(2012,2,29), datetime.date(2013,2,28), True), 359)
        self.assertEqual(days360(datetime.date(2016,1,1), datetime.date(2016,12,31), True), 359)
        self.assertEqual(days360(datetime.date(2012,2,29), datetime.date(2016,2,29), True), 1440)