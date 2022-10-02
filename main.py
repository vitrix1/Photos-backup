import shutil
import sys
from tqdm import tqdm
from pprint import pprint
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import os


class VK:

    def __init__(self, count=5, album_id='profile', version='5.131'):
        self.version = version
        self.count = count
        self.params = {'access_token': access_token_vk,
                       'v': self.version,
                       'album_id': album_id}

    def users_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': f'{user_id}',
                  'extended': 1,
                  'count': self.count,
                  'rev': 1}
        response = requests.get(url, params={**self.params, **params})
        if 'error' not in response.json().keys():
            return response.json()
        else:
            print('Error in VK response')
            raise SystemExit


class YaDisk:
    def __init__(self, photo_url, photo_likes, size):
        self.url_to_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.url_to_check_files_name = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        self.photo_url = photo_url
        self.photo_likes = photo_likes
        self.size = size

    def upload(self):
        files_names = requests.get(self.url_to_check_files_name, headers=headers)
        tmp = []
        for i in files_names.json()['items']:
            tmp.append(i['name'])
        if self.photo_likes + '.jpg' in tmp:
            date = datetime.now().strftime("%H_%M_%S")
            params = {'url': self.photo_url, 'path': f'photos_backup/{user_id}/{self.photo_likes} {date}.jpg'}
            requests.post(url=self.url_to_upload, headers=headers, params=params)
            photos_data.append({'file_name': f'{self.photo_likes} {date}.jpg', 'size': self.size})
        else:
            params = {'url': self.photo_url, 'path': f'photos_backup/{user_id}/{self.photo_likes}.jpg'}
            requests.post(url=self.url_to_upload, headers=headers, params=params)
            photos_data.append({'file_name': f'{self.photo_likes}.jpg', 'size': self.size})


class GoogleDiskUpload:
    def __init__(self):
        folder_id = '1Pg40ke6wuv9q6Q2IBgWekz5YNALBlJyj'
        name = path.split('/')[-1]
        file_path = path
        file_metadata = {
            'name': name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()


if __name__ == '__main__':
    photos_data = []
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'photos-backup-364304-e5b0eac5fc3d.json'
    with open('vk_token.txt', 'r') as vk_token, \
            open('ya_token.txt', 'r') as ya_token:
        access_token_vk = vk_token.read().rstrip()
        access_token_ya = ya_token.read().rstrip()
    try:
        user_id = sys.argv[1]
    except IndexError:
        print('Use: <name_script> <user_id>' 'y/g')
        raise SystemExit
    vk = VK()
    photos = vk.users_photo()['response']['items']
    os.mkdir('tmp_data')
    files = os.listdir('tmp_data')
    for item in tqdm(photos, desc="Upload", colour="white"):
        if sys.argv[2] == 'y':
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {access_token_ya}'}
            create_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'
            requests.put(create_dir_url,
                         headers=headers,
                         params={'path': f'photos_backup/{user_id}'})
            ya = YaDisk(photo_url=item['sizes'][-1]['url'],
                        photo_likes=str(item['likes']['count']),
                        size=item['sizes'][-1]['type'])
            ya.upload()
        elif sys.argv[2] == 'g':
            p = requests.get(item['sizes'][-1]['url'])
            if (str(item['likes']['count']) + '.jpg') not in files:
                path = f"tmp_data/{str(item['likes']['count'])}.jpg"
                with open(path, "wb") as f:
                    f.write(p.content)
            else:
                current_date = datetime.now().strftime("%H_%M_%S")
                path = f"tmp_data/{str(item['likes']['count'])} {current_date}.jpg"
                with open(path, "wb") as f:
                    f.write(p.content)
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('drive', 'v3', credentials=credentials)
            results = service.files().list(pageSize=1, fields="files(parents)").execute()
            g = GoogleDiskUpload()
            photos_data.append({'file_name': path.split('/')[-1], 'size': item['sizes'][-1]['type']})
        else:
            print('Use: <name_script> <user_id>' 'y/g')
            raise SystemExit
    with open('result.json', 'a') as result:
        json.dump(photos_data, result)
    shutil.rmtree('tmp_data')