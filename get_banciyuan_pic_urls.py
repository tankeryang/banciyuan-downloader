from bs4 import BeautifulSoup
import requests
import time
import math
import re

headers  = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.1144',
    'Connection' : 'keep-alive',
    'Referer'    : 'http://bcy.net'
}

def get_post_urls(user_id, count, home_url='https://bcy.net'):
	post_per_page  = 12
	post_urls_list = []
	user_post_url  = home_url + '/u/' + str(user_id) + '/post/cos'

	session = requests.session()
	html    = session.get(user_post_url, headers=headers)
	soup    = BeautifulSoup(html.text, 'lxml')

	post_nums_text = soup.find('li', class_='pager__item pager__item--is-cur pager__item--disabled').find('span').get_text()
	post_nums      = int(post_nums_text.strip(post_nums_text[0]).strip(post_nums_text[len(post_nums_text)-1]))
	page_nums      = math.ceil(post_nums / post_per_page)
	new_posts_nums = post_nums - count
#	print(page_nums)
	
	if count == 0:
		for page_id in range(1, page_nums + 1)[::-1]:
			html = session.get(user_post_url + '?&p={}'.format(str(page_id)), headers=headers)
			soup = BeautifulSoup(html.text, 'lxml')

			for tag in soup.find_all('div', class_='postWorkCard__img ovf'):
	#			if tag.find('span', class_='badge badge--red badge--s type-hover').get_text() == u'正片':
				post_urls_list.append(home_url + tag.find('a').get('href'))
	#				print(post_urls_list)
		return post_urls_list
	#	print(post_urls_list)
	elif new_posts_nums <= 0:
		print('the local post is latest, need not to download.')

		return None
	else:
		jump_post_nums      = 0
		new_download_nums   = 0
		new_page_count      = 0
		last_page_post_nums = 0

		last_page_id = page_nums
		html = session.get(user_post_url + '?&p={}'.format(str(last_page_id)), headers=headers)
		soup = BeautifulSoup(html.text, 'lxml')

		for tag in soup.find_all('div', class_='postWorkCard__img ovf'):
			last_page_post_nums += 1

		for page_id in range(1, math.ceil((new_posts_nums / post_per_page) + 1))[::-1]:
			html = session.get(user_post_url + '?&p={}'.format(str(page_id)), headers=headers)
			soup = BeautifulSoup(html.text, 'lxml')

			new_page_count += 1

			for tag in soup.find_all('div', class_='postWorkCard__img ovf'):
				if new_page_count == 1 and count % post_per_page != 0 and jump_post_nums < (count + post_per_page - last_page_post_nums) % post_per_page:
	#				post_urls_list.append(home_url + tag.find('a').get('href'))
	#				new_download_nums += 1
					jump_post_nums += 1
				else:
	#				if tag.find('span', class_='badge badge--red badge--s type-hover').get_text() == u'正片':
					post_urls_list.append(home_url + tag.find('a').get('href'))
					new_download_nums += 1
					if new_download_nums >= new_posts_nums:
						break
	#				print(post_urls_list)
		return post_urls_list
	#	print(post_urls_list)

def get_pic_urls(account, password, post_url, post_nums):
	pic_urls_list = []
	print('getting pics from post {}: '.format(str(post_nums)) + post_url + ' ...')

#	time.sleep(5)

	session = requests.session()
	html    = session.get(post_url, headers=headers)
	soup    = BeautifulSoup(html.text, 'lxml')
#	print(soup.text)

	if soup.find('div', class_='l-detail-no-right-to-see') is not None:
		login_url = 'https://bcy.net/public/dologin'
		form_data = {
			'email':account,
			'password':password,
			'remember':'1'
		}
		session.post(login_url, data=form_data, headers=headers)
		html    = session.get(post_url, headers=headers)
		soup    = BeautifulSoup(html.text, 'lxml')

	post_name = re.sub('[\/:*?"<>|]', '', soup.find('div', class_='post__title').find('h1').get_text().strip().strip('\n').strip('.'))
	for tag in soup.find_all('img', class_='detail_std detail_clickable'):
		pic_url = tag.get('src')
		if pic_url.find('.jpg') is not -1:
			pic_urls_list.append(pic_url.split('.jpg')[0] + '.jpg')
		elif pic_url.find('.png') is not -1:
			pic_urls_list.append(pic_url.split('.png')[0] + '.png')

	return post_name, pic_urls_list