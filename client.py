import socket
import struct
import numpy as np
import cv2 as cv
import argparse
from math import sqrt
from common import *


def read(size, s):
    data = b''
    while len(data) < size:
        data += s.recv(size - len(data))
    return data


def receiveImg(s):
    rows, cols, channels, length = struct.unpack('iiii', read(4*4, s))
    data = read(length, s)
    buf = np.frombuffer(data, dtype=np.uint8)
    img = cv.imdecode(buf, cv.IMREAD_COLOR)
    return img.reshape([rows, cols, channels])


def sendString(data, s):
    s.sendall(struct.pack('ii', TRY_TO_GUESS_CODE, len(data)) + data.encode())


def bgr2gray(img):
    raise Exception('bgr2gray is not implemented')


def gray2bin(img):
    raise Exception('gray2bin is not implemented')


def countPixels(array):
    raise Exception('countPixels is not implemented')


def checkRatios(counts):
    raise Exception('checkRatios is not implemented')


def verifyVertical(bin, x, y):
    counts = [0, 0, 0, 0, 0]

    ymin = y
    while ymin > 0 and bin[ymin, x] == 0:
        counts[2] += 1
        ymin -= 1

    while ymin > 0 and bin[ymin, x] == 255:
        counts[1] += 1
        ymin -= 1

    while ymin > 0 and bin[ymin, x] == 0:
        counts[0] += 1
        ymin -= 1

    ymax = y + 1
    while ymax < bin.shape[0] and bin[ymax, x] == 0:
        counts[2] += 1
        ymax += 1

    while ymax < bin.shape[0] and bin[ymax, x] == 255:
        counts[3] += 1
        ymax += 1

    while ymax < bin.shape[0] and bin[ymax, x] == 0:
        counts[4] += 1
        ymax += 1

    if y == (ymin + ymax) // 2:
        return checkRatios(counts), ymin, ymax
    else:
        return False, ymin, ymax


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, required=True)
    parser.add_argument('--name', type=str, required=True)
    args = parser.parse_args()

    s = socket.socket()
    s.settimeout(60)
    s.connect((args.ip, PORT))  # Connect to board.

    s.sendall(struct.pack('i', len(args.name)) + bytearray(args.name, 'utf8'))

    decoder = cv.QRCodeDetector()

    while cv.waitKey(1) < 0:
        s.send(struct.pack('i', GET_IMAGE_CODE))
        frame = receiveImg(s)

        gray = bgr2gray(frame)
        bin = gray2bin(gray)

        points = []
        for y in range(bin.shape[0]):
            row = bin[y]
            xs, counts = countPixels(row)

            i = 2 if row[0] == 0 else 3
            while i < len(counts) - 3:
                if checkRatios(counts[i - 2 : i + 3]):
                    x = (xs[i - 2] + xs[i + 3]) // 2
                    isMarker, ymin, ymax = verifyVertical(bin, x, y)
                    if isMarker:
                        cv.circle(frame, (x, y), 5, 255, thickness=cv.FILLED)
                        points.append([float(x), float(y)])
                i += 2

        if len(points) == 3:
            leftTop = points[0]
            rightTop = points[1]
            leftBottom = points[2]

            if leftTop[0] > rightTop[0]:
                leftTop, rightTop = rightTop, leftTop

            # Remap markers centers to corners.
            vHorz = [rightTop[0] - leftTop[0], rightTop[1] - leftTop[1]]
            vVert = [leftTop[0] - leftBottom[0], leftTop[1] - leftBottom[1]]
            rightTop = (int(rightTop[0] + 0.23 * vHorz[0] + 0.23 * vVert[0]), int(rightTop[1] + 0.23 * vHorz[1] + 0.23 * vVert[1]))
            leftTop = (int(leftTop[0] - 0.23 * vHorz[0] + 0.23 * vVert[0]), int(leftTop[1] - 0.23 * vHorz[1] + 0.23 * vVert[1]))
            leftBottom = (int(leftBottom[0] - 0.23 * vHorz[0] - 0.23 * vVert[0]), int(leftBottom[1] - 0.23 * vHorz[1] - 0.23 * vVert[1]))

            rightBottom = (int(leftBottom[0] + rightTop[0] - leftTop[0]),
                           int(leftBottom[1] + rightTop[1] - leftTop[1]))

            cv.circle(frame, rightTop, 5, 255, thickness=cv.FILLED)
            cv.circle(frame, leftTop, 5, 255, thickness=cv.FILLED)
            cv.circle(frame, leftBottom, 5, 255, thickness=cv.FILLED)
            cv.circle(frame, rightBottom, 5, 255, thickness=cv.FILLED)

            points = np.array([leftTop, rightTop, rightBottom, leftBottom]).reshape(4, 1, 2)
            data = decoder.decode(bin, points)[0]
            if data:
                print(data)
                sendString(data, s)

        cv.imshow('frame', frame)
