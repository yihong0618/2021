import argparse
import requests
import pendulum
from main import login

GET_UP_ISSUE_NUMBER = 14
GET_UP_MESSAGE_TEMPLATE = (
    "起床啦，喝杯咖啡，背个单词，去跑步。\r\n\r\n 今天的起床时间是--{get_up_time}.\r\n 今天的一句诗: {sentence}"
)
SENTENCE_API = "https://v1.jinrishici.com/all"
DEFAULT_SENTENCE = "赏花归去马如飞\r\n去马如飞酒力微\r\n酒力微醒时已暮\r\n醒时已暮赏花归\r\n"
TIMEZONE = "Asia/Shanghai"


def get_one_sentence():
    r = requests.get(SENTENCE_API)
    if r.ok:
        return r.json().get("content", DEFAULT_SENTENCE)
    return DEFAULT_SENTENCE


def get_today_get_up_status(issue):
    comments = list(issue.get_comments())
    if not comments:
        return False
    latest_comment = comments[-1]
    now = pendulum.now(TIMEZONE)
    latest_day = pendulum.instance(latest_comment.created_at).in_timezone(
        "Asia/Shanghai"
    )
    is_today = (latest_day.day == now.day) and (latest_day.month == now.month)
    return is_today


def make_get_up_message():
    sentence = get_one_sentence()
    now = pendulum.now(TIMEZONE)
    is_get_up_early = 4 <= now.hour <= 6
    get_up_time = now.to_datetime_string()
    body = GET_UP_MESSAGE_TEMPLATE.format(get_up_time=get_up_time, sentence=sentence)
    return body, is_get_up_early


def get_get_up_issue(repo):
    return repo.get_issue(GET_UP_ISSUE_NUMBER)


def make_new_get_up_comment(issue, body):
    # maybe use in the future
    _ = issue.create_comment(body)
    return


def main(github_token, repo_name):
    u = login(github_token)
    repo = u.get_repo(repo_name)
    issue = get_get_up_issue(repo)
    is_toady = get_today_get_up_status(issue)
    if is_toady:
        print("today has get up")
        return
    body, is_get_up_early = make_get_up_message()
    if is_get_up_early:
        make_new_get_up_comment(issue, body)
    else:
        print("today you have are late")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    options = parser.parse_args()
    main(options.github_token, options.repo_name)
