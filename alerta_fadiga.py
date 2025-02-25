import cv2
import time
import numpy as np

BLINK_COUNT = 0
TIME_WINDOW = 10 # janela de tempo pra considerar as piscadas frequentes
blincking = False
BLINK_THRESH = 0.50
BLINK_TIMESTAMPS = []
BLINK_COUNT_THRESH = 15
fadiga_triggered = False 

def calculo_ear_fadiga(landmarks, eye_idx):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_idx]
    A=np.linalg.norm(np.array(p2) - np.array(p6))
    B=np.linalg.norm(np.array(p3) - np.array(p5))
    C=np.linalg.norm(np.array(p1) - np.array(p2))

    return (A+B)/(2.0*C)

def verificar_fadiga(frame, landmarks, left_eye, right_eye,arduino):
    global BLINK_TIMESTAMPS, blincking,fadiga_triggered

    left_ear = calculo_ear_fadiga(landmarks, left_eye)
    right_ear = calculo_ear_fadiga(landmarks,right_eye)
    avg_ear =(left_ear + right_ear)/2.0
    if avg_ear < BLINK_THRESH:
        if not blincking:
            blincking = True
            BLINK_TIMESTAMPS.append(time.time())
    else:
        blincking = False

    current_time = time.time()
    BLINK_TIMESTAMPS = [t for t in BLINK_TIMESTAMPS if  current_time - t < TIME_WINDOW] # DE ACORDO COM A JANELA DE TEMPO limpar piscadas que não estão dentro desta janela de tempo

    cv2.putText(frame,f"Piscadas:({TIME_WINDOW}s): {len(BLINK_TIMESTAMPS)}", (15,40), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,100),2)  #sóarumar aqui  
    
    if len(BLINK_TIMESTAMPS) >= BLINK_COUNT_THRESH and not fadiga_triggered:
        cv2.putText(frame, "Fadiga detectada", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,100,255),2)
        arduino.write(b"FADIGA\n")
        fadiga_triggered = True

    if len(BLINK_TIMESTAMPS) < BLINK_COUNT_THRESH:
        fadiga_triggered=False
