import cv2
import numpy as np

BLINK_THRESH = 0.50
BLINK_COUNT_THRESH = 10
BLINK_COUNT = 0
blincking = False

def calculo_ear_fadiga(landmarks, eye_idx):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_idx]
    A=np.linalg.norm(np.array(p2) - np.array(p6))
    B=np.linalg.norm(np.array(p3) - np.array(p5))
    C=np.linalg.norm(np.array(p1) - np.array(p2))

    return (A+B)/(2.0*C)

def verificar_fadiga(frame, landmarks, left_eye, right_eye):
    global BLINK_COUNT

    left_ear = calculo_ear_fadiga(landmarks, left_eye)
    right_ear = calculo_ear_fadiga(landmarks,right_eye)
    avg_ear =(left_ear + right_ear)/2.0
    if avg_ear < BLINK_THRESH:
        BLINK_COUNT += 0.5
        blincking = True
    else:
        blincking = False

    if BLINK_COUNT >= BLINK_COUNT_THRESH:
        cv2.putText(frame, "Fadiga detectada", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,100,255),2)
        BLINK_COUNT=0 # reset
    cv2.putText(frame,f"contagem de pescadas:{BLINK_COUNT}", (15,40), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,100),2)
