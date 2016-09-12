import os

class Production(object):
	db_path = os.path.join(os.path.dirname(__file__), 'app.db')
	db_uri = 'sqlite:///{}'.format(db_path)
	SQLALCHEMY_DATABASE_URI = db_uri
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SQLALCHEMY_ECHO = False
