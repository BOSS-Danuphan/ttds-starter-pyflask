import eventlet
eventlet.monkey_patch()
import os
from config import Config
from flask import Flask, render_template, redirect, jsonify
from models import db, Profile

from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS', 'config.ProductionConfig'))

app.app_context().push()
db.init_app(app)
socketio = SocketIO(app, async_mode='eventlet')

indexpath = 'myindex.txt'
def loadsearchindex():
    mytext = None

    if not os.path.exists(indexpath):
        return ''

    with open(indexpath, 'r') as f:
        mytext = f.read()
    return mytext
globvar = loadsearchindex()

###########################
#         Twitter         #
###########################
from threading import Thread
from tweepy import StreamListener, Stream
import tweepy
import json

thread = None
auth = tweepy.OAuthHandler(app.config.get('TWEEPY_CONSUMER_KEY'), app.config.get('TWEEPY_CONSUMER_SECRET'))
auth.set_access_token(app.config.get('TWEEPY_ACCESS_TOKEN_KEY'), app.config.get('TWEEPY_ACCESS_TOKEN_SECRET'))

def do_whatever_processing_you_want(text):
    return text.startswith("RT "), text

class StdOutListener(StreamListener):
    def __init__(self):
        pass

    def on_data(self, data):
        print(data)
        try:
            tweet = json.loads(data)
            flag, text = do_whatever_processing_you_want(tweet['text'])
            if flag:
                socketio.emit('stream_channel',
                        {'data': text, 'id': tweet['id']},
                        namespace='/demo_streaming')
            print(text)
        except Exception as e:
            print('Failed: '+ str(e))

    def on_error(self, status):
        print('Error status code', status)
        exit()

def background_thread():
    """Example of how to send server generated events to clients."""
    stream = Stream(auth, l)
    _keywords = [':-)', ':-(']
    print('mythread')
    stream.sample()

###########################
#        Web Socket       #
###########################
# connectionCounter = 0
# @socketio.on('connect')
# def wsioconnect():
#     print('connected')
#     socketio.emit('message', {'data': 'Connected'})
#     socketio.sleep(1)
#     emit('message', {'data': 'Connected by new client'}, broadcast=True, include_self=False)
#     socketio.sleep(10)
#     emit('message', {'data': 'Connected again !!'})

#     global connectionCounter, worker
#     connectionCounter += 1
#     if worker.switch == False:
#         print('start background')
#         worker.start()
#         socketio.start_background_task(target=worker.do_work)
# @socketio.on('disconnect')
# def wsiodisconnect():
#     print('disconnected')
#     emit('message', {'data': 'Client disconnected'}, broadcast=True, include_self=False)

#     global connectionCounter
#     connectionCounter -= 1
#     if connectionCounter == 0 and worker.switch == True:
#         worker.stop()
# @socketio.on('broadcast')
# def wsiobroadcast(data):
#     emit('message', {'data': data})

###########################
#        Web Route        #
###########################
@app.route('/')
def hello_world():
    return render_template('article.html', content='Hello, World!')

@app.route('/readfile')
def readfile():
    mytext = loadsearchindex()
    return render_template('article.html', content=mytext)

@app.route('/appendfile')
def appendfile():
    with open(indexpath, 'a+') as f:
        currentdata = loadsearchindex()
        if currentdata == '':
            f.write("1: start new text!!")
        else:
            linenumber = len(currentdata.split('\n'))+1
            f.write(f"\n{linenumber}: my new text!!")
    return jsonify({'status': 'ok'})

@app.route('/deletefile')
def deletefile():
    if os.path.exists(indexpath):
       os.remove(indexpath)
       return jsonify({'status': 'ok'})
    return jsonify({'status': 'fail'})

@app.route('/globvar')
def displayglobvar():
    global globvar
    return render_template('article.html', content=globvar)

@app.route('/globvar/reload')
def reloadglobvar():
    global globvar
    globvar = loadsearchindex()
    return jsonify({'status': 'ok'})

@app.route('/websocket')
def websocket():
    return render_template('websocket.html')

@app.route('/tweetstream')
def tweetstream():
    global thread
    print(thread)
    if thread is None:
        print('start mythread')
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('tweetstream.html')

@app.route('/readdbprofile')
def readdbprofile():
    profile = Profile.query.first()
    return render_template('article.html', content=f"{profile}")

@app.route('/updatedbprofile')
def updatedbprofile():
    from random import randint
    profile = Profile.query.get(1)
    profile.name = 'default' + str(randint(0, 9))
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/schedulerlog')
def schedulerlog():
    mytext = None
    logfile = 'schedulerlog.txt'

    if os.path.exists(logfile):
        with open(logfile, 'r') as f:
            mytext = f.read()
    return render_template('article.html', content=mytext or 'No running task !!')

l = StdOutListener()

if __name__ == '__main__':
    # app.run(debug = True) # Without socketio
    socketio.run(app, port=5000)
