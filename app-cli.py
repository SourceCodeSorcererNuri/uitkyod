import os
import subprocess

import instaloader


def main():
    site = input(
        "Qaysi saytdan videoni yuklan olmoqchisiz \nYoutube, Instagram, Facebook: "
    ).lower()

    if site == "youtube":
        download_youtube_video()
    elif site == "instagram":
        download_insta_video()
    elif site == "facebook":
        download_facebook_video()
    else:
        print("Noto'g'ri sayt nomi kiritildi!")


def download_youtube_video():
    ytLink = input("Youtube video linkini qo'ying: ")

    print("Video MP4 formatda yuklanmoqda...")
    # Download MP4 video using yt-dlp
    subprocess.run(
        [
            "yt-dlp",
            "-o",
            "%(title)s.%(ext)s",  # Save with the title as filename
            ytLink,
            "-f",
            "bestvideo+bestaudio",  # Best quality video and audio
        ]
    )

    print("Video yuklandi. Endi MP3 formatini chiqarib olamiz...")
    video_file = get_video_filename(ytLink)
    if video_file:
        extract_mp3_from_mp4(video_file)


def get_video_filename(ytLink):
    """Fetch the filename of the downloaded video"""
    video_title = ytLink.split("/")[-1]  # Basic parsing of video name (could be more robust)
    mp4_filename = f"{video_title}.mp4"
    if os.path.exists(mp4_filename):
        return mp4_filename
    print(f"{mp4_filename} topilmadi.")
    return None


def extract_mp3_from_mp4(mp4_filename):
    """Extract MP3 audio from the MP4 video"""
    mp3_filename = mp4_filename.replace(".mp4", ".mp3")
    # Using ffmpeg to extract MP3 from MP4
    try:
        subprocess.run(
            ["ffmpeg", "-i", mp4_filename, "-q:a", "0", "-map", "a", mp3_filename]
        )
        print(f"MP3 formatida saqlandi: {mp3_filename}")
    except Exception as e:
        print(f"MP3 chiqarish xatoligi: {e}")


def download_insta_video():
    igLink = input("Instagram video linkini qo'ying: ")

    try:
        L = instaloader.Instaloader()
        
        # Download Instagram post or reel
        post = instaloader.Post.from_shortcode(L.context, igLink.split("/")[-2])
        print(f"Yuklanayotgan video: {post.url}")
        
        # Save the post
        L.download_post(post, target="downloads")

        print("Instagram video muvaffaqiyatli yuklandi!")
    
    except Exception as e:
        print(f"Instagram video yuklanishda xatolik: {e}")


def download_facebook_video():
    fbLink = input("Facebook video linkini qo'ying: ")

    print("Video MP4 formatda yuklanmoqda...")
    # Download MP4 video from Facebook using yt-dlp
    subprocess.run(
        [
            "yt-dlp",
            "-o",
            "%(title)s.%(ext)s",  # Save with the title as filename
            fbLink,
            "-f",
            "bestvideo+bestaudio",  # Best quality video and audio
        ]
    )

    print("Video yuklandi. Endi MP3 formatini chiqarib olamiz...")
    video_file = get_video_filename(fbLink)
    if video_file:
        extract_mp3_from_mp4(video_file)


main()

