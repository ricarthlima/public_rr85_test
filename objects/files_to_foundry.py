import os
import shutil
from pathlib import Path
from PIL import Image
import imageio_ffmpeg as ffmpeg
from pydub import AudioSegment
from tqdm import tqdm

def scan_files(root_dir):
    files_catalog = []
    total_files = 0
    for path in Path(root_dir).rglob("*.*"):
        if "output" not in path.parts:
            files_catalog.append(path)
            total_files += 1
    return files_catalog, total_files

def convert_image(input_path, output_path):
    img = Image.open(input_path)
    img.save(output_path, "WEBP", quality=85, lossless=False)

def convert_video(input_path, output_path):
    command = (
        f'ffmpeg -i "{input_path}" -c:v libvpx-vp9 -b:v 1M -c:a libopus "{output_path}"'
    )
    os.system(command)

def convert_audio(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="ogg", bitrate="128k")

def process_files(root_dir, output_dir):
    files_catalog, total_files = scan_files(root_dir)
    processed_files = 0
    
    for file_path in tqdm(files_catalog, desc="Convertendo arquivos", unit="arquivo"):
        rel_path = file_path.relative_to(root_dir)
        
        if file_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            output_path = output_dir / rel_path.with_suffix(".webp")
        elif file_path.suffix.lower() in [".mp4", ".mov"]:
            output_path = output_dir / rel_path.with_suffix(".webm")
        elif file_path.suffix.lower() in [".mp3", ".wav"]:
            output_path = output_dir / rel_path.with_suffix(".ogg")
        else:
            output_path = output_dir / rel_path  # Copia arquivos que não precisam de conversão
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.exists():
            continue  # Pula arquivos já convertidos
        
        try:
            if file_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                convert_image(file_path, output_path)
            elif file_path.suffix.lower() in [".mp4", ".mov"]:
                convert_video(file_path, output_path)
            elif file_path.suffix.lower() in [".mp3", ".wav"]:
                convert_audio(file_path, output_path)
            else:
                shutil.copy(file_path, output_path)  # Copia outros arquivos sem conversão
            
            processed_files += 1
        except Exception as e:
            print(f"Erro ao converter {file_path}: {e}")
    
    print(f"Processo concluído! {processed_files}/{total_files} arquivos convertidos.")

if __name__ == "__main__":
    root_directory = Path(os.getcwd())
    output_directory = root_directory / "output"
    process_files(root_directory, output_directory)
