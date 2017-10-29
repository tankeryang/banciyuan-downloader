import os
from create_user_folder_name import create_user_folder_name
from get_banciyuan_pic import get_pics

if __name__ == '__main__':
    account = input('input your banciyuan account (phone number/e-mail): ')
    password = input('input your banciyuan password: ')
    coser_id = input('input banciyuan coser id: ')
    banciyuan_home_dir = input('input banciyuan home path (i.e. E:\\banciyuan): ')
    coser_dir = banciyuan_home_dir + '\\' + create_user_folder_name(coser_id)

    if not os.path.exists(coser_dir):
        os.mkdir(coser_dir)
        get_pics(account, password, coser_id, coser_dir)
    else:
        count = len(os.listdir(coser_dir))
        get_pics(account, password, coser_id, coser_dir, count)