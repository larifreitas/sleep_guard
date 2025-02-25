import cv2
import numpy as np
import time

# left_eye = [362,385,387,263,373,380]
# right_eye = [33,160,158,133,153,144]

START_THRESH = 0.50
CLOSED_TIME_THRESH = 5 # limiar para limite de olhos fechados
first_time_closed = None # tempo em que os olhos começam a se fechar
sonolencia_triggered = False  # flag para saber se o alarme já foi disparado

def calculo_ear_sonolencia(landmarks, eye_idx):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_idx]
    #horizontal
    A=np.linalg.norm(np.array(p2) - np.array(p6))
    B=np.linalg.norm(np.array(p3) - np.array(p5))
    #vertical
    C=np.linalg.norm(np.array(p1) - np.array(p2)) # ponto 4- bug

    ear = (A+B)/(2.0*C)
    return ear

def verificar_sonolencia(frame, landmarks, left_eye, right_eye, arduino):
    global first_time_closed, sonolencia_triggered

    left_ear = calculo_ear_sonolencia(landmarks,left_eye)
    right_ear = calculo_ear_sonolencia(landmarks,right_eye)
    avg = (left_ear+right_ear)/2.0
    print(f"Valor de EAR: {avg:.2f}")

    # verificação pros olhos fechados
    if avg < START_THRESH:
        if first_time_closed is None: # se for 1ª vez que olhos fecham
            first_time_closed = time.time()
            sonolencia_triggered = False
        else:
            if time.time() - first_time_closed >= CLOSED_TIME_THRESH:
                cv2.putText(frame, "Ocorrencia de sonolencia!", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                arduino.write(b"SONOLENCIA\n")
                sonolencia_triggered = True
            
    else:
        first_time_closed = None
        sonolencia_triggered = False