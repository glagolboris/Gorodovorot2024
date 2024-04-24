from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user_nickname = Column(Text)
    user_firstname = Column(Text)
    user_secondname = Column(Text)

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
        user = User(user_id=user_id, user_nickname=user_nickname, user_firstname=user_firstname, user_secondname=user_secondname)
        session.add(user)
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
        session.close()
