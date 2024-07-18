import cv2
import numpy as np
import time
import sys
from ultralytics import YOLO
import telepot
from telepot.loop import MessageLoop

# Path
TOKEN = ''  # Isi dengan token bot Telegram jika digunakan
modelYOLO = 'pathnya'  # Ganti dengan path model YOLO yang benar
imagePath = 'assets\datasheets1.png'  # Pastikan path benar

# Memuat model YOLO
try:
    model = YOLO(modelYOLO)  # Pastikan path model benar
except Exception as e:
    print(f"Model tidak ada disini: {e}")
    sys.exit(1)

# Fungsi untuk memproses gambar dan melakukan deteksi objek
def detect_objects(imagePath):
    try:
        # Memuat gambar
        img = cv2.imread(imagePath)
        if img is None:
            raise ValueError(f"Image not found at {imagePath}")
        
        results = model(img)

        # Menggambar bounding box di gambar asli
        for result in results:
            for bbox in result.boxes:
                x1, y1, x2, y2 = map(int, bbox.xyxy[0])
                label = bbox.cls
                confidence = bbox.conf
                if confidence > 0.8: #Akurasinya
                    cv2.rectangle(img, (x1, y1), (x2, y2), (7, 55, 99), 2)
                    cv2.putText(img, f'{label}: {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            if label == 'person':  # Cek deteksi Limfosit
                jumlahLimfosit += 1
        
        return img
    except Exception as e:
        print(f"Error processing image: {e}")
        return None
PersentaseCD4 = 0.45
jumlahLimfosit = 2100
sistemHIV = PersentaseCD4 * jumlahLimfosit

if sistemHIV > 80:
    sistemHIV = 80

if sistemHIV <= 40:
    kesimpulan = 'HIV'
else:
    kesimpulan = 'Bebas HIV'

# Inisialisasi kamus untuk menyimpan data pengguna
user_data = {}

def handle(msg):
    global user_data  # Mengakses user_data sebagai variabel global

    try:
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if content_type == 'text':
            text = msg['text']
            
            if chat_id not in user_data:
                if text.lower() == 'mulai':
                    user_data[chat_id] = {'step': 'ask_name'}
                    bot.sendMessage(chat_id, 'Masukkan nama Anda')
                else:
                    bot.sendMessage(chat_id, 'Kirim "Mulai" untuk memulai interaksi.')
            else:
                if user_data[chat_id]['step'] == 'ask_name':
                    user_data[chat_id]['name'] = text
                    user_data[chat_id]['step'] = 'done'
                    
                    response = (
                        f"{user_data[chat_id]['name']}\n"
                        f"Jumlah CD4: {sistemHIV:.2f}%\n"
                        f"Kesimpulan: {kesimpulan}"
                    )
                    bot.sendMessage(chat_id, response)
                    del user_data[chat_id]
    
    except KeyError as e:
        print(f"Error: {e}. Pesan tidak sesuai dengan format yang diharapkan.")

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# running + stop
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna")
    sys.exit(0)

# Loop utama
try:
    while True:
        processed_image = detect_objects(imagePath)
        if processed_image is not None:
            cv2.imshow('Detected Objects', processed_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        time.sleep(10)
    
except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna")
    sys.exit(0)
