# -*- coding: utf-8 -*-
import requests
import re
import json
import hashlib
import time

import settings

USER_NAME = settings.USER_NAME


class Langamepp(object):

    url = 'http://langamepp.com/iptv/'
    playlists_url = 'http://langamepp.com/iptv/playlists'
    login_data = {'iname': USER_NAME, 'ipass': USER_NAME}
    change_data = {'name': USER_NAME + '-{}', 'pass': USER_NAME, 'change_name_pass': u'Изменить'}
    channels = []
    channels_list = 'channels.json'

    def __init__(self):
        self.session = requests.Session()
        self.login()
        self.regex = re.compile(r'''onclick="everedit\('(.+)','.+'\);"><''')

    def login(self):
        response = self.session.post(self.url, data=self.login_data)
        print (response.status_code)

    def channels_add(self):
        bulk = []
        for channel in self.channels:
            bulk.append(channel)
            if len(bulk) > 50:
                self.add_bulk(bulk)
                time.sleep(3)
                bulk = []
        self.add_bulk(bulk)

    def add_bulk(self, bulk):
        if not bulk:
            return
        if len(bulk) == 1:
            params = {'addo': bulk[0]}
        else:
            params = {'addoa': u'|'.join(bulk)}
        response = self.session.get(self.playlists_url, params=params)
        print (response.status_code)

    def grablist(self):
        """ Open playlist and fetch all chanels """
        params = {'channel': 'filteronlymychannels', 'page': 1}
        channels = True
        while channels:
            response = self.session.get(self.playlists_url, params=params)
            channels = self.parse(response)
            params['page'] += 1
        self.save_to_file()

    def grablist_copy(self):
        """ Open playlist and fetch all chanels """
        self.read_from_file()
        self.grablist()

    def parse(self, response):
        """ Parse page data """
        result = self.regex.findall(response.content.decode('utf-8'))
        self.channels.extend(result)
        return bool(result)

    def save_to_file(self):
        """ Make channels in file list """
        self.channels = list(set(self.channels))
        print (len(self.channels))
        with open(self.channels_list, 'w') as channels:
            json.dump(self.channels, channels, indent=4)

    def read_from_file(self):
        """ Open channels and read """
        with open(self.channels_list, 'r') as channels:
            self.channels = json.load(channels)

    def change_name(self):
        """ Rename old account to new name """
        data = self.change_data.copy()
        data['name'] = data['name'].format(time.time())
        print (data)
        response = self.session.post(self.playlists_url, data=data)
        # print (response.content)

    @classmethod
    def activate(cls):
        """ Register account and activate user """
        email = 'e{}@mvrht.com'.format(str(time.time()))
        row = USER_NAME + email + USER_NAME
        print ('')
        print ('Email: {}'.format(email))
        print ('Link: http://langamepp.com/iptv/reg?code={}'.format(hashlib.md5(row).hexdigest()))


import sys

ll = Langamepp()

if 'copy' in sys.argv:
    ll.read_from_file()
    ll.channels_add()
elif 'grab' in sys.argv:
    ll.grablist_copy()
elif 'reg' in sys.argv:
    ll.change_name()
    ll.activate()
