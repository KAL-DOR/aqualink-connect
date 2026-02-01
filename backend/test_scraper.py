#!/usr/bin/env python3
"""Dry run test for Twitter scraper"""

import asyncio
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

from app.services.twitter_scraper import TwitterScraper

async def main():
    api_key = os.getenv("TWITTER_API_KEY")
    if not api_key:
        print("ERROR: TWITTER_API_KEY not set in .env")
        return

    print(f"Using API key: {api_key[:10]}...")

    scraper = TwitterScraper(api_key)

    # Test query
    query = '(SACMEX OR SEGIAGUA OR "no tengo agua" OR "sin agua" OR "No responde SACMEX" OR "gobierno cdmx" agua) -is:retweet lang:es'

    print(f"\nSearching with query:\n{query}\n")
    print("-" * 60)

    try:
        complaints, next_cursor, has_next = await scraper.search_complaints(
            query=query,
            query_type="Latest",
            max_pages=1  # Just 1 page for testing
        )

        print(f"\nFound {len(complaints)} complaints\n")
        print("=" * 60)

        for i, c in enumerate(complaints[:10], 1):  # Show first 10
            print(f"\n[{i}] @{c.author_username} - {c.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"    Type: {c.complaint_type}")
            if c.location:
                print(f"    Location: {c.location.place_name} ({c.location.lat}, {c.location.lng})")
            print(f"    Text: {c.text[:150]}...")
            print(f"    URL: {c.url}")
            print(f"    Likes: {c.likes} | RT: {c.retweets}")

        print("\n" + "=" * 60)
        print(f"Has more pages: {has_next}")
        if next_cursor:
            print(f"Next cursor: {next_cursor[:50]}...")

        # Stats
        print("\n--- Stats ---")
        by_type = {}
        by_location = {}
        for c in complaints:
            by_type[c.complaint_type] = by_type.get(c.complaint_type, 0) + 1
            if c.location and c.location.place_name:
                by_location[c.location.place_name] = by_location.get(c.location.place_name, 0) + 1

        print(f"By type: {by_type}")
        print(f"By location: {by_location}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
