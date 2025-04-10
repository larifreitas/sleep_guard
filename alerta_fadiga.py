import cv2
import time
import numpy as np
from collections import deque

# limiares para piscadas
BLINK_THRESH = 0.45
TIME_WINDOW = 15
BLINK_COUNT_THRESH = 10

# limiares para caso de bocejo
YAWN_THRESH = 0.7
YAWNING_BLINKS = 8
CONTROL_ALERT = 5
FREEZE = 10 

# limiares para caso de queda cabeça
TRESH_NOSE_Y = 400
INTERVAL_FALLS = 1
THRESHOLD_FALLS = 2

# variaveis globais
YAWN_TIMESTAMPS = []
blink_timestamps = []
yawning = False # Indica se há bocejo nomomento
blincking = False # Indica se há piscadas no momento
fadiga_triggered = False # Indica se queda de cabeça foi acionada

# cabeça
queda_timestamps = deque() # Lista que armazena as quedas de cabeça detectadas
fadiga_cabeca_triggered = False # Indica se alerta de queda de cabeça foi acionada
head_falling = False  # Indica se acabeça esta caida no momento

def ear_points(landmarks, eye_idx):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_idx]
    A=np.linalg.norm(np.array(p2) - np.array(p6))
    B=np.linalg.norm(np.array(p3) - np.array(p5))
    C=np.linalg.norm(np.array(p1) - np.array(p2))

    return (A+B)/(2.0*C)

def calcular_mar(landmarks,mouth):
    p1_mouth,p2_mouth,p3_mouth,p4_mouth = [landmarks[i] for i in mouth]
    vertical = np.linalg.norm(np.array(p1_mouth) - np.array(p2_mouth))
    horizontal = np.linalg.norm(np.array(p3_mouth) - np.array(p4_mouth))

    if horizontal == 0:
        return 0
    return vertical/horizontal

def detectar_fadiga_bocejo(blink_timestamps, YAWN_TIMESTAMPS, frame, arduino):
    global fadiga_triggered, CONTROL_ALERT
    if ((len(blink_timestamps) >= BLINK_COUNT_THRESH) or (len(blink_timestamps) >= YAWNING_BLINKS and len(YAWN_TIMESTAMPS) > 0)) and not fadiga_triggered:
        if time.time() - CONTROL_ALERT >= FREEZE:
            cv2.putText(frame, "Fadiga detectada", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,100,255),2)
            arduino.write(b"FADIGA\n")
            print("Ocorrência de fadiga (1 beep)")
            fadiga_triggered = True
            CONTROL_ALERT = time.time()
            blink_timestamps.clear()
            YAWN_TIMESTAMPS.clear()
            fadiga_triggered = False

def detectar_fadiga_piscadas(blink_timestamps, YAWN_TIMESTAMPS, arduino):
    global fadiga_triggered, CONTROL_ALERT
    if len(blink_timestamps) >= BLINK_COUNT_THRESH and len(YAWN_TIMESTAMPS) == 0 and not fadiga_triggered:
        if time.time() - CONTROL_ALERT >= FREEZE:
            arduino.write(b"FADIGA\n")
            print("Ocorrência de fadiga (1 beep)")
            fadiga_triggered = True
            CONTROL_ALERT = time.time()
            blink_timestamps.clear()
            fadiga_triggered = False

def detectar_queda_cabeca(queda_timestamps, arduino):
    global fadiga_cabeca_triggered
    if len(queda_timestamps) >= THRESHOLD_FALLS and not fadiga_cabeca_triggered:
        arduino.write(b'FADIGA_2\n')
        print("Ocorrência de fadiga (2 beeps)")
        fadiga_cabeca_triggered = True
    elif len(queda_timestamps) < THRESHOLD_FALLS:
        fadiga_cabeca_triggered = False

def calcular_ear(landmarks,left_eye,right_eye):
    left_ear = ear_points(landmarks, left_eye)
    right_ear = ear_points(landmarks,right_eye)
    avg_ear =(left_ear + right_ear)/2.0
    return (left_ear+right_ear)/2.0

def update_blinks(avg_ear, blink_timestamps, current_time):
    global blincking
    if avg_ear < BLINK_THRESH:
        if not blincking:
            blincking = True
            blink_timestamps.append(current_time)
    else:
        blincking = False
    return [t for t in blink_timestamps if current_time - t <= TIME_WINDOW]

def update_bocejo(mar, YAWN_TIMESTAMPS, current_time):
    global yawning
    if mar > YAWN_THRESH:
        if not yawning:
            yawning = True
            YAWN_TIMESTAMPS.append(current_time)
    else:
        yawning = False
    return [t for t in YAWN_TIMESTAMPS if current_time - t <= TIME_WINDOW]

def update_queda_cabeca(nariz_y, queda_timestamps, current_time):
    # print("nariz_y:", nariz_y) # debug
    if nariz_y > TRESH_NOSE_Y:
        queda_timestamps.append(time.time())
    while queda_timestamps and (time.time() - queda_timestamps[0] > INTERVAL_FALLS):
        queda_timestamps.popleft()

def verificar_fadiga(frame, landmarks, left_eye, right_eye,mouth, nose, arduino):
    global blink_timestamps, blincking, fadiga_triggered, YAWN_TIMESTAMPS, yawning, CONTROL_ALERT, fadiga_cabeca_triggered
    current_time = time.time()

    #EAR    
    avg_ear = calcular_ear(landmarks, left_eye, right_eye)
    cor = (0, 255, 0) if avg_ear > BLINK_THRESH else (0, 0, 255)
    cv2.putText(frame, f"EAR: {avg_ear:.3f}", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)
    # print(f"EAR médio: {avg_ear:.3f}") # debug
    blink_timestamps = update_blinks(avg_ear, blink_timestamps, current_time)
    blink_timestamps = [t for t in blink_timestamps if  current_time - t <= TIME_WINDOW]
    
    #MAR
    mar = calcular_mar(landmarks,mouth)
    YAWN_TIMESTAMPS = update_bocejo(mar, YAWN_TIMESTAMPS, current_time)
    
    # queda de cabeça
    nariz_y = landmarks[nose[0]][1]
    update_queda_cabeca(nariz_y, queda_timestamps, current_time)

    # verificação de metricas e casos
    detectar_fadiga_bocejo(blink_timestamps, YAWN_TIMESTAMPS, frame, arduino)
    detectar_fadiga_piscadas(blink_timestamps, YAWN_TIMESTAMPS, arduino)
    detectar_queda_cabeca(queda_timestamps, arduino)