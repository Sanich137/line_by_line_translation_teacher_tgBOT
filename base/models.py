from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger, Boolean, sql, PrimaryKeyConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True, unique=True)
    is_bot = Column(Boolean)
    first_name = Column(String(50))
    username = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10))
    role = Column(String(10))  # собрать роли, например админ - "admin", "user"
    updated = Column(DateTime())
    purchases = relationship("Purchase", backref="users")


class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer(), unique=True)
    purchase_type = Column(String(100)) ## Напр, подписка, заказ на оценку и пр.
    purchase_date = Column(DateTime())
    payment_date = Column(DateTime())
    canceled_date = Column(DateTime())
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer(), unique=True, primary_key=True)
    author = Column(String(100))
    picture_url = Column(String(100))
    insert_date = Column(DateTime())
    is_hidden = Column(Boolean)
    original_language = Column(String(10))  # Оригинальный язык произведения
    # sentence = relationship("Sentences", backref="id")


class Sentence(Base):
    __tablename__ = 'sentences'
    author_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    sentence_id = Column(Integer(), unique=True)  # id предложения
    article_id = Column(String(100))  # id абзаца
    heading_id = Column(String(100))  # id заголовка (главы)
    sentence = Column(String(100))  # Непосредственно предложение
    language = Column(String(10))  # Язык текста строки

