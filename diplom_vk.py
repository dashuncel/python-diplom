import requests
from progressbar import *

#TOKEN = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'
#USER_ID = '171691064'

#TOKEN = '9784a84e76e1c8eaf7b7e4a54d75ac4bb2eb296ccdb5f4e7f1924165e5a1194587a49c41e79e03fc21e3e',
TOKEN = 'bdbe014a9ff9d877803fd90bb214227c13fde8eadee31513d3972954f7f9d102d89453d20f41ccb839849'
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
        response = requests.get(url.format(*items), self.params).json()
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
        return self.get_groups(self.id, 'name,members_count,invited_by')

    @property
    def user_friends(self):
        return self.get_friends(self.id, '')


main_user = UserVk(USER_ID, TOKEN)
main_groups = main_user.user_group
if not type(main_groups) is set:
    print('Не могу получить список групп главного пользователя!', main_groups)
    exit(0)

friends_groups = set()
widgets = ['Test: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
           ' ', ETA(), ' ', FileTransferSpeed()] #see docs for other options
pbar = ProgressBar(widgets=widgets, maxval=len(main_user.user_friends))
pbar.start()

for idx, friend in enumerate(main_user.user_friends):
    group_set = main_user.get_groups(friend)
    pbar.update(idx)
    if type(group_set) is set:
        friends_groups.update(group_set)

pbar.finish()

unique_groups = main_groups.difference(friends_groups)
print(unique_groups)
unique_groups_info = [{'name': group['name'], 'gid': group['name']} for group in main_groups if group['id'] in unique_groups]
#print(unique_groups_info)



