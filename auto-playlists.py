import os
import requests
from pprint import pprint
import yaml

class Playlists():
    def __init__(self):
        self.data = self.read_file()
        self.login(self.data)

    def login(self, data):
        user_id = self.data.get('server_data').get('user_id')
        username = self.data.get('server_data').get('user')
        password = self.data.get('server_data').get('password')
        api_url = self.data.get('server_data').get('server')
        self.music_library = self.data.get('server_data').get(
            'music_library', 'Music')

        auth_data = {
            'Username': username,
            'Pw': password
        }

        headers = {}

        authorization = (
            f'MediaBrowser UserId="{user_id}", '
            f'Client="other", '
            f'Device="computer", '
            f'DeviceId="auto-playlist", '
            f'Version="0.0.0"'
        )

        headers['x-emby-authorization'] = authorization

        auth_url = f'{api_url}/Users/AuthenticateByName'

        r = requests.post(auth_url, headers=headers, data=auth_data)

        token = r.json().get('AccessToken')

        headers['x-mediabrowser-token'] = token

        self.headers = headers
        self.api_url = api_url
        self.user_id = user_id

    def read_file(self):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(f'{path}/config.yaml', 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        return data

    def get_library_id(self, library_name):
        r = requests.get(f'{self.api_url}/Users/{self.user_id}/Views',
                         headers=self.headers)
        r.raise_for_status()
        libraries = r.json().get('Items')
        library_id = [ x.get('Id') for x in libraries
                        if x.get('Name') == library_name]
        if library_id:
            library_id = library_id[0]

        return library_id

    def get_all_playlists(self):
        library_id = self.get_library_id('Playlists')
        r = requests.get(f'{self.api_url}/Items?ParentId={library_id}'
                         f'&UserId={self.user_id}&IncludeItemTypes=Playlist'
                         f'&Recursive=true', headers=self.headers)
        r.raise_for_status()

        existing_playlists = r.json().get('Items')
        playlists = {i.get('Name'): i.get('Id') for i in existing_playlists }
        return playlists


    def create_playlist(self, playlist_name):
        data = {'Name': playlist_name, 'MediaType': 'Audio'}
        r = requests.post(f'{self.api_url}/Playlists?UserId={self.user_id}'
                          f'&Name={playlist_name}', headers=self.headers,
                          data=data)
        r.raise_for_status()

    def add_single_to_playlist(self, playlist_id, item_id):
        r = requests.post(f'{self.api_url}/Playlists/{playlist_id}/Items?'
                            f'Ids={item_id}&UserId={self.user_id}',
                            headers=self.headers)
        r.raise_for_status()

    def add_bulk_to_playlist(self, playlist_id, items):
        item_ids = [ item.get('Id') for item in items ]
        item_ids = ','.join(item_ids)

        r = requests.post(f'{self.api_url}/Playlists/{playlist_id}/Items?'
                            f'Ids={item_ids}&UserId={self.user_id}',
                            headers=self.headers)
        r.raise_for_status()

    def get_playlist_id(self, playlist_name):
        playlists = self.get_all_playlists()

        playlist_id = playlists.get(playlist_name)

        return playlist_id

    def get_playlist_contents(self, playlist_name):
        playlist_id = self.get_playlist_id(playlist_name)

        r = requests.get(f'{self.api_url}/Playlists/{playlist_id}/Items?'
                         f'UserId={self.user_id}', headers=self.headers)

        r.raise_for_status()

        return r.json().get('Items')

    def clear_playlist(self, playlist_name):
        playlist_id = self.get_playlist_id(playlist_name)
        tracks = self.get_playlist_contents(playlist_name)

        tracklist = [track.get('Id') for track in tracks ]

        grouped_ids = list(self.split_list(tracklist, 15))
        for group in grouped_ids:
            item_ids = ','.join(group)
            #print(item_ids)


        #return item_ids

            print(f'{self.api_url}/Playlists/{playlist_id}/Items?'
                              f'UserId={self.user_id}&EntryIds={item_ids}')#,
            r = requests.delete(f'{self.api_url}/Playlists/{playlist_id}/Items?'
                              f'UserId={self.user_id}&EntryIds={item_ids}',
                              headers=self.headers)
            print(r.status_code)
            r.raise_for_status()

    def split_list(self, item_ids, size):
        for i in range(0, len(item_ids), size):
            yield item_ids[i:i+size]

    def get_all_tracks(self):
        library_id = self.get_library_id(self.music_library)

        r = requests.get(f'{self.api_url}/Users/{self.user_id}/Items?'
                         f'ParentId={library_id}&Recursive=true&'
                         f'IncludeItemTypes=Audio&'
                         f'Fields=Genres', headers=self.headers)

        r.raise_for_status()

        tracks = r.json().get('Items')

        return tracks

    def get_recent_tracks(self, num):
        library_id = self.get_library_id(self.music_library)

        r = requests.get(f'{self.api_url}/Users/{self.user_id}/Items/Latest?'
                         f'IncludeItemTypes=Audio&Limit={num}&Recursive=true&'
                         f'ParentId={library_id}', headers=self.headers)

        r.raise_for_status()

        return r.json()

if __name__ == '__main__':
    generator = Playlists()
