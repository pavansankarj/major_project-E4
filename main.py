from flask import Flask, render_template, flash, Response, request

import os

import tkinter

import urllib

import json

from selenium import webdriver

import cv2

from pymongo import MongoClient

import face_recognition

from base64 import urlsafe_b64encode

from tkinter import messagebox

import sys

import numpy as np

import base64

from random import randint

#for mailing
from smtplib import SMTP
from email.message import EmailMessage

#To generate key and perform password encryption and decryption
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


#generating key for encryption and decryption
key_generate_passphrase = "mini_project@143"
kdf = PBKDF2HMAC(length=32, salt='2018_batch'.encode(), algorithm=SHA256, iterations=100000, backend=default_backend())
key = kdf.derive(key_generate_passphrase.encode())
key = urlsafe_b64encode(key).decode()
fernet = Fernet(key)

video_capture_object = cv2.VideoCapture(0)

frame_1 = None

# global variables
encodings_n18 = []  # encodings of the persons stored in this list
count_of_documents = 0  # to count total no. of documents in the collection
Order_of_IDs_inserted = []  # Insertion order of IDs in the collection

app = Flask(__name__)
app.config['SECRET_KEY'] ="major_project"   # secret key set to use flash messages

@app.route("/registered")
@app.route("/signed_in")
@app.route("/updated_details")
@app.route("/updated_images")

@app.route("/")
def home():
    print(request.path.split("/"))
    message = request.path.split("/")[-1]
    if message == "signed_in":
        flash("Signed in successfully")
    elif message == "registered":
        flash("Registered successfully")
    elif message == "updated_details":
        flash("Updated name and password successfully")
    elif message == "updated_images":
        flash("Updated images successfully")
    else:
        flash("Welcome Home")
    return render_template("index.html")

@app.route("/front/update")
@app.route("/front")    # If i call the route by url_for('front')(endpoint) it will be directed to last defined url, i.e., /front
def front():
    return render_template("front_face.html", current_page=(request.path.split('/',1)[-1]).replace("/","_"))

@app.route("/left/update")
@app.route("/left")
def left():
    return render_template("left_face.html", current_page=(request.path.split('/',1)[-1]).replace("/","_"))

@app.route("/right/update")
@app.route("/right")
def right():
    return render_template("right_face.html", current_page=(request.path.split('/',1)[-1]).replace("/","_"))

@app.route("/register_details")
def register_details():
    return render_template("register_details.html")

@app.route("/solo_or_crowd")
def solo_or_crowd():
    return render_template("solo_or_crowd.html")

@app.route("/sign_in_solo")
def sign_in_solo():
    return render_template("sign_in_solo.html",current_page=request.path.split('/')[-1])

@app.route("/sign_in_crowd")
def sign_in_crowd():
    return render_template("sign_in_crowd.html",current_page=request.path.split('/')[-1])

@app.route("/solo_recognize")
def solo_recognize():
    var = False
    recognized_IDs = []
    global count_of_documents
    ret, frame = video_capture_object.read()
    if not ret:
        return {"result" : "camera not working properly"}
    elif(count_of_documents>0):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # converting BGR format to RGB format as face_recognition module works with RGB format
        face_loacations_in_frame = face_recognition.face_locations(rgb_frame)  # finding face locations --> returns list of tuples
        face_encodings_in_frame = face_recognition.face_encodings(rgb_frame, face_loacations_in_frame)  # finding face encodings at identified locations -->returns list of arrays(an array of 128 values)
        for face_encodings_of_frame in face_encodings_in_frame:
            result = face_recognition.compare_faces(encodings_n18, face_encodings_of_frame, 0.4)
            face_distances = face_recognition.face_distance(encodings_n18, face_encodings_of_frame)
            best_index = np.argmin(face_distances)

            print("best_index:",best_index) #printing the best_index in recognized

            if result[best_index]:
                # global Order_of_IDs_inserted
                # best_index = int(best_index / 3) # to find ID, if I consider all three encodings of a single person face for recognizing, while we are signing_in

                ID_recognized = Order_of_IDs_inserted[best_index]
                # ID_recognized = "N"+str(best_index + 180001)  # to find ID, if I use previous minor_project 'sms_login_details_n18' collection for recognizing, while we are signing_in
                print("Recognized ID:",ID_recognized)
                recognized_IDs.append(ID_recognized)
                var = True
                break
        if(var == True):
            id, password = fetch(recognized_IDs[0])
            print("Password:",password)
            if(direct_login(id,password)):
                return {"result" : "true", "id":id}
            else:
                return {"result" : "no chromedriver", "id":id}
        else:
            return {"result": "false","id":"None"}
    else:
        return {"result" : "no documents"}

@app.route("/crowd_recognize")
def crowd_recognize():
    var = False
    recognized_IDs = []
    ret, frame = video_capture_object.read()
    if not ret:
        return {"result" : "camera not working properly"}
    else:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # converting BGR format to RGB format as face_recognition module works with RGB format
        face_loacations_in_frame = face_recognition.face_locations(rgb_frame)  # finding face locations --> returns list of tuples
        face_encodings_in_frame = face_recognition.face_encodings(rgb_frame, face_loacations_in_frame)  # finding face encodings at identified locations -->returns list of arrays(an array of 128 values)
        for face_encodings_of_frame in face_encodings_in_frame:
            name = "Stranger"
            result = face_recognition.compare_faces(encodings_n18, face_encodings_of_frame, 0.4)
            face_distances = face_recognition.face_distance(encodings_n18, face_encodings_of_frame)
            best_index = np.argmin(face_distances)
            if result[best_index]:
                # global Order_of_IDs_inserted
                # best_index = int(best_index / 3) # to find ID, if I consider all three encodings of a single person face for recognizing, while we are signing_in

                ID_recognized = Order_of_IDs_inserted[best_index]
                # ID_recognized = "N"+str(best_index + 180001)  # to find ID, if I use previous minor_project 'sms_login_details_n18' collection for recognizing, while we are signing_in
                print("Recognized ID:", ID_recognized)
                recognized_IDs.append(ID_recognized)
                var = True
                break
        if(var == True):
            return {"result" : "true", "recognized_IDs":recognized_IDs}
        else:
            return {"result": "false","id":"None"}

@app.route("/what_update")
def what_update():
    return render_template("what_update.html")

@app.route("/update_details/<Updating_ID>")
def update_details(Updating_ID):
    print("in details updation: ",Updating_ID)
    return render_template("update_details.html", updating_id = Updating_ID)

@app.route("/recognized_IDs")
def recognized_IDs():
    return render_template("recognized_IDs.html")

def decrypt_password(encrypted_password):
    password = fernet.decrypt(encrypted_password).decode()      #decrypt password
    return password

def direct_login(ID, PASSWORD):
    if os.path.isfile("chromedriver.exe") == False:
        tkinter.messagebox.showerror('NO_DRIVER','please place chrome driver in path i.e., in the same location of python script')
        return False
    else:
        options = webdriver.ChromeOptions()  # to set options
        options.add_experimental_option("detach",True)  # setting chrome option to detatch opened browser window from program, so that browser won't be closed even if we exit the program
        browser = webdriver.Chrome(options=options)
        browser.maximize_window()
        browser.get("https://intranet.rguktn.ac.in/SMS/")  # opening browser to this url
        browser.implicitly_wait(30)  # maximum time to wait to identify each element in browser
        user_name = browser.find_element(by="id", value="user1")  # finding elements
        password = browser.find_element(by="id", value="passwd1")
        user_name.send_keys(ID)  # sending keys
        password.send_keys(PASSWORD)
        password.submit()  # clicking on submorderit
        return True

def fetch(id):
    encrypted_password = collection.find({'_id':id},{'password':1,'_id':0})[0]['password']
    if encrypted_password != None:
        password = decrypt_password(encrypted_password)
        return (id, password)

@app.route("/fetch_data/<ID>")
def fetch_data(ID):
    encrypted_password = collection.find({'_id':ID},{'password':1,'_id':0})[0]['password']
    if encrypted_password != None:
        password = decrypt_password(encrypted_password)
        result = direct_login(ID, password)
        if result:
            return {"result":"true"}
        else:
            return {"result":"false"}

def gen_frames(current):
    if current == 'front' or current =='left' or current =='right' or current =='front_update' or current =='left_update' or current =='right_update' or current == 'sign_in_solo' or current == 'sign_in_crowd':
        while True:
            ret, frame = video_capture_object.read()
            if not ret:
                break
            else:
                ret, buffer = cv2.imencode('.jpg',frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<current>')
def response_function(current):
    variable  = gen_frames(current)
    return Response(variable, mimetype="multipart/x-mixed-replace; boundary=frame")

def face_locations_detection(frame):
    # return face_locations(which suits the locations argument in face_recognition.face_encodings(frame) function), count_of_detected_faces
    pass

def check_template_image_blurness(frame):
    return True

def template_img_encoding(frame):
    if check_template_image_blurness(frame):
        # locations, count_of_faces = face_locations_detection(frame) #locations should be list of tuples(indicates locations of detected face)
        locations = face_recognition.face_locations(frame)
        count_of_faces = len(locations)
        if count_of_faces == 0:
            return str(count_of_faces), "false"
        elif count_of_faces == 1:
            # return ("single person detected", face_recognition.face_encodings(frame, locations))
            face_encoding_in_image =  face_recognition.face_encodings(frame,locations)
            if(len(face_encoding_in_image) != 1):
                return "no face features", "false"
            return str(face_encoding_in_image[0].tolist()), "false"
        else:
            return str(count_of_faces), "false"
    else:
        return "blur image", "true"

@app.route('/video_feed_2')
def response_function_2():
    ret, frame = video_capture_object.read()
    detection_info, blur_image = template_img_encoding(frame)
    if ret:
        ret, buffer = cv2.imencode('.jpg', frame)   #type of buffer is numpy array(<class 'numpy.ndarray'>)
        global frame_1

        # frame_2 = buffer.tobytes()    #converts to bytes type

        # with open("recent.jpg",'wb') as f:
        #     f.write(base64.b64encode(buffer))   #It generates a file with name recent.jpg but we can't see anything in that picture(saying file format not supported)

        # with open("recent2.jpg",'wb') as f:
        #     f.write(buffer)                     #It also works even buffer is of numpy.ndarray type instead of bytes type

        # with open('saving.jpg', 'wb') as f:
        #     f.write(buffer.tobytes())         # It is also working

        frame_1 = base64.b64encode(buffer).decode('utf-8')

        # with open('saving.jpg', 'wb') as f:
        #     f.write(base64.b64encode(buffer).decode('utf-8'))     #Can't open the saving.jpg file

        # string_data = str([buffer.tobytes()])
        # with open('saving.jpg', 'wb') as f:
        #     f.write(eval(string_data)[0])     # It is also working

        print(frame_1)
        print(type(frame_1))

    # return { "template_img" : frame_1,"img_binary" : str([buffer.tobytes()]), "img_encoding": detection_info, "blur_img" : blur_image}
    return {"template_img" : frame_1, "img_encoding": detection_info, "blur_img" : blur_image}

@app.route('/send_sms/<ID>')
def send_sms(ID):
    server = SMTP('smtp.gmail.com', 587)  # to create a SMTP session
    server.starttls()  # starts TLS for security
    # server.login('pavansankar9@gmail.com', 'ivmqxbgptzzynalq')  # Authetication purpose - Two step verification turned on Oct 30 2022
    server.login('pavansankar9@gmail.com', 'yaxqlbvpfscpghwh')  # Authetication purpose - generated new 16 digit password on March 21 2024
    em = EmailMessage()  # base class for core email object model for creating or modifying structured messages
    em['To'] = ID + '@rguktn.ac.in'
    em['From'] = 'pavansankar9@gmail.com'
    em['Subject'] = 'OTP for Registration'
    random_otp = randint(1000, 9999)
    body = '\nEnter OTP ' + str(random_otp) + ' to register for face recognition based SMS login'
    em.set_content(body)  # setting body to message
    server.sendmail('pavansankar9@gmail.com', ID + '@rguktn.ac.in', em.as_string())
    print("Random_otp: ",random_otp)
    return {"random_otp_generated" : random_otp}

@app.route('/send_sms_confirmation/<ID>')
def send_sms_confirmation(ID):
    server = SMTP('smtp.gmail.com', 587)  # to create a SMTP session
    server.starttls()  # starts TLS for security
    # server.login('pavansankar9@gmail.com', 'ivmqxbgptzzynalq')  # Authetication purpose - Two step verification turned on Oct 30 2022
    server.login('pavansankar9@gmail.com', 'yaxqlbvpfscpghwh')  # Authetication purpose - generated new 16 digit password on March 21 2024
    em = EmailMessage()  # base class for core email object model for creating or modifying structured messages
    em['To'] = ID + '@rguktn.ac.in'
    em['From'] = 'pavansankar9@gmail.com'
    em['Subject'] = 'OTP for Registration'
    random_otp = randint(1000, 9999)
    body = 'Some other students also recognized besides you.\nEnter OTP ' + str(random_otp) + ' in the prompt of javascript to log into your SMS'
    em.set_content(body)  # setting body to message
    server.sendmail('pavansankar9@gmail.com', ID + '@rguktn.ac.in', em.as_string())
    return {"random_otp_generated" : random_otp}

def encrypt(plaintext):
    ciphertext = fernet.encrypt(plaintext.encode())
    return ciphertext

@app.route('/check_collection_for_id/<ID>')
def check_collection_for_id(ID):
    if(collection.find_one({"_id":ID})):
        return {"result" : "true"}
    else:
        return {"result" : "false"}

# function to register the user with fields(id, name, encrypted_password, front_face_encoding, left_face_encoding, right_face_encoding)
@app.route('/database_registration/<data_insertion>')
def database_registration(data_insertion):
    # data_insertion = urllib.parse.unquote(data_insertion)     # to decode the encoded data we got from the client side(i.e., encoded in javascript by using encodeURIComponent(...) to pass the data safely through URLs while using fetch in javascript)
    DATA_INSERTION = json.loads(data_insertion)
    print(type(DATA_INSERTION))
    result = collection.insert_one({"_id":DATA_INSERTION["id"], "name" : DATA_INSERTION["name"],"password" : encrypt(DATA_INSERTION["password"]),
                           "front_face_encoding": eval(DATA_INSERTION["front_encoding"]),"left_face_encoding": eval(DATA_INSERTION["left_encoding"]),
                           "right_face_encoding": eval(DATA_INSERTION["right_encoding"])})

    print("inserted_id:",result.inserted_id)
    updating_encodings_and_IDs()
    return {"result" : "true"}

#funciton to update image encodings of the user
@app.route('/database_images_updation/<data_updation>')
def database_images_updation(data_updation):
    DATA_UPDATION = json.loads(data_updation)
    result = collection.update_one({"_id":DATA_UPDATION["id"]},{"$set" : {"front_face_encoding": eval(DATA_UPDATION["front_update_encoding"]),
                                            "left_face_encoding": eval(DATA_UPDATION["left_update_encoding"]),"right_face_encoding": eval(DATA_UPDATION["right_update_encoding"])}})
    if(result.modified_count):
        updating_encodings_and_IDs()
        return {"result": "true"}
    else:
        return {"result": "false"}

#function to update details of the user(Name and password)
@app.route('/database_details_updation/<data_updation>')
def database_details_updation(data_updation):
    DATA_UPDATION = json.loads(data_updation)
    result = collection.update_one({"_id": DATA_UPDATION["id"]},{"$set": {"name": DATA_UPDATION["name"],
                                                                          "password": encrypt(DATA_UPDATION["password"])}})
    if (result.modified_count):
        return {"result": "true"}
    else:
        return {"result": "false"}

# function to update global variables
def updating_encodings_and_IDs():

    global encodings_n18
    global count_of_documents
    global Order_of_IDs_inserted

    n18_encodings_front = collection.find({}, {"_id": 0, "front_face_encoding": 1})  # Assume as it returns a list of dictionaries which only has 'face_encoding' as a key and it's encoding as a value. But in general n18_encodings is a cursor object which has dictionaries of our face encodings
    encodings_n18_front = [i['front_face_encoding'] for i in n18_encodings_front]  # It only has encodings stored in a list
    n18_encodings_left = collection.find({}, {"_id": 0, "left_face_encoding": 1})  # Assume as it returns a list of dictionaries which only has 'face_encoding' as a key and it's encoding as a value. But in general n18_encodings is a cursor object which has dictionaries of our face encodings
    encodings_n18_left = [i['left_face_encoding'] for i in n18_encodings_left]  # It only has encodings stored in a list
    n18_encodings_right = collection.find({}, {"_id": 0, "right_face_encoding": 1})  # Assume as it returns a list of dictionaries which only has 'face_encoding' as a key and it's encoding as a value. But in general n18_encodings is a cursor object which has dictionaries of our face encodings
    encodings_n18_right = [i['right_face_encoding'] for i in n18_encodings_right]  # It only has encodings stored in a list
    Order_of_IDs_inserted = collection.find({}, {"_id": 1})
    Order_of_IDs_inserted = [i["_id"] for i in Order_of_IDs_inserted]
    print(Order_of_IDs_inserted)
    count_of_documents = collection.count_documents({})
    print("count of documents: ", count_of_documents)
    # encodings_n18 = encodings_n18_front + encodings_n18_left + encodings_n18_right
    encodings_n18 = encodings_n18_front

if __name__ == "__main__":
    #for localhost connection to fetch data stored in local mongodb

    client = MongoClient("mongodb://localhost:27017")
    db = client["sample_db"]
    collection = db["sample_collection_3"]

    n18_encodings_front = collection.find({}, {"_id": 0,"front_face_encoding": 1})  # Assume as it returns a list of dictionaries which only has 'face_encoding' as a key and it's encoding as a value. But in general n18_encodings is a cursor object which has dictionaries of our face encodings
    encodings_n18_front = [i['front_face_encoding'] for i in n18_encodings_front]  # It only has encodings stored in a list
    n18_encodings_left = collection.find({}, {"_id": 0,"left_face_encoding": 1})  # Assume as it returns a list of dictionaries which only has 'face_encoding' as a key and it's encoding as a value. But in general n18_encodings is a cursor object which has dictionaries of our face encodings
    encodings_n18_left = [i['left_face_encoding'] for i in n18_encodings_left]  # It only has encodings stored in a list
    n18_encodings_right = collection.find({}, {"_id": 0,"right_face_encoding": 1})  # Assume as it returns a list of dictionaries which only has 'face_encoding' as a key and it's encoding as a value. But in general n18_encodings is a cursor object which has dictionaries of our face encodings
    encodings_n18_right = [i['right_face_encoding'] for i in n18_encodings_right]  # It only has encodings stored in a list
    Order_of_IDs_inserted = collection.find({},{"_id":1})
    Order_of_IDs_inserted = [i["_id"] for i in Order_of_IDs_inserted]
    count_of_documents = collection.count_documents({})
    print("count of documents: ",count_of_documents)
    print(Order_of_IDs_inserted)
    # encodings_n18 = encodings_n18_front + encodings_n18_left + encodings_n18_right    #If we consider three encodings the distance differences from left and right encodings of a person with other person front face may be in the below of 0.4
    # To make this application work properly, I need to check whether it is front image(then compare with front encodings), left image(then compare with left encodings), right image(then compare with right encodings)
    encodings_n18 = encodings_n18_front # considering only front face encoding even after taking three encodings from the user for better recognition(check how the inaccuracy in recognition occurs through the above mentioned comment)

    # n18_encodings = collection.find({}, {"_id": 0,"face_encoding": 1})  # Assume as it returns a list of dictionaries which only has 'face_encoding' as a key and it's encoding as a value. But in general n18_encodings is a cursor object which has dictionaries of our face encodings
    # encodings_n18 = [i['face_encoding'] for i in n18_encodings]  # It only has encodings stored in a list

    app.run(debug=True)