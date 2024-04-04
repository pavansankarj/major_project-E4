# Checking face recognition for sample images in the folder face_recognition_check_images by using detection model HOG + SVM

import os
import cv2
import face_recognition
import numpy as np

encoded_faces = []
recognized_images = []


names = [1,2,3,4,5]
# img_1 = face_recognition.load_image_file(r"/face_recognition_check_images/1.jpg")
# face_locations_1 = face_recognition.face_locations(img_1)
# face_encodings_1 = face_recognition.face_encodings(img_1,face_locations_1)

for i in os.listdir("face_recognition_check_images"):
    loaded_image = face_recognition.load_image_file("face_recognition_check_images/"+i)
    face_locations = face_recognition.face_locations(loaded_image)
    print(face_locations,i)
    face_encodings = face_recognition.face_encodings(loaded_image, face_locations)[0]
    encoded_faces.append(face_encodings)

print(encoded_faces)
video_capture = cv2.VideoCapture(0)
while True:
    ret, frame = video_capture.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations_in_image = face_recognition.face_locations(rgb_frame)
    # np.argmin
    encoding = face_recognition.face_encodings(rgb_frame,face_locations_in_image)
    print(type(face_locations_in_image))
    print(type(encoding))
    print(encoding)
    print(np.size(encoding))
    print(type(encoded_faces))
    print(type(encoded_faces[0]))

    for (top, right, left, bottom), face_encoding in zip(face_locations_in_image, encoding):
        result = face_recognition.compare_faces(encoded_faces,face_encoding,0.4)
        # if result+1 not in recognized_images:
        #     recognized_images.append(result+1)
        print(result)
        face_distances = face_recognition.face_distance(encoded_faces,face_encoding)
        print(face_distances)
        best_index = np.argmin(face_distances)
        print(face_distances[best_index])
        if face_distances[best_index]<=0.4:
            print(best_index+1)
        else:
            print("Not recognized")
        break
        cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),2)
        # name = str(result.index(True)+1)
        if result[best_index]:
            cv2.putText(frame,str(best_index+1),(left+3,bottom-3),cv2.FONT_HERSHEY_COMPLEX_SMALL,1.5,(0,255,0),2)
        # print(result.index(True)+1)
    cv2.imshow("image",frame)
    if cv2.waitKey(1)== 32:
        print(recognized_images)
        break

