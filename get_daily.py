import argparse

from github import Github

from daily.config import (
    LABEL_DAILY_DICT,
)
from daily.utils import replace_readme_comments
from daily import MY_STATUS_DICT_FROM_API, MY_STATUS_DICT_FROM_COMMENTS


MY_NUMBER_STAT_HEAD = (
    "| Name | Total | Streak | Today? | \n | ---- | ---- | ---- | ---- |\n"
)
MY_NUMBER_STAT_TEMPLATE = "| {name} | {total} | {streak} | {today} |\n"


# this is a tricky ->  [a, b][False] => [a] [a, b][True] => [b]
NO_OR_YES_LIST = ["NO", "YES"]


def make_stat_str(name, total_str, streak, today_check):
    # format
    return MY_NUMBER_STAT_TEMPLATE.format(
        name=name,
        total=total_str,
        streak=streak,
        today=NO_OR_YES_LIST[today_check],
    )


def main(duolingo_user_name, duolingo_password, github_token, repo_name):
    my_num_stat_str = MY_NUMBER_STAT_HEAD
    # API STAT STR
    for name, value_dict in MY_STATUS_DICT_FROM_API.items():
        url = value_dict.get("url")
        name = f"[{name}]({url})"
        total_data, streak, today_check = value_dict.get("daily_func")(
            duolingo_user_name, duolingo_password
        )
        total_data_str = str(total_data) + value_dict.get("unit_str", "")
        my_num_stat_str += make_stat_str(name, total_data_str, streak, today_check)

    u = Github(github_token)
    # COMMENTS STAT STR
    for name, value_dict in MY_STATUS_DICT_FROM_COMMENTS.items():
        try:
            labels, map_func, reduce_func = LABEL_DAILY_DICT.get(name)
        except:
            # tricky for mine
            continue
        func = value_dict.get("daily_func")
        if not func:
            break
        total_data, streak, today_check, url = func(
            u, repo_name, labels, map_func, reduce_func
        )
        name = f"[{name}]({url})"
        total_data_str = str(total_data) + value_dict.get("unit_str", "")
        my_num_stat_str += make_stat_str(name, total_data_str, streak, today_check)
    replace_readme_comments("README.md", my_num_stat_str, "my_number")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("duolingo_user_name", help="duolingo_user_name")
    parser.add_argument("duolingo_password", help="duolingo_password")
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    options = parser.parse_args()
    main(
        options.duolingo_user_name,
        options.duolingo_password,
        options.github_token,
        options.repo_name,
    )
