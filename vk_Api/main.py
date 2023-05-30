import argparse
import requests as requests

API_VERSION = "5.131"

class VKApi:
    def __init__(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token

    """FOR FRIENDS"""

    def get_friends(self, user_id):
        request = f"https://api.vk.com/method/friends.get?v={API_VERSION}" + \
                  f"&user_id={user_id}" + \
                  f"&fields=city" + \
                  f"&access_token={self.access_token}"
        response = requests.get(request).json()
        response = response["response"]["items"]
        return response

    def print_friends(self, friends):
        for idx, friend in enumerate(friends, start=1):
            print(f"{idx}. {friend['first_name']} {friend['last_name']}")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--friends", action="store_true", help="get top of friends")
    return parser.parse_args()


def is_valid_user_id(param):
    return param.isdigit()


if __name__ == "__main__":
    args = get_args()
    try:
        print("Enter your VK ID: ")
        u_id = input()
        if not is_valid_user_id(u_id):
            print("Invalid user id")
            exit()
        u_id = int(u_id)

        print("Enter your access token: ")
        a_token = str(input())
        api = VKApi(u_id, a_token)

        if args.friends:
            api.print_friends(api.get_friends(u_id))

    except KeyboardInterrupt:
        exit()