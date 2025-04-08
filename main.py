import cv2
import time
import serial
import mediapipe as mp

from alerta_sonolencia import verificar_sonolencia
from alerta_fadiga import verificar_fadiga

USE_ARDUINO = True

if USE_ARDUINO == True:
    arduino = serial.Serial('/dev/ttyUSB0',9600,timeout=1)
    time.sleep(3)
    arduino.flushInput()
else: 
    class FakeArduino:
        def write(self,msg):
            print("Modo de simulação com arduino. Mensagem recebida de arduino: :", msg.decode().strip())
        def flush(self): pass
    arduino=FakeArduino()


def draw_points(frame,landmarks, left_eye, right_eye, mouth,nose, Xmin,Ymin, Xmax,Ymax):
    for i in left_eye + right_eye + mouth + nose:
        cv2.circle(frame,landmarks[i],4,(0,255,0), -1)
        cv2.rectangle(frame, (Xmin, Ymin),(Xmax, Ymax), (100, 20, 200), 2, 2)
    
cap = cv2.VideoCapture(0)

mediapipe_solutions = mp.solutions.face_mesh
face_mesh = mediapipe_solutions.FaceMesh(refine_landmarks=True)

# landmarks
left_eye = [362,385,387,263,373,380]
right_eye = [33,160,158,133,153,144]
mouth = [13,14,78,308]
nose = [1]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1024, 728))
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

            draw_points(frame, landmarks, left_eye, right_eye, mouth,nose ,Xmin, Ymin, Xmax, Ymax)

            verificar_fadiga(frame,landmarks, left_eye, right_eye,mouth,nose, arduino)
            verificar_sonolencia(frame,landmarks, left_eye, right_eye, arduino, USE_ARDUINO)


    cv2.imshow('Detecetor de fadiga', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break


cap.release()
cv2.destroyAllWindows()
