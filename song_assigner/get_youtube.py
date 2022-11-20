
from tempfile import TemporaryDirectory

import subprocess

import os.path as osp

def parse_file_metadata(file):

    artists, names, urls = [], [], []

    with open(file) as f:
        for line in f:
            try:
                if line == '\n': continue
            
                artist, name, url = line.strip().split('\t')
                artists.append(artist)
                names.append(name)
                urls.append(url)
            except:
                print('Error in line:', line)

    return artists, names, urls


def parse_file(file):

    urls = []

    with open(file) as f:
        for line in f:
            try:
                if line == '\n': continue
            
                tmp = line.strip().split('\t')
                for t in tmp:
                    if t.startswith('https://') or t.startswith('www.'):
                        urls.append(t)
            except:
                print('Error in line:', line)

    return urls


def download_youtube(urls, tmp_dir):
    
    for i, url in enumerate(urls):
        print('downloading #', i, 'with URL', url)
        try:
            subprocess.run(['youtube-dl', '--rm-cache-dir'])
            subprocess.run(['youtube-dl', '-x', '--download-archive', osp.join(tmp_dir, 'downloaded.txt'), '--audio-format','mp3', '-o',osp.join(tmp_dir, '%(title)s.%(ext)s'), '--rm-cache-dir', url])
        except: 
            print(url, 'failed to download')




if __name__ == '__main__':
    
    urls = parse_file('example_song_list.txt')
    #print(urls)
    
    temp_dir = TemporaryDirectory()
    
    download_youtube(urls, 'tmp') #temp_dir.name)
    
    #print(temp_dir.name)
    
    
    
    