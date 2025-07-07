#!/usr/bin/env python3
"""
Fetch and save archived URLs from the Wayback CDX API for a domain,
with built-in retry on timeouts, smaller chunks, and guaranteed
output of all collected URLs even if an error occurs mid-fetch.
"""

import requests
import sys
import os
import time

# Configurable parameters
CHUNK_SIZE = 5000             # smaller batch size to avoid huge payloads
REQUEST_TIMEOUT = 120         # timeout for each API call (in seconds)
RETRY_DELAY = 5               # seconds to wait after a ReadTimeout

def harvest_unique_urls(domain):
    api = 'https://web.archive.org/cdx/search/cdx'
    resume_key = None
    unique_urls = set()
    headers = {'User-Agent': 'wayback-resume-harvester/1.0'}

    while True:
        params = {
            'url': f'{domain}/*',
            'output': 'json',
            'fl': 'original',
            'limit': CHUNK_SIZE,
            'showResumeKey': 'true',
            'collapse': 'original',
        }
        if resume_key:
            params['resumeKey'] = resume_key

        try:
            resp = requests.get(api, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ReadTimeout:
            print(f"ReadTimeout after {REQUEST_TIMEOUT}s for resumeKey={resume_key}, retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            continue
        except Exception as e:
            print(f"Error fetching CDX data: {e}, stopping harvest.")
            break

        # No data beyond header?
        if len(data) <= 1:
            break

        rows = data[1:]
        if [] in rows:
            sep = rows.index([])
            batch = rows[:sep]
            # next resumeKey row
            resume_key = rows[sep + 1][0] if sep + 1 < len(rows) else None
        else:
            batch = rows
            resume_key = None

        for r in batch:
            unique_urls.add(r[0])

        print(f"Fetched {len(batch)} records, total unique so far: {len(unique_urls)}, next resumeKey={resume_key}")
        if not resume_key:
            break

    return unique_urls

def main():
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = input("Enter domain (e.g. example.com): ").strip()
    if not domain:
        print("No domain entered, exiting.", file=sys.stderr)
        sys.exit(1)

    print(f"\nHarvesting unique archived URLs for {domain}…")
    urls = harvest_unique_urls(domain)

    # Write output even if errors occurred
    output_file = os.path.join(os.getcwd(), f"{domain}_urls.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        for u in sorted(urls):
            f.write(u + "\n")

    print(f"\nDone. {len(urls)} unique URLs saved to {output_file}")

if __name__ == "__main__":
    main()

