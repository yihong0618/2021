# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
import re

from github import Github


COOK_LABEL_LIST = [
    "Cook",
]
MOVIE_LABEL_LIST = [
    "Movie",
]
MY_BLOG_REPO = "yihong0618/gitblog"
GITHUB_README_COMMENTS = (
    "(<!--START_SECTION:{name}-->\n)(.*)(<!--END_SECTION:{name}-->\n)"
)

LABEL_DICT = {
    "Cook": {"label_list": COOK_LABEL_LIST, "comment_name": "my_cook"},
    "Movie": {"label_list": MOVIE_LABEL_LIST, "comment_name": "my_movie"}
}


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


def parse_blog_title(issue):
    time = format_time(issue.created_at)
    return f"- [{issue.title}]({issue.html_url})--{time}"


def replace_readme_comments(comment_str, comments_name):
    with open("README.md", "r+") as f:
        text = f.read()
        # regrex sub from github readme comments
        text = re.sub(
            GITHUB_README_COMMENTS.format(name=comments_name),
            r"\1{}\n\3".format(comment_str),
            text,
            flags=re.DOTALL,
        )
        f.seek(0)
        f.write(text)
        f.truncate()


def main(github_token, repo_name, issue_number, issue_label_name):
    # issue_number for future use
    u = login(github_token)
    me = get_me(u)
    comment_list = []
    if issue_number:
        labels = LABEL_DICT.get(issue_label_name)
        if not labels:
            return
        issues = u.get_repo(repo_name).get_issues(labels=labels.get("label_list", []))
        for issue in issues:
            comments = issue.get_comments()
            for c in comments:
                if isMe(c, me):
                    comment_list.append(
                        parse_cook_title(c.body, c.html_url, c.created_at)
                    )
        comments_name = labels.get("comment_name", "")
    else:
        since = datetime(2021, 1, 1)
        issues = u.get_repo(MY_BLOG_REPO).get_issues(since=since, creator=me)
        comment_list = []
        for issue in issues:
            if issue.created_at < since:
                continue
            comment_list.append(parse_blog_title(issue))
        comments_name = "my_blog"

    comment_str = "\n".join(comment_list)
    replace_readme_comments(comment_str, comments_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument(
        "--issue_number", help="issue_number", default=None, required=False
    )
    parser.add_argument(
        "--issue_label_name", help="issue_label_name", default=None, required=False
    )
    options = parser.parse_args()
    main(options.github_token, options.repo_name, options.issue_number, options.issue_label_name)
