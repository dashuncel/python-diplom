from urllib.parse import urlencode
import requests
import time
import json
import progressbar
import sys

TOKEN = 'cbe61b1e76142e4ed58ae1c9461b3a794f384b79d36890ca0cc7c66826dcbcb01a2e5027898d97c1f7d0a'
USER_ID = '9297520'
PARAMS = {'access_token': TOKEN,
          'v': '5.85'}


def query_vk(url):
    response = None
    while response is None:
        try:
            response = requests.get(url, PARAMS).json()
        except Exception as e:
            print('Ошибка обращения к API VK:', e)
            time.sleep(5)
    return response


def get_url(method, url_params):
    url = '?'.join((f'https://api.vk.com/method/{method}', urlencode(url_params)))
    return url


def get_result(res, node_name='response', err_name='error'):
    if res.get(node_name):
        return res[node_name]
    elif res.get(err_name):
        return res[err_name]
    else:
        return res


def get_friends(user_id, user_info=''):
    url = get_url('friends.get', {'user_id': user_id,
                                  'fields': user_info})
    friend_list = get_result(get_result(query_vk(url)), 'items', 'error_msg')
    return friend_list


def get_groups(user_id, fields=''):
    url = get_url('groups.get', {'user_id': user_id,
                                 'extended': 1,
                                 'filter': 'groups',
                                 'fields': fields})
    group_list = get_result(get_result(query_vk(url)), 'items', 'error_msg')
    return group_list


def put_in_file(file_name, obj):
    with open(file_name, 'w', encoding='utf-8') as f:
        try:
            json.dump(obj, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f'Ошибка записи в файл {e}')


def set_group_id(group):
    if type(group) is list:
        groups_set = set(grp['id'] for grp in group)
    else:
        groups_set = set()
    return groups_set


def compare_groups(user_groups, friend_list):
    user_groups_set = set_group_id(user_groups)

    bar = progressbar.ProgressBar(maxval=len(friend_list),
                                  fd=sys.stdout,
                                  widgets=['Информация о друзьях',
                                           progressbar.Bar(left='[', marker='-', right=']'), progressbar.Percentage()])\
                     .start()
    print('Получение списка групп, в которых состоят друзья')
    friends_groups = set()
    for idx, friend in enumerate(friend_list):
        bar.update(idx)
        friends_groups.update(set_group_id(get_groups(friend)))
    bar.finish()

    unique_groups = user_groups_set.difference(friends_groups)
    unique_groups_info = [{'name': group['name'], 'gid': group['id'], 'members_count': group['members_count']}\
                          for group in user_groups if group['id'] in unique_groups]
    return unique_groups_info


if __name__ == '__main__':

    user_groups = get_groups(USER_ID, 'members_count')

    if type(user_groups) is str:
        print(f'Не могу получить список групп главного пользователя. Ошибка:{user_groups}')
        exit(0)

    user_friends = get_friends(USER_ID)

    put_in_file('groups.json', compare_groups(user_groups, user_friends))



