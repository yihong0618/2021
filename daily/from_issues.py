import pendulum


def get_info_from_issue_comments(u, repo_name, labels, map_func, reduce_func=sum):
    """
    also return url for formation
    """
    issues = u.get_repo(repo_name).get_issues(labels=labels)
    calendar_list = []
    data_list = []
    url = ""
    for issue in issues:
        if not url:
            url = issue.html_url
        comments = issue.get_comments()
        for c in comments:
            number_str = c.body.splitlines()[0]
            try:
                data = map_func(number_str)
                data_list.append(data)
            except:
                continue
            calendar_list.append(c.created_at)
    end_date = pendulum.now("Asia/Shanghai")
    calendar_str_list = [
        pendulum.instance(i, "Asia/Shanghai").to_date_string() for i in calendar_list
    ]
    is_today_check = False
    streak = 0
    if end_date.to_date_string() in calendar_str_list:
        is_today_check = True
        streak += 1
        calendar_str_list.pop()
    periods = list(
        pendulum.period(
            pendulum.instance(calendar_list[0], "Asia/Shanghai"),
            pendulum.instance(calendar_list[-1], "Asia/Shanghai"),
        )
    )
    for p in periods[::-1]:
        if p.to_date_string() not in calendar_str_list:
            break
        streak += 1
    # format to int
    data = int(reduce_func(data_list))
    return data, streak, is_today_check, url
