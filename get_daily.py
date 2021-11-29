import argparse

from github import Github

from daily.config import (
    MONTH_SUMMARY_HEAD,
    MONTH_SUMMARY_STAT_TEMPLATE,
)
from daily.utils import replace_readme_comments, LABEL_DAILY_DICT
from daily import MY_STATUS_DICT_FROM_API, MY_STATUS_DICT_FROM_COMMENTS


MY_NUMBER_STAT_HEAD = (
    "| Name | Status | Streak | Today? | \n | ---- | ---- | ---- | ---- |\n"
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


def main(
    login_dict,
    github_token,
    repo_name,
):
    my_num_stat_str = MY_NUMBER_STAT_HEAD
    # API STAT STR
    for name, value_dict in MY_STATUS_DICT_FROM_API.items():
        try:
            url = value_dict.get("url")
            md_name = f"[{name}]({url})"
            # maybe a better way?
            total_data, streak, today_check = value_dict.get("daily_func")(
                *login_dict.get(name, tuple())
            )
            total_data_str = str(total_data) + value_dict.get("unit_str", "")
            my_num_stat_str += make_stat_str(
                md_name, total_data_str, streak, today_check
            )
        # just a tricky code for others for use
        except Exception as e:
            print(e)
            continue

    u = Github(github_token)
    me = u.get_user().login
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

        issues = u.get_repo(repo_name).get_issues(labels=labels)
        total_data, streak, today_check, url, month_summary_dict = func(
            me, issues, map_func, reduce_func
        )
        # change the issue body for month summary
        unit = value_dict.get("unit_str", "")
        for i in issues:
            body = ""
            for b in i.body.splitlines():
                # from the summary table
                if b.startswith("|"):
                    break
                body += b
            body = body + "\r\n" + make_month_summary_str(month_summary_dict, unit)
            # edit this issue body
            i.edit(body=body)
        name = f"[{name}]({url})"
        total_data_str = str(total_data) + unit
        my_num_stat_str += make_stat_str(name, total_data_str, streak, today_check)

    replace_readme_comments("README.md", my_num_stat_str, "my_number")


def make_month_summary_str(month_summary_dict, unit):
    s = MONTH_SUMMARY_HEAD
    for m, n in month_summary_dict.items():
        s += MONTH_SUMMARY_STAT_TEMPLATE.format(
            month=str(m) + "月", number=str(int(n)) + f" {unit}"
        )
    return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("duolingo_user_name", help="duolingo_user_name")
    parser.add_argument("duolingo_password", help="duolingo_password")
    parser.add_argument("cichang_user_name", help="cichang_user_name")
    parser.add_argument("cichang_password", help="cichang_password")
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    options = parser.parse_args()
    # add more login auth info here
    login_auth_dict = {
        "词场": (options.cichang_user_name, options.cichang_password),
        "多邻国": (options.duolingo_user_name, options.duolingo_password),
    }
    main(
        login_auth_dict,
        options.github_token,
        options.repo_name,
    )
