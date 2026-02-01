#!/usr/bin/env python3
"""Seed database with tweets from CSV"""

import csv
import random
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Create isolated Base for just Queja
Base = declarative_base()

# Import enum only
import enum

class TipoQueja(str, enum.Enum):
    SIN_AGUA = "sin_agua"
    FUGA = "fuga"
    AGUA_CONTAMINADA = "agua_contaminada"
    BAJA_PRESION = "baja_presion"
    OTRO = "otro"

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Enum
from sqlalchemy.sql import func

class Queja(Base):
    __tablename__ = "quejas"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String(50), unique=True, index=True)
    texto = Column(Text, nullable=False)
    tipo = Column(Enum(TipoQueja), default=TipoQueja.OTRO)
    username = Column(String(100))
    user_name = Column(String(200))
    user_followers = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    views = Column(Integer, default=0)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    alcaldia = Column(String(100), nullable=True)
    colonia = Column(String(200), nullable=True)
    tweet_url = Column(String(500))
    tweet_created_at = Column(DateTime)
    is_reply = Column(Boolean, default=False)
    in_reply_to = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# Database URL (use 'db' for Docker network, 'localhost:5433' for local)
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aquahub:aquahub_secret@db:5432/aquahub")

# Location extraction config
LOCATIONS = {
    'iztapalapa': {'lat': 19.3580, 'lng': -99.0930, 'alcaldia': 'Iztapalapa'},
    'tláhuac': {'lat': 19.2870, 'lng': -99.0040, 'alcaldia': 'Tláhuac'},
    'tlahuac': {'lat': 19.2870, 'lng': -99.0040, 'alcaldia': 'Tláhuac'},
    'xochimilco': {'lat': 19.2540, 'lng': -99.1027, 'alcaldia': 'Xochimilco'},
    'coyoacán': {'lat': 19.3500, 'lng': -99.1620, 'alcaldia': 'Coyoacán'},
    'coyoacan': {'lat': 19.3500, 'lng': -99.1620, 'alcaldia': 'Coyoacán'},
    'tlalpan': {'lat': 19.2965, 'lng': -99.1680, 'alcaldia': 'Tlalpan'},
    'álvaro obregón': {'lat': 19.3590, 'lng': -99.2260, 'alcaldia': 'Álvaro Obregón'},
    'alvaro obregon': {'lat': 19.3590, 'lng': -99.2260, 'alcaldia': 'Álvaro Obregón'},
    'cuajimalpa': {'lat': 19.3590, 'lng': -99.2910, 'alcaldia': 'Cuajimalpa'},
    'miguel hidalgo': {'lat': 19.4320, 'lng': -99.2030, 'alcaldia': 'Miguel Hidalgo'},
    'azcapotzalco': {'lat': 19.4870, 'lng': -99.1860, 'alcaldia': 'Azcapotzalco'},
    'gustavo a. madero': {'lat': 19.4820, 'lng': -99.1130, 'alcaldia': 'Gustavo A. Madero'},
    'gam': {'lat': 19.4820, 'lng': -99.1130, 'alcaldia': 'Gustavo A. Madero'},
    'cuauhtémoc': {'lat': 19.4285, 'lng': -99.1277, 'alcaldia': 'Cuauhtémoc'},
    'cuauhtemoc': {'lat': 19.4285, 'lng': -99.1277, 'alcaldia': 'Cuauhtémoc'},
    'venustiano carranza': {'lat': 19.4230, 'lng': -99.1070, 'alcaldia': 'Venustiano Carranza'},
    'iztacalco': {'lat': 19.3950, 'lng': -99.0970, 'alcaldia': 'Iztacalco'},
    'benito juárez': {'lat': 19.3984, 'lng': -99.1676, 'alcaldia': 'Benito Juárez'},
    'benito juarez': {'lat': 19.3984, 'lng': -99.1676, 'alcaldia': 'Benito Juárez'},
    'milpa alta': {'lat': 19.1920, 'lng': -99.0230, 'alcaldia': 'Milpa Alta'},
    'magdalena contreras': {'lat': 19.3220, 'lng': -99.2350, 'alcaldia': 'Magdalena Contreras'},
    # Colonias populares
    'del valle': {'lat': 19.3880, 'lng': -99.1710, 'alcaldia': 'Benito Juárez', 'colonia': 'Del Valle'},
    'roma': {'lat': 19.4180, 'lng': -99.1620, 'alcaldia': 'Cuauhtémoc', 'colonia': 'Roma'},
    'condesa': {'lat': 19.4120, 'lng': -99.1740, 'alcaldia': 'Cuauhtémoc', 'colonia': 'Condesa'},
    'polanco': {'lat': 19.4330, 'lng': -99.1960, 'alcaldia': 'Miguel Hidalgo', 'colonia': 'Polanco'},
    'narvarte': {'lat': 19.4010, 'lng': -99.1580, 'alcaldia': 'Benito Juárez', 'colonia': 'Narvarte'},
    'doctores': {'lat': 19.4150, 'lng': -99.1450, 'alcaldia': 'Cuauhtémoc', 'colonia': 'Doctores'},
    'tacubaya': {'lat': 19.4020, 'lng': -99.1930, 'alcaldia': 'Miguel Hidalgo', 'colonia': 'Tacubaya'},
    'mixcoac': {'lat': 19.3750, 'lng': -99.1850, 'alcaldia': 'Benito Juárez', 'colonia': 'Mixcoac'},
    'pedregal': {'lat': 19.3100, 'lng': -99.1950, 'alcaldia': 'Tlalpan', 'colonia': 'Pedregal'},
    'coapa': {'lat': 19.3020, 'lng': -99.1350, 'alcaldia': 'Tlalpan', 'colonia': 'Coapa'},
    'santa fe': {'lat': 19.3590, 'lng': -99.2750, 'alcaldia': 'Cuajimalpa', 'colonia': 'Santa Fe'},
    'tepito': {'lat': 19.4420, 'lng': -99.1280, 'alcaldia': 'Cuauhtémoc', 'colonia': 'Tepito'},
    'zacatenco': {'lat': 19.5040, 'lng': -99.1280, 'alcaldia': 'Gustavo A. Madero', 'colonia': 'Zacatenco'},
    'lindavista': {'lat': 19.4930, 'lng': -99.1320, 'alcaldia': 'Gustavo A. Madero', 'colonia': 'Lindavista'},
    'chapultepec': {'lat': 19.4200, 'lng': -99.1890, 'alcaldia': 'Miguel Hidalgo', 'colonia': 'Chapultepec'},
}

# Keywords for classification
TYPE_KEYWORDS = {
    TipoQueja.SIN_AGUA: [
        'sin agua', 'no hay agua', 'no tengo agua', 'no tenemos agua',
        'falta de agua', 'corte de agua', 'no llega agua', 'desabasto',
        'no cae agua', 'sin suministro', 'no sube el agua'
    ],
    TipoQueja.FUGA: [
        'fuga', 'fuga de agua', 'tubería rota', 'se rompió',
        'derrame', 'desperdicio', 'borbotón', 'agua corriendo'
    ],
    TipoQueja.AGUA_CONTAMINADA: [
        'agua sucia', 'contaminada', 'agua café', 'agua amarilla',
        'mal olor', 'turbia', 'no potable', 'contaminación'
    ],
    TipoQueja.BAJA_PRESION: [
        'baja presión', 'poca presión', 'sin presión', 'apenas sale',
        'gotea', 'sale poquita', 'presión baja', 'bajo suministro'
    ],
}


def extract_location(text: str) -> dict:
    """Extract location from tweet text"""
    text_lower = text.lower()

    for keyword, loc_data in LOCATIONS.items():
        if keyword in text_lower:
            # Add small random offset to avoid overlapping markers
            lat = loc_data['lat'] + random.uniform(-0.008, 0.008)
            lng = loc_data['lng'] + random.uniform(-0.008, 0.008)
            return {
                'latitud': lat,
                'longitud': lng,
                'alcaldia': loc_data['alcaldia'],
                'colonia': loc_data.get('colonia')
            }
    return {'latitud': None, 'longitud': None, 'alcaldia': None, 'colonia': None}


def classify_type(text: str) -> TipoQueja:
    """Classify complaint type from text"""
    text_lower = text.lower()

    scores = {}
    for tipo, keywords in TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[tipo] = score

    if scores:
        return max(scores, key=scores.get)

    # Default to SIN_AGUA if mentions SACMEX/SEGIAGUA
    if 'sacmex' in text_lower or 'segiagua' in text_lower:
        return TipoQueja.SIN_AGUA

    return TipoQueja.OTRO


def parse_twitter_date(date_str: str) -> datetime:
    """Parse Twitter date format"""
    try:
        # Format: "Sun Feb 01 02:35:16 +0000 2026"
        return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
    except:
        return datetime.now()


def seed_database(csv_file: str = "water_complaints_cdmx_all.csv"):
    """Seed database from CSV file"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Tables created/verified")

    Session = sessionmaker(bind=engine)
    session = Session()

    # Read CSV
    print(f"Reading {csv_file}...")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} tweets to import")

    # Stats
    imported = 0
    skipped = 0
    with_location = 0
    by_type = {}

    for row in rows:
        # Check if already exists
        existing = session.query(Queja).filter_by(tweet_id=row['tweet_id']).first()
        if existing:
            skipped += 1
            continue

        # Extract location
        location = extract_location(row['text'])

        # Classify type
        tipo = classify_type(row['text'])
        by_type[tipo.value] = by_type.get(tipo.value, 0) + 1

        # Create record
        queja = Queja(
            tweet_id=row['tweet_id'],
            texto=row['text'],
            tipo=tipo,
            username=row['username'],
            user_name=row['user_name'],
            user_followers=int(row['user_followers'] or 0),
            likes=int(row['likes'] or 0),
            retweets=int(row['retweets'] or 0),
            replies=int(row['replies'] or 0),
            views=int(row['views'] or 0),
            latitud=location['latitud'],
            longitud=location['longitud'],
            alcaldia=location['alcaldia'],
            colonia=location['colonia'],
            tweet_url=row['url'],
            tweet_created_at=parse_twitter_date(row['created_at']),
            is_reply=row['is_reply'].lower() == 'true',
            in_reply_to=row['in_reply_to'] or None
        )

        session.add(queja)
        imported += 1

        if location['latitud']:
            with_location += 1

        if imported % 100 == 0:
            print(f"  Imported {imported}...")
            session.commit()

    session.commit()
    session.close()

    print("\n" + "=" * 50)
    print("SEED COMPLETE")
    print("=" * 50)
    print(f"Total imported: {imported}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"With location: {with_location} ({100*with_location/max(imported,1):.1f}%)")
    print(f"\nBy type:")
    for tipo, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {tipo}: {count}")


if __name__ == "__main__":
    seed_database()
