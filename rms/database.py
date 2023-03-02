import sys
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Boolean, \
                       ForeignKey, DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy_serializer import SerializerMixin

from PyQt5.QtCore import QCoreApplication

from utils import formattime
from constants import SORT_MODE__LAPS, SORT_MODE__LAPTIME, \
    COMP_MODE__RACE_LAPS, COMP_MODE__RACE_TIME, COMP_MODE__QUALIFYING_TIME, \
    COMP_MODE__QUALIFYING_LAPS_SEQ, COMP_MODE__QUALIFYING_TIME_SEQ, \
    COMP_MODE__TRAINING, COMP_MODE__QUALIFYING_LAPS

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


class Car(Base, SerializerMixin):
    __tablename__ = 'car'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    number = Column(String, unique=True)
    tires = Column(String, unique=False)
    scale = Column(Integer, unique=False)
    sync = Column(Boolean, default=False)

    racingplayer = relationship("RacingPlayer", back_populates="car")

    def __repr__(self):
        return "<Car(name='%s')>" % (
            self.name)


class Player(Base, SerializerMixin):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    name = Column(String)
    sync = Column(Boolean, default=False)

    racingplayer = relationship("RacingPlayer", back_populates="player")

    def __repr__(self):
        return "<Car(username='%s')>" % (
            self.username)


class Competition(Base, SerializerMixin):
    __tablename__ = 'competition'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    time = Column(DateTime, default=datetime.now)
    mode = Column(Integer)
    sortmode = Column(Integer)
    duration = Column(Integer)
    sync = Column(Boolean, default=False)

    racingplayer = relationship("RacingPlayer", back_populates="competition")

    resultcache = {}

    def __repr__(self):
        return "<Competition(title='%s', mode='%s')>" % (
            self.title, self.mode)

    def get_result(self):
        try:
            cached = Competition.resultcache[self.id]
            return cached
        except (KeyError, IndexError):
            pass
        r = []
        for p in self.racingplayer:
            flt = None
            if len(p.lap) < 1:
                t = {
                    'player': p,
                    'pid': p.id,
                    'laps': 0,
                    'time': sys.maxsize,
                    'bestlap': sys.maxsize,
                    'diff': None,
                    'rank': None
                }
                r.append(t)
                continue
            for i in range(1, len(p.lap)):
                l0 = p.lap[i-1].timestamp
                l1 = p.lap[i].timestamp
                lt = l1 - l0
                if flt is None or flt > lt:
                    flt = lt
            t = {
                'player': p,
                'pid': p.id,
                'laps': len(p.lap)-1,
                'time': p.lap[-1].timestamp,
                'bestlap': flt,
                'diff': None,
                'rank': None
            }
            r.append(t)
        last_drank = '0'
        last_bl = 0
        last_tm = 0
        last_lp = 0
        if self.sortmode == SORT_MODE__LAPS:
            r.sort(key=lambda dr: (0, 0) if dr['bestlap'] is None
                   else (-dr['laps'], dr['time']))
            for i in range(0, len(r)):
                t = r[i]
                if i == 0 or t['time'] == sys.maxsize:
                    t['diff'] = ' '
                else:
                    if r[0]['time'] is not None:
                        if r[0]['laps'] <= t['laps']:
                            t['diff'] = '+' + formattime(
                                t['time'] - r[0]['time'],
                                longfmt=False)
                        else:
                            t['diff'] = QCoreApplication.translate(
                                '+%n Lap(s)', '',
                                r[0]['laps'] - t['laps'])
            for i in range(0, len(r)):
                t = r[i]
                t['rank'] = str(i+1)
                if int(t['laps']) == int(last_lp) and \
                        int(t['time']) == int(last_tm):
                    t['rank'] = str(last_drank)
                last_drank = str(i+1)
                last_bl = int(t['bestlap'])
                last_lp = int(t['laps'])
                last_tm = int(t['time'])
                if t['time'] == sys.maxsize:
                    t['time'] = ' '
                    t['rank'] = str(QCoreApplication.translate('DNS'))
                else:
                    t['time'] = formattime(t['time'])
                if t['bestlap'] == sys.maxsize:
                    t['bestlap'] = ' '
                else:
                    t['bestlap'] = formattime(t['bestlap'], longfmt=False)
        if self.sortmode == SORT_MODE__LAPTIME:
            r.sort(key=lambda dr: 0 if dr['bestlap'] is None
                   else dr['bestlap'])
            for i in range(0, len(r)):
                t = r[i]
                if i == 0 or t['bestlap'] == sys.maxsize:
                    t['diff'] = ' '
                else:
                    if r[0]['bestlap'] is not None:
                        t['diff'] = '+' + formattime((int(t['bestlap']) -
                                                      float(r[0]['bestlap'])),
                                                     longfmt=False)
            for i in range(0, len(r)):
                t = r[i]
                t['rank'] = str(i+1)
                if int(t['bestlap']) == int(last_bl):
                    t['rank'] = str(last_drank)
                last_drank = str(i+1)
                last_bl = int(t['bestlap'])
                last_lp = int(t['laps'])
                last_tm = int(t['time'])
                if t['time'] == sys.maxsize:
                    t['time'] = ' '
                    t['rank'] = str(QCoreApplication.translate('DNS'))
                else:
                    t['time'] = formattime(t['time'])
                if t['bestlap'] == sys.maxsize:
                    t['bestlap'] = ' '
                else:
                    t['bestlap'] = formattime(t['bestlap'], longfmt=False)
        print(r)
        Competition.resultcache[self.id] = r
        return r


class RacingPlayer(Base, SerializerMixin):
    __tablename__ = 'racingplayer'

    id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('competition.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    car_id = Column(Integer, ForeignKey('car.id'))
    sync = Column(Boolean, default=False)

    competition = relationship("Competition", back_populates="racingplayer")
    player = relationship("Player", back_populates="racingplayer")
    car = relationship("Car", back_populates="racingplayer")

    lap = relationship("Lap", back_populates="racingplayer",
                       order_by='Lap.timestamp.asc()')

    def __repr__(self):
        return "<RacingPlayer(id='%s')>" % (
            self.id)


class Lap(Base, SerializerMixin):
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

    def getPlayersForSync(self):
        session = self.Session()
        cs = session.query(Player).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'username', 'name', 'sync')
                ))
            self.Session.remove()
            return cas
        self.Session.remove()
        return cs

    def getCarsForSync(self):
        session = self.Session()
        cs = session.query(Car).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'name', 'number', 'tires', 'scale', 'sync')
                ))
            self.Session.remove()
            return cas
        self.Session.remove()
        return cs

    def getCompetitionsForSync(self, widget):
        session = self.Session()
        cs = session.query(Competition).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                result = c.get_result()
                for re in result:
                    re['player'] = re['player'].id
                cas.append({'competition': c.to_dict(
                    only=('id', 'title', 'time', 'mode', 'sortmode',
                          'duration', 'sync')
                ), 'result': result})
            self.Session.remove()
            return cas
        self.Session.remove()
        return cs

    def getRacingPlayersForSync(self):
        session = self.Session()
        cs = session.query(RacingPlayer).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'car_id', 'player_id', 'competition_id',
                          'sync')
                ))
            self.Session.remove()
            return cas
        self.Session.remove()
        return cs

    def getLapsForSync(self):
        session = self.Session()
        cs = session.query(Lap).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'timestamp', 'racingplayer_id', 'fuel',
                          'pit', 'sync')
                ))
            self.Session.remove()
            return cas
        self.Session.remove()
        return cs

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
        # self.Session.remove()
        if c is not None:
            return c
        return []

    def setPlayersSync(self, ids):
        session = self.Session()
        for id in ids:
            c = session.query(Player).filter_by(id=id).first()
            c.sync = True
        session.commit()
        self.Session.remove()

    def setLapsSync(self, ids):
        session = self.Session()
        for id in ids:
            c = session.query(Lap).filter_by(id=id).first()
            c.sync = True
        session.commit()
        self.Session.remove()

    def setRacingPlayersSync(self, ids):
        session = self.Session()
        for id in ids:
            c = session.query(RacingPlayer).filter_by(id=id).first()
            c.sync = True
        session.commit()
        self.Session.remove()

    def setCompetitionsSync(self, ids):
        session = self.Session()
        for id in ids:
            c = session.query(Competition).filter_by(id=id).first()
            c.sync = True
        session.commit()
        self.Session.remove()

    def setCarsSync(self, ids):
        session = self.Session()
        for id in ids:
            c = session.query(Car).filter_by(id=id).first()
            c.sync = True
        session.commit()
        self.Session.remove()

    def setCar(self, name, number, tires, scale):
        session = self.Session()
        try:
            nc = Car(name=str(name), number=str(number), tires=str(tires),
                     scale=str(scale))
            session.add(nc)
            session.commit()
        except IntegrityError:
            self.Session.remove()
            return False
        self.Session.remove()
        return True

    def updateCar(self, id, name=None, number=None, tires=None, scale=None):
        session = self.Session()
        try:
            c = session.query(Car).filter_by(id=id).first()
            if c is not None:
                if name is not None:
                    c.name = str(name)
                if number is not None:
                    c.number = str(number)
                if tires is not None:
                    c.tires = str(tires)
                if scale is not None:
                    if scale == 'null':
                        c.scale = None
                    else:
                        c.scale = str(scale)
                c.sync = False
            session.commit()
        except IntegrityError:
            self.Session.remove()
            return False
        self.Session.remove()
        return True

    def updatePlayer(self, id, name=None, username=None):
        session = self.Session()
        try:
            c = session.query(Player).filter_by(id=id).first()
            if c is not None:
                if name is not None:
                    c.name = str(name)
                if username is not None:
                    c.username = str(username)
                c.sync = False
            session.commit()
        except IntegrityError:
            self.Session.remove()
            return False
        self.Session.remove()
        return True

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

    def getAllCarsDetails(self):
        session = self.Session()
        c = session.query(Car).all()
        details = []
        for p in c:
            numtrainings = 0
            numtrainingwins = 0
            numqualifyings = 0
            numqualifyingwins = 0
            numraces = 0
            numracewins = 0
            for rp in p.racingplayer:
                results = rp.competition.get_result()
                for result in results:
                    if rp.id == result['pid']:
                        if rp.competition.mode == COMP_MODE__TRAINING:
                            numtrainings += 1
                            if result['rank'] == '1':
                                numtrainingwins += 1
                        if rp.competition.mode in [
                                    COMP_MODE__QUALIFYING_LAPS,
                                    COMP_MODE__QUALIFYING_TIME,
                                    COMP_MODE__QUALIFYING_LAPS_SEQ,
                                    COMP_MODE__QUALIFYING_TIME_SEQ
                                ]:
                            numqualifyings += 1
                            if result['rank'] == '1':
                                numqualifyingwins += 1
                        if rp.competition.mode in [
                                    COMP_MODE__RACE_TIME,
                                    COMP_MODE__RACE_LAPS
                                ]:
                            numraces += 1
                            if result['rank'] == '1':
                                numracewins += 1
            details.append({
                'car': p,
                'numcompetitions': len(p.racingplayer),
                'numtrainings': numtrainings,
                'numtrainingwins': numtrainingwins,
                'numqualifyings': numqualifyings,
                'numqualifyingwins': numqualifyingwins,
                'numraces': numraces,
                'numracewins': numracewins
            })
            print('testnums', p.number, numraces, numracewins)
        self.Session.remove()
        return details

    def getAllPlayers(self):
        session = self.Session()
        c = session.query(Player).all()
        self.Session.remove()
        return c

    def getAllPlayersDetails(self):
        session = self.Session()
        c = session.query(Player).all()
        details = []
        for p in c:
            numtrainings = 0
            numtrainingwins = 0
            numqualifyings = 0
            numqualifyingwins = 0
            numraces = 0
            numracewins = 0
            for rp in p.racingplayer:
                results = rp.competition.get_result()
                for result in results:
                    if rp.id == result['pid']:
                        if rp.competition.mode == COMP_MODE__TRAINING:
                            numtrainings += 1
                            if result['rank'] == '1':
                                numtrainingwins += 1
                        if rp.competition.mode in [
                                    COMP_MODE__QUALIFYING_LAPS,
                                    COMP_MODE__QUALIFYING_TIME,
                                    COMP_MODE__QUALIFYING_LAPS_SEQ,
                                    COMP_MODE__QUALIFYING_TIME_SEQ
                                ]:
                            numqualifyings += 1
                            if result['rank'] == '1':
                                numqualifyingwins += 1
                        if rp.competition.mode in [
                                    COMP_MODE__RACE_TIME,
                                    COMP_MODE__RACE_LAPS
                                ]:
                            numraces += 1
                            if result['rank'] == '1':
                                numracewins += 1
            details.append({
                'player': p,
                'numcompetitions': len(p.racingplayer),
                'numtrainings': numtrainings,
                'numtrainingwins': numtrainingwins,
                'numqualifyings': numqualifyings,
                'numqualifyingwins': numqualifyingwins,
                'numraces': numraces,
                'numracewins': numracewins
            })
        self.Session.remove()
        return details

    def setPlayer(self, username, name):
        session = self.Session()
        try:
            nc = Player(username=str(username), name=str(name))
            session.add(nc)
            session.commit()
        except IntegrityError:
            self.Session.remove()
            return False
        self.Session.remove()
        return True

    def getPlayer(self, username):
        session = self.Session()
        c = session.query(Player).filter_by(username=username).first()
        self.Session.remove()
        if c is not None:
            return c
        return c
