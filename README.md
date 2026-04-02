# Eye Controlled Car

A real-time eye-tracking system that controls an ESP32-based car using a CNN model. The system detects eye movements via webcam, classifies gaze direction, and sends movement commands to the car over WiFi.

## About the Project

This project uses a webcam to track the user's eyes in real time using OpenCV's Haar Cascade detector. A trained CNN model classifies the eye region into one of 5 directional commands. When the same command is detected 3 times consecutively, it is sent to an ESP32 microcontroller via HTTP, which then drives the motors accordingly.

## Technologies Used

**Python Side**
- **TensorFlow / Keras** — CNN model for gaze classification
- **OpenCV** — real-time eye detection with Haar Cascade
- **NumPy** — image preprocessing
- **Requests / Threading** — non-blocking HTTP command sending to ESP32

**Hardware Side**
- **ESP32** — WiFi-enabled microcontroller
- **Arduino (C++)** — motor control firmware
- **L298N Motor Driver** — DC motor control
- **DC Motors** — vehicle movement

## Supported Commands

| Gaze Direction | Command | Car Action |
|----------------|---------|------------|
| Center | dur | Stop |
| Up | ileri | Forward |
| Down | geri | Backward |
| Right | sag | Turn Right |
| Left | sol | Turn Left |

## System Architecture

The system works in two layers. The Python script captures webcam frames, detects the eye region using Haar Cascade, and feeds the cropped eye image into the CNN model. When a command is confirmed 3 times in a row, it sends an HTTP GET request to the ESP32. The ESP32 runs a web server that listens for these requests and drives the motors for 5 seconds before automatically stopping.

## Project Structure
```
├── main.py                  # Python eye tracking and prediction
├── goz_modeli.h5            # Trained CNN model (auto-generated)
├── esp32_firmware/
│   └── motor_control.ino    # Arduino firmware for ESP32
└── data/
    ├── dur/
    ├── ileri/
    ├── geri/
    ├── sag/
    └── sol/
```

## How to Run

### 1. Install Python dependencies
```bash
pip install tensorflow opencv-python numpy requests
```

### 2. Prepare training data
Collect eye images for each direction and place them in the folder structure above.

### 3. Train and run
```bash
python main.py
```
The model trains automatically if no saved model is found. After training, the webcam activates and eye tracking begins.

### 4. Flash ESP32
Open `motor_control.ino` in Arduino IDE, enter your WiFi credentials, and flash to the ESP32.

## Hardware Requirements

- ESP32 development board
- L298N motor driver module
- 2x DC motors
- Webcam or laptop camera
- Power supply for motors

