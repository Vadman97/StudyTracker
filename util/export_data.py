import csv
import re
from db_conn import DB
from tables import *

fields = []
db = DB()

for exp in db.session.query(Experiment).all():
  path = unicode(re.sub('[^\w\s-]', '', exp.name).strip().lower())
  path = unicode(re.sub('[-\s]+', '-', path)) + '.csv'
  with open(path, 'wb') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for person in exp.people.all():
      print(person)
      for annotation in person.annotations:
        print(annotation.annotatorName)
        first_ts = annotation.experimentStatuses.first().timestamp
        last_ts = annotation.experimentStatuses.order_by(PersonStatus.timestamp.desc()).first().timestamp
        for status in annotation.experimentStatuses.all():
          print(status.timestamp)
