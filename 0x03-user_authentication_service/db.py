#!/usr/bin/env python3
"""The DB module.
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """DB class.
    """

    def __init__(self) -> None:
        """Initialize a new DB instance.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """The memoized session object.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """This adds a new user to the database.
        """
        try:
            new_user = User(email=email, hashed_password=hashed_password)
            self._session.add(new_user)
            self._session.commit()
        except Exception:
            self._session.rollback()
            new_user = None
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """This finds a user based on a set of filters.
        """
        fields, values = [], []
        for key, value in kwargs.items():
            if hasattr(User, key):
                fields.append(getattr(User, key))
                values.append(value)
            else:
                raise InvalidRequestError()
        result = self._session.query(User).filter(
            tuple_(*fields).in_([tuple(values)])
        ).first()
        if result is None:
            raise NoResultFound()
        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        """updates user by ids and a given attribute"""
        user = self.find_user_by(id=user_id)
        if user is None:
            return
        updated_info = {}
        for key, value in kwargs.items():
            if hasattr(user, key):
                updated_info[getattr(user, key)] = value
            else:
                raise ValueError()
        self._session.commit()
