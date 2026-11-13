from video_generator.pipeline import (
    generate_video,
    UserVideoParams,
    BackgroundCutFrequency,
)
from video_generator.media import BackgroundType
from video_generator.montage import FullVideoDuration, AudioSpeed

def main() -> None:
    video = generate_video(
        UserVideoParams(
            background_type=BackgroundType.IMAGE,
            background_freq=BackgroundCutFrequency.SINGLE,
            full_duration=FullVideoDuration.SHORT,
            speed=AudioSpeed.ORIGINAL,
            lyrics=False,
            emoji=False,
        )
    )
    print(video.path)

if __name__ == "__main__":
    main()