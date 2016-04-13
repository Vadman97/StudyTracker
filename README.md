Study Tracker Website
======================

Description
-----------------
TODO


Notes to self
-----------------
Work on frontend first (design template using bootstrap based on pictures from Eric of how it should look)

Once the (multiple) users of the website have connected and requirements met based on initialization, poll server every second (sockets instead?) for start of experiment.

Once started, users' interfaces will send updates only when selections on their screens change - server will keep track of what the selections are and when they change based on the server timescale. 

Information is put in a db where it is easy to process the results.

Timer will keep track of experiment (poll/sockets to find out when end?) duration and users' interfaces will move on to notes screen upon end (approximate) but server will refuse changes after its official knowledge of the end of the experiment.

Write HTML files first and then worry about converting them to templates with inheritance: http://flask.pocoo.org/docs/0.10/patterns/templateinheritance/

Running server
----------------
```python main.py```

Note: Flask must be installed - ```sudo apt-get install -y python-pip && sudo pip install Flask && sudo pip install flask_sqlalchemy```