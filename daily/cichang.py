import hashlib
import json

import pendulum
import requests

HJ_APPKEY = "45fd17e02003d89bee7f046bb494de13"
LOGIN_URL = "https://pass.hujiang.com/Handler/UCenter.json?action=Login&isapp=true&language=zh_CN&password={password}&timezone=8&user_domain=hj&username={user_name}"
COVERT_URL = "https://pass-cdn.hjapi.com/v1.1/access_token/convert"
MY_LOG_URL = "https://cichang.hjapi.com/v3/user/center/?userId={user_id}&startDate={start_date}&endDate={end_date}"


def md5_encode(string):
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()


def _get_cichang_streak(s, user_id, end_date=pendulum.now("Asia/Shanghai"), streak=0):
    start_date = end_date.start_of("month")
    r = s.get(
        MY_LOG_URL.format(
            user_id=user_id,
            start_date=start_date.to_date_string(),
            end_date=end_date.to_date_string(),
        )
    )
    if not r.ok:
        raise Exception("Can not get days from cichang API")
    data = r.json()
    logs = data["data"]["studyCountDays"]
    if not logs:
        return streak
    periods = list(pendulum.period(start_date, end_date.subtract(days=1)))
    periods.sort(reverse=True)

    # cichang log data like [{'studyCount': 10, 'studyDate': '2021/02/09'}, {'studyCount': 20, 'studyDate': '2021/02/18'}]
    log_dates = [i["studyDate"].replace("/", "-") for i in logs]
    # if today id done
    if end_date.to_date_string() in log_dates:
        streak += 1

    # for else if not break not else
    for p in periods:
        if p.to_date_string() not in log_dates:
            break
        streak += 1
    else:
        streak = _get_cichang_streak(
            s, user_id, start_date.subtract(months=1).end_of("month"), streak=streak
        )
    return streak


def login(user_name, password):
    s = requests.Session()
    password_md5 = md5_encode(password)
    r = s.get(LOGIN_URL.format(user_name=user_name, password=password_md5))
    if not r.ok:
        raise Exception(f"Someting is wrong to login -- {r.text}")
    club_auth_cookie = r.json()["Data"]["Cookie"]
    data = {"club_auth_cookie": club_auth_cookie}
    headers = {"hj_appkey": HJ_APPKEY, "Content-Type": "application/json"}
    # real login to get real token
    r = s.post(COVERT_URL, headers=headers, data=json.dumps(data))
    if not r.ok:
        raise Exception(f"Get real token failed -- {r.text}")
    data = r.json()["data"]
    access_token = data["access_token"]
    user_id = data["user_id"]
    headers["Access-Token"] = access_token
    s.headers = headers
    return s, user_id


def get_cichang_daily(user_name, password):
    s, user_id = login(user_name, password)
    is_today_check = False
    now = pendulum.now("Asia/Shanghai")
    end_date = now.to_date_string()
    start_date = now.subtract(months=1).to_date_string()
    r = s.get(
        MY_LOG_URL.format(user_id=user_id, start_date=start_date, end_date=end_date)
    )
    data = r.json()
    logs = data["data"]["studyCountDays"]
    total_days = data["data"]["studyDayCount"]
    if logs:
        last_day_check = logs[-1]["studyDate"].replace("/", "-")
        is_today_check = last_day_check == end_date
    streak = _get_cichang_streak(s, user_id)
    return total_days, streak, is_today_check
