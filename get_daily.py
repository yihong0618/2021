import argparse
import os
from getpass import getpass

import pendulum
import requests
from github import Github

from config import PUSHUP_LABEL_LIST
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


def get_duolingo_words_and_save_mp3(session, latest_num=100):
    r = session.get("https://www.duolingo.com/vocabulary/overview")
    if not r.ok:
        raise Exception("get duolingo words failed")
    words = r.json()["vocab_overview"]
    words_list = []
    i = 1
    for w in words[:latest_num]:
        if w["normalized_string"] == "<*sf>":
            continue
        words_list.append(w["word_string"])
        try:
            word_info = session.get(
                f"https://www.duolingo.com/api/1/dictionary_page?lexeme_id={w['lexeme_id']}"
            ).json()
            mp3_content = requests.get(word_info["tts"])
            with open(os.path.join("MP3_NEW", str(i) + ".mp3"), "wb") as f:
                f.write(mp3_content.content)
            i += 1
        except:
            pass
    if words_list:
        return "\n".join(words_list)


def get_push_up_daily(github_token, repo_name):
    u = Github(github_token)
    issues = u.get_repo(repo_name).get_issues(labels=PUSHUP_LABEL_LIST)
    push_up_total = 0
    push_up_date_list = []
    for issue in issues:
        comments = issue.get_comments()
        for c in comments:
            push_up_number_str = c.body.split("\r\n")[0]
            try:
                push_up_number = int(push_up_number_str)
            except:
                continue
            push_up_total += push_up_number
            push_up_date_list.append(c.created_at)
    end_date = pendulum.now("Asia/Shanghai")
    date_str_list = [pendulum.instance(i).to_date_string() for i in push_up_date_list]
    is_today_check = False
    streak = 0
    if end_date.to_date_string() in date_str_list:
        is_today_check = True
        streak += 1
    periods = list(
        pendulum.period(
            pendulum.instance(push_up_date_list[-1]), end_date.subtract(days=1)
        )
    )
    for p in periods:
        if p.to_date_string() not in date_str_list:
            break
        streak += 1
    return push_up_total, streak, is_today_check


def main(
    duolingo_user_name,
    duolingo_password,
    tele_token,
    tele_chat_id,
    github_token,
    repo_name,
):
    shanbay_total, shanbay_today_check = get_shanbay_today_info()
    shanbay_streak = get_shanbay_streak()
    s, duolingo_name = get_duolingo_session_and_name(
        duolingo_user_name, duolingo_password
    )
    duolingo_total, duolingo_streak, duolingo_today_check = get_duolingo_daily(
        s, duolingo_name
    )
    push_up_total, push_up_streak, push_up_totay_check = get_push_up_daily(
        github_token, repo_name
    )
    str_shanbay = MY_NUMBER_STAT_TEMPLATE.format(
        name="扇贝",
        total=str(shanbay_total) + " (Days)",
        streak=shanbay_streak,
        today=NO_OR_YES_LIST[shanbay_today_check],
    )
    str_duolingo = MY_NUMBER_STAT_TEMPLATE.format(
        name="多邻国",
        total=str(duolingo_total) + " (Points)",
        streak=duolingo_streak,
        today=NO_OR_YES_LIST[duolingo_today_check],
    )
    str_push_up = MY_NUMBER_STAT_TEMPLATE.format(
        name="俯卧撑",
        total=str(push_up_total) + " (number)",
        streak=push_up_streak,
        today=NO_OR_YES_LIST[push_up_totay_check],
    )
    my_num_stat_str = MY_NUMBER_STAT_HEAD + str_shanbay + str_duolingo
    duolingo_words = get_duolingo_words_and_save_mp3(s)
    if duolingo_words:
        duolingo_words = "New words\n" + duolingo_words
        requests.post(
            url="https://api.telegram.org/bot{0}/{1}".format(tele_token, "sendMessage"),
            data={"chat_id": tele_chat_id, "text": duolingo_words},
        )
    if not (shanbay_today_check and duolingo_today_check):
        requests.post(
            url="https://api.telegram.org/bot{0}/{1}".format(tele_token, "sendMessage"),
            data={"chat_id": tele_chat_id, "text": "今天还没完成 streak 请注意"},
        )
    replace_readme_comments(my_num_stat_str, "my_number")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("duolingo_user_name", help="duolingo_user_name")
    parser.add_argument("duolingo_password", help="duolingo_password")
    parser.add_argument("tele_token", help="tele_token")
    parser.add_argument("tele_chat_id", help="tele_chat_id")
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    options = parser.parse_args()
    main(
        options.duolingo_user_name,
        options.duolingo_password,
        options.tele_token,
        options.tele_chat_id,
        options.github_token,
        options.repo_name,
    )
