from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db')

Base = declarative_base()
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

    def __repr__(self):
        return self.username


def create_db():
    Base.metadata.create_all(engine)


def populate_db():
    session = Session()
    session.add_all([
        User(username='felipe', password='123456'),
        User(username='matheus', password='123456'),
        User(username='guidoni', password='123456'),
    ])
    session.commit()


def authenticated(session, username, password):
    query = session.query(User).filter(User.username == username, User.password == password)
    return query.first()


def create_user(session, username):
    try:
        user = User(username=username, password='123456')
        session.add(user)
        session.commit()
        return True
    except:
        return False


def delete_user(session, username):
    try:
        user = session.query(User).filter(User.username == username).first()
        session.delete(user)
        session.commit()
        return True
    except:
        return False


def change_password(session, user, password):
    try:
        user = session.query(User).filter(User.username == user.username).first()
        user.password = password
        session.commit()
        return True
    except:
        return False


if __name__ == "__main__":
    create_db()
    populate_db()