import collections
import datetime
import os
import subprocess

from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

MIN_PERSON = 1
MAX_PERSON = 6

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)
Base = db.Model


class Experiment(Base):
    id = db.Column(db.Integer, primary_key=True)
    # hash = db.Column(db.String(64))
    name = db.Column(db.String(64))
    timeGroup = db.Column(db.Time())
    group = db.Column(db.String(10))
    outlier = db.Column(db.String(1))
    friendship = db.Column(db.Integer)
    notes = db.Column(db.String(2048))
    status = db.Column(db.String(20))

    def __init__(self, name, timeGroup, group, outlier, friendship, notes):
        # m = hashlib.sha512()
        # m.update(str(id))
        # self.hash = m.hexdigest()
        self.name = name
        self.timeGroup = datetime.datetime.strptime(timeGroup, "%I:%M %p").time()
        self.group = group
        self.outlier = outlier
        self.friendship = friendship
        self.notes = notes
        self.status = "Created"  # or Running or Done

    def __repr__(self):
        return str(self.id)


class Annotation(Base):
    id = db.Column(db.Integer, primary_key=True)
    annotatorName = db.Column(db.String(64))
    personID = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person', backref='annotations', uselist=False)

    __table_args__ = (UniqueConstraint('annotatorName', 'personID'),)

    def __init__(self, annotatorName, experiment):
        self.annotatorName = annotatorName
        self.experiment = experiment


class Person(Base):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(1))
    age = db.Column(db.Integer)
    idInExperiment = db.Column(db.Integer)

    experimentID = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('people', lazy='dynamic'))

    def __init__(self, gender, age, idInExperiment, experiment):
        self.gender = gender
        self.age = age
        self.experiment = experiment
        self.idInExperiment = idInExperiment

    def __repr__(self):
        return str(self.id)


class PersonStatus(Base):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    engaged = db.Column(db.Boolean)
    usingTablet = db.Column(db.Boolean)
    currentTask = db.Column(db.String(20))

    personID = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person', backref=db.backref('personStatuses', lazy='dynamic'))

    experimentID = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('experimentStatuses', lazy='dynamic'))

    def __init__(self, engaged, usingTablet, currentTask, person, experiment):
        self.engaged = engaged
        self.usingTablet = usingTablet
        self.currentTask = currentTask
        self.person = person
        self.experiment = experiment

    def __repr__(self):
        return str(self.id)


class PostExperimentData(Base):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    experimentID = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('postResponses', lazy='dynamic'))

    finalTime = db.Column(db.Time)
    rankNum = db.Column(db.Integer)
    rankDenom = db.Column(db.Integer)
    solved = db.Column(db.Boolean)
    howMuchSolved = db.Column(db.String(100))
    notes = db.Column(db.String(2048))

    def __init__(self, finalTimeMins, finalTimeSecs, rankNum, rankDenom, solved, howMuchSolved, notes, experiment):
        self.finalTime = datetime.datetime.strptime(str(finalTimeMins) + " " + str(finalTimeSecs), "%M %S").time()
        self.rankNum = rankNum
        self.rankDenom = rankDenom
        self.solved = True if (solved == "Yes") else False
        self.howMuchSolved = howMuchSolved
        self.notes = notes
        self.experiment = experiment

    def __repr__(self):
        return str(self.id)


db.create_all()

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route('/gitupdate/', methods=['GET', 'POST'])
def git():
    subprocess.Popen(["git", "pull"], cwd='/var/interactionlab')
    # return str(subprocess.check_output(["ls", "-lsah"]))
    # return str(subprocess.check_output(["git", "pull"]))
    return "OK!"


@app.route('/')
def index():
    # return 'Index Page'
    users = collections.OrderedDict()
    exps = Experiment.query.filter(Experiment.status != "Done").all()
    for u in exps:
        users.update({u: u.__dict__})
    return render_template('index.html', exps=users)


@app.route('/init/')
def init():
    return render_template('initialize.html')


@app.route('/joinExperiment/<int:experimentID>')
def join_experiment(experimentID=None):
    exp = Experiment.query.filter(Experiment.id == experimentID).first()
    if exp is None:
        return redirect(url_for('index'), code=302)
    annotations = exp.people.first().annotations
    return render_template('joinExperiment.html', anno=annotations, exp=exp)


@app.route('/createAnnotation/<int:experimentID>', methods=['POST'])
def create_annotation(experimentID=None):
    exp = Experiment.query.filter(Experiment.id == experimentID).first()
    if exp is None:
        return redirect(url_for('index'), code=302)

    for person in exp.people.all():
        annotation = Annotation(request.form.get("annotatorName"), person.experiment)
        annotation.person = person
        db.session.add(annotation)

    db.session.commit()
    return redirect(url_for('experiment', annotationID=annotation.id))

@app.route('/experiment/<int:annotationID>')
def experiment(annotationID=None):
    # found = False
    # REWRITE AS NOT IN QUERY as in if experimentID not in Experiment table
    # for exp in Experiment.query.all():
    # 	if str(experimentID) is str(exp):
    # 		found = True
    # 		break;
    # if not found:
    # 	return redirect(url_for('index'), code=302)

    annotation = Annotation.query.filter(Annotation.id == annotationID).first()
    if annotation.person is None:
        return "Server Error!"

    experiment = annotation.person.experiment.first()

    if experiment is None or annotation is None:
        return redirect(url_for('index'), code=302)

    return render_template('experiment.html', exp=experiment, anno=annotation)


@app.route('/done/<int:annotationID>', methods=['GET', 'POST'])
def done(annotationID=None):
    if (request.method == 'GET'):
        if Experiment.query.filter_by(id=experimentID).count() == 0:
            return redirect(url_for('index'), code=302)

        return render_template('postExperiment.html', experiment=experimentID)
    elif request.method == 'POST':
        if "notes" not in request.form:
            notes = ""
        else:
            notes = request.form["notes"]

        if "howMuchSolved" not in request.form:
            howMuchSolved = ""
        else:
            howMuchSolved = request.form["howMuchSolved"]

        try:
            exp = Experiment.query.filter_by(id=experimentID)
            exp.update({Experiment.status: "Done"})
            exp = exp.first()
            data = PostExperimentData(request.form["finalTimeMins"], request.form["finalTimeSecs"],
                                      request.form["rankNum"],
                                      request.form["rankDenom"], request.form["solved"], howMuchSolved, notes, exp)
            db.session.add(data)
            db.session.commit()
        except KeyError, e:
            print "ERROR done form missing keys: %s" % e
            return redirect(url_for('index'), code=302)

        return redirect(url_for('index'), code=302)


@app.route('/data/<int:annotationID>/<string:action>', methods=['GET', 'POST'])
def data(annotationID=None, action=None):
    if Annotation.query.filter_by(id=annotationID).count() == 0:
        return "BAD"

    annotation = Annotation.query.filter_by(id=annotationID)
    exp = annotation.experiment

    if action == "start":
        exp.update({Experiment.status: "Running"})
        db.session.commit()

    if action == "poll":
        return str('{"status": "' + str(exp.status) + '"}')

    if action == "push":

        for item in request.form:
            print item + ":"
            name = item.strip("[]")
            for one in request.form.getlist(item):
                print str(one)
        if "notes" not in request.form:
            notes = ""
        else:
            notes = request.form["notes"]
        if "task" not in request.form:
            task = ""
        else:
            task = request.form["task"]

        info = [{"notes": notes, "currentTask": task} for _ in range(MIN_PERSON, MAX_PERSON)]

        try:
            for i in range(MIN_PERSON, MAX_PERSON):
                info.update({i: {"engaged": False, "usingTablet": False}})

            for i in range(MIN_PERSON, MAX_PERSON):
                if (str("person") + str(i)) in request.form.getlist("engagement[]"):
                    info[i]["engaged"] = True
                else:
                    info[i]["engaged"] = False

                if (str("person") + str(i)) in request.form.getlist("tablet"):
                    info[i]["usingTablet"] = True
                else:
                    info[i]["usingTablet"] = False

        except KeyError, e:
            print "ERROR pushData form missing keys: %s" % e
            return "BAD"

        print str(info)

        for i in range(MIN_PERSON, MAX_PERSON):
            person = exp.people.filter_by(idInExperiment=i).first()
            # print person.__dict__

            personStatus = PersonStatus(info[i]["engaged"], info[i]["usingTablet"], info["currentTask"], person, exp)
            db.session.add(personStatus)
        db.session.commit()

    return "OK"


@app.route('/setupExperiment/', methods=['POST'])
def setupExperiment():
    if request.method == 'POST':
        # for item in request.form:
        #	print item + " " + request.form[item]
        if "notes" not in request.form:
            notes = ""
        else:
            notes = request.form["notes"]

        try:
            exp = Experiment(request.form["experimentName"], request.form["timeGroup"], request.form["group"],
                             request.form["outlier"], request.form["friendship"], notes)
        except KeyError, e:
            print "ERROR setupExperiment form missing keys: %s" % e
            return redirect(url_for('index'), code=302)

        db.session.add(exp)

        for i in range(MIN_PERSON, MAX_PERSON):
            p = Person(request.form["person" + str(i) + "Gender"], request.form["person" + str(i) + "Age"], i, exp)
            db.session.add(p)

        db.session.commit()

    # return redirect(url_for('experiment'), code=302) #TODO should forward to specific experiment with id
    return redirect(url_for('index'), code=302)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8878)
