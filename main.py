import cv2
import numpy as np
import mediapipe as mp

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"Usando : {device}")
# model = YOLO('best.pt')
# model.to(device)

cap = cv2.VideoCapture('mulher_piscando.mp4')

mediapipe_solutions = mp.solutions.face_mesh
face_mesh = mediapipe_solutions.FaceMesh(refine_landmarks=True)

left_eye = [362,385,387,263,373,380]
right_eye = [33,160,158,133,153,144]


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    resized_frame = cv2.resize(frame, (640, 416)) # 640, 480
    face_frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(face_frame_rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            height, width, _ = frame.shape
            landmarks = []

            for l in face_landmarks.landmark:
                x = int(l.x * width)
                y = int(l.y * height)
                landmarks.append((x, y))

    cv2.imshow('output', resized_frame)
    if cv2.waitKey(1) & 0xFF == ord('q') == ord(27):
        break

cap.release()
cv2.destroyAllWindows()