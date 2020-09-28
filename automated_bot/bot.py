import requests
import names
import json
import toml
from random import randrange

timeout = 20
base_url = 'http://127.0.0.1:8000'
create_post = '/api/create'
list_all = '/api/list_all'
user_register = '/user/register'



# actions
# sign-up users
# each user creates random number of posts
# likes random number of posts (multi-like allowed)


class Bot:
    """Bot that reads data from config, creates random number of random users, posts, likes"""
    def __init__(self):
        self.access_token = self.get_token()['access']      # generating a pair of tokens and getting access token

        # getting parameters from bot config file
        config_dict = toml.load("bot_config.toml")
        number_of_users = config_dict['number_of_users']
        max_posts_per_user = config_dict['max_posts_per_user']
        max_likes_per_user = config_dict['max_likes_per_user']

        # 1. create users
        for i in range(number_of_users):    # creating n users, each with random username
            random_full_name = names.get_full_name().replace(" ", "")
            self.create_user(random_full_name)

        # 2. Each user creates random number of posts
        for i in range(number_of_users):
            print(i)
            for i in range(max_posts_per_user):
                self.create_post()

        # 3. Users randomly like posts

        # self.list_posts()
        # self.create_user(random_full_name)

    def create_user(self, full_name):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token),
                   'Content-Type': 'application/json',
                   # 'Host': base_url,
                   # 'Content-Length': '73'
                   }
        password = full_name
        payload = {"username": full_name, "password": password}
        payload = json.dumps(payload)
        response = requests.post(base_url + user_register, data=payload, headers=headers, timeout=timeout)
        print(response)
        return response

    def get_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {"username": "qwer", "password": "6AJxkScJ4lnT"}              # !!!!!!!!!!!!!!!
        response = requests.post('{}/api/token'.format(base_url), data=payload, headers=headers, timeout=timeout).json()
        if 'access' not in response:       # response['access'] contains access token. If not, there was an error.
            print('Could not generate token, please check your login details.')
        return response

    def create_post(self):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token),
                   'Content-Type': 'application/x-www-form-urlencoded',
                   }
        response = requests.get('{}'.format(base_url), headers=headers, timeout=timeout)
        # print(response.text)
        payload = {
            "content": "88888",
            "author": 1,
            "date_posted": "2020-04-22T21:15:50Z",
            "number_of_likes": 0
        }
        response = requests.post(base_url + create_post, headers=headers, data=payload, timeout=timeout)
        if str(response.status_code) == "201":
            print('Post successfully created.')

    def list_posts(self):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        response = requests.get('{}'.format(base_url + list_all), headers=headers, timeout=timeout)
        print(response.text)


if __name__ == '__main__':
    bot = Bot()
