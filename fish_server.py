from flask import Flask, Response
import cv2
import numpy as np
import serial
import time

app = Flask(__name__)

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ser = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)
time.sleep(2)

LOWER_RED1 = np.array([0, 40, 40])
UPPER_RED1 = np.array([20, 255, 255])

LOWER_RED2 = np.array([150, 40, 40])
UPPER_RED2 = np.array([180, 255, 255])

MIN_AREA = 1000
MAX_SPEED = 15
DEAD_ZONE = 60

last_seen = time.time()

def clamp(val, low, high):
    return max(min(val, high), low)

def send_to_vex(left_speed, right_speed):
    cmd = f"{left_speed:.1f},{right_speed:.1f}\n"
    ser.write(cmd.encode())

def generate():
    global last_seen

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        raw = frame.copy()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
        mask2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
        mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        tracking = frame.copy()
        frame_h, frame_w = tracking.shape[:2]
        center_x = frame_w // 2
        center_y = frame_h // 2

        cv2.circle(tracking, (center_x, center_y), 6, (255, 255, 255), -1)
        cv2.line(tracking, (center_x, 0), (center_x, frame_h), (255, 255, 255), 1)
        cv2.line(tracking, (0, center_y), (frame_w, center_y), (255, 255, 255), 1)

        left_speed = 0
        right_speed = 0
        found_fish = False

        if len(contours) > 0:
            biggest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(biggest)

            if area > MIN_AREA:
                x, y, w, h = cv2.boundingRect(biggest)
                M = cv2.moments(biggest)

                if M["m00"] != 0:
                    found_fish = True
                    last_seen = time.time()

                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    dx = cx - center_x
                    dy = center_y - cy

                    turn = dx / center_x
                    forward = dy / center_y

                    if abs(dx) < DEAD_ZONE:
                        turn = 0
                    if abs(dy) < DEAD_ZONE:
                        forward = 0

                    left_speed = forward * MAX_SPEED + turn * MAX_SPEED
                    right_speed = forward * MAX_SPEED - turn * MAX_SPEED

                    left_speed = clamp(left_speed, -MAX_SPEED, MAX_SPEED)
                    right_speed = clamp(right_speed, -MAX_SPEED, MAX_SPEED)

                    send_to_vex(left_speed, right_speed)

                    cv2.drawContours(tracking, [biggest], -1, (0, 255, 0), 3)
                    cv2.rectangle(tracking, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.circle(tracking, (cx, cy), 8, (0, 0, 255), -1)
                    cv2.line(tracking, (center_x, center_y), (cx, cy), (0, 255, 255), 2)

                    cv2.putText(tracking, f"Centroid: ({cx},{cy})", (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(tracking, f"dx: {dx}", (20, 75),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    cv2.putText(tracking, f"dy: {dy}", (20, 110),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    cv2.putText(tracking, f"L: {left_speed:.1f}", (20, 145),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    cv2.putText(tracking, f"R: {right_speed:.1f}", (20, 180),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        if not found_fish:
            if time.time() - last_seen > 0.5:
                send_to_vex(0, 0)

            cv2.putText(tracking, "Fish not found", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.putText(tracking, "HSV Tracking + Motor Commands", (20, 450),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(raw, "Raw Feed", (20, 450),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        combined = np.hstack((tracking, raw))

        _, buffer = cv2.imencode(".jpg", combined)

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

@app.route("/")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

app.run(host="0.0.0.0", port=5000, threaded=True)
