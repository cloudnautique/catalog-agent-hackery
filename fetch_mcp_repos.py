import httpx
import time
import asyncio

BASE_URL = "https://catalog-service-y1zj.onrender.com/api/repos"
LIMIT = 12  # Number of items per page
SEARCH_URL = "https://catalog-service-y1zj.onrender.com/api/search"


async def fetch_repos_page(limit=12, offset=0):
    """Fetch a single page of repos from the API asynchronously."""
    params = {"limit": limit, "offset": offset, "sort": "stars", "order": "desc"}
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params, timeout=4.5)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    return response.json()


async def get_repo_by_id(repo_id):
    """Fetch a single repo by its ID from the API asynchronously."""
    url = f"{BASE_URL}/{repo_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=4.5)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    return response.json()


async def search_repos(query: str):
    """Search for repositories using a query string asynchronously. Returns the API URL and results."""
    params = {"q": query}
    url = f"{SEARCH_URL}?q={query}"
    async with httpx.AsyncClient() as client:
        response = await client.get(SEARCH_URL, params=params, timeout=4.5)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return {"url": url, "results": []}
    return {"url": url, "results": response.json()}


async def fetch_all_repos(limit=12, max_pages=None) -> list[dict]:
    """Fetch all repositories asynchronously, paginating until no more results or max_pages reached."""
    offset = 0
    page_count = 0
    all_repos: list[dict] = []
    while True:
        page = await fetch_repos_page(limit=limit, offset=offset)
        if not page:
            break
        all_repos.extend(page)
        if len(page) < limit:
            break
        offset += limit
        page_count += 1
        if max_pages and page_count >= max_pages:
            break
        await asyncio.sleep(0.2)
    return all_repos


async def process_all_repos(limit=12, process_fn=None, max_pages=None):
    """Async loop through all pages, awaiting fetch_repos_page and calling process_fn for each list of repos."""
    import asyncio

    offset = 0
    page_count = 0
    while True:
        repos = await fetch_repos_page(limit=limit, offset=offset)
        if not repos:
            break
        if process_fn:
            # allow process_fn to be async or sync
            result = process_fn(repos)
            if asyncio.iscoroutine(result):
                await result
        if len(repos) < limit:
            break
        offset += limit
        page_count += 1
        if max_pages and page_count >= max_pages:
            break
        await asyncio.sleep(0.2)


def main():
    def print_sample(repos):
        for repo in repos[:288]:
            print(f"- {repo['fullName']} ({repo['stars']} stars)")

    asyncio.run(process_all_repos(limit=12, process_fn=print_sample, max_pages=24))


if __name__ == "__main__":
    main()
