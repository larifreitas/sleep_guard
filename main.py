import cv2
import time
import numpy as np
import mediapipe as mp

cap = cv2.VideoCapture('mulher_piscando.mp4')

mediapipe_solutions = mp.solutions.face_mesh
face_mesh = mediapipe_solutions.FaceMesh(refine_landmarks=True)

left_eye = [362,385,387,263,373,380]
right_eye = [33,160,158,133,153,144]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 416)) # 640, 480
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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