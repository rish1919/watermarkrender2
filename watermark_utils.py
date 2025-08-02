import os
import ffmpeg
from PIL import Image

async def apply_image_watermark(input_path, wm_path):
    base = Image.open(input_path).convert("RGBA")
    wm = Image.open(wm_path).convert("RGBA")

    # Resize watermark if larger
    if wm.size[0] > base.size[0] // 3:
        ratio = (base.size[0] // 3) / wm.size[0]
        wm = wm.resize((int(wm.size[0]*ratio), int(wm.size[1]*ratio)))

    # Bottom right
    pos = (base.size[0] - wm.size[0] - 10, base.size[1] - wm.size[1] - 10)
    base.paste(wm, pos, wm)
    out_path = f"{input_path}_wm.png"
    base.save(out_path)
    return out_path

async def apply_video_watermark(input_path, wm_path):
    out_path = f"{input_path}_wm.mp4"
    stream = ffmpeg.input(input_path)
    wm = ffmpeg.input(wm_path)

    video = ffmpeg.overlay(stream.video, wm, x='main_w-overlay_w-10', y='main_h-overlay_h-10')
    audio = stream.audio

    ffmpeg.output(video, audio, out_path).run(overwrite_output=True, quiet=True)
    return out_path
