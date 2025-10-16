import cv2
import face_recognition
import os
from datetime import datetime

# --- Setup ---
os.makedirs("faces", exist_ok=True)
cap = cv2.VideoCapture(0)

def take_picture():
    name = input("Enter your name: ").strip()
    student_id = input("Enter your student ID: ").strip()
    
    if not name or not student_id:
        print("Name or ID cannot be empty!")
        return
    
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image from camera.")
        return
    
    filename = f"{name}_{student_id}.jpg"
    filepath = os.path.join("faces", filename)
    cv2.imwrite(filepath, frame)
    print(f"Face saved as {filename}")

def main():
    print("Press 'Enter' to take a picture or type 'exit' to quit.")
    while True:
        cmd = input(">> ").strip().lower()
        if cmd == "exit":
            break
        take_picture()

    cap.release()
    print("Camera released. Exiting...")

if __name__ == "__main__":
    main()
