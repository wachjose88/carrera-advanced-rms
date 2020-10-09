from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    sync = Column(Boolean, default=False)

    def __repr__(self):
        return "<Config(key='%s', value='%s')>" % (
            self.key, self.value)


class Car(Base):
    __tablename__ = 'car'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    number = Column(String, unique=True)
    sync = Column(Boolean, default=False)

    def __repr__(self):
        return "<Car(name='%s')>" % (
            self.name)


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    name = Column(String)
    sync = Column(Boolean, default=False)

    def __repr__(self):
        return "<Car(username='%s')>" % (
            self.username)


class DatabaseHandler(object):

    def __init__(self, debug):
        super(DatabaseHandler, self).__init__()
        self.engine = create_engine('sqlite:///carrera.db', echo=debug)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def setConfig(self, key, value):
        session = self.Session()
        c = session.query(Config).filter_by(key=key).first()
        if c is None:
            nc = Config(key=key, value=str(value))
            session.add(nc)
        else:
            c.value = str(value)
        session.commit()
        self.Session.remove()

    def getConfigStr(self, key):
        session = self.Session()
        c = session.query(Config).filter_by(key=key).first()
        self.Session.remove()
        if c is not None:
            return str(c.value)
        return c

    def setCar(self, name, newname, number):
        session = self.Session()
        c = session.query(Car).filter_by(name=str(name)).first()
        if c is None:
            nc = Car(name=str(newname), number=str(number))
            session.add(nc)
        else:
            c.name = str(newname)
            c.number = str(number)
        session.commit()
        self.Session.remove()

    def getCarByName(self, name):
        session = self.Session()
        c = session.query(Car).filter_by(name=name).first()
        self.Session.remove()
        if c is not None:
            return c
        return c

    def getCar(self, id):
        session = self.Session()
        c = session.query(Car).filter_by(id=id).first()
        self.Session.remove()
        if c is not None:
            return c
        return c

    def getAllCars(self):
        session = self.Session()
        c = session.query(Car).all()
        self.Session.remove()
        return c

    def getAllPlayers(self):
        session = self.Session()
        c = session.query(Player).all()
        self.Session.remove()
        return c

    def setPlayer(self, username, newusername, name):
        session = self.Session()
        c = session.query(Player).filter_by(username=str(username)).first()
        if c is None:
            nc = Player(username=str(newusername), name=str(name))
            session.add(nc)
        else:
            c.username = str(newusername)
            c.name = str(name)
        session.commit()
        self.Session.remove()

    def getPlayer(self, username):
        session = self.Session()
        c = session.query(Player).filter_by(username=username).first()
        self.Session.remove()
        if c is not None:
            return c
        return c
