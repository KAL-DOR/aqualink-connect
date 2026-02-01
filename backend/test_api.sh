#!/bin/bash

API_KEY="new1_58fb75c586d942d6bff07065d94b5129"

echo "Testing Twitter API - Water Complaints CDMX"
echo "============================================"

# More specific query for actual water supply issues
curl -s "https://api.twitterapi.io/twitter/tweet/advanced_search" \
  -G \
  --data-urlencode "query=(@SEGIAGUA OR @SACMEX_ OR @GobCDMX) (agua OR fuga OR corte) -is:retweet lang:es" \
  --data-urlencode "queryType=Latest" \
  -H "X-API-Key: $API_KEY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tweets = data.get('tweets', [])
    print(f'Found {len(tweets)} tweets')
    print()
    for i, t in enumerate(tweets[:15], 1):
        author = t.get('author', {})
        username = author.get('userName', '?')
        created = t.get('createdAt', '?')[:25]
        text = t.get('text', '').replace('\n', ' ')[:180]
        likes = t.get('likeCount', 0)
        rts = t.get('retweetCount', 0)
        print(f'[{i}] @{username} | Likes: {likes} | RTs: {rts}')
        print(f'    Date: {created}')
        print(f'    {text}')
        print()
    print(f'Has next page: {data.get(\"has_next_page\")}')
except Exception as e:
    print(f'Error: {e}')
"
