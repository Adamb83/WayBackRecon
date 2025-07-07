WayBackRecon
Export all historical URLs from the Wayback Machine from a single entity

Automates a purely passive OSINT step in your pentest/bug-bounty workflow:
 1. It queries the Internet Archive’s Wayback Machine for every snapshot of the target domain.
 2. Pipes those archive entries through waybackurls to extract raw URLs.
 3. Deduplicates and filters them down to the target host, outputting a clean list you can feed
 into your live-URL checker (httpx), directory brute-forcers, parameter fuzzers, etc.
