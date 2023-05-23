import sys
import csv
import os
import re
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
from datetime import datetime
from colorama import Fore, Style

def get_metadata(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forceurl': True,
        'forcetitle': True,
        'forcedescription': True,
        'writeinfojson': True,
        'simulate': True,
        'youtube_include_dash_manifest': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(url, download=False)
            return meta
        except Exception:
            print(f"{Fore.RED}Failed to get metadata for {url}{Style.RESET_ALL}")
            return None

def parse_html(input_file, output_file, resume=False):
    with open(input_file, "r") as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')
    divs = soup.find_all('div', {'class': 'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1'})

    if resume:
        last_processed_index = get_last_processed_index(output_file)
        if last_processed_index is None:
            print(f"{Fore.YELLOW}Unable to determine the last processed index. Resuming from the beginning.{Style.RESET_ALL}")
            last_processed_index = 0
        else:
            last_processed_index += 1
        divs = divs[last_processed_index:]

    # Open CSV writer in append mode
    with open(output_file, 'a', newline='') as file:
        writer = csv.writer(file)

        try:
            for index, div in enumerate(divs, last_processed_index):
                link = div.find('a', href=re.compile(r'https://www.youtube.com/watch\?v=.+'))
                if link:
                    print(f"{Fore.GREEN}Parsing: {link['href']}{Style.RESET_ALL}")
                    meta = get_metadata(link['href'])

                    text_list = div.text.split('\n')
                    timestamp_text = None
                    for text in text_list:
                        if "WIB" in text:
                            timestamp_text = text.split("WIB")[0].strip().replace(',', '').replace('\xa0', ' ')
                            break

                    if timestamp_text:
                        dt_obj = datetime.strptime(timestamp_text, '%b %d %Y %I:%M:%S %p')
                        timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

                        # Get the album, artist, and track details
                        artist = ""
                        track = ""
                        album = ""
                        duration = ""
                        if meta:
                            if 'artist' in meta:
                                artist = meta['artist']
                            if 'track' in meta:
                                track = meta['track']
                            if 'album' in meta:
                                album = meta['album']
                            if 'duration' in meta:
                                duration = str(meta['duration'])

                        # Skip the div if artist or track is empty
                        if not artist or not track:
                            print(f"{Fore.YELLOW}Skipping empty artist or track{Style.RESET_ALL}")
                            continue

                        row = [artist, track, album, timestamp, artist, duration]
                        writer.writerow(row)
                        print(row)

                # Save the index of the last processed div
                save_last_processed_index(output_file, index)

        except KeyboardInterrupt:
            print(f"{Fore.RED}Parsing interrupted by user.{Style.RESET_ALL}")

    print(f"{Fore.GREEN}Parsing complete.{Style.RESET_ALL}")

def get_last_processed_index(output_file):
    progress_file = f"{output_file}.progress"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as file:
            last_index = file.read()
            if last_index.isdigit():
                return int(last_index)
    return None

def save_last_processed_index(output_file, index):
    progress_file = f"{output_file}.progress"
    with open(progress_file, 'w') as file:
        file.write(str(index))

def main(input_file, output_file):
    parse_html(input_file, output_file, resume=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
