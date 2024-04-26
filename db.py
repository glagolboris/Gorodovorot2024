from sqlalchemy import create_engine, Column, Integer, Text, Boolean, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user_nickname = Column(Text)
    user_firstname = Column(Text)
    user_secondname = Column(Text)


class InGame(Base):
    __tablename__ = 'in_game'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    in_game = Column(Boolean)
    waiting_for_city = Column(Boolean)


class Games(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    city = Column(Text)
    available_categories = Column(ARRAY(String))
    last_callback_id = Column(Integer)


class UserInfo(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    score = Column(Integer)


class Database:
    def __init__(self, user, password):
        self.engine = create_engine(f'postgresql://{user}:{password}@localhost:5432/gorodovorot')
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)

    def add_user(self, user_id, user_nickname, user_firstname, user_secondname):
        session = self.Session()
        user = User(user_id=user_id, user_nickname=user_nickname, user_firstname=user_firstname,
                    user_secondname=user_secondname)
        session.add(user)
        in_game = InGame(user_id=user_id, in_game=False, waiting_for_city=False)
        session.add(in_game)
        session.commit()
        user_score = UserInfo(user_id=user_id, score=0)
        session.add(user_score)
        session.commit()
        session.close()

    def get_user_by_id(self, user_id):
        session = self.Session()
        user = session.query(User).filter_by(user_id=user_id).first()
        session.close()
        return user

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def delete_user_by_user_id(self, user_id):
        session = self.Session()
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            session.delete(user)
            session.commit()

        user = session.query(Games).filter_by(user_id=user_id).first()
        if user:
            session.delete(user)
            session.commit()

        user = session.query(InGame).filter_by(user_id=user_id).first()
        if user:
            session.delete(user)
            session.commit()

        session.close()

    def clear_after_game(self, user_id):
        session = self.Session()
        user = session.query(Games).filter_by(user_id=user_id).first()
        if user:
            session.delete(user)
            session.commit()

        self.set_waiting_for_city(user_id=user_id, status=False)
        self.game_status(user_id=user_id, status=False)

        session.close()

    def game_status(self, user_id, status=None):
        session = self.Session()
        user = session.query(InGame).filter_by(user_id=user_id).first()
        if user:
            if status is None:
                user.in_game = not user.in_game
                session.commit()

            else:
                user.in_game = status
                session.commit()
        session.close()

    def get_game_status(self, user_id):
        session = self.Session()
        user = session.query(InGame).filter_by(user_id=user_id).first()
        if user:
            status = user.in_game
            session.close()
            return status
        session.close()

    def waiting_for_city_get(self, user_id):
        session = self.Session()
        user = session.query(InGame).filter_by(user_id=user_id).first()
        if user:
            status = user.waiting_for_city
            session.close()
            return status
        session.close()

    def add_game(self, user_id, city, categories):
        session = self.Session()
        games = Games(user_id=user_id, city=city, available_categories=categories, last_callback_id=0)
        session.add(games)
        session.commit()
        session.close()

    def get_game_data(self, user_id):
        session = self.Session()
        game = session.query(Games).filter_by(user_id=user_id).first()
        if game:
            info = [game.city, game.available_categories]
            session.close()
            return info

        session.close()

    def set_available_categories(self, user_id, categories):
        session = self.Session()
        user = session.query(Games).filter_by(user_id=user_id).first()
        if user:
            user.available_categories = categories
            session.commit()
        session.close()

    def set_waiting_for_city(self, user_id, status):
        session = self.Session()
        user = session.query(InGame).filter_by(user_id=user_id).first()
        if user:
            print(1)
            user.waiting_for_city = status
            session.commit()
        session.close()
