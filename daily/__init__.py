from .shanbay import get_shanbay_daily
from .duolingo import get_duolingo_daily
from .config import MY_SHANBAY_URL, MY_DUOLINGO_URL
from .from_issues import get_info_from_issue_comments


MY_STATUS_DICT_FROM_API = {
    # TODO url
    "扇贝": {"daily_func": get_shanbay_daily, "url": MY_SHANBAY_URL, "unit_str": " (天)"},
    "多邻国": {
        "daily_func": get_duolingo_daily,
        "url": MY_DUOLINGO_URL,
        "unit_str": " (点)",
    },
}

MY_STATUS_DICT_FROM_COMMENTS = {
    "俯卧撑": {"daily_func": get_info_from_issue_comments, "unit_str": " (个)"},
    "花费": {"daily_func": get_info_from_issue_comments, "unit_str": " (元)"},
    "冥想": {"daily_func": get_info_from_issue_comments, "unit_str": " (分钟)"},
}
