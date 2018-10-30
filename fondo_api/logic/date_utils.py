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

    startDate, endDate = normalizeDates(startDate, endDate, europeanMethod)
    
    startDay = 30 if startDate.month == 2 and startDate.day == calendar.monthrange(startDate.year, startDate.month)[1] else startDate.day
    endDay = 30 if endDate.month == 2 and endDate.day == calendar.monthrange(endDate.year, endDate.month)[1] else endDate.day

    diffYear = endDate.year - startDate.year
    if (diffYear > 0) and ((endDate.month < startDate.month) or (endDate.month == startDate.month and endDay < startDay)):
        diffYear -= 1

    diffMonth = endDate.month - startDate.month
    if diffMonth < 0:
        diffMonth = 12 - abs(diffMonth)
    if diffMonth > 0 and endDay < startDay:
        diffMonth -= 1
    elif diffMonth == 0 and endDate.year > startDate.year and endDay < startDay:
        diffMonth = 11

    diffDay = endDay - startDay
    if diffDay < 0:
        diffDay = 30 - abs(diffDay)
    
    if diffYear < 0 or diffMonth < 0 or diffDay < 0:
        raise Exception('Something went wrong: dy{} dm{} dd{}'.format(diffYear, diffMonth, diffDay))

    return (diffYear * 12 * 30) + (diffMonth * 30) + diffDay

def normalizeDates(startDate, endDate, europeanMethod = False):
    if europeanMethod:
        return (normalizeEuropeDate(startDate), normalizeEuropeDate(endDate))
    
    # NASD method
    daysInMonthStart = calendar.monthrange(startDate.year, startDate.month)[1]
    daysInMonthEnd = calendar.monthrange(endDate.year, endDate.month)[1]
    if daysInMonthStart == startDate.day:
        if startDate.month != 2:
            startDate = startDate.replace(day=30)
    if daysInMonthEnd == endDate.day:
        if (startDate.day < 30 and startDate.month != 2) or (startDate.day < daysInMonthStart and startDate.month == 2):
            endDate = endDate + datetime.timedelta(days = 1)
        elif (startDate.day >= 30 and startDate.month != 2) or (startDate.day >= daysInMonthStart and startDate.month == 2):
            endDate = endDate.replace(day=30)
    return (startDate, endDate)

def normalizeEuropeDate(date):
    if date.day > 30:
        return date.replace(day=30)
    return date