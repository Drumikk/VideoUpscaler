import os
import subprocess
import time


def extract_frames(input_file, input_dir):
    os.makedirs(input_dir, exist_ok=True)
    subprocess.call(['ffmpeg', '-i', input_file, '-q:v', '1', os.path.join(input_dir, 'frame_%05d.png')])

def process_frames(input_dir, output_dir, scale_factor, emit_progress, emit_remaining_time):
    os.makedirs(output_dir, exist_ok=True)
    frames = os.listdir(input_dir)
    total_frames = len(frames)
    processed_frames = 0
    start_time = time.time()  # Засекаем время начала обработки видео
    for frame in frames:
        input_path = os.path.join(input_dir, frame)
        output_path = os.path.join(output_dir, frame)
        subprocess.call(['./srmd-ncnn-vulkan.exe', '-i', input_path, '-o', output_path, '-s', str(scale_factor)])
        processed_frames += 1
        progress = processed_frames / total_frames
        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time / progress
        estimated_remaining_time = estimated_total_time - elapsed_time
        progress_percent = "{:.1%}".format(progress)
        estimated_remaining_time_formatted = "{:.2f}".format(estimated_remaining_time)
        emit_progress(progress_percent)
        emit_remaining_time(estimated_remaining_time_formatted)
        print(f"Прогресс: {progress:.1%}  Осталось времени: {estimated_remaining_time:.2f} сек.")
        os.remove(input_path)  # Удаляем обработанный кадр

def create_video(input_dir, output_file, input_file):
    subprocess.call(['ffmpeg', '-i', os.path.join(input_dir, 'frame_%05d.png'), '-i', input_file, '-c:v', 'copy', '-c:a', 'copy', output_file])

def process_video(input_file, output_file, scale_factor,socketio):
    input_dir = 'inputs'
    output_dir = 'outputs'
    extract_frames(input_file, input_dir)
    @socketio.on('connect', namespace='/upload')
    def on_connect():
        socketio.emit('message', {'message': 'Connected'}, namespace='/upload')

    @socketio.on('disconnect', namespace='/upload')
    def on_disconnect():
        socketio.emit('message', {'message': 'Disconnected'}, namespace='/upload')

    def emit_progress(progress):
        socketio.emit('progress', {'message':"<a>Прогресс: </a>" + progress}, namespace='/upload')

    def emit_remaining_time(time):
        socketio.emit('estimated_remaining_time', {'message': "<a>Время обработки: </a>" + time +" сек."}, namespace='/upload')

    process_frames(input_dir, output_dir, scale_factor, emit_progress, emit_remaining_time)
    create_video(output_dir, output_file, input_file)
    # Удаляем кадры из директории outputs
    frames = os.listdir(output_dir)
    for frame in frames:
        frame_path = os.path.join(output_dir, frame)
        os.remove(frame_path)
    # Удаляем директорию outputs
    os.rmdir(output_dir)


# input_file = 'videos/TESTO.mp4'
# output_file = 'videos/TESTO-output.mp4'
# scale_factor = 4
#
# start_time = time.time()
# process_video(input_file, output_file, scale_factor)
# end_time = time.time()
# total_processing_time = (end_time - start_time)//60
# print(f"Обработка видео завершена. Общее время: {total_processing_time:.2f} мин.")
