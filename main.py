import os, subprocess, json, sys
sys.path.insert(0, r'D:\OpenCode\Wav2Lip')

FFMPEG = r'C:\Users\denk0\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe'
FINAL_DIR = r'D:\OpenCode\ai-blogger\content\final'
REF_DIR = r'D:\OpenCode\ai-blogger\content\ref_photos'
TEMP_DIR = r'D:\OpenCode\ai-blogger\content\temp_studio'
os.makedirs(TEMP_DIR, exist_ok=True)

PROMPTS_FILE = r'D:\OpenCode\ai-blogger\script_generator\prompts.py'
TTS_FILE = r'D:\OpenCode\ai-blogger\tts\generate.py'
COMPOSER_FILE = r'D:\OpenCode\ai-blogger\video_composer\compose.py'
PUBLISHER_FILE = r'D:\OpenCode\ai-blogger\publisher\publish.py'

print('=== AI Блогер: Кандинский ===')

# 1. Script generation
script_path = os.path.join(TEMP_DIR, 'script.json')
if os.path.exists(script_path):
    with open(script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)
    print(f'1. Script loaded: {script["title"]}')
else:
    print('1. No script found, creating default...')
    script = {
        "title": "Нейросеть Кандинский",
        "total_duration": 30,
        "scenes": [
            {
                "id": 1,
                "start": 0,
                "duration": 10,
                "background": "ref_05.png",
                "text": "Кандинский — это нейросеть от Сбера, которая генерирует изображения по текстовому описанию. Она понимает русский язык и создаёт уникальные картинки за считанные секунды.",
                "overlay": "Что такое Кандинский?"
            },
            {
                "id": 2,
                "start": 10,
                "duration": 10,
                "background": "ref_01.png",
                "text": "В основе технологии лежат две нейросети: одна понимает текст и превращает его в математическое описание, вторая рисует изображение по этому описанию. Это работает как художник и его ассистент.",
                "overlay": "Как это работает"
            },
            {
                "id": 3,
                "start": 20,
                "duration": 10,
                "background": "ref_06.png",
                "text": "Кандинский доступен каждому: просто напишите что хотите увидеть, и нейросеть создаст это за вас. Попробуйте сами и убедитесь в силе искусственного интеллекта!",
                "overlay": "Попробуйте сами"
            }
        ]
    }
    with open(script_path, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print('   Default script created')

# 2. TTS Generation
audio_path = os.path.join(TEMP_DIR, 'kandinsky_tts.mp3')
if os.path.exists(audio_path):
    print(f'2. TTS audio exists: {os.path.getsize(audio_path)/1024:.0f} KB')
else:
    print('2. Generating TTS...')
    full_text = ' '.join(s['text'] for s in script['scenes'])
    cmd = [sys.executable, TTS_FILE, '--text', full_text, '--output', audio_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'   TTS failed: {result.stderr[:200]}')
        print('   Using fallback: silence with sub titles')
        
        import numpy as np
        from scipy.io import wavfile
        
        sr = 16000
        duration = script['total_duration']
        silence = np.zeros(sr * duration, dtype=np.int16)
        wavfile.write(audio_path.replace('.mp3', '.wav'), sr, silence)
        audio_path = audio_path.replace('.mp3', '.wav')
        
        cmd2 = [FFMPEG, '-y', '-f', 's16le', '-ar', str(sr), '-ac', '1', '-i', audio_path, audio_path.replace('.wav', '.mp3')]
        subprocess.run(cmd2, capture_output=True)
        audio_path = audio_path.replace('.wav', '.mp3')
        print(f'   Fallback audio: {audio_path}')
    else:
        print(f'   TTS done: {os.path.getsize(audio_path)/1024:.0f} KB')

# 3. Prepare extended studio video
extended_video = os.path.join(TEMP_DIR, 'extended_30s.mp4')
studio_video = r'D:\Фото блогер\Видео0.mp4'
target_frames = int(script['total_duration'] * 25)

if not os.path.exists(extended_video):
    print(f'3. Extending studio video to {script["total_duration"]}s...')

    import cv2
    cap = cv2.VideoCapture(studio_video)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    
    usable = frames[10:100]
    extended = []
    for i in range(target_frames):
        extended.append(usable[i % len(usable)].copy())
    
    tmp_nosound = os.path.join(TEMP_DIR, 'extended_30s_nosound.mp4')
    h, w = extended[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(tmp_nosound, fourcc, 25, (w, h))
    for f in extended:
        out.write(f)
    out.release()
    
    subprocess.run([FFMPEG, '-y', '-i', tmp_nosound, '-i', audio_path, 
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                    '-shortest', extended_video], check=True)
    os.remove(tmp_nosound)
    print(f'   Extended video: {os.path.getsize(extended_video)/1024/1024:.1f} MB')
else:
    print(f'3. Extended video exists: {os.path.getsize(extended_video)/1024/1024:.1f} MB')

# 4. Wav2Lip
wav2lip_out = os.path.join(FINAL_DIR, 'kandinsky_wav2lip.mp4')
if not os.path.exists(wav2lip_out):
    print(f'4. Running Wav2Lip ({script["total_duration"]}s)...')
    cmd = [sys.executable, r'D:\OpenCode\Wav2Lip\run_inference.py']
    env = os.environ.copy()
    subprocess.run(cmd, env=env, check=True)
    print(f'   Wav2Lip done')
else:
    print(f'4. Wav2Lip output exists: {os.path.getsize(wav2lip_out)/1024/1024:.1f} MB')

# 5. Compose final video with scene backgrounds
final_out = os.path.join(FINAL_DIR, 'kandinsky_final.mp4')
print(f'5. Composing final video...')

import cv2
import numpy as np

def load_background(path, target_w=1080, target_h=1920):
    img = cv2.imread(os.path.join(REF_DIR, path))
    if img is None:
        img = cv2.imread(path)
    if img is None:
        print(f'   WARN: Cannot load background {path}, using black')
        return np.zeros((target_h, target_w, 3), dtype=np.uint8)
    h, w = img.shape[:2]
    scale = max(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    y = (new_h - target_h) // 2
    x = (new_w - target_w) // 2
    return resized[y:y+target_h, x:x+target_w]

def add_text_overlay(frame, text, position='top'):
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    thickness = 3
    color = (255, 255, 255)
    
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = (w - tw) // 2
    
    if position == 'top':
        text_y = 200
    else:
        text_y = h - 200
    
    bg_x1 = max(0, text_x - 40)
    bg_y1 = max(0, text_y - th - 20)
    bg_x2 = min(w, text_x + tw + 40)
    bg_y2 = min(h, text_y + 20)
    cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
    return frame

def fade_transition(frame_a, frame_b, t):
    return cv2.addWeighted(frame_a, 1 - t, frame_b, t, 0)

cap = cv2.VideoCapture(wav2lip_out)
wav2lip_frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    wav2lip_frames.append(frame)
cap.release()
print(f'   Wav2Lip frames: {len(wav2lip_frames)}')

total_frames = len(wav2lip_frames)
bg_cache = {}
scene_frames = len(wav2lip_frames) // 3
fade_frames = min(15, scene_frames // 4)

W, H = 1080, 1920
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
tmp_final = os.path.join(TEMP_DIR, 'final_nosound.mp4')
out = cv2.VideoWriter(tmp_final, fourcc, 25, (W, H))

for i in range(total_frames):
    # Determine current scene
    scene_idx = min(i // scene_frames, 2)
    scene = script['scenes'][scene_idx]
    
    # Background with crossfade between scenes
    bg_path = scene['background']
    if bg_path not in bg_cache:
        bg_cache[bg_path] = load_background(bg_path, W, H)
    bg = bg_cache[bg_path].copy()
    
    # Crossfade between scenes
    if scene_idx > 0 and scene_idx < len(script['scenes']):
        local_pos = i - scene_idx * scene_frames
        if local_pos < fade_frames:
            prev_bg_path = script['scenes'][scene_idx - 1]['background']
            if prev_bg_path not in bg_cache:
                bg_cache[prev_bg_path] = load_background(prev_bg_path, W, H)
            prev_bg = bg_cache[prev_bg_path]
            t = local_pos / fade_frames
            bg = fade_transition(prev_bg, bg, t)
    
    # Scale Wav2Lip frame to fill width
    w_frame = wav2lip_frames[i]
    w_h, w_w = w_frame.shape[:2]
    scale = W / w_w
    new_h = int(w_h * scale)
    w_scaled = cv2.resize(w_frame, (W, new_h), interpolation=cv2.INTER_LANCZOS4)
    
    # Create alpha mask for wav2lip person (non-black/non-border)
    gray = cv2.cvtColor(w_scaled, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    
    # Place person over background
    y_offset = (H - new_h) // 2
    canvas = bg.copy()
    if y_offset >= 0:
        person_region = canvas[y_offset:y_offset+new_h, :]
        mask_3ch = np.stack([mask/255.0]*3, axis=2)
        composited = (person_region * (1 - mask_3ch) + w_scaled * mask_3ch).astype(np.uint8)
        canvas[y_offset:y_offset+new_h, :] = composited
    
    # Add text overlay for scene title
    canvas = add_text_overlay(canvas, scene['overlay'])
    
    out.write(canvas)
    
    if (i + 1) % 100 == 0:
        print(f'   Frame {i+1}/{total_frames}')

out.release()

# Add audio
subprocess.run([FFMPEG, '-y', '-i', tmp_final, '-i', audio_path,
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', final_out], check=True)
os.remove(tmp_final)

sz = os.path.getsize(final_out)
print(f'\n=== Done! ===')
print(f'Final video: {final_out} ({sz/1024/1024:.1f} MB)')
print(f'Duration: {script["total_duration"]}s')
print(f'Scenes: {len(script["scenes"])}')
for s in script['scenes']:
    print(f'  {s["id"]}. [{s["start"]}s-{s["start"]+s["duration"]}s] {s["overlay"]}')
