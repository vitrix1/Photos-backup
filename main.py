import shutil
import sys
from tqdm import tqdm
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import os


class VK:

    def __init__(self, count=5, album_id='profile', version='5.131'):
        with open('vk_token.txt', 'r') as vk_token:
            self.access_token_vk = vk_token.read().rstrip()
        self.version = version
        self.count = count
        self.params = {'access_token': self.access_token_vk,
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

    def __init__(self, picture):
        self.url_to_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.url_to_check_files_name = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        self.photo_url = picture['sizes'][-1]['url']
        self.photo_likes = str(picture['likes']['count'])
        self.size = picture['sizes'][-1]['type']
        with open('ya_token.txt', 'r') as ya_token:
            self.access_token_ya = ya_token.read().rstrip()
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'OAuth {self.access_token_ya}'}
        self.create_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'

        # create a remote dir on YaDisk for future uploads
        requests.put(url=self.create_dir_url,
                     headers=self.headers,
                     params={'path': f'photos_backup/{user_id}'})

    def upload(self):
        tmp = []
        files_names = requests.get(self.url_to_check_files_name, headers=self.headers)
        for i in files_names.json()['items']:
            tmp.append(i['name'])
        if self.photo_likes + '.jpg' in tmp:
            date = datetime.now().strftime("%H_%M_%S")
            params = {'url': self.photo_url, 'path': f'photos_backup/{user_id}/{self.photo_likes} {date}.jpg'}
            requests.post(url=self.url_to_upload, headers=self.headers, params=params)
            photos_data.append({'file_name': f'{self.photo_likes} {date}.jpg', 'size': self.size})
        else:
            params = {'url': self.photo_url, 'path': f'photos_backup/{user_id}/{self.photo_likes}.jpg'}
            requests.post(url=self.url_to_upload, headers=self.headers, params=params)
            photos_data.append({'file_name': f'{self.photo_likes}.jpg', 'size': self.size})


class GoogleDisk:

    def __init__(self, picture):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.SERVICE_ACCOUNT_FILE = 'photos-backup-364304-93dd16f41f18.json'
        self.folder_id = '1Pg40ke6wuv9q6Q2IBgWekz5YNALBlJyj'
        self.credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.picture = picture

        # download photo from VK and save it in tmp_dir
        self.pic = requests.get(self.picture['sizes'][-1]['url'])
        # check the same names in tmp_dir
        if (str(self.picture['likes']['count']) + '.jpg') not in tmp_dir:
            self.path = f"tmp_dir/{str(self.picture['likes']['count'])}.jpg"
            with open(self.path, "wb") as f:
                f.write(self.pic.content)
        else:
            self.current_date = datetime.now().strftime("%H_%M_%S")
            self.path = f"tmp_dir/{str(self.picture['likes']['count'])} {self.current_date}.jpg"
            with open(self.path, "wb") as f:
                f.write(self.pic.content)

    def upload(self):
        name = self.path.split('/')[-1]
        file_path = self.path
        file_metadata = {
            'name': name,
            'parents': [self.folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        photos_data.append({'file_name': self.path.split('/')[-1], 'size': self.picture['sizes'][-1]['type']})


if __name__ == '__main__':
    photos_data = []
    try:
        user_id = sys.argv[1]
    except IndexError:
        print('Use: <name_script> <user_id>' 'y/g')
        raise SystemExit
    vk = VK()
    photos = vk.users_photo()['response']['items']
    os.mkdir('tmp_dir')
    tmp_dir = os.listdir('tmp_dir')
    for photo in tqdm(photos, desc="Upload", colour="white"):
        if sys.argv[2] == 'y':
            ya = YaDisk(photo)
            ya.upload()
        elif sys.argv[2] == 'g':
            g = GoogleDisk(photo)
            g.upload()
        else:
            print('Use: <name_script> <user_id>' 'y/g')
            raise SystemExit
    with open('result.json', 'a') as result:
        json.dump(photos_data, result)
    shutil.rmtree('tmp_dir')
