# -*- coding: utf-8 -*-
import codecs
import requests
import urllib
import webbrowser
import json
import os
import math
import time
import sys
import logger
from threading import Thread

# Настройки приложения
client_id = "3998121"
client_secret = "AlVXZFMUqyrnABp8ncuU"

# Функция обращения к API
def api_call(method, param):
	api_url = "https://api.vk.com/method/" + method + "?" + urllib.urlencode(param)
	s = requests.Session()
	r = s.get(api_url)

	response = json.loads(r.text)

	return response["response"]

# Array Shift
def shift(array):
	array.remove(array[0])
	return array  

# Вывод простых ошибок
def error():
	logger.fail("Пусто!")

# Поток удаления фотографий
def erasePhotos(photos, threadId, uid):
	photos = shift(photos)
	for photo in photos:
		result = api_call("photos.delete", {
			"owner_id": uid,
			"photo_id": photo["pid"],
			"version": "5.63",
			"access_token": access_token
		})
		logger.success("[%s]: Фото %s удалено" % (threadId, str(photo["pid"])))

# Проверяем есть ли файл с access_token
if os.path.isfile("./access_token.txt"):
	file = open("./access_token.txt", "r")
	access_token = file.read()
	file.close()

	logger.success("Авторизовались!")
else:
	data = {
		"client_id": client_id,
		"redirect_uri": "https://oauth.vk.com/blank.html",
		"display": "page",
		"scope": "photos,offline",
		"response_type": "token",
		"v": "5.0"
	}

	url = "https://oauth.vk.com/authorize?" + urllib.urlencode(data)

	webbrowser.open(url, new=2)

	logger.info("В браузере нужно разрешить приложение получение access_token");
	logger.info("После этого скопируйте значение параметра access_token из браузерной строки")

	access_token = raw_input("[~] Введите параметр access_token из браузера: ")

	if len(access_token) > 0:
		logger.success("Авторизовались!")

		file = open("./access_token.txt", "w")
		file.write(access_token)
		file.close()
	else:
		error()

result = api_call("users.get", {
	"access_token": access_token
})

user_id = int(result[0]["uid"])

if user_id > 0:

	block = 200
	offset = 0
	result = api_call("photos.getAll", {
		"owner_id": user_id,
		"version": "5.63",
		"count": block,
		"access_token": access_token
	})

	totalCount = result[0]
	if totalCount == 0:
		logger.fail("Фото не найдены!")
		sys.exit()
	tId = 0
	for x in range(0, int(totalCount / block) + 1):
		offset = block * x
		result = api_call("photos.getAll", {
			"owner_id": user_id,
			"version": "5.63",
			"count": block,
			"offset": offset,
			"access_token": access_token
		})
		thread = Thread(target = erasePhotos, args = (result, tId, user_id, ))
		thread.start()
		tId = tId + 1