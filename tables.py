import datetime

import sqlalchemy as sqa
from sqlalchemy.dialects.sqlite import INTEGER, VARCHAR, TIME, \
                                       DATETIME, SMALLINT, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()
COL = sqa.Column


class Experiment(Base):
    __tablename__ = 'experiment'
    id = COL(INTEGER, primary_key=True)
    # hash = COL(VARCHAR(64))
    name = COL(VARCHAR(64))
    numPeople = COL(SMALLINT)
    timeGroup = COL(TIME())
    group = COL(VARCHAR(10))
    outlier = COL(VARCHAR(1))
    friendship = COL(SMALLINT)
    notes = COL(VARCHAR(2048))
    status = COL(VARCHAR(20))

    def __init__(self, name, numPeople, timeGroup, group, outlier, friendship, notes):
        # m = hashlib.sha512()
        # m.update(str(id))
        # self.hash = m.hexdigest()
        self.name = name
        self.numPeople = int(numPeople)
        self.timeGroup = datetime.datetime.strptime(timeGroup, "%I:%M %p").time()
        self.group = group
        self.outlier = outlier
        self.friendship = friendship
        self.notes = notes
        self.status = "Created"  # or Running or Done

    def __repr__(self):
        return str(self.id)


class Annotation(Base):
    __tablename__ = 'annotation'
    id = COL(INTEGER, primary_key=True)
    annotatorName = COL(VARCHAR(64))
    personID = COL(INTEGER, sqa.ForeignKey('person.id'))
    person = relationship('Person', backref='annotations', uselist=False)

    __table_args__ = (sqa.UniqueConstraint('annotatorName', 'personID'),)

    def __init__(self, annotatorName, experiment):
        self.annotatorName = annotatorName
        self.experiment = experiment


class Person(Base):
    __tablename__ = 'person'
    id = COL(INTEGER, primary_key=True)
    gender = COL(VARCHAR(1))
    age = COL(INTEGER)
    idInExperiment = COL(INTEGER)

    experimentID = COL(INTEGER, sqa.ForeignKey('experiment.id'))
    experiment = relationship('Experiment', backref=backref('people', lazy='dynamic'))

    def __init__(self, gender, age, idInExperiment, experiment):
        self.gender = gender
        self.age = age
        self.experiment = experiment
        self.idInExperiment = idInExperiment

    def __repr__(self):
        return str(self.id)


class PersonStatus(Base):
    __tablename__ = 'person_status'
    id = COL(INTEGER, primary_key=True)
    timestamp = COL(DATETIME, default=datetime.datetime.utcnow)
    engaged = COL(BOOLEAN)
    usingTablet = COL(BOOLEAN)
    currentTask = COL(VARCHAR(20))

    personID = COL(INTEGER, sqa.ForeignKey('person.id'))
    person = relationship('Person', backref=backref('personStatuses', lazy='dynamic'))

    annotationID = COL(INTEGER, sqa.ForeignKey('annotation.id'))
    annotation = relationship('Annotation', backref=backref('experimentStatuses', lazy='dynamic'))

    def __init__(self, engaged, usingTablet, currentTask, person, annotation):
        self.engaged = engaged
        self.usingTablet = usingTablet
        self.currentTask = currentTask
        self.person = person
        self.annotation = annotation

    def __repr__(self):
        return str(self.id)


class PostExperimentData(Base):
    __tablename__ = 'post_experiment_data'
    id = COL(INTEGER, primary_key=True)
    timestamp = COL(DATETIME, default=datetime.datetime.utcnow)
    annotationID = COL(INTEGER, sqa.ForeignKey('annotation.id'))
    annotation = relationship('Annotation', backref=backref('postResponses', lazy='dynamic'))

    finalTime = COL(TIME)
    rankNum = COL(INTEGER)
    rankDenom = COL(INTEGER)
    solved = COL(BOOLEAN)
    howMuchSolved = COL(VARCHAR(100))
    notes = COL(VARCHAR(2048))

    def __init__(self, finalTimeMins, finalTimeSecs, rankNum, rankDenom, solved, howMuchSolved, notes, annotation):
        self.finalTime = datetime.datetime.strptime(str(finalTimeMins) + " " + str(finalTimeSecs), "%M %S").time()
        self.rankNum = rankNum
        self.rankDenom = rankDenom
        self.solved = True if (solved == "Yes") else False
        self.howMuchSolved = howMuchSolved
        self.notes = notes
        self.annotation = annotation

    def __repr__(self):
        return str(self.id)