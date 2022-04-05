import subprocess
from moviepy.editor import VideoFileClip
import re

# Функция принмает на вход путь к видео и минимальную длительность пауз, создает список
def get_marks(video_path, duration):
    stamps = {'start' : [], 'end' : []}
    subprocess.call(
        f'ffmpeg -i {video_path} -af silencedetect=noise=-30dB:d={duration} -f null - 2> vol.txt',
        shell=True)
    
    with open('vol.txt') as text:
        for line_ in text:
            line = line_.strip()
            # Выделение значений времени
            if 'silence_start' in line:
                dig = re.findall(r'[silence_start: ][0-9]\d{0,31}[.,]\d{1,6}', line)
                stamps['start'].append(float(dig[0]))
            elif 'silence_end' in line:
                dig = re.findall(r'[silence_end: ][0-9]\d{0,31}[.,]\d{1,6}', line)
                stamps['end'].append(float(dig[0]))
    
    return stamps

stamps = get_marks('Third.mp4', 2)
print(stamps)

# Создание клипов по полученным фрагментам
def cut_video(stamps, video_path):
    video = VideoFileClip(video_path)
    if stamps['start']:
        fragment = video.subclip(0, stamps['start'][0])
        fragment.write_videofile(f'./outputs/test_{0}.mp4')
        if len(stamps['start']) > 1:
            for elem in range(0, len(stamps['start'])-1):
                fragment = video.subclip(stamps['end'][elem], stamps['start'][elem+1])
                fragment.write_videofile(f'./outputs/test_{elem+1}.mp4')

        # Сохранение последнего фрагмента
        try:
            elem = len(stamps['start'])-1
            fragment = video.subclip(stamps['end'][-1])
            fragment.write_videofile(f'./outputs/test_{elem+1}.mp4')
        except:
            pass


cut_video(stamps, 'Third.mp4')