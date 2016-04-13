from flask import *
from flask_sqlalchemy import *
import util
import hashlib
import datetime

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
    timeGroup = db.Column(db.Time())
    annotatorName = db.Column(db.String(64))
    group = db.Column(db.String(10))
    outlier = db.Column(db.String(1))
    friendship = db.Column(db.Integer)
    notes = db.Column(db.String(2048))

    def __init__(self, timeGroup, annotatorName, group, outlier, friendship, notes):
    	# m = hashlib.sha512()
    	# m.update(str(id))
    	# self.hash = m.hexdigest()

    	self.timeGroup = datetime.datetime.strptime(timeGroup, "%I:%M %p").time()
    	self.annotatorName = annotatorName
    	self.group = group
    	self.outlier = outlier
    	self.friendship = friendship
    	self.notes = notes

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
        return '<Person ID %r>' % self.id

db.create_all()

@app.route('/')
def index():
	#return 'Index Page'
	users = dict()
	exps = Experiment.query.all()
	for u in exps:
   		users.update({u: u.__dict__})
	return render_template('index.html', exps=users)

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.route('/test/')
@app.route('/test/<name>')
def test(name=None):
	return render_template('test.html', name=name)

@app.route('/init/')
def init():
	return render_template('initialize.html')

@app.route('/experiment/')
def experiment():
	return render_template('experiment.html')

@app.route('/done/')
def done():
	return render_template('postExperiment.html')

@app.route('/setupExperiment/', methods=['POST'])
def setupExperiment():
	if request.method == 'POST':
		for item in request.form:
			print item + " " + request.form[item]

		exp = Experiment(request.form["timeGroup"], request.form["annotatorName"], request.form["group"], 
			request.form["outlier"], request.form["friendship"], request.form["notes"])

		db.session.add(exp)

		for i in range(1, 6):
			p = Person(request.form["person" + str(i) + "Gender"], request.form["person" + str(i) + "Age"], exp)
			db.session.add(p)

		db.session.commit()

	return redirect(url_for('experiment'), code=302) #TODO should forward to specific experiment with id

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)