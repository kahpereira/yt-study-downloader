import os
import yt_dlp
import re

def validate_url(url):
    youtube_regex = re.compile(
        r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'
    )
    return youtube_regex.match(url) is not None

def get_url():
    return input("Paste the URL here: ")

def get_directory():
    directory = input("Enter the directory: ").strip()
    if not directory:
        return "."
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def download_content(url, dir="."):
    options = {
        'outtmpl': f'{dir}/%(title)s.%(ext)s',
    }

    try:
        print(f"Analyzing the URL: {url} ...")
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        print("\nProcess completed!")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading content: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    print("--- YT Downloader ---")
    link = get_url()
    if validate_url(link):
        directory = get_directory()
        download_content(link, directory)
    else:
        print("Invalid URL. Please provide a valid YouTube URL.")