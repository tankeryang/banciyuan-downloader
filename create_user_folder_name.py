from bs4 import BeautifulSoup
import requests

headers  = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.1144',
    'Connection' : 'keep-alive',
    'Referer' : 'http://bcy.net'
}

def create_user_folder_name(user_id):
	session = requests.session()
	html = session.get('https://bcy.net/u/{}'.format(str(user_id)), headers=headers)
	soup = BeautifulSoup(html.text, 'lxml')

	user_folder_name = soup.find('a', href='/u/{}'.format(str(user_id))).get('title')
	
	return user_folder_name