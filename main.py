import cv2
import time
import numpy as np
import mediapipe as mp

# cap = cv2.VideoCapture('mulher_piscando.mp4')
# cap = cv2.VideoCapture('fechando_olhos.mp4')
cap = cv2.VideoCapture(0)

mediapipe_solutions = mp.solutions.face_mesh
face_mesh = mediapipe_solutions.FaceMesh(refine_landmarks=True)

left_eye = [362,385,387,263,373,380]
right_eye = [33,160,158,133,153,144]

START_THRESH = 0.50
CLOSED_TIME_THRESH = 5 # limiar para limite de olhos fechados
first_time_closed = None # tempo em que os olhos começam a se fechar

"""Calculo de EAR com base nos landmarks"""
def calculo_ear(leandmarks, eye_idx):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_idx]
    #horizontal
    A=np.linalg.norm(np.array(p2) - np.array(p6))
    B=np.linalg.norm(np.array(p3) - np.array(p5))
    #vertical
    C=np.linalg.norm(np.array(p1) - np.array(p2))

    ear = (A+B)/(2.0*C)
    return ear

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 416)) # 640, 480
    results = face_mesh.process(frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            height, width, _ = frame.shape

            x1, y1 = 0, 0
            x2, y2 = width, height
            landmarks = []

            for l in face_landmarks.landmark:
                x = int(l.x * width)
                y = int(l.y * height)
                landmarks.append((x, y))

            # calculo de EAR
            left_ear = calculo_ear(landmarks,left_eye)
            right_ear = calculo_ear(landmarks,right_eye)
            avg = (left_ear+right_ear)/2.0
            cv2.putText(frame,f"Valor de EAR: {avg:.2f}",(30,60),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,100),2)

            # verificação pros olhos fechados
            if avg < START_THRESH:
                if first_time_closed is None: # se for 1ª vez que olhos fecham
                    first_time_closed = time.time()
                else:
                    tempo_decorrido = time.time() - first_time_closed
                    if tempo_decorrido > CLOSED_TIME_THRESH:
                        cv2.putText(frame, "Ocorrencia de sonolencia!", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                    
            else:
                tempo_decorrido = None # TODO:: AJUSTE bug

            Xmin = min([landmarks[i][0] for i in range(len(landmarks))])
            Ymin = min([landmarks[i][1] for i in range(len(landmarks))])
            Xmax = max([landmarks[i][0] for i in range(len(landmarks))])
            Ymax = max([landmarks[i][1] for i in range(len(landmarks))])

            # face
            cv2.rectangle(frame, (Xmin, Ymin),(Xmax, Ymax), (100, 20, 200), 2, 2)

            # olhos
            for i in left_eye + right_eye:
                cv2.circle(frame[y1:y2, x1:x2], landmarks[i], 2, (0, 255, 0), -1)

    cv2.imshow('Detecetor de sonolencia', frame)
    if cv2.waitKey(1) & 0xFF == ord('q') == ord(27):
        break

cap.release()
cv2.destroyAllWindows()
