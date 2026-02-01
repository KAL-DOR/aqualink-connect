#!/usr/bin/env python3
"""Fetch 1000 water complaint tweets and save to CSV"""

import csv
import json
import subprocess
import time

API_KEY = "new1_58fb75c586d942d6bff07065d94b5129"
QUERY = "(@SEGIAGUA OR @SACMEX_ OR @GobCDMX) (agua OR fuga OR corte OR sin agua) -is:retweet lang:es"
OUTPUT_FILE = "water_complaints_cdmx.csv"
TARGET_TWEETS = 1000

def fetch_page(cursor=""):
    """Fetch a single page of tweets"""
    cmd = [
        "curl", "-s",
        "https://api.twitterapi.io/twitter/tweet/advanced_search",
        "-G",
        "--data-urlencode", f"query={QUERY}",
        "--data-urlencode", "queryType=Latest",
        "--data-urlencode", f"cursor={cursor}",
        "-H", f"X-API-Key: {API_KEY}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def main():
    all_tweets = []
    cursor = ""
    page = 0

    print(f"Fetching {TARGET_TWEETS} tweets...")
    print(f"Query: {QUERY}")
    print("-" * 60)

    while len(all_tweets) < TARGET_TWEETS:
        page += 1
        print(f"Page {page}: fetching... (total so far: {len(all_tweets)})")

        try:
            data = fetch_page(cursor)
            tweets = data.get("tweets", [])

            if not tweets:
                print("No more tweets found")
                break

            all_tweets.extend(tweets)

            has_next = data.get("has_next_page", False)
            cursor = data.get("next_cursor", "")

            if not has_next or not cursor:
                print("Reached end of results")
                break

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"\nTotal tweets fetched: {len(all_tweets)}")
    print(f"Saving to {OUTPUT_FILE}...")

    # Write to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "tweet_id",
            "created_at",
            "username",
            "user_name",
            "user_followers",
            "text",
            "likes",
            "retweets",
            "replies",
            "views",
            "url",
            "is_reply",
            "in_reply_to"
        ])

        # Data
        for t in all_tweets:
            author = t.get("author", {})
            writer.writerow([
                t.get("id", ""),
                t.get("createdAt", ""),
                author.get("userName", ""),
                author.get("name", ""),
                author.get("followers", 0),
                t.get("text", "").replace("\n", " "),
                t.get("likeCount", 0),
                t.get("retweetCount", 0),
                t.get("replyCount", 0),
                t.get("viewCount", 0),
                t.get("url", ""),
                t.get("isReply", False),
                t.get("inReplyToUsername", "")
            ])

    print(f"Done! Saved {len(all_tweets)} tweets to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
