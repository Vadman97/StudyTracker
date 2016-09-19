Study Tracker Website
======================

Description
-----------------
TODO
Deployed on http://vadweb.us:8005


Running server
----------------
Install dependencies
```sudo apt-get install -y python-pip && sudo pip install Flask && sudo pip install flask_sqlalchemy```
```sudo apt-get install -y npm```
```sudo npm install bower -g```
In this directory
```bower install```
```python main.py```


Retrieving experiment data
--------------------
From the root directory of this project
For bash:
```export PYTHONPATH=$PYTHONPATH:$(pwd)```
For fish:
```set -x PYTHONPATH $PYTHONPATH:(pwd)```
```python utils/export_data.py```
CSV files are exported to folder `experimentData`


Notes to self
-----------------
Once the (multiple) users of the website have connected and requirements met based on initialization, poll server every second (sockets instead?) for start of experiment.

Once started, users' interfaces will send updates only when selections on their screens change - server will keep track of what the selections are and when they change based on the server timescale. 

Information is put in a db where it is easy to process the results.

Timer will keep track of experiment (poll/sockets to find out when end?) duration and users' interfaces will move on to notes screen upon end (approximate) but server will refuse changes after its official knowledge of the end of the experiment.