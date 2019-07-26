import socket
import struct
import cv2 as cv
import argparse

import RPi.GPIO as GPIO
import time

from common import *

SERVO_PIN = 3

parser = argparse.ArgumentParser('This is server for ISI-2019 QRCodes practice')
parser.add_argument('--words', nargs='+', type=str, required=True)
args = parser.parse_args()

def sendImg(img, conn):
    if not img is None:
        _, buf = cv.imencode(".jpg", img, [cv.IMWRITE_JPEG_QUALITY, 90])
        rows = img.shape[0]
        cols = img.shape[1]
        channels = img.shape[2]
        conn.sendall(struct.pack('iiii', rows, cols, channels, len(buf)) + buf.tobytes())


def receiveString(conn):
    length = struct.unpack('i', conn.recv(4))[0]
    return conn.recv(length).decode('ascii')


def setAngle(pwm, angle, timeout):
    duty = float(angle) / 18 + 2
    GPIO.output(3, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(timeout)
    GPIO.output(3, False)
    pwm.ChangeDutyCycle(0)


# Setup servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Setup socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(1)

currentAngle = 0
moveCube = False

class Client():
    def __init__(self):
        global currentAngle
        while currentAngle > 20:
            currentAngle -= 5
            setAngle(pwm, angle=currentAngle, timeout=0.1)
        self.conn, self.addr = s.accept()
        self.conn.settimeout(60)  # 1 minute
        self.wordId = 0
        self.startTime = time.time()

    def getCode(self):
        try:
            return struct.unpack('i', self.conn.recv(4))[0]
        except Exception as e:
            self.conn.close()
            return CLOSE_CONNECTION

print(args.words)

while True:
    print('Waiting for client...')
    moveCube = False
    client = Client()
    currentAngle = 20
    clientName = receiveString(client.conn)
    print('New client: %s:%s (%s)' % (client.addr[0], client.addr[1], clientName))

    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        if time.time() - client.startTime > 60:
            client.conn.close()
            break

        if moveCube:
            currentAngle += 5
            setAngle(pwm, currentAngle, 0.1)
            if client.wordId == 1 and currentAngle >= 100:
                moveCube = False
            if client.wordId == 2 and currentAngle >= 190:
                moveCube = False

        code = client.getCode()
        if code == GET_IMAGE_CODE:
            _, frame = cap.read()
            sendImg(frame, client.conn)
        elif code == TRY_TO_GUESS_CODE:
            data = receiveString(client.conn)
            print(data)
            if data == args.words[client.wordId] and client.wordId < 2:
                client.wordId += 1
                moveCube = True
        elif CLOSE_CONNECTION:
            break
        else:
            print('Unexpected code: %d' % code)
            exit(0)
    cap.release()
    print('')
