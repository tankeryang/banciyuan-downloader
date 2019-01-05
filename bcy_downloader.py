import os
import sys
import time
import math
import re
import random
import logging
import requests
import json
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
        # self.__web_user_url = "https://bcy.net/passport/web/user/login/?account_sdk_source=web"
        # self.__dologin_url = "https://bcy.net/public/dologin"
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

    def __login(self):
        session = requests.session()
        request_retry = requests.adapters.HTTPAdapter(max_retries=10)

        session.mount('https://',request_retry)
        session.mount('http://',request_retry)
        session.get(url=self.__home_url)
        session.headers.update({'X-Requested-With': 'XMLHttpRequest', 'Referer': 'http://bcy.net/'})

        # # 先请求https://bcy.net/passport/web/user/login/?account_sdk_source=web拿到user_id
        # form_data_web_user = {
        #     'account': self.account,
        #     'password': self.password,
        #     'aid': '1305'
        # }
        # response_web_user = session.post(url=self.__web_user_url, data=form_data_web_user).json()
        # if response_web_user['message'] == 'error':
        #     logging.error("account or password error. login failed.")
        #     sys.exit(1)
        # else:
        #     user_id = response_web_user['data']['user_id']

        # # 再请求dologin登录
        # form_data_dologin = {
        #     'user_id': user_id,
        #     '_csrf_token': session.cookies.get_dict()['_csrf_token']
        # }
        # session.post(url=self.__dologin_url, data=form_data_dologin)

        # 因为现在登录加了滑块验证，因此这里就不做登录的模拟了，太麻烦。。
        # 要是遇到粉丝可见的主题则直接跳过。有心的自己手动下载吧
        return session

    def __create_coser_dir_name(self):
        session = requests.session()
        resp = self.__session.get(self.__home_url + '/u/{}'.format(self.coser_id))
        soup = BeautifulSoup(resp.text, 'lxml')

        return soup.find(name='a', href='/u/{}'.format(str(self.coser_id))).get('title')

    def __create_post_dir(self, post_name):
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
        return post_name

    def get_post_url_list(self):
        post_urls_list = []
        local_post_url_list = []

        coser_post_url = '{home_url}/u/{coser_id}/post'.format(home_url=self.__home_url, coser_id=self.coser_id)
        resp = self.__session.get(url=coser_post_url)
        soup = BeautifulSoup(resp.text, 'lxml')

        # 获取发布作品数与总页数
        if soup.find(name='div', class_='dm-pager-total') is not None:
            post_nums_text = soup.find(name='div', class_='dm-pager-total').get_text()
            post_nums = eval(
                post_nums_text.strip(post_nums_text[0]).strip(post_nums_text[len(post_nums_text) - 1])
            )
            page_nums = math.ceil(post_nums / self.__post_per_page)
        else:
            post_nums = len(soup.find_all(name='li', class_='_box note'))
            page_nums = 1

        # 所有作品
        if self.post_type == 'all':
            for page_id in range(1, page_nums + 1):
                resp = self.__session.get(url=coser_post_url + '?&p={}'.format(str(page_id)))
                soup = BeautifulSoup(resp.text, 'lxml')
                for tag in soup.find_all(name='li', class_='_box note'):
                    post_urls_list.append(self.__home_url + tag.find('a', class_='db posr').get('href'))
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
        
        logging.info("There are %d posts you can update." % len(post_urls_list))
        self.__post_url_list = post_urls_list

    def __get_pics_url_list(self, post_url):
        """获取每个主题下的所有图片url"""
        
        pics_url_list = []

        resp = self.__session.get(url=post_url)
        soup = BeautifulSoup(resp.text, 'lxml')

        # 判断是否粉丝可见，是就跳过
        if soup.find(name='span', style='padding-left:10px;color:#4d70a5;font-size:16px') is None:
            # 获取所属作品名
            post_name = re.sub(
                r'[\/:*?"<>|]', '-',
                '-'.join(list(map(
                    lambda x: x.find(name='span').get_text().strip().strip('\n').strip('.'),
                    soup.find_all(name='a', class_='dm-tag dm-tag-a ')
                )))
            )
            
            print(post_url, post_name)

            # 获取图片url列表
            ## 半次元为了防止爬虫可谓煞费苦心啊...所有的图片url和加载都用js来控制,
            ## 好在不是很复杂，只要把内容json解析出来就好...
            json_txt = ''
            for script in soup.find_all(name='script'):
                if 'window.__ssr_data = JSON.parse' in script.text:
                    json_txt = script.text

            json_txt = json_txt.split('JSON.parse("')[1].split('");')[0]
            json_txt = json_txt.replace('\\"', '"')
            json_txt = json_txt.replace('\\\\"', '"')
            json_txt = json_txt.replace('https:\\\\u002F\\\\u002F', 'https://')
            json_txt = json_txt.replace('\\\\u002F', '/')
            json_txt = json_txt.replace('"{', '{')
            json_txt = json_txt.replace('}"', '}')

            resp_json = json.loads(json_txt)

            for pic_id, detail in enumerate(resp_json['detail']['post_data']['multi'], 1):
                pics_url_list.append(detail['original_path'] + '?' + str(pic_id))

        else:
            post_name = post_url.split('/')[-1] + '_粉丝可见'
            pics_url_list.append('None')

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
        if pic_url != 'None':
            pic = self.__session.get(pic_url.split('?')[0], timeout=3)
            if pic.status_code is 200:
                logging.info(" url: {} id: {}".format(pic_url.split('?')[0], pic_url.split('?')[1]))
                open(post_dir + '/' + pic_url.split('?')[1] + '.jpg', 'wb').write(pic.content)
            else:
                logging.error(" {} not found. status code: {}".format(pic_url.split('?')[0], pic.status_code))
        else:
            logging.warning('该作品为粉丝可见, 请手动下载')

    def get_pics(self):
        pool = ThreadPool(processes=4)
        logging.info("Downloading...")

        for post_url in self.__download_data.keys():
            logging.info("Downloading pictrues from {}".format(post_url))

            post_name = self.__create_post_dir(self.__download_data[post_url]['post_name'])
            pics_url_list = self.__download_data[post_url]['pics_url_list']

            pool.map(partial(self.__get_pics, post_url, post_name), pics_url_list)
            print(100*"=")
            # time.sleep(1)
        pool.close()
        pool.join()

        print("Download compelete!!")

    def run(self):
        self.get_post_url_list()
        self.get_pics_url_list()
        self.get_pics()
