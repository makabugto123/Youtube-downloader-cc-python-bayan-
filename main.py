from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import yt_dlp
import os
import time
import json
import concurrent.futures
import threading

class MyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path.startswith('/ytdl'):
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                if 'url' in params and 'type' in params:
                    video_url = params['url'][0]
                    media_type = params['type'][0]
                    timestamp = str(int(time.time()))

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(self.download_and_convert, video_url, timestamp, media_type)
                        media_filename, title = future.result()

                    download_url = f"https://{self.headers.get('Host')}/download/{timestamp}.{media_type}"

                    response_data = {
                        'url': video_url,
                        'download': download_url,
                        'title': title,
                        'response': f'Time Response: {time.ctime()}',
                    }

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())

                    threading.Thread(target=self.delete_file, args=(timestamp, media_type)).start()
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Missing URL or type parameter'}).encode())
            elif self.path.startswith('/download/'):
                timestamp = self.path.split('/')[-1].split('.')[0]
                media_type = self.path.split('.')[-1]
                file_path = f'downloads/{timestamp}.{media_type}'

                if os.path.exists(file_path):
                    if media_type == 'mp3':
                        self.send_response(200)
                        self.send_header('Content-type', 'audio/mp3')
                    elif media_type == 'mp4':
                        self.send_response(200)
                        self.send_header('Content-type', 'video/mp4')
                    else:
                        self.send_response(415)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Unsupported media type'}).encode())
                        return

                    self.send_header('Content-Disposition', f'inline; filename="{timestamp}.{media_type}"')
                    self.end_headers()
                    with open(file_path, 'rb') as file:
                        self.wfile.write(file.read())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'File not found'}).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not Found'}).encode())

        def download_and_convert(self, url, timestamp, media_type):
            cookies_file = 'cookies.txt'
            ydl_opts = {
                'outtmpl': f'downloads/{timestamp}.%(ext)s',
                'quiet': True,
                'concurrent_fragment_downloads': 4,
                'noplaylist': True,
                'cookiefile': cookies_file if os.path.exists(cookies_file) else None,
            }
            if media_type == 'mp3':
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif media_type == 'mp4':
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                title = info_dict.get('title', 'Unknown Title')
                for file in os.listdir('downloads'):
                    if file.startswith(timestamp) and (file.endswith('.webm') or file.endswith('.mkv')):
                        os.rename(f'downloads/{file}', f'downloads/{timestamp}.mp4')

            return f"{timestamp}.{media_type}", title

        def delete_file(self, timestamp, media_type):
            file_path = f'downloads/{timestamp}.{media_type}'
            time.sleep(300)
            if os.path.exists(file_path):
                os.remove(file_path)

def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f'Starting server on port {port}...')
        httpd.serve_forever()

if __name__ == '__main__':
        run()
