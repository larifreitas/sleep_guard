import cv2
import time
import numpy as np

# TODO:documentar
# TODO: implementação de queda de cabeça

# conts para fadiga
BLINK_THRESH = 0.50 # threshold de olho fechado
TIME_WINDOW = 10 # janela de tempo pra considerar as piscadas frequentes
BLINK_COUNT_THRESH = 15 # numero de piscadas considerado fadiga (de acordo também com limiar da janela de tempo)

# consts para bocejo
YAWN_THRESH = 0.7 # threshOLD para o bocejo
YAWNING_BLINKS = 10
CONTROL_ALERT =0 # controle de alertapara não ser acionado próximo do tempo em que já foi acionado
FREEZE = 30 # "congelar" o acionamento do alarme para não acionar beeps consecultivos logo após o acionamento de alerme

# variaveis globais
YAWN_TIMESTAMPS = []
blincking = False
yawning = False
blink_timestamps = []
fadiga_triggered = False 



def calculo_ear(landmarks, eye_idx):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_idx]
    A=np.linalg.norm(np.array(p2) - np.array(p6))
    B=np.linalg.norm(np.array(p3) - np.array(p5))
    C=np.linalg.norm(np.array(p1) - np.array(p2))

    return (A+B)/(2.0*C)

# TODO: Mouth Aspect Ratio, detecção de bocejo analisar o aumento de MAR
def calculo_mar(landmarks,mouth):
    p1_mouth,p2_mouth,p3_mouth,p4_mouth = [landmarks[i] for i in mouth]
    vertical = np.linalg.norm(np.array(p1_mouth) - np.array(p2_mouth))
    horizontal = np.linalg.norm(np.array(p3_mouth) - np.array(p4_mouth))

    if horizontal == 0:
        return 0
    return vertical/horizontal

def verificar_fadiga(frame, landmarks, left_eye, right_eye,mouth):
    global blink_timestamps, blincking,fadiga_triggered,YAWN_TIMESTAMPS, yawning, CONTROL_ALERT

    #:::analise com ear para piscadas
    left_ear = calculo_ear(landmarks, left_eye)
    right_ear = calculo_ear(landmarks,right_eye)
    avg_ear =(left_ear + right_ear)/2.0
    if avg_ear < BLINK_THRESH:
        if not blincking:
            blincking = True
            blink_timestamps.append(time.time())
    else:
        blincking = False

    current_time = time.time()
    blink_timestamps = [t for t in blink_timestamps if  current_time - t <= TIME_WINDOW] # limpar piscadas que nao estao dentro da janela de tempo

    cv2.putText(frame,f"Piscadas:({TIME_WINDOW}s): {len(blink_timestamps)}", (15,40), cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,100),2)  
    
    #::: analise com mar para bocejo
    mar = calculo_mar(landmarks,mouth)
    print("Valor MAR: ", mar)
    if mar > YAWN_THRESH:
        if not yawning:
            yawning = True
            YAWN_TIMESTAMPS.append(time.time())
    else:
        yawning = False
    YAWN_TIMESTAMPS = [t for t in YAWN_TIMESTAMPS if  current_time - t <= TIME_WINDOW] # limpar yawns antigos de fora da janela de tempo assim como no bocejo

    # acionamento de alarme para piscadas e combinação de piscadas com bocejo
    if ((len(blink_timestamps) >= BLINK_COUNT_THRESH) or (len(blink_timestamps) >= YAWNING_BLINKS and len(YAWN_TIMESTAMPS) > 0)) and not fadiga_triggered:
        if time.time() - CONTROL_ALERT >= FREEZE:
            cv2.putText(frame, "Fadiga detectada", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,100,255),2)
            # arduino.write(b"FADIGA\n")
            fadiga_triggered = True
            CONTROL_ALERT = time.time()

    if len(blink_timestamps) < BLINK_COUNT_THRESH:
        fadiga_triggered=False
