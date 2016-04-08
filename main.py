from flask import *
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)