import collections
import datetime
import os
import subprocess

from flask import *
from flask_sqlalchemy import SQLAlchemy
from tables import *

MIN_PERSON = 1
MAX_PERSON = 6

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)
Base.metadata.create_all(db.engine)

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
    exps = db.session.query(Experiment).filter(Experiment.status != "Done").all()
    for u in exps:
        users.update({u: u.__dict__})
    return render_template('index.html', exps=users)


@app.route('/init/')
def init():
    return render_template('initialize.html')


@app.route('/joinExperiment/<int:experimentID>')
def join_experiment(experimentID=None):
    exp = db.session.query(Experiment).filter(Experiment.id == experimentID).first()
    if exp is None:
        return redirect(url_for('index'), code=302)
    annotations = exp.people.first().annotations
    return render_template('joinExperiment.html', anno=annotations, exp=exp)


@app.route('/createAnnotation/<int:experimentID>', methods=['POST'])
def create_annotation(experimentID=None):
    exp = db.session.query(Experiment).filter(Experiment.id == experimentID).first()
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
    # for exp in db.session.query(Experiment).all():
    #     if str(experimentID) is str(exp):
    #         found = True
    #         break;
    # if not found:
    #     return redirect(url_for('index'), code=302)

    annotation = db.session.query(Annotation).filter(Annotation.id == annotationID).first()
    if annotation is None:
        return redirect(url_for('index'), code=302)
    if annotation.person is None:
        return "Server Error!"

    experiment = annotation.person.experiment

    if experiment is None or annotation is None:
        return redirect(url_for('index'), code=302)

    return render_template('experiment.html', exp=experiment, anno=annotation, numPeople=experiment.numPeople)


@app.route('/done/<int:annotationID>', methods=['GET', 'POST'])
def done(annotationID=None):
    annotation = db.session.query(Annotation).filter_by(id=annotationID).first()
    if annotation is None or annotation.person is None or annotation.person.experiment is None:
        return redirect(url_for('index'), code=302)

    if request.method == 'GET':
        return render_template('postExperiment.html', annotation=annotation)
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
            exp = annotation.person.experiment
            exp.status = "Done"
            data = PostExperimentData(request.form["finalTimeMins"], request.form["finalTimeSecs"],
                                      request.form["rankNum"],
                                      request.form["rankDenom"], request.form["solved"], howMuchSolved, notes,
                                      annotation)
            db.session.add(data)
            db.session.commit()
        except KeyError, e:
            print "ERROR done form missing keys: %s" % e
            return redirect(url_for('index'), code=302)

        return redirect(url_for('index'), code=302)


@app.route('/data/<int:annotationID>/<string:action>', methods=['GET', 'POST'])
def data(annotationID=None, action=None):
    if db.session.query(Annotation).filter_by(id=annotationID).count() == 0:
        return "BAD"

    annotation = db.session.query(Annotation).filter_by(id=annotationID).first()
    if annotation is None or annotation.person is None or annotation.person.experiment is None:
        return "BAD"

    exp = annotation.person.experiment

    if action == "start":
        exp.status = "Running"
        db.session.commit()

    if action == "poll":
        return str('{"status": "' + str(exp.status) + '"}')

    if action == "push":

        for item in request.form:
            name = item.strip("[]")
        if "notes" not in request.form:
            notes = ""
        else:
            notes = request.form["notes"]
        if "task" not in request.form:
            task = ""
        else:
            task = request.form["task"]

        info = {i: {"notes": notes, "currentTask": task} for i in range(MIN_PERSON, exp.numPeople + 1)}

        try:
            for i in range(MIN_PERSON, exp.numPeople + 1):
                info[i].update({"engaged": False, "usingTablet": False})

            for i in range(MIN_PERSON, exp.numPeople + 1):
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

        for i in range(MIN_PERSON, exp.numPeople + 1):
            person = exp.people.filter_by(idInExperiment=i).first()
            # print person.__dict__

            personStatus = PersonStatus(info[i]["engaged"], info[i]["usingTablet"], info[i]["currentTask"], person,
                                        annotation)
            db.session.add(personStatus)
        db.session.commit()

    return "OK"


@app.route('/setupExperiment/', methods=['POST'])
def setupExperiment():
    if request.method == 'POST':
        # for item in request.form:
        #    print item + " " + request.form[item]
        if "notes" not in request.form:
            notes = ""
        else:
            notes = request.form["notes"]

        time_group = request.form["timeGroupMins"] + ":" + request.form["timeGroupSecs"]
        if len(time_group) < 3:
            time_group = request.form["timeGroup"]
        else:
            time_group = datetime.datetime.strptime(time_group, "%H:%M").strftime("%I:%M %p")

        try:
            exp = Experiment(request.form["experimentName"], request.form["numPeople"],
                             time_group, request.form["group"], request.form["outlier"],
                             request.form["friendship"], notes)
        except KeyError, e:
            print "ERROR setupExperiment form missing keys: %s" % e
            return redirect(url_for('index'), code=302)

        db.session.add(exp)

        for i in range(MIN_PERSON, exp.numPeople + 1):
            p = Person(request.form["person" + str(i) + "Gender"], request.form["person" + str(i) + "Age"], i, exp)
            db.session.add(p)

        db.session.commit()

    # return redirect(url_for('experiment'), code=302) #TODO should forward to specific experiment with id
    return redirect(url_for('index'), code=302)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8878)
