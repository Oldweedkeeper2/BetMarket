import asyncio

import sqlalchemy.types
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Enum, BigInteger, Numeric
from datetime import datetime

from data.config import ALCHEMY_DATABASE_URL

Base = declarative_base()