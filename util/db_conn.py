from config import Production
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DB(object):
  def __init__(self):
    engine = create_engine(Production.SQLALCHEMY_DATABASE_URI, echo=False)
    Session = sessionmaker(bind=engine)
    self._session = Session()

  @property
  def session(self):
  	return self._session
  
