import cv2
import face_recognition
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import os
import csv
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import shutil
import hashlib

# --- Setup ---
os.makedirs("faces", exist_ok=True)
csv_file = "attendance.csv"
frontend_csv = "../frontend/public/attendance.csv"
correct_headers = ["Name", "Student ID", "Timestamp"]

# Ensure CSV exists and headers are correct
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(correct_headers)
else:
    # Check existing headers
    with open(csv_file, "r", newline="") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            headers = []

    if headers != correct_headers:
        # Preserve existing data
        with open(csv_file, "r", newline="") as f:
            rows = list(csv.reader(f))[1:]  # skip old header

        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(correct_headers)
            writer.writerows(rows)

# --- Global variables ---
known_faces, known_names, known_ids, last_seen = [], [], [], {}
cap = cv2.VideoCapture(0)
last_csv_hash = None  # For detecting changes

# --- Load faces ---
def load_faces():
    known_faces.clear()
    known_names.clear()
    known_ids.clear()
    for file in os.listdir("faces"):
        if file.endswith(".jpg") or file.endswith(".png"):
            img = face_recognition.load_image_file(f"faces/{file}")
            encs = face_recognition.face_encodings(img)
            if encs:
                enc = encs[0]
                name_id = file.split(".")[0].split("_")
                if len(name_id) == 2:
                    name, student_id = name_id
                else:
                    name, student_id = name_id[0], "UnknownID"
                known_faces.append(enc)
                known_names.append(name)
                known_ids.append(student_id)

# --- Tkinter GUI ---
root = tk.Tk()
root.title("Live Attendance System")
root.geometry("1000x700")
root.resizable(False, False)

# --- Camera frame ---
camera_label = tk.Label(root)
camera_label.pack(padx=10, pady=10)

# --- Buttons ---
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

def register_face():
    name = simpledialog.askstring("Name", "Enter your name:")
    student_id = simpledialog.askstring("Student ID", "Enter your student ID:")
    if not name or not student_id:
        return
    ret, frame = cap.read()
    if ret:
        filename = f"{name}_{student_id}.jpg"
        cv2.imwrite(f"faces/{filename}", frame)
        messagebox.showinfo("Saved", f"Face saved as {filename}")
        load_faces()

def clear_table():
    for row in tree.get_children():
        tree.delete(row)

def exit_app():
    cap.release()
    root.destroy()

tk.Button(button_frame, text="Register Face", width=20, command=register_face).pack(side="left", padx=10)
tk.Button(button_frame, text="Reload Known Faces", width=20, command=load_faces).pack(side="left", padx=10)
tk.Button(button_frame, text="Clear Table", width=20, command=clear_table).pack(side="left", padx=10)
tk.Button(button_frame, text="Exit", width=20, command=exit_app).pack(side="left", padx=10)

# --- Attendance table ---
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10, fill="both", expand=True)

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=("Name", "Student ID", "Timestamp"), show="headings",
                    yscrollcommand=tree_scroll.set)
tree.heading("Name", text="Name")
tree.heading("Student ID", text="Student ID")
tree.heading("Timestamp", text="Timestamp")
tree.pack(fill="both", expand=True)
tree_scroll.config(command=tree.yview)

# --- Real-time face recognition ---
def update_frame():
    ret, frame = cap.read()
    if ret:
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            name, student_id = "Unknown", "UnknownID"

            if True in matches:
                idx = matches.index(True)
                name = known_names[idx]
                student_id = known_ids[idx]
                now = datetime.now()
                if name not in last_seen or now - last_seen[name] > timedelta(seconds=5):
                    last_seen[name] = now
                    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                    with open(csv_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([name, student_id, timestamp])
                    tree.insert("", tk.END, values=(name, student_id, timestamp))

            # Draw rectangle
            top *= 4; right *= 4; bottom *= 4; left *= 4
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, f"{name} ({student_id})", (left, top-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Convert to Tkinter image
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)

    root.after(10, update_frame)

# --- Copy CSV if changed ---
def hash_file(filename):
    hasher = hashlib.md5()
    with open(filename, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def copy_csv_if_changed():
    global last_csv_hash
    try:
        current_hash = hash_file(csv_file)
        if current_hash != last_csv_hash:
            shutil.copy(csv_file, frontend_csv)
            last_csv_hash = current_hash
            print(f"CSV copied at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"Error copying CSV: {e}")
    root.after(1000, copy_csv_if_changed)  # check every second

# --- Start ---
load_faces()
update_frame()
copy_csv_if_changed()
root.mainloop()
cap.release()
