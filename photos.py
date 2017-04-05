# -*- coding: utf-8 -*-
import codecs
import requests
import urllib
import webbrowser
import json
import os
import math
import time
import logger

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

# Вычисляем размер файла
def size(size_bytes):
	if (size_bytes == 0):
		return '0 B'
	size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(size_bytes/p, 2)
	return '%s %s' % (s, size_name[i])

# Вывод простых ошибок
def error():
	logger.fail("Пусто!")

# Если нет папки для документов создаем
if not os.path.exists("./photos/"):
	os.makedirs("./photos/")

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

# Ищем документы
user_id = raw_input("[~] Введите ID пользователя: ")

if len(user_id) > 0:
	user_id = user_id.replace("id","")

	# Если нет папки для фотографий юзера
	if not os.path.exists("./photos/" + user_id):
		os.makedirs("./photos/" + user_id)

	result = api_call("photos.get", {
		"photo_sizes": 1,
		"owner_id": user_id,
		"version": "5.63",
		"count": 200,
		"album_id": "profile",
		"access_token": access_token
	})

	result = shift(result)

	for photo in result:
		try:
		  if os.path.isfile("./photos/" + str(user_id) + "/" + str(photo['pid']) + ".jpg"):
			  logger.success("Повтор файла: " + str(user_id) + "/" + str(photo['pid']) + ".jpg")
		  else:
			  logger.success("Скачиваем файл: " + str(user_id) + "/" + str(photo['pid']) + ".jpg")
			  urllib.urlretrieve(photo['sizes'][len(photo['sizes']) - 1]['src'], "./photos/" + str(user_id) + "/" + str(photo['pid']) + ".jpg")
		except Exception, e: 
		  logger.warning(str(e))
else:
	error()
