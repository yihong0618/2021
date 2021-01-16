import argparse
from getpass import getpass

import pendulum
import requests

from utils import replace_readme_comments

MY_SHANBAY_USER_NAME = "ufewz"
SHANBAY_CALENDAR_API = "https://apiv3.shanbay.com/uc/checkin/calendar/dates/?user_id={user_name}&start_date={start_date}&end_date={end_date}"

MY_NUMBER_STAT_HEAD = (
    "| Name | Total | Streak | Today? | \n | ---- | ---- | ---- | ---- |\n"
)
MY_NUMBER_STAT_TEMPLATE = "| {name} | {total} | {streak} | {today} |\n"

# this is a tricky ->  [a, b][False] => [a] [a, b][True] => [b]
NO_OR_YES_LIST = ["NO", "YES"]


def get_shanbay_today_info():
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
    return total_days, is_today_check


def get_shanbay_streak(end_date=pendulum.now("Asia/Shanghai"), streak=0):
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
        streak = get_shanbay_streak(
            start_date.subtract(months=1).end_of("month"), streak=streak
        )
    return streak


def get_duolingo_session_and_name(user_name, password):
    if password is None:
        password = getpass()
    s = requests.Session()
    r = s.post(
        "https://www.duolingo.com/login",
        params={"login": user_name, "password": password},
    )
    if r.status_code != 200:
        raise Exception("Login failed")
    name = r.json()["username"]
    return s, name


def get_duolingo_daily(session, name):
    r = session.get(f"https://www.duolingo.com/users/{name}")
    if r.status_code != 200:
        raise Exception("Get profile failed")
    data = r.json()

    is_today_check = data["streak_extended_today"]
    streak = data["site_streak"]
    lauguage = data["learning_language"]
    level_progress = data["language_data"].get(lauguage, {}).get("level_progress", 0)
    return level_progress, streak, is_today_check


def main(duolingo_user_name, duolingo_password):
    shanbay_total, shanbay_today_check = get_shanbay_today_info()
    shanbay_streak = get_shanbay_streak()
    s, duolingo_name = get_duolingo_session_and_name(
        duolingo_user_name, duolingo_password
    )
    duolingo_total, duolingo_streak, duolingo_today_check = get_duolingo_daily(
        s, duolingo_name
    )
    str_shanbay = MY_NUMBER_STAT_TEMPLATE.format(
        name="扇贝",
        total=str(shanbay_total) + "(Days)",
        streak=shanbay_streak,
        today=NO_OR_YES_LIST[shanbay_today_check],
    )
    str_duolingo = MY_NUMBER_STAT_TEMPLATE.format(
        name="多邻国",
        total=str(duolingo_total) + "(Points)",
        streak=duolingo_streak,
        today=NO_OR_YES_LIST[duolingo_today_check],
    )
    my_num_stat_str = MY_NUMBER_STAT_HEAD + str_shanbay + str_duolingo

    replace_readme_comments(my_num_stat_str, "my_number")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("duolingo_user_name", help="duolingo_user_name")
    parser.add_argument("duolingo_password", help="duolingo_password")
    options = parser.parse_args()
    main(options.duolingo_user_name, options.duolingo_password)
