import requests
import progressbar
import time
import json

#TOKEN = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'
#USER_ID = '171691064'

TOKEN = '19da8c6dce232885ee0d47afd2d0773f0d7e4bfad13fe11dd7c6c7c567ce60458b9fd04ebba685be4ea10'
USER_ID = '9297520'

class UserVk:

    def __init__(self, user_id, token):
        self.ERROR = 'error_msg'
        self.id = user_id
        self.params = {'access_token': token,
                       'v': '5.85'}

    def __query_vk__(self, items, url):
        # произвольный vk-запрос url с параметрами items
        #print(url.format(*items))
        response = None
        while response is None:
            try:
                response = requests.get(url.format(*items), self.params).json()
            except Exception as e:
                print('Ошибка обращения к API VK:', e)
                time.sleep(5)

        if response.get('error'):
            return response['error']
        elif response.get('response'):
            return response['response']
        else:
            return ''

    def get_friends(self, user_id, user_info):
        # список друзей для user_id
        url = 'https://api.vk.com/method/friends.get?user_id={}&fields={}'
        friend_list = self.__query_vk__((user_id, user_info), url)
        if friend_list.get('items'):
            return friend_list['items']
        elif friend_list.get(self.ERROR):
            return friend_list[self.ERROR]
        else:
            return friend_list

    def get_groups(self, user_id, group_info='', type_res='set'):
        # возвращает список групп для user_id
        url = 'https://api.vk.com/method/groups.get?user_id={}&extended=1&filter=groups&fields={}'
        group_list = self.__query_vk__((user_id, group_info), url)
        if group_list.get('items'):
            if type_res == 'set':
                my = set(grp['id'] for grp in group_list['items'])
                return set(my)
            else:
                return group_list['items']
        elif group_list.get(self.ERROR):
            return group_list[self.ERROR]
        else:
            return list()

    def get_users_info(self, target_ids, info):
        # target_ids - список, айдишники пользователей
        # info - строка, допинформация через запятую, которую надо получить для каждого id
        target_ids = ','.join(str(x) for x in target_ids)
        url = 'https://api.vk.com/method/users.get?user_ids={}&fields={}'
        user_info = self.__query_vk__((target_ids, info), url)
        return user_info

    @property
    def user_group(self):
        return self.get_groups(self.id, 'name,members_count', 'list')

    @property
    def user_friends(self):
        return self.get_friends(self.id, '')


main_user = UserVk(USER_ID, TOKEN)
main_groups = main_user.user_group
main_friends = main_user.user_friends

if not type(main_groups) is set and not type(main_groups) is list:
    print(f'Не могу получить список групп главного пользователя. Ошибка:{main_groups}')
    exit(0)

friends_groups = set()
bar = progressbar.ProgressBar(maxval=len(main_friends),

                              widgets=['Информация о друзьях',
                                       progressbar.Bar(left='[', marker='-',right=']'),progressbar.Percentage()])\
                 .start()
print('Получение информации о группах друзей...')
for idx, friend in enumerate(main_friends):
    bar.update(idx)
    group_set = main_user.get_groups(friend)
    if type(group_set) is set:
        friends_groups.update(group_set)
bar.finish()

if not main_groups is set:
    main_groups_set = set(grp['id'] for grp in main_groups)
else:
    main_groups_set = main_groups

unique_groups = main_groups_set.difference(friends_groups)
unique_groups_info = [{'name': group['name'], 'gid': group['id'], 'members_count': group['members_count']}
                    for group in main_groups if group['id'] in unique_groups]
print(f'Группы, в которых состоит только пользователь {main_user.id}\n', unique_groups_info)

with open('groups.json', 'w', encoding='utf-8') as f:
    try:
        json.dump(unique_groups_info, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f'Ошибка записи в файл {e}')


