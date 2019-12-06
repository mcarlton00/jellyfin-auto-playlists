import os
import requests
from pprint import pprint
import yaml

class playlists():
    def __init__(self):
        self.login()

    def login(self):
        self.data = self.read_file()
        user_id = self.data.get('auth').get('user_id')
        username = self.data.get('auth').get('user')
        password = self.data.get('auth').get('password')
        api_url = self.data.get('auth').get('server')

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

        api_url = 'https://streaming.nerdyredneck.net'
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

    def get_library_id(self):
        r = requests.get(f'{self.api_url}/Users/{self.user_id}/Views',
                         headers=self.headers)
        libraries = r.json().get('Items')
        pl_library_id = [ x.get('Id') for x in libraries
                        if x.get('Name') == 'Playlists']
        return pl_library_id

    def get_all_playlists(self):
        self.pl_library_id = self.get_library_id()
        r = requests.get(f'{self.api_url}/Items?ParentId={self.pl_library_id}'
                         f'&UserId={self.user_id}&IncludeItemTypes=Playlist'
                         f'&Recursive=true', headers=self.headers)

        existing_playlists = r.json().get('Items')
        playlists = [{i.get('Name'): i.get('Id')} for i in existing_playlists ]
        return playlists


    def create_playlist(self, playlist_name):
        data = {'Name': playlist_name, 'MediaType': 'Audio'}
        r = requests.post(f'{self.api_url}/Playlists?UserId={self.user_id}'
                          f'&Name={playlist_name}', headers=self.headers,
                          data=data)


if __name__ == '__main__':
    thing = playlists()

# TODO
# Add items to a playlist
# make sure to check for duplicates before adding
#https://jellyfin.example.com/Playlists/65e0a0d4bc429a24b987a14c29202983/Items?EntryIds=0e098cbf4dbadebb07ae26a5242ad01a%2Cace016257fa209a68d05351828c011a9&UserId=02722887cbe547f49ca42b5c12e61f4b&format=json
