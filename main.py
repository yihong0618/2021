# -*- coding: utf-8 -*-
import argparse
import re

from github import Github


COOK_LABEL_LIST = ["Cook", ]
MY_BLOG_REPO = "yihong0618/blog"


def get_me(user):
    return user.get_user().login


def isMe(issue, me):
    return issue.user.login == me


def format_time(time):
    return str(time)[:10]


def login(token):
    return Github(token)


def get_repo(user: Github, repo: str):
    return user.get_repo(repo)


def parse_cook_title(comment_body, comment_url, create_time):
    title = comment_body.split("\r\n")[0]
    return f"- [{title}]({comment_url}) " + format_time(create_time)


def change_cook_readme(cook_comment_str):
    with open("README.md", "r+") as f:
        text = f.read()
        # regrex sub from github readme comments
        text = re.sub("(<!--START_SECTION:my_cook-->\n)(.*)(<!--END_SECTION:my_cook-->\n)", r"\1{}\n\3".format(cook_comment_str), text, flags=re.DOTALL)
        f.seek(0)
        f.write(text)
        f.truncate()


def main(github_token, repo_name):
    u = login(github_token)
    me = get_me(u)
    issues = u.get_repo(repo_name).get_issues(labels=COOK_LABEL_LIST)
    cook_comment_list = []
    for issue in issues:
        comments = issue.get_comments()
        for c in comments:
            if isMe(c, me):
                cook_comment_list.append(parse_cook_title(c.body, c.html_url, c.created_at))
    cook_comment_str = "\n".join(cook_comment_list)
    # replace readme cook
    change_cook_readme(cook_comment_str)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    options = parser.parse_args()
    main(options.github_token, options.repo_name)
