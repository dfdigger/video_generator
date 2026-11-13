from enum import Enum
from dataclasses import dataclass

from .media import (
    Audio, 
    Background, 
    BackgroundType, 
    pick_random_audio, 
    pick_random_image, 
    pick_random_video
)
from .montage import (
    BackgroundConfig, 
    AudioConfig, 
    MontageParams, 
    FullVideoDuration, 
    AudioSpeed, 
    Video, 
    Montage
)
from .config import (
    ASSETS_AUDIO_DIR, 
    ASSETS_BACKGROUNDS_IMAGES_DIR, 
    ASSETS_BACKGROUNDS_VIDEOS_DIR, 
    IMAGE_EXTS, 
    VIDEO_EXTS, 
    AUDIO_EXTS
)

class BackgroundCutFrequency(int, Enum):
    SINGLE = 1
    SLOW = 5
    MEDIUM = 10
    FAST = 20
    VERY_FAST = 30

ALLOWED_FREQUENCIES: dict[BackgroundType, frozenset[BackgroundCutFrequency]] = {
    BackgroundType.IMAGE: frozenset(BackgroundCutFrequency),
    BackgroundType.VIDEO: frozenset({
        BackgroundCutFrequency.SINGLE,
        BackgroundCutFrequency.SLOW,
        BackgroundCutFrequency.MEDIUM,
    }),
}

def allowed_frequencies(kind: BackgroundType) -> frozenset[BackgroundCutFrequency]:
    return ALLOWED_FREQUENCIES[kind]

def ensure_frequency(kind: BackgroundType, freq: BackgroundCutFrequency) -> None:
    if freq not in ALLOWED_FREQUENCIES[kind]:
        raise ValueError(
            f"{freq.value} is not allowed for {kind.value} background"
        )

# TODO: улучшить логику выбора (предотвратить выбор одного и того же фонового изображения)
def choose_image_backgrounds(freq: BackgroundCutFrequency) -> list[Background]:
    ensure_frequency(BackgroundType.IMAGE, freq)

    return [pick_random_image(ASSETS_BACKGROUNDS_IMAGES_DIR, IMAGE_EXTS) for _ in range(freq.value)]

# TODO: улучшить логику выбора (предотвратить выбор одного и того же фонового видео)
def choose_video_backgrounds(freq: BackgroundCutFrequency, duration: FullVideoDuration) -> list[Background]:
    ensure_frequency(BackgroundType.VIDEO, freq)

    videos = []
    duration_per_asset = duration.value / freq.value

    # TODO: поставить лимит попыток (предотвратить бесконечный цикл)
    while len(videos) < freq.value:
        video = pick_random_video(ASSETS_BACKGROUNDS_VIDEOS_DIR, VIDEO_EXTS)
        if video.duration <= duration_per_asset:
            videos.append(video)

    return videos

def choose_audio(duration: FullVideoDuration) -> Audio | None:
    audio = None

    # TODO: поставить лимит попыток (предотвратить бесконечный цикл)
    while audio is None:
        audio = pick_random_audio(ASSETS_AUDIO_DIR, AUDIO_EXTS)
        if audio.duration <= duration.value:
            return audio

    return None

def make_background_config(
    background_type: BackgroundType, 
    background_assets: list[Background], 
    full_duration: FullVideoDuration) -> BackgroundConfig:

    if len(background_assets) == 0:
        raise ValueError("No background assets provided")

    return BackgroundConfig(
        background_type=background_type,
        background_assets=background_assets,
        full_duration=full_duration,
        duration_per_asset=full_duration.value / len(background_assets)
    )

def make_audio_config(
    speed: AudioSpeed,
    audio_asset: Audio,
    full_duration: FullVideoDuration) -> AudioConfig:

    return AudioConfig(
        speed=speed,
        audio_asset=audio_asset,
        full_duration=full_duration
    )

def make_montage_params(
    lyrics: bool,
    emoji: bool) -> MontageParams:

    return MontageParams(
        lyrics=lyrics,
        emoji=emoji
    )


@dataclass
class UserVideoParams:
    background_type: BackgroundType             # тип фонового видео или изображения
    background_freq: BackgroundCutFrequency     # частота смены фоновых видео или изображений
    full_duration: FullVideoDuration            # длительность итогового видео
    speed: AudioSpeed                           # скорость аудио
    lyrics: bool                                # включить ли тексты песен
    emoji: bool                                 # включить ли эмодзи

def generate_video(user_video_params: UserVideoParams) -> Video:
    background_assets = None
    if user_video_params.background_type == BackgroundType.VIDEO:
        background_assets = choose_video_backgrounds(user_video_params.background_freq, user_video_params.full_duration)
    else:
        background_assets = choose_image_backgrounds(user_video_params.background_freq)

    if background_assets is None:
        raise ValueError("Failed to choose background assets")

    audio = choose_audio(user_video_params.full_duration)
    if audio is None:
        raise ValueError("Failed to choose audio")

    montage_params = make_montage_params(user_video_params.lyrics, user_video_params.emoji)
    background_config = make_background_config(user_video_params.background_type, background_assets, user_video_params.full_duration)
    audio_config = make_audio_config(user_video_params.speed, audio, user_video_params.full_duration)

    montager = Montage(background_config, audio_config, montage_params)

    return montager.render()