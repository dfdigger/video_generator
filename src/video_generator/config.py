# EXTENSIONS
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
VIDEO_EXTS = {".mp4", ".mov", ".webm"}
AUDIO_EXTS = {".mp3", ".m4a", ".wav"}
LYRICS_EXT = ".srt"

# PATHS
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"
TMP_DIR = PROJECT_ROOT / "tmp"
TMP_AUDIO_DIR = TMP_DIR / "audio"
TMP_VIDEO_DIR = TMP_DIR / "video"
TMP_VIDEO_CONCAT_DIR = TMP_VIDEO_DIR / "concat"
TMP_VIDEO_WITH_LYRICS_DIR = TMP_VIDEO_DIR / "with_lyrics"
TMP_VIDEO_WITH_EMOJI_DIR = TMP_VIDEO_DIR / "with_emoji"
TMP_VIDEO_OTHER_DIR = TMP_VIDEO_DIR / "other"