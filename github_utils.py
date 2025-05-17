# github_utils.py - Contains functions for searching GitHub MCP repos
from github import Github

def search_github_repos_with_pagination(token, query, max_items=20):
    g = Github(token)
    result = g.search_repositories(query=query, sort="stars", order="desc")
    count = 0
    for repo in result:
        yield repo
        count += 1
        if count >= max_items:
            break
