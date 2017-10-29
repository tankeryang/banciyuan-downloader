import requests
import time
import os
import random
from get_banciyuan_pic_urls import get_post_urls, get_pic_urls

def get_pics(account, password, coser_id, coser_dir, count=0):
	print('downloading...')

	post_urls_list = get_post_urls(coser_id, count)

	if  post_urls_list is not None:
		post_nums = 1

		for post_url in post_urls_list:
			post_name, pic_urls = get_pic_urls(account, password, post_url, post_nums)
			post_dir = coser_dir + '\\' + post_name

			if not os.path.exists(post_dir):
				os.makedirs(post_dir)
				number = 0
				time.sleep(3)
			else:
			#	pic_count = 0
			#	for fn in os.listdir(post_dir):
			#		pic_count += 1
			#	number = pic_count
				is_exists = True
				while is_exists:
					post_dir = post_dir + '(' + str(random.randint(1, 10)) + ')'
					if not os.path.exists(post_dir):
						os.makedirs(post_dir)
						is_exists = False
					pass
				time.sleep(3)

			for pic_url in pic_urls:
				time.sleep(3)
				pic = requests.get(pic_url)
				if pic.status_code is 200:
					number += 1
					open(post_dir + '\\' + str(number) + '.jpg', 'wb').write(pic.content)
			post_nums += 1

	print('done.')