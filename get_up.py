import argparse
import requests
import pendulum
from main import login

GET_UP_ISSUE_NUMBER = 14
GET_UP_MESSAGE_TEMPLATE = "起床啦，喝杯咖啡，背个单词，去跑步。\r\n\r\n 今天的起床时间是--{get_up_time}.\r\n 今天的天气是: {weather}\r\n 今天的一句话: {sentence}"
SENTENCE_API = "https://v1.jinrishici.com/all"
DEFAULT_SENTENCE = "赏花归去马如飞\r\n去马如飞酒力微\r\n酒力微醒时已暮\r\n醒时已暮赏花归\r\n"
TIMEZONE = "Asia/Shanghai"


def get_one_sentence():
    r = requests.get(SENTENCE_API)
    if r.ok:
        return r.json().get("content", DEFAULT_SENTENCE)
    return DEFAULT_SENTENCE


def make_get_up_message(weather):
    weather = str(weather)
    sentence = get_one_sentence()
    now = pendulum.now(TIMEZONE)
    is_get_up_early = 4 <= now.hour <= 6
    get_up_time = now.to_datetime_string()
    body = GET_UP_MESSAGE_TEMPLATE.format(
        get_up_time=get_up_time, weather=weather, sentence=sentence
    )
    return body, is_get_up_early


def make_new_get_up_comment(repo, body):
    issue = repo.get_issue(GET_UP_ISSUE_NUMBER)
    # maybe use in the future
    _ = issue.create_comment(body)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument("weather", help="weather")
    options = parser.parse_args()
    u = login(options.github_token)
    repo = u.get_repo(options.repo_name)
    body, is_get_up_early = make_get_up_message(options.weather)
    if is_get_up_early:
        pass
    make_new_get_up_comment(repo, body)
