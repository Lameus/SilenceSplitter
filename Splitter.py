import subprocess
import ffmpeg
import re


# Function what returns dictionary with starts and ends of silence 
def get_marks(video_path, duration):
    stamps = {'start': [], 'end': []}
    subprocess.call(
        f'ffmpeg -i {video_path} -af silencedetect=noise=-32dB:d={duration} -f null - 2> vol.txt',
        shell=True)

    with open('vol.txt') as text:
        for line_ in text:
            line = line_.strip()
            # Extracting timestamps from notebook with information
            if 'silence_start' in line:
                dig = re.findall(r'[silence_start: ][0-9]\d{0,31}[.,]\d{1,6}', line)
                stamps['start'].append(float(dig[0]))
            elif 'silence_end' in line:
                dig = re.findall(r'[silence_end: ][0-9]\d{0,31}[.,]\d{1,6}', line)
                stamps['end'].append(float(dig[0]))

    return stamps


def cut(video, audio, start, name, end=None):
    if end:
        video_trimmed = video.trim(start=start, end=end).setpts('PTS-STARTPTS')
        audio_trimmed = audio.filter('atrim', start=start, end=end).filter_('asetpts', 'PTS-STARTPTS')
        out = ffmpeg.output(video_trimmed, audio_trimmed, name)
        ffmpeg.run(out)
    # cut from the start point to the end of the video
    else:
        video_trimmed = video.trim(start=start).setpts('PTS-STARTPTS')
        audio_trimmed = audio.filter('atrim', start=start).filter_('asetpts', 'PTS-STARTPTS')
        out = ffmpeg.output(video_trimmed, audio_trimmed, name)
        ffmpeg.run(out)


# Creates fragments with extracted stamps
def cut_video(stamps, video_path):
    raw_video = ffmpeg.input(video_path)
    audio = raw_video.audio
    video = raw_video.video

    if stamps['start']:
        cut(video, audio, start=0, end=stamps['start'][0], name='./outputs/test_0.mp4')
        if len(stamps['start']) > 1:
            for elem in range(0, len(stamps['start']) - 1):
                name = './outputs/test_' + str(elem + 1) + '.mp4'
                cut(video, audio, start=stamps['end'][elem], end=stamps['start'][elem + 1], name=name)

        # Save the last part (from the last silence stamp to the end of the video)
        try:
            elem = len(stamps['start']) - 1
            name = './outputs/test_' + str(elem + 1) + '.mp4'
            cut(video, audio, start=stamps['end'][-1], name=name)
        except:
            pass

def main(video_path, silence_duration):
    stamps = get_marks(video_path, silence_duration)
    cut_video(stamps=stamps, video_path=video_path)

if __name__ == '__main__':
    _info = input().split(' ')
    video_path, silence_duration = _info[0], float(_info[1])
    main(video_path, silence_duration)
