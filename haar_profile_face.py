import cv2

haar_xml = cv2.CascadeClassifier(r"C:\Users\DELL\OneDrive\Desktop\Major_project\haar-cascade-files\haarcascade_profileface.xml")

video_capture = cv2.VideoCapture(0)
while True:
    ret, frame = video_capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_locations = haar_xml.detectMultiScale(gray_frame, minNeighbors=5, scaleFactor=1.3)

    for (x,y,w,h) in face_locations:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    cv2.imshow("image",frame)
    if cv2.waitKey(1)==32:
        break