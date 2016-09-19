import csv
import datetime
import re
from db_conn import DB
from tables import *

DATA_FREQUENCY = 2;
DELTA_S = 1.0 / DATA_FREQUENCY;
DELTA = datetime.timedelta(seconds=DELTA_S)
EXP_CONFIG_PATH = 'experiment_configurations.csv'

fields = ['annotator', 'personID', 'age', 'gender', 'timestamp', 'engaged', 'usingTablet', 'currentTask']
exp_config_fields = ['name', 'numPeople', 'timeGroup', 'group', 'outlier', 'friendship', 'notes']
post_exp_fields = ['experimentName', 'finalTime', 'rank', 'solved', 'howMuchSolved', 'notes']
db = DB()

with open(EXP_CONFIG_PATH, 'wb') as configfile:
  exp_config_writer = csv.DictWriter(configfile, fieldnames=exp_config_fields, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  exp_config_writer.writeheader()

  for exp in db.session.query(Experiment).all():
    # write experiment configuration details
    data = {}
    for field in exp_config_fields:
      data[field] = getattr(exp, field)
    exp_config_writer.writerow(data)

    # replace illegal file characters with dash
    path = unicode(re.sub('[^\w\s-]', '', exp.name).strip().lower())
    path = unicode(re.sub('[-\s]+', '-', path)) + '.csv'

    # for each experiment, populate the statuses at a constant rate
    with open(path, 'wb') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
      writer.writeheader()
      for person in exp.people.all():
        for annotation in person.annotations:

          # write the annotators post-experiment status
          if annotation.post_experiment_response:
            with open(path[:-4] + '_post_experiment.csv', 'wb') as post_exp_file:
              post_exp_writer = csv.DictWriter(post_exp_file, fieldnames=post_exp_fields, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
              post_exp_writer.writeheader()
              data = {}
              data['experimentName'] = path[:-4] # take the safe name with removed unsafe chars
              for field in post_exp_fields:
                if hasattr(annotation.post_experiment_response, field):
                  data[field] = getattr(annotation.post_experiment_response, field)
              post_exp_writer.writerow(data)

          # write statuses for each participant with constant frequency
          first_ts = annotation.experimentStatuses.first().timestamp
          last_ts = annotation.experimentStatuses.order_by(PersonStatus.timestamp.desc()).first().timestamp
          statuses = annotation.experimentStatuses.all()

          curr_ts = first_ts
          for curr_status in statuses:
            while curr_ts < curr_status.timestamp and curr_ts < last_ts:
              writer.writerow({'annotator': annotation.annotatorName, 'personID': person.id, 
                               'age': person.age, 'gender': person.gender, 'timestamp': curr_ts,
                               'engaged': curr_status.engaged, 'usingTablet': curr_status.usingTablet, 
                               'currentTask': curr_status.currentTask})
              curr_ts += DELTA