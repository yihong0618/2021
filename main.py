# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
from collections import defaultdict

from github import Github

from daily.config import LABEL_DICT, MY_BLOG_REPO
from daily.utils import (
    replace_readme_comments,
    parse_blog_issues_str,
    parse_base_issues_comments_str,
    parse_cook_issue_table,
)


def get_me(user):
    return user.get_user().login


def login(token):
    return Github(token)


def main(github_token, repo_name, issue_number, issue_label_name):
    # issue_number for future use
    u = login(github_token)
    me = get_me(u)
    if issue_number:
        labels = LABEL_DICT.get(issue_label_name)
        if not labels:
            return
        issues = u.get_repo(repo_name).get_issues(labels=labels.get("label_list", []))
        parse_func = parse_base_issues_comments_str
        # only Cook now, if one more, refactor it
        if issue_label_name == "Cook":
            parse_func = parse_cook_issue_table
        comment_str = parse_func(me, issues)
        comments_name = labels.get("comment_name", "")
    else:
        # from 2021
        since = datetime(2021, 1, 1)
        issues = u.get_repo(MY_BLOG_REPO).get_issues(since=since, creator=me)
        comment_str = parse_blog_issues_str(since, issues)
        comments_name = "my_blog"
    replace_readme_comments("README.md", comment_str, comments_name)


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
