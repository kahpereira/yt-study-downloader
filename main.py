import os
import re
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str

def validate_url(url):
    youtube_regex = re.compile(
        r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'
    )
    return youtube_regex.match(url) is not None

@app.post("/download")
async def download_video(request: DownloadRequest):
    if not validate_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    temp_dir = tempfile.mkdtemp()
    
    try:
        options = {
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                    'skip': ['webpage']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'no_check_certificate': True,
            'no_warnings': False,
            'quiet': False,
        }

        cookies_file = os.getenv('YOUTUBE_COOKIES_FILE')
        if cookies_file and os.path.exists(cookies_file):
            options['cookiefile'] = cookies_file
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(request.url, download=True)
            filename = ydl.prepare_filename(info)
        if os.path.exists(filename):
            return FileResponse(
                path=filename,
                media_type='application/octet-stream',
                filename=os.path.basename(filename),
                background=None
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to download video")
            
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Error downloading content: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "YouTube Downloader API - Use POST /download with {url: 'youtube_url'}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
