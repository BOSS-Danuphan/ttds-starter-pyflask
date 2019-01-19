import os
from config import Config
from flask import Flask, render_template, redirect, jsonify
from models import db, Profile

from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS', 'config.ProductionConfig'))

app.app_context().push()
db.init_app(app)

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
#        Web Socket       #
###########################
connectionCounter = 0
socketio = SocketIO(app, async_mode='eventlet')

class Worker(object):

    switch = False
    unit_of_work = 0

    def __init__(self, socketio):
        self.socketio = socketio

    def do_work(self):
        while self.switch:
            self.unit_of_work += 1
            self.socketio.emit("feed", {"data": self.unit_of_work})
            eventlet.sleep(3)

    def stop(self):
        self.switch = False

    def start(self):
        self.switch = True

global worker
worker = Worker(socketio)

@socketio.on('connect')
def wsioconnect():
    print('connected')
    emit('message', {'data': 'Connected'})
    emit('message', {'data': 'Connected by new client'}, broadcast=True, include_self=False)

    global connectionCounter, worker
    connectionCounter += 1
    if worker.switch == False:
        print('start background')
        worker.start()
        socketio.start_background_task(target=worker.do_work)
@socketio.on('disconnect')
def wsiodisconnect():
    print('disconnected')
    emit('message', {'data': 'Client disconnected'}, broadcast=True, include_self=False)

    global connectionCounter
    connectionCounter -= 1
    if connectionCounter == 0 and worker.switch == True:
        worker.stop()
@socketio.on('broadcast')
def wsiobroadcast(data):
    emit('message', {'data': data})

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

    if os.path.exists(indexpath):
        with open('scheduler-log.txt', 'r') as f:
            mytext = f.read()
    return render_template('article.html', content= mytext or 'No running task !!')

if __name__ == '__main__':
    # app.run(debug = True) # Without socketio
    socketio.run(app, port=5000)
