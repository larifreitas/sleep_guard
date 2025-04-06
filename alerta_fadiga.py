import cv2
import time
import numpy as np
from collections import deque

# TODO:documentar
# TODO: implementação de queda de cabeça
# 10 piscadas no limiar de 15 segundos

# conts para piscadas
BLINK_THRESH = 0.45 # threshold de olho fechado (limiares testados 25, 38 e 45)
TIME_WINDOW = 15 # janela de tempo pra considerar as piscadas frequentes
BLINK_COUNT_THRESH = 10 # numero de piscadas considerado fadiga (de acordo também com limiar da janela de tempo)

# consts para bocejo
YAWN_THRESH = 0.7 # threshOLD para o bocejo
YAWNING_BLINKS = 8 # piscada com bocejo
CONTROL_ALERT =0 # controle de alertapara não ser acionado próximo do tempo em que já foi acionado
FREEZE = 30 # "congelar" o acionamento do alarme para não acionar beeps consecultivos logo após o acionamento de alerme

# consts para cabeça
TRESH_NOSE_Y = 400 # posição y (vertical do nariz)
INSTERVAL_FALLS = 1 # INTERVALO ENTRE CADA QUEDA DE CABEÇA
THRESHOLD_FALLS = 2 # QUANTAS QUEDAS DE CABEÇA por intervalo

# variaveis globais
YAWN_TIMESTAMPS = []
blincking = False
yawning = False
blink_timestamps = []
fadiga_triggered = False 

# cabeça
queda_timestamps = deque()
fadiga_cabeca_triggered = False

def calculo_ear(landmarks, eye_idx):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_idx]
    A=np.linalg.norm(np.array(p2) - np.array(p6))
    B=np.linalg.norm(np.array(p3) - np.array(p5))
    C=np.linalg.norm(np.array(p1) - np.array(p2))

    return (A+B)/(2.0*C)

def calculo_mar(landmarks,mouth):
    p1_mouth,p2_mouth,p3_mouth,p4_mouth = [landmarks[i] for i in mouth]
    vertical = np.linalg.norm(np.array(p1_mouth) - np.array(p2_mouth))
    horizontal = np.linalg.norm(np.array(p3_mouth) - np.array(p4_mouth))

    if horizontal == 0:
        return 0
    return vertical/horizontal

def verificar_fadiga(frame, landmarks, left_eye, right_eye,mouth, nose, arduino):
    global blink_timestamps, blincking, fadiga_triggered, YAWN_TIMESTAMPS, yawning, CONTROL_ALERT, fadiga_cabeca_triggered
    
    ##########################################################################
    #:::analise com ear para piscadas
    left_ear = calculo_ear(landmarks, left_eye)
    right_ear = calculo_ear(landmarks,right_eye)
    avg_ear =(left_ear + right_ear)/2.0

    # debug
    # cor = (0, 255, 0) if avg_ear > BLINK_THRESH else (0, 0, 255)
    # cv2.putText(frame, f"EAR: {avg_ear:.3f}", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)
    # print(f"EAR médio: {avg_ear:.3f}")
    ###

    if avg_ear < BLINK_THRESH:
        if not blincking:
            blincking = True
            blink_timestamps.append(time.time())
    else:
        blincking = False

    current_time = time.time()
    blink_timestamps = [t for t in blink_timestamps if  current_time - t <= TIME_WINDOW] # limpar piscadas que nao estao dentro da janela de tempo
    
    #::: analise com mar para bocejo
    mar = calculo_mar(landmarks,mouth)
    # print("Valor MAR: ", mar)
    if mar > YAWN_THRESH:
        if not yawning:
            yawning = True
            YAWN_TIMESTAMPS.append(time.time())
    else:
        yawning = False

    YAWN_TIMESTAMPS = [t for t in YAWN_TIMESTAMPS if  current_time - t <= TIME_WINDOW] # limpar yawns antigos de fora da janela de tempo assim como no bocejo

    #:::analise para cabeça caindo
    nariz_y = landmarks[nose[0]][1]

    if nariz_y > TRESH_NOSE_Y:
        queda_timestamps.append(time.time())
    while queda_timestamps and (time.time() - queda_timestamps[0] > INSTERVAL_FALLS):
        queda_timestamps.popleft()
    
    #########################################################################

    # acionaemento de alarme para 10 piscadas
    if (len(blink_timestamps)>=BLINK_COUNT_THRESH and len(YAWN_TIMESTAMPS) == 0) and not fadiga_cabeca_triggered:
        if time.time() - CONTROL_ALERT >= FREEZE:
            arduino.write(b'FADIGA\n')
            fadiga_triggered = True
            CONTROL_ALERT  = time.time()
            blink_timestamps.clear()

    # acionamento de alarme para combinação de 8 piscadas com bocejo
    if ((len(blink_timestamps) >= BLINK_COUNT_THRESH) or (len(blink_timestamps) >= YAWNING_BLINKS and len(YAWN_TIMESTAMPS) > 0)) and not fadiga_triggered:
        if time.time() - CONTROL_ALERT >= FREEZE:
            cv2.putText(frame, "Fadiga detectada", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,100,255),2)
            arduino.write(b"FADIGA\n")
            fadiga_triggered = True
            CONTROL_ALERT = time.time()
            blink_timestamps.clear()
            YAWN_TIMESTAMPS.clear()

    if len(blink_timestamps) < BLINK_COUNT_THRESH and len(YAWN_TIMESTAMPS) == 0:
        fadiga_triggered=False


    # acionamento para queda de cabeça
    #print(f"[DEBUG] Quedas recentes: {len(queda_timestamps)}")

    if len(queda_timestamps) >= THRESHOLD_FALLS and not fadiga_cabeca_triggered:
        if arduino:
            arduino.write(b'FADIGA_2\n')
        fadiga_cabeca_triggered = True
    elif len(queda_timestamps) <THRESHOLD_FALLS:
        fadiga_cabeca_triggered = False