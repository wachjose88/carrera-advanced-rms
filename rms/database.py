from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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


class DatabaseHandler(object):

    def __init__(self):
        super(DatabaseHandler, self).__init__()
        self.engine = create_engine('sqlite:///carrera.db', echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def setConfig(self, key, value):
        session = self.Session()
        c = session.query(Config).filter_by(key=key).first()
        if c is None:
            nc = Config(key=key, value=str(value))
            session.add(nc)
        else:
            c.value = str(value)
        session.commit()

    def getConfigStr(self, key):
        session = self.Session()
        c = session.query(Config).filter_by(key=key).first()
        if c is not None:
            return str(c.value)
        return c
