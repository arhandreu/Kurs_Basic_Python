import requests
import json
from datetime import datetime
from progress.bar import Bar
import uploader_google


with open('token.txt', 'r') as file:
    tokenVK = file.readline().strip()
    tokenYa = file.readline().strip()


class Vkontakte:
    def __init__(self, token=tokenVK, version='5.131'):
        self.params = {
            'access_token': token,
            'v': version,
        }

    def info_photo(self, owner_id=None, album_id='profile'):
        url = 'https://api.vk.com/method/photos.get'
        params_photo_load = {
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': '1',
            'photo_sizes': '1',
        }
        return requests.get(url, params={**self.params, **params_photo_load}).json()

    def save_in_json_file(self, owner_id=None, file_s=True, album_id='profile'):
        res = self.info_photo(owner_id=owner_id, album_id=album_id)
        json_data = []
        for i in range(int(res['response']['count'])):
            size = 0
            for j in range(len(res["response"]["items"][i]["sizes"])):
                if res["response"]["items"][i]["sizes"][j]["height"]*res["response"]["items"][i]["sizes"][j]["width"] > size:
                    size = res["response"]["items"][i]["sizes"][j]["height"]*res["response"]["items"][i]["sizes"][j]["width"]
                    sizes_count = j
            json_data.append({
                'file_name': f'{str(res["response"]["items"][i]["likes"]) + ".jpg"}',
                'size': res["response"]["items"][i]["sizes"][sizes_count],
                })
        if file_s:
            with open('photo.json', 'w') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
        else:
            json_data = sorted(json_data, key=lambda photo: photo["size"]["height"] * photo["size"]["width"])
            return json_data

    def save_photo(self, owner_id=None, album_id='profile', count_photo=5, path='images/'):
        json_data = self.save_in_json_file(owner_id=owner_id, file_s=False, album_id=album_id)
        for i in range(count_photo):
            with open(f'{path + json_data[i]["file_name"]}', 'wb') as image:
                image.write(requests.get(json_data[i]["size"]["url"]).content)

    def upload_in_ya(self, token_ya, owner_id=None, album_id='profile', count_photo=5):
        uploader = YandexDisk(token_ya)
        json_data = self.save_in_json_file(owner_id=owner_id, file_s=False, album_id=album_id)
        bar = Bar('Загрузка', max=count_photo)
        folder = uploader.create_folder()
        for i in range(count_photo):
            uploader.upload(folder, json_data[i]["file_name"], json_data[i]["size"]["url"])
            bar.next()
        bar.finish()

    def upload_in_google(self, token='token.json', folder_name=datetime.now().strftime("%Y-%m-%d_%H-%M"), owner_id=None, album_id='profile', count_photo=5):
        uploader_goog = uploader_google.create_uploader(token)
        id = uploader_google.create_folder(uploader_goog, folder_name)
        json_data = self.save_in_json_file(owner_id=owner_id, file_s=False, album_id=album_id)
        for i in range(count_photo):
            uploader_google.upload(uploader_goog, id, json_data[i]["size"]["url"], json_data[i]["file_name"])


class YandexDisk:
    def __init__(self, token):
        self.token = token
        self.URL = 'https://cloud-api.yandex.net:443/'
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}',
        }

    def upload(self, folder, file_name, url):
        requests.post(self.URL + "v1/disk/resources/upload", headers=self.headers, params={'path': folder + '/' + file_name, 'url': url})

    def create_folder(self, folder_name=datetime.now().strftime("%Y-%m-%d_%H-%M")):
        requests.put(self.URL + "v1/disk/resources", headers=self.headers, params={'path': folder_name})
        return folder_name


