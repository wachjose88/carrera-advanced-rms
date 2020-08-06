from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    sync = Column(Boolean, default=True)

    def __repr__(self):
        return "<Config(key='%s', value='%s')>" % (
            self.key, self.value)


class Car(Base):
    __tablename__ = 'car'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    sync = Column(Boolean, default=True)

    def __repr__(self):
        return "<Car(name='%s')>" % (
            self.name)


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

    def setCar(self, name, newname):
        session = self.Session()
        c = session.query(Car).filter_by(name=str(name)).first()
        if c is None:
            nc = Car(name=str(newname))
            session.add(nc)
        else:
            c.name = str(newname)
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
