import requests


def _get_duolingo_session_and_name(user_name, password):
    s = requests.Session()
    r = s.post(
        "https://www.duolingo.com/login",
        params={"login": user_name, "password": password},
    )
    if r.status_code != 200:
        raise Exception("Login failed")
    name = r.json()["username"]
    return s, name


def get_duolingo_daily(user_name, password):
    s, name = _get_duolingo_session_and_name(user_name, password)
    r = s.get(f"https://www.duolingo.com/users/{name}")
    if r.status_code != 200:
        raise Exception("Get profile failed")
    data = r.json()

    is_today_check = data["streak_extended_today"]
    streak = data["site_streak"]
    lauguage = data["learning_language"]
    total = data["language_data"].get(lauguage, {}).get("level_progress", 0)
    return total, streak, is_today_check
