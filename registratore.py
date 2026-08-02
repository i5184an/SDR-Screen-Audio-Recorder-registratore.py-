import ctypes
from ctypes import wintypes
import cv2
import mss
import numpy as np
import time
import os
import threading
import sounddevice as sd
import soundfile as sf
import subprocess
import imageio_ffmpeg

print("===========================================")
print("   RICERCA AUTOMATICA FINESTRA RADIO       ")
print("===========================================")

def find_main_window_by_title_part(part):
    hwnd_found = None
    def enum_proc(hwnd, lParam):
        nonlocal hwnd_found
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                if part.lower() in buff.value.lower():
                    rect_temp = wintypes.RECT()
                    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect_temp))
                    w = rect_temp.right - rect_temp.left
                    h = rect_temp.bottom - rect_temp.top
                    if w > 600 and h > 400:
                        hwnd_found = hwnd
                        return False
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(enum_proc), 0)
    return hwnd_found

print("===========================================")
software_scelto = input("Inserisci il nome (o parte del nome) del software da registrare: ")
print("===========================================")

hwnd = find_main_window_by_title_part(software_scelto)

if not hwnd:
    print("[ERRORE CRITICO] Finestra principale di 'SDR Console' non trovata!")
    print("Assicurati che il programma della radio sia aperto, visibile e non ridotto a icona.")
    exit()

rect = wintypes.RECT()
ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))

left, top = rect.left, rect.top
width = rect.right - rect.left
height = rect.bottom - rect.top

if width % 2 != 0:
    width -= 1
if height % 2 != 0:
    height -= 1

print(f"Trovata la finestra principale corretta!")
print(f"X={left}, Y={top} | Dimensioni: {width}x{height} pixel\n")

monitor_area = {"top": top, "left": left, "width": width, "height": height}

video_temp = "video_temp.mp4"
audio_temp = "audio_temp.wav"
output_file = "registrazione_radio_finale.mp4"
fps = 20.0
logo_path = "logo_radio.png"

logo = None
if os.path.exists(logo_path):
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)

sample_rate = 44100
channels = 2
audio_frames = []

def record_audio():
    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        audio_frames.append(indata.copy())
    
    with sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback):
        while recording_active:
            sd.sleep(50)

sct_rec = mss.mss()
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_temp, fourcc, fps, (width, height))

global recording_active
recording_active = True

audio_thread = threading.Thread(target=record_audio)
audio_thread.start()

print("===========================================")
print("   REGISTRAZIONE IN CORSO (VELOCITA' REALE)")
print("                                           ")
print("   PER FERMARE LA REGISTRAZIONE:           ")
print("   Torna su questa finestra e premi:       ")
print("   CTRL + C                                ")
print("===========================================")

frame_interval = 1.0 / fps
next_frame_time = time.time()

try:
    while recording_active:
        current_time = time.time()
        if current_time < next_frame_time:
            time.sleep(next_frame_time - current_time)
        next_frame_time += frame_interval

        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        monitor_area["top"] = rect.top
        monitor_area["left"] = rect.left

        img = sct_rec.grab(monitor_area)
        frame = np.array(img)
        # Questa riga corregge i colori slavati e la tonalità bluastra:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        frame = cv2.convertScaleAbs(frame, alpha=0.8, beta=-15)

        if frame.shape[1] != width or frame.shape[0] != height:
            frame = cv2.resize(frame, (width, height))

      
        # --- EVENTUALE LOGO IN ALTO A SINISTRA (Se presente il file logo_radio.png) ---
        if logo is not None:
            l_height, l_width = logo.shape[:2]
            aspect = l_width / l_height
            new_w = 150
            new_h = int(new_w / aspect)
            logo_resized = cv2.resize(logo, (new_w, new_h))
            x_pos, y_pos = 20, 20
            if logo_resized.shape[2] == 4:
                alpha = logo_resized[:, :, 3] / 255.0
                for c in range(3):
                    frame[y_pos:y_pos+new_h, x_pos:x_pos+new_w, c] = (
                        alpha * logo_resized[:, :, c] + (1 - alpha) * frame[y_pos:y_pos+new_h, x_pos:x_pos+new_w, c]
                    )
            else:
                frame[y_pos:y_pos+new_h, x_pos:x_pos+new_w] = logo_resized[:, :, :3]

        out.write(frame)

except KeyboardInterrupt:
    print("\nInterrompo e unisco audio/video...")

finally:
    recording_active = False
    audio_thread.join()
    out.release()

    if audio_frames:
        audio_data = np.concatenate(audio_frames, axis=0)
        sf.write(audio_temp, audio_data, sample_rate)

    if os.path.exists(video_temp) and os.path.exists(audio_temp):
        print("Unione istantanea in corso...")
        try:
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            cmd = [
                ffmpeg_exe,
                '-y',
                '-i', video_temp,
                '-i', audio_temp,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_file
            ]
            
            subprocess.run(cmd, check=True)
            
            os.remove(video_temp)
            os.remove(audio_temp)
            print(f"\n[SUCCESSO] File finale pronto, pulito e sincronizzato: {output_file}")
        except Exception as e:
            print(f"[ERRORE durante l'unione]: {e}")