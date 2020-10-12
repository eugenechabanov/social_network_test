import requests
import names
import json
import toml
from essential_generators import DocumentGenerator
from random import randrange, choice

timeout = 20
base_url = 'http://127.0.0.1:8000'
create_post = '/api/create_post'
like_post = '/api/like/'
list_all = '/api/list_all'
user_register = '/user/register'


class Bot:
    """Bot that reads data from config, creates random number of random users, posts, likes"""
    def __init__(self):
        self.access_token = self.get_token()['access']      # generating a pair of tokens and getting access token

        # getting parameters from bot config file
        config_dict = toml.load("bot_config.toml")
        number_of_users = config_dict['number_of_users']
        max_posts_per_user = config_dict['max_posts_per_user']
        max_likes_per_user = config_dict['max_likes_per_user']

        # dict to store created users' credentials:
        self.credentials_dict = {}      # {'username1': 'password1', 'username2': 'password2', ...}

        # 1. create users
        print('====== Creating {} users =========='.format(number_of_users))
        for i in range(number_of_users):    # creating n users, each with random username
            random_full_name = names.get_full_name().replace(" ", "")
            self.create_user(random_full_name)
        print('====== Creating Posts =======')

        # 2. Each user creates random number of posts
        for i, user_name in enumerate(self.credentials_dict):           # iterating through created users
            random_number_of_posts = randrange(1, max_posts_per_user)
            # generating random number of posts less than max_posts_per_user:
            for __ in range(1, random_number_of_posts + 1):
                self.create_post(user_name)
            print('[{}/{}] User {} created {} posts.'.format(i+1, len(self.credentials_dict),
                                                            user_name, random_number_of_posts))
        # 3. Users randomly like posts
        print('====== Liking Posts =======')
        for i, user_name in enumerate(self.credentials_dict):  # iterating through created users
            # generating random number of likes for current user less than max_likes_per_user:
            random_number_of_likes = randrange(1, max_likes_per_user)
            for __ in range(1, random_number_of_likes + 1):
                self.like_post(user_name)
            print('[{}/{}] User {} liked {} posts.'.format(i + 1, len(self.credentials_dict),
                                                             user_name, random_number_of_likes))
        print('Done.')

    def create_user(self, user_name):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token),
                   'Content-Type': 'application/json'}
        password = user_name    # for simplicity, to be changed later
        payload = {"username": user_name, "password": password}
        payload = json.dumps(payload)
        response = requests.post(base_url + user_register, data=payload, headers=headers, timeout=timeout)
        if response.status_code == 201:
            print('User {} created.'.format(user_name))
        else:
            print('Error creating user:\n{}'.format(response))
        self.credentials_dict[user_name] = password
        return response

    def get_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {"username": "test", "password": "6AJxkScJ4lnT"}              # !!!!!!!!!!!!!!!
        response = requests.post('{}/api/token'.format(base_url), data=payload, headers=headers, timeout=timeout).json()
        if 'access' not in response:       # response['access'] contains access token. If not, there was an error.
            print('Could not generate token, please check your login details.')
        return response

    def create_post(self, user_name):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {
            "content": DocumentGenerator().paragraph(),
            "author": user_name,
            # sufficient degree of date customisation:
            "date_posted": "2020-0{}-{}T21:15:50Z".format(randrange(1, 10), randrange(10, 28)),
            "number_of_likes": 0
        }
        response = requests.post(base_url + create_post, headers=headers, data=payload, timeout=timeout)
        # print(response.status_code)
        if str(response.status_code) == "201":
            print('--> User {} created new post.'.format(user_name))

    def like_post(self, user):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token),
                   'Content-Type': 'application/x-www-form-urlencoded'}

        # passing post id = 0 will select a random post to like.
        response = requests.post(base_url + like_post + '0', headers=headers, data={'author': user}, timeout=timeout)
        # print(response.status_code)
        # print(response.text)
        json_data = json.loads(response.text)
        if str(response.status_code) == "200":
            print('--> User {} liked random post "{}..." by {}.'.format(user, json_data['content'][:30],
                                                                            json_data['author']))

    def list_posts(self):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        response = requests.get('{}'.format(base_url + list_all), headers=headers, timeout=timeout)
        print(response.text)


if __name__ == '__main__':
    bot = Bot()
