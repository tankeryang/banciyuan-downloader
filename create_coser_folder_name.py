from bs4 import BeautifulSoup
import requests

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.1144',
    'Connection' : 'keep-alive',
    'Referer' : 'http://bcy.net'
}

def create_coser_folder_name(coser_id):
    session = requests.session()
    html = session.get('https://bcy.net/u/{}'.format(str(coser_id)), headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')

    coser_folder_name = soup.find(name='a', href='/u/{}'.format(str(coser_id))).get('title')
    
    return coser_folder_name