COOK_LABEL_LIST = [
    "Cook",
]
MOVIE_LABEL_LIST = [
    "Movie",
]
READ_LABEL_LIST = [
    "Read",
]
DRAMA_LABEL_LIST = [
    "Drama",
]
PUSHUP_LABEL_LIST = [
    "PushUps",
]
BANGUMI_LABEL_LIST = [
    "Bangumi",
]
GAME_LABEL_LIST = [
    "Game",
]
MONEY_LABEL_LIST = [
    "Money",
]
MEDITATION_LABEL_LIST = [
    "Meditation",
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
    "Drama": {"label_list": DRAMA_LABEL_LIST, "comment_name": "my_drama"},
    "Bangumi": {"label_list": BANGUMI_LABEL_LIST, "comment_name": "my_bangumi"},
    "Game": {"label_list": GAME_LABEL_LIST, "comment_name": "my_game"},
}

##### COMMENTS DAILY ######
LABEL_DAILY_DICT = {
    # label, map_func, reduce_func
    "俯卧撑": [PUSHUP_LABEL_LIST, int, sum],
    "花费": [MONEY_LABEL_LIST, float, sum],
    "冥想": [MEDITATION_LABEL_LIST, int, sum],
}

##### SHANBAY ######
MY_SHANBAY_USER_NAME = "ufewz"
SHANBAY_CALENDAR_API = "https://apiv3.shanbay.com/uc/checkin/calendar/dates/?user_id={user_name}&start_date={start_date}&end_date={end_date}"
MY_SHANBAY_URL = f"https://web.shanbay.com/web/users/{MY_SHANBAY_USER_NAME}/zone"

##### DUO ######
MY_DUOLINGO_URL = "https://www.duolingo.com/profile/yihong0618"

##### FOOD ######
MY_FOOD_STAT_HEAD = (
    "| Name | First_date | Last_date | Times | \n | ---- | ---- | ---- | ---- |\n"
)
MY_FOOD_STAT_TEMPLATE = "| {name} | {first_date} | {last_date} | {times} |\n"
