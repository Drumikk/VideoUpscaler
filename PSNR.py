import ffmpeg
import numpy as np
from skimage.transform import resize

def calculate_psnr(original_video, reconstructed_video):

    original_stream = ffmpeg.input(original_video)
    reconstructed_stream = ffmpeg.input(reconstructed_video)

    original_info = ffmpeg.probe(original_video)
    reconstructed_info = ffmpeg.probe(reconstructed_video)

    original_width = int(original_info['streams'][0]['width'])
    original_height = int(original_info['streams'][0]['height'])
    reconstructed_width = int(reconstructed_info['streams'][0]['width'])
    reconstructed_height = int(reconstructed_info['streams'][0]['height'])

    original_frames, _ = ffmpeg.output(original_stream, 'pipe:', format='rawvideo', pix_fmt='rgb24').run(capture_stdout=True)
    reconstructed_frames, _ = ffmpeg.output(reconstructed_stream, 'pipe:', format='rawvideo', pix_fmt='rgb24').run(capture_stdout=True)

    original_array = np.frombuffer(original_frames, np.uint8).reshape([-1, original_height, original_width, 3])
    reconstructed_array = np.frombuffer(reconstructed_frames, np.uint8).reshape([-1, reconstructed_height, reconstructed_width, 3])

    num_frames = min(original_array.shape[0], reconstructed_array.shape[0])

    total_psnr = 0.0

    for i in range(num_frames):
        original_frame = original_array[i].astype(np.float32)
        reconstructed_frame = reconstructed_array[i].astype(np.float32)

        reconstructed_frame = resize(reconstructed_frame, (original_height, original_width), anti_aliasing=True)

        # Вычисление среднеквадратической ошибки (MSE)
        mse = np.mean((original_frame - reconstructed_frame) ** 2)

        # Максимальное значение яркости для пикселей изображений
        max_pixel = 255.0

        if mse == 0:
            # Коэффициент совпадения, где 100 - идеальное совпадение
            psnr = 100.0
        else:
            # Вычисление PSNR с учетом различий в разрешении кадров
            psnr = 10 * np.log10((max_pixel ** 2) / mse)

        total_psnr += psnr

    # Среднее значение PSNR по всем кадрам
    average_psnr = total_psnr / num_frames

    return average_psnr

#
# original_video = "videos/TESTO.mp4"
# reconstructed_video = "videos/TESTO-outputPC.mp4"
# psnr_score_1 = calculate_psnr(original_video, reconstructed_video)
#
# original_video = "videos/TESTO.mp4"
# reconstructed_video = "videos/TESTO-output_nout.mp4"
# psnr_score_2 = calculate_psnr(original_video, reconstructed_video)
#
# original_video = "videos/TESTO.mp4"
# reconstructed_video = "videos/TESTO_SRMD_NCNN.mp4"
# psnr_score_3 = calculate_psnr(original_video, reconstructed_video)
#
# original_video = "videos/TESTO.mp4"
# reconstructed_video = "videos/TESTO_WAIFU2X_CAFFE.mp4"
# psnr_score_4 = calculate_psnr(original_video, reconstructed_video)
#
# original_video = "videos/TESTO.mp4"
# reconstructed_video = "videos/TESTO_WAIFU2X_CPP.mp4"
# psnr_score_5 = calculate_psnr(original_video, reconstructed_video)
#
# original_video = "videos/TESTO.mp4"
# reconstructed_video = "videos/TESTO_WAIFU2X-NCNN-VULKAN.mp4"
# psnr_score_6 = calculate_psnr(original_video, reconstructed_video)
#
# print("PSNR PC:", psnr_score_1)
# print("PSNR NOUT:", psnr_score_2)
# print("PSNR SRMD_NCNN:", psnr_score_3)
# print("PSNR WAIFU2X_CAFFE:", psnr_score_4)
# print("PSNR _WAIFU2X_CPP:", psnr_score_5)
# print("PSNR WAIFU2X-NCNN-VULKAN:", psnr_score_6)