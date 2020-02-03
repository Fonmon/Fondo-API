import calendar
import datetime

def days360(startDate, endDate, europeanMethod = False):
    diffDates = endDate - startDate
    if diffDates.days == 0:
        return 0

    if diffDates.days < 0:
        tmpDate = startDate
        startDate = endDate
        endDate = tmpDate

    startDay = startDate.day
    endDay = endDate.day

    if europeanMethod:
        startDay = min(startDay, 30)
        endDay = min(endDay, 30)
    else:
        # US NASD
        if isLastDay(startDate):
            startDay = 30
        if startDay == 30 and endDay == 31:
            endDay = 30

    return ((endDate.year - startDate.year)*360) + ((endDate.month - startDate.month)*30) + (endDay - startDay)

def isLastDay(date):
    return calendar.monthrange(date.year, date.month)[1] == date.day