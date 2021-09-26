import argparse
import pendulum
from main import login

YEAR = pendulum.now().year

# Bookmark issue id
BOOKMARK_ISSUE_NUMBER = 21

BOOKMARK_FILE_NAME = f"bookmark_{YEAR}.md"

BOOKMARK_FILE_HEAD = f"# 我的 [{YEAR}](https://github.com/yihong0618/2021/issues/21) 的书签\n\n"
BOOKMARK_STAT_HEAD = (
    "| Name | Link | Add | Update | Has_file | \n | ---- | ---- | ---- | ---- | ---- |\n"
)
BOOKMARK_STAT_TEMPLATE = "| {name} | {link} | {add} | {update} | {has_file} |\n"

def make_bookmark_str(name, link, add, update, has_file):
    # format
    return BOOKMARK_STAT_TEMPLATE.format(
        name=name,
        link=link,
        add=add,
        update=update,
        has_file=has_file,
    )


def main(github_token, repo_name):
    u = login(github_token)
    repo = u.get_repo(repo_name)
    bookmark_issue = repo.get_issue(BOOKMARK_ISSUE_NUMBER)
    comments = bookmark_issue.get_comments()


    bookmark_str = BOOKMARK_STAT_HEAD    
    for c in comments:
        has_file = False
        comment_str_list = c.body.splitlines()
        # drop the empty line
        comment_str_list = [c for c in comment_str_list if c]
        if len(comment_str_list) < 2:
            continue
        name, link = comment_str_list[0], comment_str_list[1]
        if link.find(f"{repo_name}/{YEAR}/files") != -1:
            has_file = True
        bookmark_str += make_bookmark_str(f"[name](link)", c.html_url, str(c.created_at)[:10], str(c.updated_at)[:10], has_file)
    with open(BOOKMARK_FILE_NAME, "w+") as f:
        f.write(BOOKMARK_FILE_HEAD)
        f.write(bookmark_str)
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    options = parser.parse_args()
    main(options.github_token, options.repo_name)