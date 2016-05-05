#!/usr/bin/env python3
#-*- coding: UTF-8 -*-
import vk
from time import sleep
import re
import requests
from urllib.parse import urlencode
import json
import random


def get_text(uid,img):
    params = urlencode({
        # Request parameters
        'language': 'ru',
        'detectOrientation ': 'true',
    })
    print(params)
    url = 'https://api.projectoxford.ai/vision/v1/ocr?%s' % params
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'key',
    }

    body = {
        'Url' : img
    }
    try:
        mess=''
        r = requests.post(url, headers=headers, data=json.dumps(body))
        print(r.text)
        r = json.loads(r.text)
        for lines in r['regions']:
            for words in lines['lines']:
                for text in words['words']:
                    mess+=text['text']+' '
                mess+='\n'
            mess+='\n'
        vkapi.messages.send(user_id=uid, message=mess)
    except Exception as e:
        print(e)



def get_gifs(message):
    query=re.findall(r'\s(\w+)',  message)
    params = urlencode({
        # Request parameters
        'q': query,
        'api_key': 'dc6zaTOxFJmzC',
    })
    
    url = 'http://api.giphy.com/v1/gifs/search?%s' % params
    print(url)
    try:
        mess=''
        r = requests.get(url)
        r = json.loads(r.text)
        print(r['data'][0]['embed_url'])
        dt=random.choice(r['data']) 
        return dt['images']['fixed_height']['url']
    except Exception as e:
        print(e)

def add_photo(url):
    photo_server = vkapi.docs.getWallUploadServer(group_id='id')

    print('[LOG] '+ url)
    req = requests.get(url)
    f = open("sample.gif", 'wb')
    f.write(req.content)
    f.close()
    file = {'file': open("sample.gif", 'rb')}
    r = requests.post(photo_server['upload_url'], files=file)
    r.status_code == requests.codes.ok
    data = json.loads(r.text)

    buf = vkapi.docs.save(file=data['file'], title='orehov.gif')[0]
    print(buf)
    # </magic>

    photo_id = 'doc{}_{}'.format(buf['owner_id'], str(buf['id']))

    return photo_id

def validateCommand(command,respbody):
    if command in 'gettext getText взятьТекст':
        #сделать цикл по всем атачм 
        #взять максимальный размер
        photo_size = ['photo_2560','photo_1280','photo_807','photo_604','photo_130','photo_75']
        for photo in respbody['attachments']:
            for size in photo_size:
                print(size)
                if photo['photo'].get(size)!=None:
                    get_text(respbody['user_id'],photo['photo'][size])
                    break
    if command in 'gif':
        vkapi.messages.send(user_id=respbody['user_id'], attachment=add_photo(get_gifs(respbody['body'])))

# Авторизація
   
access_token='token'
session = vk.Session(access_token=access_token)
vkapi = vk.API(session,v=5.52)

#vkapi.messages.send(user_id=230663881, message='Bot start!')
#vkapi.messages.send(user_id=99709842, attachment=add_photo(get_gifs('dog')))
new_pts=vkapi.messages.getLongPollServer(need_pts=1)
ts=new_pts['pts']
while True:
    sleep(4)
    try:
        LongPollHistory=vkapi.messages.getLongPollHistory(pts=ts,onlines=1)
    except Exception as e:
        print(e)
        continue
    print('[LOG]Message count: ',LongPollHistory['messages']['count'])
    for message in LongPollHistory['messages']['items']:
        for mess in re.findall(r'^~(\w+)~',  message['body']):
            validateCommand(mess,message)


    ts=LongPollHistory['new_pts']
