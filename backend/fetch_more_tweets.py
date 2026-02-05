#!/usr/bin/env python3
"""Fetch 1000 MORE water complaint tweets (different from existing)"""

import csv
import json
import subprocess
import time

API_KEY = "new1_58fb75c586d942d6bff07065d94b5129"
QUERY = "(@SEGIAGUA OR @SACMEX_ OR @GobCDMX) (agua OR fuga OR corte OR sin agua) -is:retweet lang:es"
EXISTING_FILE = "water_complaints_cdmx.csv"
OUTPUT_FILE = "water_complaints_cdmx_batch2.csv"
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
    # Load existing tweet IDs
    existing_ids = set()
    try:
        with open(EXISTING_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row['tweet_id'])
        print(f"Loaded {len(existing_ids)} existing tweet IDs to skip")
    except:
        print("No existing file found, starting fresh")

    all_tweets = []
    cursor = ""
    page = 0
    skipped = 0

    print(f"\nFetching {TARGET_TWEETS} NEW tweets...")
    print(f"Query: {QUERY}")
    print("-" * 60)

    while len(all_tweets) < TARGET_TWEETS:
        page += 1
        print(f"Page {page}: fetching... (new: {len(all_tweets)}, skipped: {skipped})")

        try:
            data = fetch_page(cursor)
            tweets = data.get("tweets", [])

            if not tweets:
                print("No more tweets found")
                break

            # Filter out existing tweets
            for t in tweets:
                if t.get("id") not in existing_ids:
                    all_tweets.append(t)
                else:
                    skipped += 1

            has_next = data.get("has_next_page", False)
            cursor = data.get("next_cursor", "")

            if not has_next or not cursor:
                print("Reached end of results")
                break

            time.sleep(0.3)

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"\nTotal NEW tweets fetched: {len(all_tweets)}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"Saving to {OUTPUT_FILE}...")

    # Write to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "tweet_id", "created_at", "username", "user_name", "user_followers",
            "text", "likes", "retweets", "replies", "views", "url", "is_reply", "in_reply_to"
        ])

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

    print(f"Done! Saved {len(all_tweets)} NEW tweets to {OUTPUT_FILE}")

    # Also create combined file
    combined_file = "water_complaints_cdmx_all.csv"
    print(f"\nCreating combined file: {combined_file}")

    with open(combined_file, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow([
            "tweet_id", "created_at", "username", "user_name", "user_followers",
            "text", "likes", "retweets", "replies", "views", "url", "is_reply", "in_reply_to"
        ])

        # Copy existing
        with open(EXISTING_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                writer.writerow([row[k] for k in reader.fieldnames])

        # Add new
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

    print(f"Combined file has {len(existing_ids) + len(all_tweets)} total tweets")

if __name__ == "__main__":
    main()
