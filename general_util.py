from datetime import date

def get_academic_year():
    today = date.today()

    if today.month < 9: #before september
        begin = date(today.year - 1,9,1)
        end = date(today.year, 8, 31)
    else:
        begin = date(today.year,9,1)
        end = date(today.year+1,8,31)

    return begin, end