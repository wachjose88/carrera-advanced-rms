import sys
import json
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Boolean, \
    ForeignKey, DateTime, Text, or_
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
    statistic = Column(Text, unique=False)
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
    statistic = Column(Text, unique=False)
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
    statisticdone = Column(Boolean, default=False)
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
                    t['rank'] = str(QCoreApplication.translate('DNS', 'DNS'))
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
                    t['rank'] = str(QCoreApplication.translate('DNS', 'DNS'))
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
        self.engine = create_engine(
            'sqlite:///carrera.db?check_same_thread=False', echo=debug)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self.session = self.Session()

    def setConfig(self, key, value):
        c = self.session.query(Config).filter_by(key=key).first()
        if c is None:
            nc = Config(key=key, value=str(value))
            self.session.add(nc)
        else:
            c.value = str(value)
        self.session.commit()

    def getPlayersForSync(self):
        cs = self.session.query(Player).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'username', 'name', 'sync')
                ))
            return cas
        return cs

    def getCarsForSync(self):
        cs = self.session.query(Car).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'name', 'number', 'tires', 'scale', 'sync')
                ))
            return cas
        return cs

    def getCompetitionsForSync(self, widget):
        cs = self.session.query(Competition).filter_by(sync=False).all()
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
            return cas
        return cs

    def getRacingPlayersForSync(self):
        cs = self.session.query(RacingPlayer).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'car_id', 'player_id', 'competition_id',
                          'sync')
                ))
            return cas
        return cs

    def getLapsForSync(self):
        cs = self.session.query(Lap).filter_by(sync=False).all()
        if cs is not None:
            cas = []
            for c in cs:
                cas.append(c.to_dict(
                    only=('id', 'timestamp', 'racingplayer_id', 'fuel',
                          'pit', 'sync')
                ))
            return cas
        return cs

    def getConfigStr(self, key):
        c = self.session.query(Config).filter_by(key=key).first()
        if c is not None:
            return str(c.value)
        return c

    def saveResult(self, title, time, mode, sort_mode, duration,
                   drivers, cu_drivers):
        comp = Competition(title=title,
                           time=time,
                           mode=mode,
                           sortmode=sort_mode,
                           duration=duration)
        for addr, driver in drivers.items():
            cu_driver = cu_drivers[addr]
            car = self.session.query(Car).filter_by(name=driver['car']).first()
            player = self.session.query(Player).filter_by(
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
        self.session.add(comp)
        self.session.commit()

    def getCompetitions(self, mode):
        c = self.session.query(Competition).filter(
            Competition.mode.in_(mode)).order_by(Competition.time.desc()).all()
        if c is not None:
            return c
        return []

    def setPlayersSync(self, ids):
        for id in ids:
            c = self.session.query(Player).filter_by(id=id).first()
            c.sync = True
        self.session.commit()

    def setLapsSync(self, ids):
        for id in ids:
            c = self.session.query(Lap).filter_by(id=id).first()
            c.sync = True
        self.session.commit()

    def setRacingPlayersSync(self, ids):
        for id in ids:
            c = self.session.query(RacingPlayer).filter_by(id=id).first()
            c.sync = True
        self.session.commit()

    def setCompetitionsSync(self, ids):
        for id in ids:
            c = self.session.query(Competition).filter_by(id=id).first()
            c.sync = True
        self.session.commit()

    def setCarsSync(self, ids):
        for id in ids:
            c = self.session.query(Car).filter_by(id=id).first()
            c.sync = True
        self.session.commit()

    def setCar(self, name, number, tires, scale):
        try:
            nc = Car(name=str(name), number=str(number), tires=str(tires),
                     scale=str(scale))
            self.session.add(nc)
            self.session.commit()
        except IntegrityError:
            return False
        return True

    def updateCar(self, id, name=None, number=None, tires=None, scale=None):
        try:
            c = self.session.query(Car).filter_by(id=id).first()
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
            self.session.commit()
        except IntegrityError:
            return False
        return True

    def updatePlayer(self, id, name=None, username=None):
        try:
            c = self.session.query(Player).filter_by(id=id).first()
            if c is not None:
                if name is not None:
                    c.name = str(name)
                if username is not None:
                    c.username = str(username)
                c.sync = False
            self.session.commit()
        except IntegrityError:
            return False
        return True

    def getCarByName(self, name):
        c = self.session.query(Car).filter_by(name=name).first()
        if c is not None:
            return c
        return c

    def getCar(self, id):
        c = self.session.query(Car).filter_by(id=id).first()
        if c is not None:
            return c
        return c

    def getAllCars(self):
        c = self.session.query(Car).all()
        return c

    def getAllCarsDetails(self):
        c = self.session.query(Car).all()
        details = []
        for p in c:
            # numtrainings = 0
            # numtrainingwins = 0
            # numqualifyings = 0
            # numqualifyingwins = 0
            # numraces = 0
            # numracewins = 0
            # for rp in p.racingplayer:
            #     results = rp.competition.get_result()
            #     for result in results:
            #         if rp.id == result['pid']:
            #             if rp.competition.mode == COMP_MODE__TRAINING:
            #                 numtrainings += 1
            #                 if result['rank'] == '1':
            #                     numtrainingwins += 1
            #             if rp.competition.mode in [
            #                         COMP_MODE__QUALIFYING_LAPS,
            #                         COMP_MODE__QUALIFYING_TIME,
            #                         COMP_MODE__QUALIFYING_LAPS_SEQ,
            #                         COMP_MODE__QUALIFYING_TIME_SEQ
            #                     ]:
            #                 numqualifyings += 1
            #                 if result['rank'] == '1':
            #                     numqualifyingwins += 1
            #             if rp.competition.mode in [
            #                         COMP_MODE__RACE_TIME,
            #                         COMP_MODE__RACE_LAPS
            #                     ]:
            #                 numraces += 1
            #                 if result['rank'] == '1':
            #                     numracewins += 1
            # details.append({
            #     'car': p,
            #     'numcompetitions': len(p.racingplayer),
            #     'numtrainings': numtrainings,
            #     'numtrainingwins': numtrainingwins,
            #     'numqualifyings': numqualifyings,
            #     'numqualifyingwins': numqualifyingwins,
            #     'numraces': numraces,
            #     'numracewins': numracewins
            # })
            if p.statistic is not None:
                statistic = json.loads(p.statistic)
                details.append({
                    'car': p,
                    'numcompetitions': len(p.racingplayer),
                    'numtrainings': statistic['numtrainings'],
                    'numtrainingwins': statistic['numtrainingwins'],
                    'numqualifyings': statistic['numqualifyings'],
                    'numqualifyingwins': statistic['numqualifyingwins'],
                    'numraces': statistic['numraces'],
                    'numracewins': statistic['numracewins']
                })
            else:
                details.append({
                    'car': p,
                    'numcompetitions': len(p.racingplayer),
                    'numtrainings': 0,
                    'numtrainingwins': 0,
                    'numqualifyings': 0,
                    'numqualifyingwins': 0,
                    'numraces': 0,
                    'numracewins': 0
                })
        return details

    def getAllPlayers(self):
        c = self.session.query(Player).all()
        return c

    def getAllPlayersDetails(self):
        c = self.session.query(Player).all()
        details = []
        for p in c:
            # numtrainings = 0
            # numtrainingwins = 0
            # numqualifyings = 0
            # numqualifyingwins = 0
            # numraces = 0
            # numracewins = 0
            # for rp in p.racingplayer:
            #     results = rp.competition.get_result()
            #     for result in results:
            #         if rp.id == result['pid']:
            #             if rp.competition.mode == COMP_MODE__TRAINING:
            #                 numtrainings += 1
            #                 if result['rank'] == '1':
            #                     numtrainingwins += 1
            #             if rp.competition.mode in [
            #                         COMP_MODE__QUALIFYING_LAPS,
            #                         COMP_MODE__QUALIFYING_TIME,
            #                         COMP_MODE__QUALIFYING_LAPS_SEQ,
            #                         COMP_MODE__QUALIFYING_TIME_SEQ
            #                     ]:
            #                 numqualifyings += 1
            #                 if result['rank'] == '1':
            #                     numqualifyingwins += 1
            #             if rp.competition.mode in [
            #                         COMP_MODE__RACE_TIME,
            #                         COMP_MODE__RACE_LAPS
            #                     ]:
            #                 numraces += 1
            #                 if result['rank'] == '1':
            #                     numracewins += 1
            if p.statistic is not None:
                statistic = json.loads(p.statistic)
                details.append({
                    'player': p,
                    'numcompetitions': len(p.racingplayer),
                    'numtrainings': statistic['numtrainings'],
                    'numtrainingwins': statistic['numtrainingwins'],
                    'numqualifyings': statistic['numqualifyings'],
                    'numqualifyingwins': statistic['numqualifyingwins'],
                    'numraces': statistic['numraces'],
                    'numracewins': statistic['numracewins']
                })
            else:
                details.append({
                    'player': p,
                    'numcompetitions': len(p.racingplayer),
                    'numtrainings': 0,
                    'numtrainingwins': 0,
                    'numqualifyings': 0,
                    'numqualifyingwins': 0,
                    'numraces': 0,
                    'numracewins': 0
                })
        return details

    def setPlayer(self, username, name):
        try:
            nc = Player(username=str(username), name=str(name))
            self.session.add(nc)
            self.session.commit()
        except IntegrityError:
            return False
        return True

    def getPlayer(self, username):
        c = self.session.query(Player).filter_by(username=username).first()
        if c is not None:
            return c
        return c

    def updateStatistic(self):
        playerstatistic = {}
        carstatistic = {}
        comps = self.session.query(Competition).filter(or_(Competition.statisticdone==False,
                                                      Competition.statisticdone==None))
        for comp in comps:
            results = comp.get_result()
            for result in results:
                if result['player'].player_id not in playerstatistic:
                    playerstatistic[result['player'].player_id] = {
                        'numtrainings': 0,
                        'numtrainingwins': 0,
                        'numqualifyings': 0,
                        'numqualifyingwins': 0,
                        'numraces': 0,
                        'numracewins': 0
                    }
                if result['player'].car_id not in carstatistic:
                    carstatistic[result['player'].car_id] = {
                        'numtrainings': 0,
                        'numtrainingwins': 0,
                        'numqualifyings': 0,
                        'numqualifyingwins': 0,
                        'numraces': 0,
                        'numracewins': 0
                    }
                if comp.mode == COMP_MODE__TRAINING:
                    playerstatistic[result['player'].player_id]['numtrainings'] += 1
                    carstatistic[result['player'].car_id]['numtrainings'] += 1
                    if result['rank'] == '1':
                        playerstatistic[result['player'].player_id]['numtrainingwins'] += 1
                        carstatistic[result['player'].car_id]['numtrainingwins'] += 1
                if comp.mode in [
                            COMP_MODE__QUALIFYING_LAPS,
                            COMP_MODE__QUALIFYING_TIME,
                            COMP_MODE__QUALIFYING_LAPS_SEQ,
                            COMP_MODE__QUALIFYING_TIME_SEQ
                        ]:
                    playerstatistic[result['player'].player_id]['numqualifyings'] += 1
                    carstatistic[result['player'].car_id]['numqualifyings'] += 1
                    if result['rank'] == '1':
                        playerstatistic[result['player'].player_id]['numqualifyingwins'] += 1
                        carstatistic[result['player'].car_id]['numqualifyingwins'] += 1
                if comp.mode in [
                            COMP_MODE__RACE_TIME,
                            COMP_MODE__RACE_LAPS
                        ]:
                    playerstatistic[result['player'].player_id]['numraces'] += 1
                    carstatistic[result['player'].car_id]['numraces'] += 1
                    if result['rank'] == '1':
                        playerstatistic[result['player'].player_id]['numracewins'] += 1
                        carstatistic[result['player'].car_id]['numracewins'] += 1
        for playerid, statistic in playerstatistic.items():
            player = self.session.query(Player).filter_by(id=playerid).first()
            if player.statistic is None:
                player.statistic = json.dumps(statistic)
            else:
                db_statistic = json.loads(player.statistic)
                for stat_name, stat_value in db_statistic.items():
                    db_statistic[stat_name] = stat_value + statistic[stat_name]
                player.statistic = json.dumps(db_statistic)
            self.session.commit()

        for carid, statistic in carstatistic.items():
            car = self.session.query(Car).filter_by(id=carid).first()
            if car.statistic is None:
                car.statistic = json.dumps(statistic)
            else:
                db_statistic = json.loads(car.statistic)
                for stat_name, stat_value in db_statistic.items():
                    db_statistic[stat_name] = stat_value + statistic[stat_name]
                car.statistic = json.dumps(db_statistic)
            self.session.commit()

        for comp in comps:
            comp.statisticdone = True
            self.session.commit()

    def removeSession(self):
        self.Session.remove()