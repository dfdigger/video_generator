from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import random

class BackgroundType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"

@dataclass
class Background:
    path: Path
    type_: BackgroundType

@dataclass
class Audio:
    path: Path
    lyrics_path: Path

def pick_random_image(folder: Path, exts: set[str]) -> Background:
    images = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in exts]
    if not images:
        raise FileNotFoundError(f"No images found in {folder}")

    return Background(path=random.choice(images), type_=BackgroundType.IMAGE)

def pick_random_video(folder: Path, exts: set[str]) -> Background:
    videos = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in exts]
    if not videos:
        raise FileNotFoundError(f"No videos found in {folder}")

    return Background(path=random.choice(videos), type_=BackgroundType.VIDEO)

def pick_random_audio(folder: Path, exts: set[str], lyrics_ext: str = ".srt") -> Audio:
    names = {f for f in folder.iterdir() if f.is_file()}
    songs = []
    for name in names:
        path = folder / name
        if path.suffix.lower() not in exts:
            continue
        lyrics = path.stem + lyrics_ext
        if lyrics in names:
            songs.append(Audio(path=path, lyrics_path=folder / lyrics))

    if not songs:
        raise FileNotFoundError(f"No songs found in {folder}")

    return random.choice(songs)