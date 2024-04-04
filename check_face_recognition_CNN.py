# Checking face recognition for sample images in the folder face_recognition_check_images by using detection model MMOD CNN

import os, dlib
import cv2
import face_recognition
import numpy as np

encoded_faces = []
names = [1,2,3,4,5]
cnn_detector = dlib.cnn_face_detection_model_v1(r"C:\Users\mahes\Desktop\pavansankar\Major project\major_project\Lib\site-packages\face_recognition_models\models\mmod_human_face_detector.dat")

for i in os.listdir("face_recognition_check_images"):
    loaded_image = face_recognition.load_image_file("face_recognition_check_images/"+i)
    print(loaded_image)
    # gray_frame = cv2.cvtColor(loaded_image, cv2.COLOR_BGR2GRAY)
    # face_locations_in_image = cnn_detector(gray_frame, 1)
    face_locations = cnn_detector(loaded_image)[0]
    print(face_locations)
    print(type(face_locations))
    print(face_locations.rect)
    x =face_locations.rect.left()
    y = face_locations.rect.top()
    X = face_locations.rect.right()
    Y = face_locations.rect.bottom()
    print(x,y,X,Y)
    break
    # for r in face_locations:
    #     print(r.rect)
    # face_encodings = face_recognition.face_encodings(loaded_image, face_locations)
    # encoded_faces.append(face_encodings)
print(encoded_faces)
video_capture = cv2.VideoCapture(0)
while True:
    ret, frame = video_capture.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_locations_in_image_1 = cnn_detector(gray_frame,1)
    if cnn_detector(gray_frame,1)[0]:
        face_locations_in_image_2 = cnn_detector(gray_frame,1)[0]
    for r in face_locations_in_image_1:
        print(r.rect)

    # np.argmin

    print(face_locations_in_image_1)
    print(face_locations_in_image_2.rect)
    # print(face_locations_in_image.rect)

    encoding = face_recognition.face_encodings(rgb_frame,face_locations_in_image_1[0].rect)
    encoding_2 = face_recognition.face_encodings(rgb_frame, face_locations_in_image_2.rect)
    print(type(face_locations_in_image_1))
    print(type(encoding))
    print(encoding)
    print(np.size(encoding))
    print(type(encoded_faces))
    print(type(encoded_faces[0]))
    for face_locations, face_encoding in zip(face_locations_in_image, encoding):
        x = face_locations.rect.left()
        y = face_locations.rect.top()
        X = face_locations.rect.right()
        Y = face_locations.rect.bottom()
        result = face_recognition.compare_faces(encoded_faces,face_encoding,0.4)
        face_distances = face_recognition.face_distance(encoded_faces,face_encoding)
        best_index = np.argmin(face_distances)
        cv2.rectangle(frame,(x,y),(X,Y),(0,255,0),2)
        # name = str(result.index(True)+1)
        if result[best_index]:
            cv2.putText(frame,str(best_index),(x+3,Y-3),cv2.FONT_HERSHEY_COMPLEX_SMALL,1.5, (0,244,0), 2)
        # print(result.index(True)+1)
    cv2.imshow("image",frame)
    if cv2.waitKey(1)== 32:
        break

