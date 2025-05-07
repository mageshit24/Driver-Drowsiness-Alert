import numpy as np
import cv2
import time
import pygame  # For user-defined alarm sound
import smtplib  # For sending email alerts
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import geocoder  # For IP-based geolocation

# Initialize Pygame mixer
pygame.mixer.init()
ALARM_SOUND = "pianos-by-jtwayne-7-174717.wav"

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "mageshhariramk2004@gmail.com"
EMAIL_PASSWORD = "aaaa bbbb cccc dddd" # Original passcode
EMAIL_RECEIVER = "kmageshhariram2004@gmail.com"

# Function to play the alarm sound
def play_alarm():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(ALARM_SOUND)
        pygame.mixer.music.play(-1)

# Function to stop the alarm sound
def stop_alarm():
    pygame.mixer.music.stop()

# Function to get current GPS coordinates using IP
def get_location():
    try:
        g = geocoder.ip('me')
        if g.ok:
            return g.latlng  # [latitude, longitude]
    except Exception as e:
        print(f"Location fetch failed: {e}")
    return [None, None]

# Function to send email alert with GPS coordinates
def send_alert():
    try:
        lat, lon = get_location()
        location_msg = f"Location: https://www.google.com/maps?q={lat},{lon}" if lat and lon else "Location: Not Available"

        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = "Drowsiness Alert!"
        body = (
            "Alert! The driver has closed their eyes for more than 5 seconds.\n"
            "Immediate attention required.\n\n" + location_msg
        )
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
        server.quit()
        print("Alert email sent to admin!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Load camera and Haar cascades
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

eye_closed_time = None
alarm_triggered = False
CLOSE_THRESHOLD = 5  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    eyes_detected = False

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.3, 5)

        if len(eyes) > 0:
            eyes_detected = True
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    if not eyes_detected:
        if eye_closed_time is None:
            eye_closed_time = time.time()
        elif time.time() - eye_closed_time >= CLOSE_THRESHOLD and not alarm_triggered:
            print("ALERT! Eyes closed for too long!")
            play_alarm()
            send_alert()
            alarm_triggered = True
    else:
        eye_closed_time = None
        if alarm_triggered:
            stop_alarm()
            alarm_triggered = False

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()