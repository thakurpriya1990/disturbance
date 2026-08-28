#!/usr/bin/env python
"""
Load test for /api/das_map_proposal.json to reproduce the memory blowup that
crashes pods when many users hit the map dashboard concurrently.

Usage:
    python scripts/loadtest_das_map.py --base-url http://localhost:8000 \\
        --username someone@example.com --password secret --concurrency 11

While this runs, watch server-side memory in another terminal, e.g.:
    tail -f logs/ledger.log | grep "Memory used by"
    docker stats <container>   # if running in a container with a memory limit
"""
import argparse
import concurrent.futures
import time

import requests

ENDPOINT = "/api/das_map_proposal.json"
LOGIN_PATH = "/ssologin/"


def login(base_url, username, password):
    session = requests.Session()
    resp = session.get(base_url + LOGIN_PATH)
    resp.raise_for_status()
    csrftoken = session.cookies.get("csrftoken")
    # Don't raise_for_status: Django redirects to LOGIN_REDIRECT_URL on success,
    # which may 404 in this app (e.g. /accounts/profile/) even though login worked.
    session.post(
        base_url + LOGIN_PATH,
        data={
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": csrftoken,
        },
        headers={"Referer": base_url + LOGIN_PATH},
    )
    if "sessionid" not in session.cookies:
        raise RuntimeError("Login failed, no sessionid cookie returned - check credentials")
    return session


def fetch(session, url, index):
    start = time.time()
    resp = session.get(url)
    elapsed = time.time() - start
    size_mb = len(resp.content) / (1024 * 1024)
    print(f"[{index:02d}] status={resp.status_code} time={elapsed:6.2f}s size={size_mb:8.2f}MB")
    return size_mb


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--username", required=True, help="Login as an internal/staff user to get a non-empty queryset")
    parser.add_argument("--password", required=True)
    parser.add_argument("--concurrency", type=int, default=11, help="Number of concurrent requests to fire at once")
    args = parser.parse_args()

    print(f"Logging in as {args.username} ...")
    session = login(args.base_url, args.username, args.password)

    url = args.base_url + ENDPOINT
    print(f"Firing {args.concurrency} concurrent requests at {url} ...")

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(fetch, session, url, i) for i in range(args.concurrency)]
        sizes = [f.result() for f in futures]
    total_elapsed = time.time() - start

    print()
    print(f"Done in {total_elapsed:.2f}s")
    print(f"Per-request payload: {sizes[0]:.2f}MB (approx, all responses are the same query)")
    print(f"Sum of payload sizes across concurrent requests: {sum(sizes):.2f}MB")
    print("Compare this against the memory limit of the pod/container to confirm the OOM risk.")


if __name__ == "__main__":
    main()
