import sys
import time
from pprint import pprint
import json
import requests
from datetime import datetime


class VK:

    def __init__(self, version='5.131', count=5):
        self.version = version
        self.params = {'access_token': access_token_vk, 'v': self.version}
        self.count = count

    def users_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': f'{user_id}',
                  'album_id': 'profile',
                  'extended': 1,
                  'count': self.count,
                  'rev': 1}
        response = requests.get(url, params={**self.params, **params})
        return response.json()


class YaDisk:
    def __init__(self, photo_url, photo_likes):
        self.url_to_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.url_to_check_files_name = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        self.photo_url = photo_url
        self.photo_likes = photo_likes

    def upload(self):
        files_names = requests.get(self.url_to_check_files_name, headers=headers)
        tmp = []
        for i in files_names.json()['items']:
            tmp.append(i['name'])
        if self.photo_likes in tmp:
            date = datetime.now().strftime("%H_%M_%S")
            params = {'url': self.photo_url, 'path': f'photos_backup/{user_id}/{self.photo_likes} {date}'}
            resp = requests.post(url=self.url_to_upload, headers=headers, params=params)
            print(resp)
        else:
            params = {'url': self.photo_url, 'path': f'photos_backup/{user_id}/{self.photo_likes}'}
            resp = requests.post(url=self.url_to_upload, headers=headers, params=params)
            print(resp)
        names = requests.get(self.url_to_check_files_name, headers=headers)
        photos_data = []
        for image in names.json()['items']:
            if 'photos_backup' in image['path']:
                photos_data.append({'file_name': image['name'], 'size': image['size']})
        with open('result.json', 'w') as result:
            json.dump(photos_data, result)


if __name__ == '__main__':
    with open('vk_token.txt', 'r') as vk_token, \
            open('ya_token.txt', 'r') as ya_token:
        access_token_vk = vk_token.read().rstrip()
        access_token_ya = ya_token.read().rstrip()
    try:
        user_id = sys.argv[1]
    except IndexError:
        print('Use: <name_script> <user_id>')
        raise SystemExit
    headers = {'Content-Type': 'application/json',
               'Authorization': f'OAuth {access_token_ya}'}
    create_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    requests.put(create_dir_url,
                 headers=headers,
                 params={'path': f'photos_backup/{user_id}'})
    if len(sys.argv) < 3:
        vk = VK()
        photos = vk.users_photo()['response']['items']
    else:
        vk = VK(count=int(sys.argv[2]))
        photos = vk.users_photo()['response']['items']
    for item in photos:
        ya = YaDisk(photo_url=item['sizes'][-1]['url'],
                    photo_likes=str(item['likes']['count']) + '.jpg')
        ya.upload()
