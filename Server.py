from flask import Flask, render_template, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField, SelectField
from flask_socketio import SocketIO
from flask_socketio import emit
import os
import time
from Codec import *
from PSNR import *


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)
UPLOAD_FOLDER = 'videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class UploadForm(FlaskForm):
    file = FileField('Выбрать файл', validators=[FileRequired()])
    scale_factor = SelectField('Множитель масштабирования', choices=[('2', '2'), ('3', '3'), ('4', '4')], default='2')
    submit = SubmitField('Загрузить')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        scale_factor = int(form.scale_factor.data)
        if file and file.filename.endswith('.mp4'):
            # Сохранение файла на сервере
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Обработка видео
            input_file = "videos/" + file.filename
            output_file = "videos/"+file.filename.split('.')[0] + '-output.mp4'
            start_time = time.time()
            process_video(input_file, output_file, scale_factor,socketio)
            psnr_score = calculate_psnr(input_file, output_file)
            print("PSNR:", psnr_score)
            end_time = time.time()
            total_processing_time = (end_time - start_time)//60
            print(f"Обработка видео завершена. Общее время: {total_processing_time:.2f} мин.")

            # Ожидание появления выходного файла
            output_filename = file.filename.split('.')[0] + '-output.mp4'
            output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            while not os.path.exists(output_file_path):
                pass

            return render_template('download.html', filename=output_filename, psnr_score=psnr_score, total_processing_time=total_processing_time)
        else:
            return 'Invalid file format. Only MP4 files are allowed', 400
    return render_template('upload.html', form=form)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)