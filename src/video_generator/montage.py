from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import subprocess

from .media import Background, Audio, BackgroundType
from .config import TMP_VIDEO_CONCAT_DIR, TMP_AUDIO_DIR, OUTPUT_DIR

class AudioSpeed(str, Enum):
    SLOWED = "slowed"
    ORIGINAL = "original"
    SPEEDED_UP = "speeded_up"

# Montage Effects
@dataclass
class MontageParams:
    lyrics: bool
    emoji: bool
    # start_fade_in: bool
    # end_fade_out: bool

class FullVideoDuration(float, Enum):
    SHORT = 5       # секунды
    STANDARD = 10   # секунды
    LONG = 15       # секунды

@dataclass
class BackgroundConfig:
    background_type: BackgroundType
    background_assets: list[Background]
    full_duration: FullVideoDuration        # длительность итогового видео
    duration_per_asset: float               # должен быть <= для любого background_asset[i]

@dataclass
class AudioConfig:
    speed: AudioSpeed
    audio_asset: Audio
    full_duration: FullVideoDuration        # длительность итогового видео

@dataclass
class Video:
    path: Path
    duration: FullVideoDuration            # длительность итогового видео
    background: Background
    audio: Audio
    montage_params: MontageParams
    background_config: BackgroundConfig
    audio_config: AudioConfig

class Montage:
    def __init__(
        self,
        background_config: BackgroundConfig,
        audio_config: AudioConfig,
        montage_params: MontageParams
    ):
        if background_config.full_duration != audio_config.full_duration:
            raise ValueError(
                "Background and audio durations differ: "
                f"{background_config.full_duration} != {audio_config.full_duration}"
            )

        self.background_config = background_config
        self.audio_config = audio_config
        self.montage_params = montage_params

    def concat_video_backgrounds(self) -> Background:
        background_type = self.background_config.background_type

        if background_type != BackgroundType.VIDEO:
            raise ValueError(f"Background type is not video, but {background_type}")

        cfg = self.background_config
        assets = cfg.background_assets
        d = cfg.duration_per_asset
        n = len(assets)
        TMP_VIDEO_CONCAT_DIR.mkdir(parents=True, exist_ok=True)
        out = TMP_VIDEO_CONCAT_DIR / "background_mid_montage.mp4" # TODO: изменить имя файла

        cmd: list[str] = ["ffmpeg", "-y"]
        for asset in assets:
            cmd += ["-i", str(asset.path)]

        parts: list[str] = []
        labels: list[str] = []
        for i in range(n):
            parts.append(
                f"[{i}:v]trim=duration={d},setpts=PTS-STARTPTS,"
                f"scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,setsar=1,fps=30[v{i}]"
            )
            labels.append(f"[v{i}]")

        parts.append(f"{''.join(labels)}concat=n={n}:v=1:a=0[outv]")
        cmd += [
            "-filter_complex", ";".join(parts),
            "-map", "[outv]",
            "-an",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(out),
        ]
        subprocess.run(cmd, check=True)

        return Background(path=out, type_=BackgroundType.VIDEO, duration=cfg.full_duration.value)
        

    def concat_image_backgrounds(self) -> Background:
        background_type = self.background_config.background_type

        if background_type != BackgroundType.IMAGE:
            raise ValueError(f"Background type is not image, but {background_type}")

        cfg = self.background_config
        assets = cfg.background_assets
        d = cfg.duration_per_asset
        n = len(assets)
        TMP_VIDEO_CONCAT_DIR.mkdir(parents=True, exist_ok=True)
        out = TMP_VIDEO_CONCAT_DIR / "background_mid_montage.mp4" # TODO: изменить имя файла

        cmd: list[str] = ["ffmpeg", "-y"]
        for asset in assets:
            cmd += ["-loop", "1", "-framerate", "30", "-t", str(d), "-i", str(asset.path)]

        parts: list[str] = []
        labels: list[str] = []
        for i in range(n):
            parts.append(
                f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,setsar=1,fps=30,setpts=PTS-STARTPTS[v{i}]"
            )
            labels.append(f"[v{i}]")

        parts.append(f"{''.join(labels)}concat=n={n}:v=1:a=0[outv]")
        cmd += [
            "-filter_complex", ";".join(parts),
            "-map", "[outv]",
            "-an",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(out),
        ]
        subprocess.run(cmd, check=True)

        return Background(path=out, type_=BackgroundType.VIDEO, duration=cfg.full_duration.value)

    def add_lyrics(self, background: Background) -> Background:
        pass

    def add_emoji(self, background: Background) -> Background:
        pass

    def cut_audio(self) -> Audio:
        cfg = self.audio_config
        audio_asset = cfg.audio_asset
        speed = cfg.speed
        duration = cfg.full_duration.value
        TMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        out = TMP_AUDIO_DIR / "audio_mid_montage.mp3" # TODO: изменить имя файла

        if speed == AudioSpeed.SLOWED:
            audio_asset = audio_asset.slowed()
        elif speed == AudioSpeed.SPEEDED_UP:
            audio_asset = audio_asset.speeded_up()
        elif speed == AudioSpeed.ORIGINAL:
            audio_asset = audio_asset.original()
        else:
            raise ValueError(f"Invalid audio speed: {speed}")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", str(audio_asset.path),
                "-t", str(duration),
                "-c:a", "libmp3lame",
                str(out),
            ],
            check=True,
        )

        return Audio(path=out, lyrics_path=audio_asset.lyrics_path, duration=duration)


    def make_video(self, background: Background, audio: Audio) -> Video:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUTPUT_DIR / "final.mp4"  # TODO: изменить имя файла
        cfg = self.audio_config
        duration = cfg.full_duration

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", str(background.path),
                "-i", str(audio.path),
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-movflags", "+faststart",
                str(out),
            ],
            check=True,
        )

        return Video(
            path=out,
            duration=duration,
            background=background,
            audio=audio,
            montage_params=self.montage_params,
            background_config=self.background_config,
            audio_config=self.audio_config,
        )

    def render(self) -> Video:
        if self.background_config.background_type == BackgroundType.VIDEO:
            background = self.concat_video_backgrounds()
        else:
            background = self.concat_image_backgrounds()

        if self.montage_params.lyrics:
            background = self.add_lyrics(background)
        if self.montage_params.emoji:
            background = self.add_emoji(background)

        audio = self.cut_audio()
        return self.make_video(background, audio)