import re
from collections import defaultdict
from datetime import datetime

from .config import (
    BASE_ISSUE_STAT_HEAD,
    BASE_ISSUE_STAT_TEMPLATE,
    BLOG_ISSUE_STAT_HEAD,
    BLOG_ISSUE_STAT_TEMPLATE,
    FOOD_ISSUE_STAT_HEAD,
    FOOD_ISSUE_STAT_TEMPLATE,
    GITHUB_README_COMMENTS,
    GTD_LABEL_LIST,
    MEDITATION_LABEL_LIST,
    WEEKLY_LABEL_LIST,
    MORNING_LABEL_LIST,
    PUSHUP_LABEL_LIST,
)


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


def make_cook_issue_table(me, issues):
    comments_str = FOOD_ISSUE_STAT_HEAD
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
        comments_str += FOOD_ISSUE_STAT_TEMPLATE.format(
            name=k, first_date=v[0], last_date=v[1], times=v[2]
        )
    return comments_str


def make_base_issues_comments_str(me, issues):
    comments_str = BASE_ISSUE_STAT_HEAD
    for issue in issues:
        comments = issue.get_comments()
        for c in comments:
            is_me = isMe(c, me)
            # for format
            if is_me:
                name = c.body.splitlines()[0]
                comments_str += BASE_ISSUE_STAT_TEMPLATE.format(
                    name=f"[{name}]({c.html_url})",
                    start=format_time(c.created_at),
                    update=format_time(c.updated_at),
                )
    return comments_str


def make_blog_issues_str(since, issues):
    """
    only get this year post
    """
    comment_str = BLOG_ISSUE_STAT_HEAD
    for issue in issues:
        if issue.created_at < since:
            continue
        comments = issue.get_comments()
        comments_count = len(list(comments))
        # min datetime
        year = datetime.now().year
        comments_update = (
            max([i.updated_at for i in comments])
            if comments_count
            else datetime(year, 1, 1)
        )
        create = format_time(issue.created_at)
        # the latest update no matter comment or post min data(2021?)
        update = (
            format_time(issue.updated_at)
            if comments_update < issue.updated_at
            else format_time(comments_update)
        )
        comment_str += BLOG_ISSUE_STAT_TEMPLATE.format(
            name=f"[{issue.title}]({issue.html_url})",
            start=create,
            update=update,
            comments=comments_count,
        )
    return comment_str


def comment_to_int(comment):
    """
    comment -> int from first line
    """
    data = comment.body.splitlines()[0]
    try:
        return int(data)
    except:
        return 0


def comment_to_float(comment):
    """
    comment -> float from first line
    """
    data = comment.body.splitlines()[0]
    try:
        return float(data)
    except:
        return float(0)


def commnet_to_count(comment):
    """
    comment -> just count it just return a number 1
    my code I am the God
    """
    return 1


def comment_to_GTD_count(comment):
    """
    start - [x] means task done in md
    """
    data = comment.body.splitlines()
    count = 0
    for d in data:
        if d.startswith("- [x]"):
            count += 1
    return count


##### COMMENTS DAILY ######
LABEL_DAILY_DICT = {
    # label, map_func, reduce_func
    "俯卧撑": [PUSHUP_LABEL_LIST, comment_to_int, sum],
    "冥想": [MEDITATION_LABEL_LIST, comment_to_int, sum],
    "早起": [MORNING_LABEL_LIST, commnet_to_count, len],  # Do Nothing
    "GTD": [GTD_LABEL_LIST, comment_to_GTD_count, sum],  # Do Nothing
    "周记": [WEEKLY_LABEL_LIST, commnet_to_count, len],  # Do Nothing
}
