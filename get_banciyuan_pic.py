import requests
import time
import os
import random
import logging
from get_banciyuan_pic_urls import get_post_urls, get_pic_urls
logging.basicConfig(level=logging.INFO)


def get_pics(account, password, coser_id, coser_dir, count=0):
    """
    获取原图，保存到本地
    :params account:    登录账号(type: string)
    :params password:   登录密码(type: string)
    :params coser_id:   要下载的coser的id号(type: int)
    :params coser_dir:  coser作品存放文件夹路径(type: string)
    :params count:      本地已下载的作品数(type: int)
    :return:
    """

    logging.info('downloading...')

    # 获取发布作品url列表
    post_urls_list = get_post_urls(coser_id, count)

    if post_urls_list is not None:
        post_nums = 1

        for post_url in post_urls_list:
            post_name, pic_urls = get_pic_urls(account, password, post_url, post_nums)
            post_dir = coser_dir + '/' + post_name
            
            # 创建新作品文件夹
            if not os.path.exists(post_dir):
                os.makedirs(post_dir)
            # 处理同名作品
            else:
                is_exists = True
                while is_exists:
                    post_dir = post_dir + '(' + str(random.randint(1, 10)) + ')'
                    if not os.path.exists(post_dir):
                        os.makedirs(post_dir)
                        is_exists = False
                    pass
            time.sleep(3)

            # 下载图片并保存到本地
            number = 0
            for pic_url in pic_urls:
                time.sleep(2)
                pic = requests.get(pic_url)
                if pic.status_code is 200:
                    number += 1
                    open(post_dir + '/' + str(number) + '.jpg', 'wb').write(pic.content)
            post_nums += 1

    logging.info('done.')
    