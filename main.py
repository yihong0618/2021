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
READ_LABEL_LIST = [
    "Read",
]
MY_BLOG_REPO = "yihong0618/gitblog"
GITHUB_README_COMMENTS = (
    "(<!--START_SECTION:{name}-->\n)(.*)(<!--END_SECTION:{name}-->\n)"
)

# add new label here
LABEL_DICT = {
    "Cook": {"label_list": COOK_LABEL_LIST, "comment_name": "my_cook"},
    "Movie": {"label_list": MOVIE_LABEL_LIST, "comment_name": "my_movie"},
    "Read": {"label_list": READ_LABEL_LIST, "comment_name": "my_read"},
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


def to_add_spaces(longest_str_len, title):
    spaces = " " * (longest_str_len + 1 - len(title))
    return spaces + "-->" + "  "


def parse_comment_title(comment_body, comment_url, create_time, longest_str_len):
    title = comment_body.split("\r\n")[0]
    # format markdown with same length
    return (
        f"- [{title}]({comment_url})"
        + to_add_spaces(longest_str_len, title)
        + format_time(create_time)
    )


def parse_blog_title(issue, longest_str_len):
    title = issue.title
    return (
        f"- [{title}]({issue.html_url})"
        + to_add_spaces(title, longest_str_len)
        + format_time(issue.created_at)
    )


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
    longest_str_len = 0
    if issue_number:
        labels = LABEL_DICT.get(issue_label_name)
        if not labels:
            return
        issues = u.get_repo(repo_name).get_issues(labels=labels.get("label_list", []))
        for issue in issues:
            comments = issue.get_comments()
            for c in comments:
                str_len = len(c.body.split("\r\n")[0])
                # for format
                if str_len > longest_str_len:
                    longest_str_len = str_len
                if isMe(c, me):
                    comment_list.append(c)
        comment_list = [
            parse_comment_title(c.body, c.html_url, c.created_at, longest_str_len)
            for c in comment_list
        ]
        comments_name = labels.get("comment_name", "")
    else:
        since = datetime(2021, 1, 1)
        issues = u.get_repo(MY_BLOG_REPO).get_issues(since=since, creator=me)
        comment_list = []
        for issue in issues:
            if issue.created_at < since:
                continue
            str_len = len(issue.title)
            # for format
            if str_len > longest_str_len:
                longest_str_len = str_len
            comment_list.append(issue)
        comment_list = [parse_blog_title(c, longest_str_len) for c in comment_list]
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
    main(
        options.github_token,
        options.repo_name,
        options.issue_number,
        options.issue_label_name,
    )
