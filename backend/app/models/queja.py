from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class TipoQueja(str, enum.Enum):
    SIN_AGUA = "sin_agua"
    FUGA = "fuga"
    AGUA_CONTAMINADA = "agua_contaminada"
    BAJA_PRESION = "baja_presion"
    OTRO = "otro"


class Queja(Base):
    __tablename__ = "quejas"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String(50), unique=True, index=True)

    # Tweet content
    texto = Column(Text, nullable=False)
    tipo = Column(Enum(TipoQueja), default=TipoQueja.OTRO)

    # Author info
    username = Column(String(100))
    user_name = Column(String(200))
    user_followers = Column(Integer, default=0)

    # Engagement
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    views = Column(Integer, default=0)

    # Location (extracted from text)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    alcaldia = Column(String(100), nullable=True)
    colonia = Column(String(200), nullable=True)

    # Metadata
    tweet_url = Column(String(500))
    tweet_created_at = Column(DateTime)
    is_reply = Column(Boolean, default=False)
    in_reply_to = Column(String(100), nullable=True)

    # System timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
