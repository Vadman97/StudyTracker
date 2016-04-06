from flask import *
app = Flask(__name__)

@app.route('/')
def index():
	print str(url_for('static', filename='bootstrap/css/bootstrap.css'))
	return 'Index Page'

@app.route('/test/')
@app.route('/test/<name>')
def test(name=None):
	return render_template('test.html', name=name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)