from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import random
import subprocess

INF = float('inf')

class BackgroundType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"

@dataclass
class Background:
    path: Path
    type_: BackgroundType
    duration: float = INF

@dataclass
class Audio:
    path: Path
    lyrics_path: Path
    duration: float

    def slowed(self) -> "Audio":
        pass

    def speeded_up(self) -> "Audio":
        pass

    def original(self) -> "Audio":
        return self

def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()

    if not value or value == "N/A":
        raise RuntimeError(f"No duration for {path}")

    return float(value)

def pick_random_image(folder: Path, exts: set[str]) -> Background:
    images = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in exts]
    if not images:
        raise FileNotFoundError(f"No images found in {folder}")

    return Background(path=random.choice(images), type_=BackgroundType.IMAGE)

def pick_random_video(folder: Path, exts: set[str]) -> Background:
    videos = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in exts]
    if not videos:
        raise FileNotFoundError(f"No videos found in {folder}")

    path = random.choice(videos)
    return Background(
        path=path, 
        type_=BackgroundType.VIDEO,
        duration=probe_duration(path)
    )

def pick_random_audio(folder: Path, exts: set[str], lyrics_ext: str = ".srt") -> Audio:
    names = {f for f in folder.iterdir() if f.is_file()}
    songs = []
    for name in names:
        path = folder / name
        if path.suffix.lower() not in exts:
            continue
        
        lyrics_path = path.with_suffix(lyrics_ext)
        if lyrics_path in names:
            songs.append(Audio(path=path, lyrics_path=lyrics_path, duration=probe_duration(path)))

    if not songs:
        raise FileNotFoundError(f"No songs found in {folder}")

    return random.choice(songs)