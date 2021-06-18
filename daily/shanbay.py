import pendulum
import requests

from .config import MY_SHANBAY_USER_NAME, SHANBAY_CALENDAR_API


def _get_shanbay_streak(end_date=pendulum.now("Asia/Shanghai"), streak=0):
    start_date = end_date.start_of("month")
    r = requests.get(
        SHANBAY_CALENDAR_API.format(
            user_name=MY_SHANBAY_USER_NAME,
            start_date=start_date.to_date_string(),
            end_date=end_date.to_date_string(),
        )
    )
    if not r.ok:
        raise Exception("Can not get days from shanbay API")

    data = r.json()
    logs = data["logs"]
    if not logs:
        return streak
    periods = list(pendulum.period(start_date, end_date.subtract(days=1)))
    periods.sort(reverse=True)

    log_dates = [i["date"] for i in logs]
    # if today id done
    if end_date.to_date_string() in log_dates:
        streak += 1

    # for else if not break not else
    for p in periods:
        if p.to_date_string() not in log_dates:
            break
        streak += 1
    else:
        streak = _get_shanbay_streak(
            start_date.subtract(months=1).end_of("month"), streak=streak
        )
    return streak


def get_shanbay_daily(*args):
    """
    first get today status
    """
    end_date = pendulum.now("Asia/Shanghai")
    start_date = end_date.start_of("month")
    r = requests.get(
        SHANBAY_CALENDAR_API.format(
            user_name=MY_SHANBAY_USER_NAME,
            start_date=start_date.to_date_string(),
            end_date=end_date.to_date_string(),
        )
    )
    if not r.ok:
        raise Exception("Can not get days from shanbay API")

    data = r.json()
    is_today_check = False
    total_days = data.get("checkin_days_num", 0)
    log_dates = [i["date"] for i in data["logs"]]
    if end_date.to_date_string() in log_dates:
        is_today_check = True
    streak = _get_shanbay_streak()
    return total_days, streak, is_today_check
