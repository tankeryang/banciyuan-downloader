import os
import sys
import time
import math
import re
import random
import logging
import requests
from bs4 import BeautifulSoup
from functools import partial
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
logging.basicConfig(level=logging.INFO)


class Downloader():
    def __init__(self, account=None, password=None, coser_id=None, bcy_home_dir=None, post_type='all', config=None):
        self.account = account
        self.password = password
        self.coser_id = coser_id
        self.bcy_home_dir = bcy_home_dir
        self.post_type = post_type
        self.__home_url = "https://bcy.net"
        self.__login_url = "https://bcy.net/public/dologin"
        self.__session = self.__login()
        self.__coser_dir = self.bcy_home_dir + '/' + self.__create_coser_dir_name()
        self.__post_per_page = 35
        self.__post_url_list = []
        self.__download_data = {}

        if not os.path.exists(self.__coser_dir):
            os.mkdir(self.__coser_dir)

    @property
    def home_url(self):
        return self.__home_url

    @home_url.setter
    def home_url(self, values):
        if not isinstance(values, str):
            raise ValueError("attribute home_url type shoud be str!!")
        self.__home_url = values

    @property
    def post_per_page(self):
        return self.__post_per_page

    @post_per_page.setter
    def post_per_page(self, values):
        if not isinstance(values, int):
            raise ValueError("attribute post_per_page type shoud be int!!")
        self.__post_per_page = values

    @property
    def post_url_list(self):
        return self.__post_url_list
    
    @post_url_list.setter
    def post_url_list(self, values):
        if not isinstance(values, list):
            raise ValueError("attribute post_per_page type shoud be list!!")
            
        self.__post_url_list = list(set(values).difference(set(self.local_post_url_list)))

        if len(self.__post_url_list) == 0:
            logging.info('The local post is latest, need not to download.')
            sys.exit(0)

    @property
    def download_data(self):
        return self.__download_data
    
    @property
    def local_post_url_list(self):
        """返回本地已下载作品列表"""
        local_post_url_list = []

        def get_local_post_url(post_dir):
            if post_dir == '.DS_Store':
                pass
            elif os.path.exists(self.__coser_dir + '/' + post_dir + '/' + 'url.local'):
                f = open(self.__coser_dir + '/'+ post_dir + '/url.local', 'r')
                local_post_url_list.append(f.readline().strip().strip('\n'))

        pool = ThreadPool(processes=4)
        pool.map(get_local_post_url, os.listdir(self.__coser_dir))             
        pool.close()
        pool.join()

        return local_post_url_list

    def __create_coser_dir_name(self):
        session = requests.session()
        resp = self.__session.get(self.__home_url + '/u/{}'.format(self.coser_id))
        soup = BeautifulSoup(resp.text, 'lxml')

        return soup.find(name='a', href='/u/{}'.format(str(self.coser_id))).get('title')

    def __login(self):
        session = requests.session()
        request_retry = requests.adapters.HTTPAdapter(max_retries=10)

        session.mount('https://',request_retry)
        session.mount('http://',request_retry)
        session.get(url=self.__home_url)
        session.headers.update({'X-Requested-With': 'XMLHttpRequest', 'Referer': 'http://bcy.net/'})

        form_data = {
            'email': self.account,
            'password': self.password,
            'remember': '1',
            '_csrf_token': session.cookies.get_dict()['_csrf_token']
        }
        resp = session.post(url=self.__login_url, data=form_data)
        if 'LOGGED_USER' not in resp.cookies.get_dict().keys():
            logging.error("account or password error. login failed.")
            sys.exit(1)
        else:
            return session

    def get_post_url_list(self):
        post_urls_list = []
        local_post_url_list = []

        coser_post_url = '{home_url}/u/{coser_id}/post'.format(home_url=self.__home_url, coser_id=self.coser_id)
        resp = self.__session.get(url=coser_post_url)
        soup = BeautifulSoup(resp.text, 'lxml')

        # 获取发布作品数与总页数
        if soup.find(name='ul', class_='pager') is not None:
            post_nums_text = soup.find(
                name='li', class_='pager__item pager__item--is-cur pager__item--disabled'
            ).find('span').get_text()
            post_nums = eval(
                post_nums_text.strip(post_nums_text[0]).strip(post_nums_text[len(post_nums_text) - 1])
            )
            page_nums = math.ceil(post_nums / self.__post_per_page)
        else:
            post_nums = len(soup.find_all(name='li', class_='js-smallCards _box'))
            page_nums = 1

        # 本地已下载作品列表
        # for post_dir in os.listdir(self.__coser_dir):
        #     if post_dir == '.DS_Store':
        #         continue
        #     if os.path.exists(self.__coser_dir + '/' + post_dir + '/' + 'url.local'):
        #         f = open(self.__coser_dir + '/'+ post_dir + '/url.local', 'r')
        #         local_post_url_list.append(f.readline().strip().strip('\n'))

        # 所有作品
        if self.post_type == 'all':
            for page_id in range(1, page_nums + 1):
                resp = self.__session.get(url=coser_post_url + '?&p={}'.format(str(page_id)))
                soup = BeautifulSoup(resp.text, 'lxml')
                for tag in soup.find_all(name='li', class_='js-smallCards _box'):
                    post_urls_list.append(self.__home_url + tag.find('a', class_='db posr ovf').get('href'))
        elif self.post_type == 'cos':
            # TODO: 只获取带有`COS`标签的作品，这个必须解析每个作品页才能获取到
            logging.warning("This type dosen't support now. Please use type [all].")
            sys.exit(1)
        
        # 需下载的作品
        post_urls_list = list(set(post_urls_list).difference(set(self.local_post_url_list)))

        # 无需更新
        if len(post_urls_list) == 0:
            logging.info('The local post is latest, need not to download.')
            sys.exit(0)
        
        logging.info("There are %d post you can update." % len(post_urls_list))
        self.__post_url_list = post_urls_list

    def __get_pics_url_list(self, post_url):
        # if post_url_list is None:
        #     post_url_list = self.__post_url_list
        # if len(post_url_list) == 0:
        #     logging.warning("There are no post url to download. Please execute get_post_url_list() first.")
        #     sys.exit(1)

        # for post_url in post_url_list:
        pics_url_list = []

        resp = self.__session.get(url=post_url)
        soup = BeautifulSoup(resp.text, 'lxml')

        # 获取所属作品名
        post_name = re.sub(
            r'[\/:*?"<>|]', '-',
            '-'.join(list(map(lambda x: x.text.strip().strip('\n').strip('.'), soup.find_all(name='a', class_='_tag _tag--normal db'))))
        )
        print(post_url, post_name)
        # 创建新作品文件夹
        if not os.path.exists(self.__coser_dir + '/' + post_name):
            os.mkdir(self.__coser_dir + '/' + post_name)
        # 处理同名作品
        else:
            is_exists = True
            post_name_id_list = [str(i) for i in range(20, 0, -1)]
            while is_exists:
                post_id = post_name_id_list.pop()
                if not os.path.exists(self.__coser_dir + '/' + post_name + '({})'.format(post_id)):
                    os.mkdir(self.__coser_dir + '/' + post_name + '({})'.format(post_id))
                    post_name = post_name + '({})'.format(post_id)
                    is_exists = False

        # 获取图片url列表
        for pic_id, tag in enumerate(soup.find_all(name='img', class_='detail_std detail_clickable'), 1):
            pic_url = tag.get('src')
            # url后加?pic_id是为了后面写入时能按编号命名文件
            if pic_url[-5:] == '/w650':
                pics_url_list.append(pic_url[:-5] + '?' + str(pic_id))
            else:
                pics_url_list.append(pic_url + '?'+ str(pic_id))

        self.__download_data[post_url] = {'post_name': post_name, 'pics_url_list': pics_url_list}

    def get_pics_url_list(self, post_url_list=None):
        if post_url_list is None:
            post_url_list = self.__post_url_list
        if len(post_url_list) == 0:
            logging.warning("There are no post url to download. Please execute get_post_url_list() first.")
            sys.exit(1)
        print("Folowing post will be downloaded.")
        pool = ThreadPool(processes=4)
        pool.map(self.__get_pics_url_list, post_url_list)
        pool.close()
        pool.join()
        print(100*"=")

    def __get_pics(self, post_url, post_name, pic_url):
        post_dir = self.__coser_dir + '/' + post_name

        if not os.path.exists(post_dir + '/' + 'url.local'):
            open(post_dir + '/url.local', 'wb').write(post_url.encode('utf-8'))
        
        # 保存图片
        # time.sleep(0.2)
        pic = self.__session.get(pic_url.split('?')[0], timeout=3)
        if pic.status_code is 200:
            logging.info(" url: {} id: {}".format(pic_url.split('?')[0], pic_url.split('?')[1]))
            open(post_dir + '/' + pic_url.split('?')[1] + '.jpg', 'wb').write(pic.content)
        else:
            logging.error(" {} not found. status code: {}".format(pic_url.split('?')[0], pic.status_code))

    def get_pics(self):
        pool = ThreadPool(processes=4)
        logging.info("Downloading...")
        for post_url in self.__download_data.keys():
            logging.info("Downloading pictrues from {}...".format(post_url))
            post_name = self.__download_data[post_url]['post_name']
            pics_url_list = self.__download_data[post_url]['pics_url_list']
            pool.map(partial(self.__get_pics, post_url, post_name), pics_url_list)
            print(100*"=")
            # time.sleep(1)
        pool.close()
        pool.join()

    def run(self):
        self.get_post_url_list()
        self.get_pics_url_list()
        self.get_pics()
