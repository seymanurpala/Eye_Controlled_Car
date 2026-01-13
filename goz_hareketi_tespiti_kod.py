import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import requests
import threading
from collections import deque

# === 1. AYARLAR ===
veri_yolu = "C:/Users/Casper/OneDrive/Masaüstü/veriler"
model_kayit_yolu = "goz_modeli.h5"
esp32_ip = "http://10.245.251.121"
etiketler = ["dur", "geri", "ileri", "sag", "sol"]
img_size = 64

# === 2. MODEL EĞİTİMİ ===
def modeli_egit():
    datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

    train_generator = datagen.flow_from_directory(
        veri_yolu,
        target_size=(img_size, img_size),
        color_mode="grayscale",
        class_mode="categorical",
        batch_size=32,
        subset='training'
    )

    val_generator = datagen.flow_from_directory(
        veri_yolu,
        target_size=(img_size, img_size),
        color_mode="grayscale",
        class_mode="categorical",
        batch_size=32,
        subset='validation'
    )

    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(img_size, img_size, 1)),
        MaxPooling2D(2, 2),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(len(etiketler), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_generator, validation_data=val_generator, epochs=10)
    model.save(model_kayit_yolu)
    print("✅ Model eğitildi ve kaydedildi.")

# === 3. MODELİ YÜKLE ===
def modeli_yukle():
    if not os.path.exists(model_kayit_yolu):
        modeli_egit()
    return tf.keras.models.load_model(model_kayit_yolu)

# === 4. ESP32 KOMUTU GÖNDER ===
def esp32_gonder(url):
    try:
        requests.get(url, timeout=1)
        print("📡 ESP32'ye gönderildi:", url)
    except:
        print("🚫 ESP32 bağlantı hatası")

# === 5. GÖZ TAKİP ve TAHMİN ===
def komut_tahmin_et(model):
    cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
    eye_cascade = cv2.CascadeClassifier(cascade_path)

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Kamera açılamadı.")
        return

    komut_gecmisi = deque(maxlen=3)
    sayac = 0

    print("✅ Göz takibi başlatıldı. Çıkmak için Q'ya bas.")

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1) 
        gri = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gozler = eye_cascade.detectMultiScale(gri, 1.3, 5)

        if len(gozler) >= 2:
            x1, y1, w1, h1 = gozler[0]
            x2, y2, w2, h2 = gozler[1]

            x = min(x1, x2)
            y = min(y1, y2)
            w = max(x1 + w1, x2 + w2) - x
            h = max(y1 + h1, y2 + h2) - y

            # Göz çevresine dikdörtgen
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Göz bebeğine yuvarlak
            for (gx, gy, gw, gh) in [gozler[0], gozler[1]]:
                center_x = gx + gw // 2
                center_y = gy + gh // 2
                radius = min(gw, gh) // 4
                cv2.circle(frame, (center_x, center_y), radius, (0, 255, 255), 2)

            sayac += 1
            if sayac % 10 == 0:
                gozon = gri[y:y+h, x:x+w]
                gozon = cv2.resize(gozon, (img_size, img_size))
                gozon = gozon / 255.0
                gozon = np.expand_dims(gozon, axis=(0, -1))

                tahmin = model.predict(gozon, verbose=0)[0]
                komut = etiketler[np.argmax(tahmin)]
                print("🎯 Tahmin:", komut)

                komut_gecmisi.append(komut)

                if komut_gecmisi.count(komut) == 3:
                    url = f"{esp32_ip}/{komut}"
                    threading.Thread(target=esp32_gonder, args=(url,), daemon=True).start()
                    komut_gecmisi.clear()

                cv2.putText(frame, f"Komut: {komut}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Göz Takibi", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🔚 Program kapatılıyor.")
            break

    cam.release()
    cv2.destroyAllWindows()

# === 6. ANA ===
if __name__ == "__main__":
    model = modeli_yukle()
    komut_tahmin_et(model)