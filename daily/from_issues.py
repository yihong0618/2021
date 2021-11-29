from collections import defaultdict

import pendulum
from .utils import isMe


def get_info_from_issue_comments(me, issues, map_func, reduce_func=sum):
    """
    also return url for formation
    """
    calendar_list = []
    data_list = []
    url = ""
    month_summary_dict = defaultdict(int)
    data = None
    for issue in issues:
        if not url:
            url = issue.html_url
        comments = issue.get_comments()
        for c in comments:
            if not isMe(c, me):
                continue
            try:
                data = map_func(c)
                data_list.append(data)
            except:
                # becaue the format maybe wrong just pass
                continue
            calendar_list.append(c.created_at)
            month = pendulum.instance(c.created_at).in_timezone("Asia/Shanghai").month
            if map_func == len:
                month_summary_dict[month] += 1
            else:
                month_summary_dict[month] += data
    end_date = pendulum.now("Asia/Shanghai")
    calendar_str_list = [
        pendulum.instance(i).in_timezone("Asia/Shanghai").to_date_string()
        for i in calendar_list
    ]
    is_today_check = False
    streak = 0
    if end_date.to_date_string() in calendar_str_list:
        is_today_check = True
        streak += 1
        calendar_str_list.pop()
        calendar_list.pop()
    if not calendar_list:
        return data, streak, is_today_check, url
    # fuck pendulum's period
    periods = list(
        pendulum.period(
            pendulum.instance(calendar_list[0]).in_timezone("Asia/Shanghai"), end_date
        )
    )
    periods = [p.to_date_string() for p in periods]
    # fix pendulum's period bug I don't know why ???? the period are different
    if end_date.to_date_string() in periods:
        periods.pop()
    for p in periods[::-1]:
        if p not in calendar_str_list:
            break
        streak += 1
    # format to int
    data = int(reduce_func(data_list))
    return data, streak, is_today_check, url, month_summary_dict
