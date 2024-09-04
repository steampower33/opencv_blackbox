import cv2
import threading
import time, os

recording = True
rec_length = 3  # 녹화 시간 (초)

# 1분 타이머 스레드 함수
def timer_thread(stop_event):
    global recording
    loop  = rec_length
    while(recording):
        time.sleep(1)  # 60초 (1분) 대기
        loop-=1
        if loop==0:
            break
    
    stop_event.set()  # 이벤트 설정 (녹화 중지)

# 녹화 중지 이벤트 생성
stop_recording = threading.Event()

# 웹캠 캡처 객체 생성
cap = cv2.VideoCapture(0)

# 녹화 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 코덱 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))  # 프레임 레이트 설정

video_cnt = 0
while video_cnt != 10:
    
    # 폴더 경로 설정 및 생성
    now = time.strftime("%Y%m%d_%H%M%S")
    current_path = os.getcwd()
    files = os.listdir(current_path)
    nowFolder = now[:11]
    if nowFolder not in files:
        os.makedirs(nowFolder, exist_ok=True)
    out = cv2.VideoWriter(nowFolder + '/' + now + '.mp4', fourcc, fps, (width, height))  # 출력 파일 설정

	# 타이머 스레드 생성 및 시작 (녹화 시작과 동시에)
    timer = threading.Thread(target=timer_thread, args=(stop_recording,))
    timer.start()  # 타이머 시작
    
    # 녹화 시작 (내부 while 루프)
    while recording:
        ret, frame = cap.read()  # 프레임 읽기

        if ret:
            out.write(frame)  # 프레임 저장
            cv2.imshow('Webcam Recording', frame)  # 미리보기 표시

            # 'q' 키를 누르면 즉시 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                recording = False
                break

        # 타이머 이벤트 확인 (1분 경과 여부)
        if stop_recording.is_set():
            recording = False
            
    recording = True
    stop_recording.clear()
    
    # video_cnt 증가
    video_cnt += 1

# 녹화 종료
cap.release()
out.release()  # 녹화 종료 후 해제
cv2.destroyAllWindows()


current_path = os.getcwd()
files = os.listdir(current_path)

# 영상인지 확인
def is_video(video):
    _, ext = os.path.splitext(video)
    if ext.lower() in ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'):
        return True
    return False

size = 0
oldest_folder = None
oldest_time = time.time()

for f in files:
    # 파일이 폴더인지 확인
    if os.path.isdir(f):
        videos_path = current_path + '/' + f
        videos = os.listdir(videos_path)
        # 폴더 안에 영상이 있는지
        for v in videos:
            if is_video(v):
                # 사이즈 더하기
                size += os.path.getsize(videos_path)
                
                # 해당 폴더 생성일 확인하고, 가자 오래된 폴더 저장
                stat = os.stat(videos_path)
                created_time = stat.st_ctime
                if created_time < oldest_time:
                    oldest_time = created_time
                    oldest_folder = videos_path
                break

threshold = 500 * 1024 * 1024
# 500MB 이상이면 가장 오래된 폴더 삭제
if size > threshold:
    files = os.listdir(oldest_folder)
    if len(files) > 0:
        for filename in files:
            file_path = os.path.join(oldest_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(oldest_folder)