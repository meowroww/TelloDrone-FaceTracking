# Packages
import cv2 as cv
import numpy as np
from djitellopy import tello
import time

# Create Tello object
drone = tello.Tello()
drone.connect()

# Check battery
print(drone.get_battery())

drone.streamon()
drone.takeoff()
# 25 beacuse it landed lower level than average height, so make it little bit higher
drone.send_rc_control(0, 0, 25, 0)
time.sleep(2.2)

# width and height
w, h = 260, 240
# Create a range
fbRange = [6200, 6800]

pid = [0.4, 0.4, 0]
pError = 0


def findFace(img):
    faceCascade = cv.CascadeClassifier(
        'Project 3 - Face Tracking\haarcascades\haarcascade_frontalface_default.xml')
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)


# List of all the faces
    myFaceListC = []  # have the information of the cnter point of the face
    myFaceListArea = []  # have the area value

    for (x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        # create center x
        cx = x + w//2
        # create center y
        cy = y + h//2
        area = w*h
        # create point heading so it print the center
        cv.circle(img, (cx, cy), 5, (0, 255, 0), cv.FILLED)
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)

    # to check if myFaceListArea empty or filled
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]


def trackFace(drone, info, w, pid, pError):

    area = info[1]
    x, y = info[0]
    fb = 0

    # to find out how far away our object from the center
    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error-pError)
    speed = int(np.clip(speed, -100, 100))

    # to stay stationary (green zone, the drone won't move)
    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    # if too close, then move backward
    elif area > fbRange[1]:
        fb = -20
    # if too far, then move forward
    elif area < fbRange[0] and area != 0:
        fb = 20

    # print out the value of speed and forward-backward (fb)
    # print(speed, fb)

    # if it doesn't get anything, then it has to stop
    if x == 0:
        speed = 0
        error = 0

    drone.send_rc_control(0, fb, 0, speed)
    return error


# Webcam camera
# cap = cv.VideoCapture(0)

while True:
    # _, img = cap.read()
    img = drone.get_frame_read().frame
    img = cv. resize(img, (w, h))
    img, info = findFace(img)
    pError = trackFace(drone, info, w, pid, pError)
    # print('center', info[0], 'Area', info[1])
    cv.imshow('Output', img)
    if cv.waitKey(1) & 0xFF == ord('q'):
        drone.land()
        break
