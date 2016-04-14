from flask import *
from flask_sqlalchemy import *
import util
import hashlib
import datetime
import collections
import subprocess

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Experiment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	# hash = db.Column(db.String(64))
	name = db.Column(db.String(64))
	timeGroup = db.Column(db.Time())
	annotatorName = db.Column(db.String(64))
	group = db.Column(db.String(10))
	outlier = db.Column(db.String(1))
	friendship = db.Column(db.Integer)
	notes = db.Column(db.String(2048))
	status = db.Column(db.String(20))

	def __init__(self, name, timeGroup, annotatorName, group, outlier, friendship, notes):
		# m = hashlib.sha512()
		# m.update(str(id))
		# self.hash = m.hexdigest()
		self.name = name
		self.timeGroup = datetime.datetime.strptime(timeGroup, "%I:%M %p").time()
		self.annotatorName = annotatorName
		self.group = group
		self.outlier = outlier
		self.friendship = friendship
		self.notes = notes
		self.status = "Created" #or Running or Done

	def __repr__(self):
		return str(self.id)

class Person(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gender = db.Column(db.String(1))
	age = db.Column(db.Integer)

	experimentID = db.Column(db.Integer, db.ForeignKey('experiment.id'))
	experiment = db.relationship('Experiment', backref=db.backref('people', lazy='dynamic'))

	def __init__(self, gender, age, experiment):
		self.gender = gender
		self.age = age
		self.experiment = experiment

	def __repr__(self):
		return str(self.id)

class PersonStatus(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime)
	engaged = db.Column(db.Boolean)
	usingTablet = db.Column(db.Boolean)
	currentTask = db.Column(db.String(20))
	
	personID = db.Column(db.Integer, db.ForeignKey('person.id'))
	person = db.relationship('Person', backref=db.backref('personStatuses', lazy='dynamic'))

	def __init__(self, engaged, usingTablet, currentTask):
		self.timestamp = datetime.datetime()
		self.engaged = engaged
		self.usingTabled = usingTablet
		self.currentTask = currentTask

	def __repr__(self):
		return str(self.id)

class PostExperimentData(db.Model):
	id = db.Column(db.Integer, primary_key=True)	
	experimentID = db.Column(db.Integer, db.ForeignKey('experiment.id'))
	experiment = db.relationship('Experiment', backref=db.backref('postResponses', lazy='dynamic'))

	finalTime = db.Column(db.Time)
	rank = db.Column(db.String(32))
	solvedMaze = db.Column(db.String(3))
	howMuchSolved = db.Column(db.String(100))
	notes = db.Column(db.String(2048))

	def __init__(self, finalTime, rank, solvedMaze, howMuchSolved, notes):
		self.finalTime = finalTime
		self.rank = rank
		self.solvedMaze = solvedMaze
		self.howMuchSolved = howMuchSolved
		self.notes = notes

	def __repr__(self):
		return str(self.id)

db.create_all()

#@app.route('/static/<path:path>')
#def send_js(path):
#	return send_from_directory('static', path)

@app.route('/gitupdate/')
def git():
	subprocess.call(["git", "pull"])
	return "OK!"

@app.route('/')
def index():
	#return 'Index Page'
	users = collections.OrderedDict()
	exps = Experiment.query.filter(Experiment.status != "Done").all()
	for u in exps:
   		users.update({u: u.__dict__})
	return render_template('index.html', exps=users)

@app.route('/init/')
def init():
	return render_template('initialize.html')

@app.route('/experiment/<int:experimentID>')
def experiment(experimentID=None):
	found = False
	#TODO REWRITE AS NOT IN QUERY 
	# as in if experimentID not in Experiment table
	for exp in Experiment.query.all(): 
		if str(experimentID) is str(exp):
			found = True
			break;
	if not found:
		return redirect(url_for('index'), code=302)

	return render_template('experiment.html', experiment=experimentID)

@app.route('/done/<int:experimentID>', methods=['GET', 'POST"'])
def done(experimentID=None):
	if (request.method == 'GET'):
		return render_template('postExperiment.html', experiment=experimentID)
	else:

		return redirect(url_for('index'), code=302)

@app.route('/setupExperiment/', methods=['POST'])
def setupExperiment():
	if request.method == 'POST':
		for item in request.form:
			print item + " " + request.form[item]

		try:
			exp = Experiment(request.form["experimentName"], request.form["timeGroup"], request.form["annotatorName"], request.form["group"], 
			request.form["outlier"], request.form["friendship"], request.form["notes"])
		except KeyError, e:
			return redirect(url_for('index'), code=302)

		db.session.add(exp)

		for i in range(1, 6):
			p = Person(request.form["person" + str(i) + "Gender"], request.form["person" + str(i) + "Age"], exp)
			db.session.add(p)

		db.session.commit()

	# return redirect(url_for('experiment'), code=302) #TODO should forward to specific experiment with id
	return redirect(url_for('index'), code=302)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=7878)
