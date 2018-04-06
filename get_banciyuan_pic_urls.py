import requests
import time
import math
import re
import logging
from bs4 import BeautifulSoup
logging.basicConfig(level=logging.INFO)


headers  = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.1144',
    'Connection' : 'keep-alive',
    'Referer' : 'http://bcy.net'
}


def get_post_urls(coser_id, count, home_url='https://bcy.net'):
    """
    获取发布作品的url列表
    :params coser_id: 要下载的coser的id号(type: int)
    :params count:    本地已下载的作品数/文件夹数(type: int)
    :params home_url: 半次元官网url(type: string)
    :return post_url_list: 发布作品的url列表(type: list)
    """

    post_per_page = 12
    post_urls_list = []
    
    coser_post_url = home_url + '/u/' + str(coser_id) + '/post/cos'
    session = requests.session()
    html = session.get(url=coser_post_url, headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')

    # 获取发布作品数与显示页数
    if soup.find(
        name='li', class_='pager__item pager__item--is-cur pager__item--disabled'
    ) is not None:
        post_nums_text = soup.find(
            name='li', class_='pager__item pager__item--is-cur pager__item--disabled'
        ).find('span').get_text()
        post_nums = eval(
            post_nums_text.strip(post_nums_text[0]).strip(post_nums_text[len(post_nums_text) - 1])
        )
        page_nums = math.ceil(post_nums / post_per_page)
    else:
    	post_nums = len(soup.find_all(name='li', class_='_box posr imgCard-l'))
    	page_nums = 1

    # 需要更新下载的作品数(本地有的就不用重新下了)
    new_posts_nums = post_nums - count
    
    # 第一次下载
    if new_posts_nums > 0 and count == 0:
        for page_id in range(1, page_nums + 1)[::-1]:
            html = session.get(url=coser_post_url + '?&p={}'.format(str(page_id)), headers=headers)
            soup = BeautifulSoup(html.text, 'lxml')
            for tag in soup.find_all(name='li', class_='_box posr imgCard-l')[::-1]:
                post_urls_list.append(home_url + tag.find('a', class_='postWorkCard__link').get('href'))
    
    # 更新下载
    elif new_posts_nums > 0 and count != 0:
        jump_post_count = 0       # 需要跳过下载的作品计数
        new_download_count = 0    # 需要新下载的作品计数
        new_page_count = 0        # 需要新下载的页计数
        last_page_id = page_nums  # 最后一页页码

        html = session.get(url=coser_post_url + '?&p={}'.format(str(last_page_id)), headers=headers)
        soup = BeautifulSoup(html.text, 'lxml')

        #最后一页显示作品数
        last_page_post_nums = len(soup.find_all(name='li', class_='_box posr imgCard-l'))

        for page_id in range(1, math.ceil((new_posts_nums / post_per_page) + 1))[::-1]:
            html = session.get(url=coser_post_url + '?&p={}'.format(str(page_id)), headers=headers)
            soup = BeautifulSoup(html.text, 'lxml')

            new_page_count += 1

            for tag in soup.find_all(name='li', class_='_box posr imgCard-l')[::-1]:
                if new_page_count == 1 \
                    and count % post_per_page != 0 \
                    and jump_post_count < (count - last_page_post_nums) % post_per_page:
                    jump_post_count += 1
                else:
                    post_urls_list.append(home_url + tag.find(name='a', class_='postWorkCard__link').get('href'))
                    new_download_count += 1
                    if new_download_count == new_posts_nums:
                        break
    
    # 无需更新
    else:
        logging.info('the local post is latest, need not to download.')
    
    return post_urls_list


def get_pic_urls(account, password, post_url, post_count):
    """
    获取图片url
    :params account:    登录账号(type: string)
    :params password:   登录密码(type: string)
    :params post_url:   所属作品url(type: string | from: get_pic_url_list())
    :params post_count: 下载过程计数/从第post_count个主题下载(type: int)
    :return post_name:    所属作品名(type: string)
    :return pic_url_list: 图片url列表(type: list)
    """

    pic_urls_list = []
    logging.info('getting pics from post [{}]: '.format(str(post_count)) + post_url + ' ...')

#    time.sleep(5)
    session = requests.session()
    html = session.get(url=post_url, headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')

    # 粉丝可见的作品就将账号密码post过去，前提是你关注了
    if soup.find(name='div', class_='l-detail-no-right-to-see') is not None:
        login_url = 'https://bcy.net/public/dologin'
        form_data = {
            'email':account,
            'password':password,
            'remember':'1'
        }
        session.post(url=login_url, data=form_data, headers=headers)
        html = session.get(url=post_url, headers=headers)
        soup = BeautifulSoup(html.text, 'lxml')

    # 获取所属作品名
    if soup.find(name='div', class_='post__title').find('h1') is not None:
        post_name = re.sub(
            r'[\/:*?"<>|]',
            '',
            soup.find(
                name='div',
                class_='post__title'
            ).find('h1').get_text().strip().strip('\n').strip('.')
        )
    else:
    	post_name = re.sub(
            r'[\/:*?"<>|]',
            '',
            soup.find(
                name='li',
                class_='tag'
            ).find(
                'i',
                class_='i-origin-tag vam'
            ).get_text().strip().strip('\n').strip('.')
        )

    # 获取图片url列表
    for tag in soup.find_all(name='img', class_='detail_std detail_clickable'):
        pic_url = tag.get('src')
        if pic_url.find('.jpg') != -1:
            pic_urls_list.append(pic_url.split('.jpg')[0] + '.jpg')
        elif pic_url.find('.png') != -1:
            pic_urls_list.append(pic_url.split('.png')[0] + '.png')

    return post_name, pic_urls_list