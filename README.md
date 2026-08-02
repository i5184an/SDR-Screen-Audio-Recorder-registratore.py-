# SDR-Screen-Audio-Recorder-registratore.py-
A specialized Python utility designed to record Software-Defined Radio (SDR) applications—specifically optimized for **AIRSPY SDR# Studio**—featuring pixel-perfect window tracking, real-time gamma/color calibration, transparent logo watermarking, and synchronized audio-video recording.
## 🚀 Key Features

- **Precise Window Tracking**: Automatically locates and captures the exact coordinates and dimensions of the target window using the Windows API (`ctypes.windll.user32.GetwindowRect`) and `mss`.
- **Custom Color & Gamma Calibration**: Overcomes video codec compression artifacts and monitor display discrepancies using OpenCV's `cv2.convertScaleAbs` (`alpha` and `beta` tuning) to ensure recorded footage precisely matches what you see live.
- **Dynamic Watermarking**: Automatically overlays a transparent PNG logo (`logo_radio.png`) on the top-left corner of the video frames using precise alpha channel blending.
- **Audio-Video Synchronization**: Cleanly merges high-framerate screen captures with captured audio streams using FFmpeg.
- **One-Click Batch Launcher**: Includes a Windows `.bat` script for rapid execution.

---

## 📋 Prerequisites

Ensure your Windows environment has the following installed and accessible:
- Python (compatible with Python 3.x)
- **OpenCV** (`opencv-python`)
- **MSS** (`mss`)
- **NumPy** (`numpy`)
- **FFmpeg** (must be installed and added to the Windows System PATH for audio/video muxing)

Install the required Python libraries via pip:
```bash
pip install opencv-python mss numpy
```

---

## 🛠️ Color & Gamma Calibration

When recording dark-themed UI software like SDR applications, standard video encoders (`mp4v`) often flatten gamma and desaturate contrast compared to physical monitors. 

To fix this, the script applies an on-the-fly adjustment filter right before writing each frame:
```python
frame = cv2.convertScaleAbs(frame, alpha=0.8, beta=-15)
```
- **`alpha = 0.8`**: Fine-tunes and softens the contrast curve to prevent washed-out highlights.
- **`beta = -15`**: Deepens the shadow tones and background blacks (crucial for waterfall displays) to match physical monitor calibration.

---

## 🚀 Usage & Execution

### 1. File Structure
Place the following files in the same working directory:
- `registratore.py` (The main recording script)
- `logo_radio.png` (Optional transparent overlay logo)

### 2. Batch Launcher (`run_recorder.bat`)
To streamline execution on Windows, create a batch file named `run_recorder.bat` in the project directory:

```batch
@echo off
TITLE SDR Screen & Audio Recorder
echo ==========================================
echo Starting SDR Screen & Audio Recorder...
echo ==========================================
python registratore.py
pause
```

Simply double-click `run_recorder.bat` to launch your recording session.

---

## 📄 License
This project is open-source and free to use for amateur radio enthusiasts and developers.



<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/c47bd1f0-ef9f-4f4c-8eae-b3efa4fffd54" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/06483b38-1499-462b-ab58-6b1eeb28949e" />











