from flask import Flask, render_template
from flask_socketio import SocketIO,send,emit
import pika
from threading import Lock
import ast
from gevent import monkey


tv=True #TV HDMI üzerinden kontrol edilebiliyorsa True olmalı

if tv:
   import cec
   cec.init()
   tv=cec.Device(0)


monkey.patch_all(thread=False) #, socket=False)
async_mode = None
app = Flask(__name__,template_folder='templates')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app) #, async_mode=async_mode)
thread = None
thread_lock = Lock()
issues=0


@app.route("/")


def index():
    return render_template('index.html') #,async_mode=socketio.async_mode)


@socketio.on('connect')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=startPika)

@socketio.on('my event')
def handle_my_custom_event(data):
    emit('new_issue', data)

def startPika():#Pika
    socketio.sleep(0)
    credentials = pika.PlainCredentials('raspberry', 'test1')
    connection = pika.BlockingConnection(pika.ConnectionParameters('10.10.0.10',5672,'/',credentials))
    channel = connection.channel()
    channel.queue_declare(queue='KALIPBAKIM',durable= True)

    channel.basic_consume(queue='KALIPBAKIM', on_message_callback=callback, auto_ack=True)
    print('Starting')
    channel.start_consuming()
    print('Startted')

def issuestart(data):
        global issues
        socketio.emit('new_issue',data)
        issues+=1
        if tv:
            tv.power_on()

def issuetimer(data):
    socketio.emit('timer',data)

def issuefinish(data):
    global issues
    socketio.emit('finish',data)
    issues+=-1
    if issues<=0:
        if tv:
            tv.standby()


def callback(ch, method, properties, body):
    #if tv:
       # tv.power_on()
        #os.popen("echo 'on 0.0.0.0' | cec-client -s -d 1")
    data=ast.literal_eval(body.decode('utf-8'))
    print('d:',data)


##    #msg=str(data['client'])
    if data['type']=='device_fault_start':
       issuestart(data)
    elif data['type']=='employee_fault_start':
        issuetimer(data)
    elif data['type']=='device_fault_finish':
       issuefinish(data)
    else:
        socketio.send(data)
        #if tv and issues==0:
        if tv:
            tv.standby()
                #sleep(5)
                #os.popen("echo 'standby 0.0.0.0' | cec-client -s -d 1")


def my_background():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=startPika)
    print('Background thread started')
    #os.popen("xset s off s npblank s noexpose")
    #os.popen("chromium --start-fullscreen --noerrdialogs --diasble-infobars --kiosk http://localhost:5000")
my_background()
if __name__ == '__main__':
   # os.popen("chormium http://localhost:5000")
    socketio.run(app)
def issuestart(data):
        global issues
        socketio.emit('new_issue',data)
        issues+=1
        if tv:
            tv.power_on()

def issuetimer(data):
    socketio.emit('timer',data)

def issuefinish(data):
    global issues
    socketio.emit('finish',data)
    issues+=-1
    if issues<=0:
        if tv:
            tv.standby()