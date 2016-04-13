from flask import *
import util

app = Flask(__name__)

@app.route('/')
def index():
	return 'Index Page'

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

	return redirect(url_for('experiment'), code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)