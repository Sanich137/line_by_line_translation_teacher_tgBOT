from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

import config
import datetime
from base.models import User, Base

database = 'sqlite:///base/sqlite3.db'
ADMIN = 358708312
default_admin = User(
    id=358708312,
    is_bot=False,
    first_name='Александр',
    username=None,
    last_name='Кожевников',
    language_code='en',
    role='admin',
    # updated=datetime.datetime.now
    )
