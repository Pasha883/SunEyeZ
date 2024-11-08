import cv2
from datetime import datetime

def capture_image(stream_url='rtsp://admin:mpei_2024@169.254.147.237/Streaming/Channels/101',
                  save_path="../data/fish_eye"):
    print("Start capturing")
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print("Не удалось подключиться к камере.")
        return
    ret, frame = cap.read()
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_path}/image_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Изображение сохранено: {filename}")
    else:
        print("Не удалось захватить изображение.")
    cap.release()
