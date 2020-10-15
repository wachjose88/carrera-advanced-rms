from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Boolean, \
                       ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship


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

    racingplayer = relationship("RacingPlayer", back_populates="car")

    def __repr__(self):
        return "<Car(name='%s')>" % (
            self.name)


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    name = Column(String)
    sync = Column(Boolean, default=False)

    racingplayer = relationship("RacingPlayer", back_populates="player")

    def __repr__(self):
        return "<Car(username='%s')>" % (
            self.username)


class Competition(Base):
    __tablename__ = 'competition'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    time = Column(DateTime, default=datetime.now)
    mode = Column(Integer)
    sortmode = Column(Integer)
    duration = Column(Integer)
    sync = Column(Boolean, default=False)

    racingplayer = relationship("RacingPlayer", back_populates="competition")

    def __repr__(self):
        return "<Competition(title='%s', mode='%s')>" % (
            self.title, self.mode)


class RacingPlayer(Base):
    __tablename__ = 'racingplayer'

    id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('competition.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    car_id = Column(Integer, ForeignKey('car.id'))
    sync = Column(Boolean, default=False)

    competition = relationship("Competition", back_populates="racingplayer")
    player = relationship("Player", back_populates="racingplayer")
    car = relationship("Car", back_populates="racingplayer")

    lap = relationship("Lap", back_populates="racingplayer")

    def __repr__(self):
        return "<RacingPlayer(id='%s')>" % (
            self.id)


class Lap(Base):
    __tablename__ = 'lap'

    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)
    fuel = Column(Integer)
    pit = Column(Boolean, default=False)
    racingplayer_id = Column(Integer, ForeignKey('racingplayer.id'))
    sync = Column(Boolean, default=False)

    racingplayer = relationship("RacingPlayer", back_populates="lap")

    def __repr__(self):
        return "<Lap(id='%s')>" % (
            self.id)


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

    def saveResult(self, title, time, mode, sort_mode, duration,
                   drivers, cu_drivers):
        session = self.Session()
        comp = Competition(title=title,
                           time=time,
                           mode=mode,
                           sortmode=sort_mode,
                           duration=duration)
        for addr, driver in drivers.items():
            cu_driver = cu_drivers[addr]
            car = session.query(Car).filter_by(name=driver['car']).first()
            player = session.query(Player).filter_by(
                username=cu_driver.name).first()
            racingplayer = RacingPlayer()
            racingplayer.player = player
            racingplayer.car = car
            comp.racingplayer.append(racingplayer)
            for i in range(0, len(cu_driver.timestamps)):
                lap = Lap(timestamp=cu_driver.timestamps[i],
                          fuel=cu_driver.fuels[i],
                          pit=cu_driver.pitslist[i])
                racingplayer.lap.append(lap)
        session.add(comp)
        session.commit()
        self.Session.remove()

    def getCompetitions(self, mode):
        session = self.Session()
        c = session.query(Competition).filter(
            Competition.mode.in_(mode)).order_by(Competition.time.desc()).all()
        self.Session.remove()
        if c is not None:
            return c
        return []

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
