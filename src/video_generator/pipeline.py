from enum import Enum

class BackgroundCutFrequency(str, Enum):
    SINGLE = "single"
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"
    VERY_FAST = "very_fast"

# TODO: проверить корректность длительности видео и суммарной длительности фонов
def choose_backgrounds() -> None:
    pass

def choose_audio() -> None:
    pass

def generate_video(video_type: str) -> None:
    pass