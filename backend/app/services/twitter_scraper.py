import httpx
import re
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class TweetLocation(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_name: Optional[str] = None


class WaterComplaint(BaseModel):
    tweet_id: str
    text: str
    author_username: str
    author_name: str
    created_at: datetime
    complaint_type: str  # no_water, leak, contamination, low_pressure
    location: Optional[TweetLocation] = None
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    url: str


class TwitterScraper:
    BASE_URL = "https://api.twitterapi.io"

    # Keywords to classify complaint types
    COMPLAINT_KEYWORDS = {
        'no_water': [
            'no tengo agua', 'sin agua', 'no hay agua', 'no llega agua',
            'falta de agua', 'corte de agua', 'no tenemos agua', 'llevamos días sin agua',
            'semanas sin agua', 'desabasto'
        ],
        'leak': [
            'fuga', 'fuga de agua', 'tubería rota', 'se rompió la tubería',
            'derrame', 'desperdicio de agua', 'borbotón'
        ],
        'contamination': [
            'agua sucia', 'agua contaminada', 'agua café', 'agua amarilla',
            'mal olor', 'agua turbia', 'agua con olor', 'no potable'
        ],
        'low_pressure': [
            'baja presión', 'poca presión', 'no sube el agua', 'apenas sale',
            'gotea', 'sale poquita', 'presión baja'
        ]
    }

    # CDMX colonias/alcaldías for location extraction
    CDMX_LOCATIONS = [
        'iztapalapa', 'tláhuac', 'xochimilco', 'coyoacán', 'benito juárez',
        'tlalpan', 'álvaro obregón', 'magdalena contreras', 'cuajimalpa',
        'miguel hidalgo', 'azcapotzalco', 'gustavo a. madero', 'cuauhtémoc',
        'venustiano carranza', 'iztacalco', 'milpa alta', 'santa fe',
        'del valle', 'roma', 'condesa', 'polanco', 'tepito', 'doctores',
        'santa maría la ribera', 'san rafael', 'juárez', 'anzures',
        'narvarte', 'portales', 'escandón', 'tacubaya', 'mixcoac'
    ]

    # Approximate coordinates for CDMX areas
    LOCATION_COORDS = {
        'iztapalapa': (19.3580, -99.0930),
        'tláhuac': (19.2870, -99.0040),
        'xochimilco': (19.2540, -99.1027),
        'coyoacán': (19.3500, -99.1620),
        'benito juárez': (19.3984, -99.1676),
        'tlalpan': (19.2965, -99.1680),
        'álvaro obregón': (19.3590, -99.2260),
        'cuauhtémoc': (19.4285, -99.1277),
        'gustavo a. madero': (19.4820, -99.1130),
        'azcapotzalco': (19.4870, -99.1860),
        'miguel hidalgo': (19.4320, -99.2030),
        'venustiano carranza': (19.4230, -99.1070),
        'iztacalco': (19.3950, -99.0970),
        'del valle': (19.3880, -99.1710),
        'roma': (19.4180, -99.1620),
        'condesa': (19.4120, -99.1740),
        'polanco': (19.4330, -99.1960),
        'doctores': (19.4150, -99.1450),
        'narvarte': (19.4010, -99.1580),
        'tacubaya': (19.4020, -99.1930),
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"X-API-Key": api_key},
            timeout=30.0
        )

    async def search_complaints(
        self,
        query: Optional[str] = None,
        query_type: str = "Latest",
        cursor: str = "",
        max_pages: int = 5
    ) -> tuple[List[WaterComplaint], str, bool]:
        """
        Search for water-related complaints on Twitter/X.

        Returns: (complaints, next_cursor, has_next_page)
        """
        if query is None:
            # Default query for water complaints in CDMX - targets actual complaints to authorities
            query = (
                '(@SEGIAGUA OR @SACMEX_ OR @GobCDMX) (agua OR fuga OR corte OR "sin agua") '
                '-is:retweet lang:es'
            )

        complaints = []
        current_cursor = cursor
        pages_fetched = 0
        has_next = True

        while pages_fetched < max_pages and has_next:
            try:
                response = await self.client.get(
                    "/twitter/tweet/advanced_search",
                    params={
                        "query": query,
                        "queryType": query_type,
                        "cursor": current_cursor
                    }
                )
                response.raise_for_status()
                data = response.json()

                tweets = data.get("tweets", [])
                has_next = data.get("has_next_page", False)
                current_cursor = data.get("next_cursor", "")

                for tweet in tweets:
                    complaint = self._parse_tweet(tweet)
                    if complaint:
                        complaints.append(complaint)

                pages_fetched += 1

            except httpx.HTTPError as e:
                print(f"Error fetching tweets: {e}")
                break

        return complaints, current_cursor, has_next

    def _parse_tweet(self, tweet: dict) -> Optional[WaterComplaint]:
        """Parse a tweet into a WaterComplaint object."""
        try:
            text = tweet.get("text", "")

            # Classify the complaint type
            complaint_type = self._classify_complaint(text)
            if not complaint_type:
                return None  # Not a valid water complaint

            # Extract location from tweet
            location = self._extract_location(tweet)

            # Get author info
            author = tweet.get("author", {})

            created_at_str = tweet.get("createdAt", "")
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            except:
                created_at = datetime.now()

            return WaterComplaint(
                tweet_id=tweet.get("id", ""),
                text=text,
                author_username=author.get("userName", "unknown"),
                author_name=author.get("name", "Unknown"),
                created_at=created_at,
                complaint_type=complaint_type,
                location=location,
                likes=tweet.get("likeCount", 0),
                retweets=tweet.get("retweetCount", 0),
                replies=tweet.get("replyCount", 0),
                url=f"https://twitter.com/{author.get('userName', 'i')}/status/{tweet.get('id', '')}"
            )
        except Exception as e:
            print(f"Error parsing tweet: {e}")
            return None

    def _classify_complaint(self, text: str) -> Optional[str]:
        """Classify the type of water complaint based on keywords."""
        text_lower = text.lower()

        # Check each complaint type
        scores = {}
        for complaint_type, keywords in self.COMPLAINT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[complaint_type] = score

        if not scores:
            # Default to no_water if it mentions SACMEX/SEGIAGUA but no specific type
            if 'sacmex' in text_lower or 'segiagua' in text_lower:
                return 'no_water'
            return None

        # Return the type with highest score
        return max(scores, key=scores.get)

    def _extract_location(self, tweet: dict) -> Optional[TweetLocation]:
        """Extract location from tweet text or metadata."""
        # First check if tweet has geo data
        place = tweet.get("place")
        if place:
            coords = place.get("coordinates")
            if coords:
                return TweetLocation(
                    lat=coords.get("lat"),
                    lng=coords.get("lng"),
                    place_name=place.get("fullName")
                )

        # Try to extract location from text
        text_lower = tweet.get("text", "").lower()

        for location in self.CDMX_LOCATIONS:
            if location in text_lower:
                coords = self.LOCATION_COORDS.get(location)
                if coords:
                    # Add some randomness to avoid overlapping markers
                    import random
                    lat_offset = random.uniform(-0.01, 0.01)
                    lng_offset = random.uniform(-0.01, 0.01)
                    return TweetLocation(
                        lat=coords[0] + lat_offset,
                        lng=coords[1] + lng_offset,
                        place_name=location.title()
                    )

        return None

    async def close(self):
        await self.client.aclose()
