import re
from collections import defaultdict

from .config import GITHUB_README_COMMENTS, MY_FOOD_STAT_HEAD, MY_FOOD_STAT_TEMPLATE


def isMe(issue, me):
    return issue.user.login == me


def format_time(time):
    return str(time)[:10]


def replace_readme_comments(file_name, comment_str, comments_name):
    with open(file_name, "r+") as f:
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


def to_add_spaces(longest_str_len, title):
    # 这是个全角的空格
    spaces = "　" * (longest_str_len + 1 - len(title))
    return spaces + "-->" + "　"


def parse_comment_title(comment_body, comment_url, create_time, longest_str_len):
    title = comment_body.splitlines()[0]
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
        + to_add_spaces(longest_str_len, title)
        + format_time(issue.created_at)
    )


def parse_cook_issue_table(me, issues):
    comments_str = MY_FOOD_STAT_HEAD
    food_dict = defaultdict(lambda: ["", "", 0])
    for issue in issues:
        comments = issue.get_comments()
        for c in comments:
            if not isMe(c, me):
                continue
            date_str = format_time(c.created_at)
            food_list_str = c.body.splitlines()[0]
            food_list = food_list_str.split(" ")
            for food in food_list:
                if food not in food_dict:
                    food_dict[food][0] = f"[{date_str}]({c.html_url})"
                    food_dict[food][1] = f"[{date_str}]({c.html_url})"
                else:
                    food_dict[food][1] = f"[{date_str}]({c.html_url})"
                food_dict[food][2] += 1
    for k, v in food_dict.items():
        comments_str += MY_FOOD_STAT_TEMPLATE.format(
            name=k, first_date=v[0], last_date=v[1], times=v[2]
        )
    return comments_str


def parse_base_issues_comments_str(me, issues):
    comment_list = []
    longest_str_len = 0
    for issue in issues:
        comments = issue.get_comments()
        for c in comments:
            str_len = len(c.body.splitlines()[0])
            # for format
            if str_len > longest_str_len:
                longest_str_len = str_len
            if isMe(c, me):
                comment_list.append(c)
    comment_list = [
        parse_comment_title(c.body, c.html_url, c.created_at, longest_str_len)
        for c in comment_list
    ]
    comment_str = "\n".join(comment_list)
    return comment_str


def parse_blog_issues_str(since, issues):
    comment_list = []
    longest_str_len = 0
    for issue in issues:
        if issue.created_at < since:
            continue
        str_len = len(issue.title)
        # for format
        if str_len > longest_str_len:
            longest_str_len = str_len
        comment_list.append(issue)
    comment_list = [parse_blog_title(c, longest_str_len) for c in comment_list]
    comment_str = "\n".join(comment_list)
    return comment_str
