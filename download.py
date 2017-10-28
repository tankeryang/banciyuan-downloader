import os
from create_user_folder_name import create_user_folder_name
from get_banciyuan_pic import get_pics

if __name__ == '__main__':
	account            = input('input your banciyuan account (phone number/e-mail): ')
	password 	       = input('input your banciyuan password: ')
	user_id            = input('input banciyuan coser id: ')
	banciyuan_home_dir = input('input banciyuan home path (i.e. E:\\banciyuan): ')
	user_dir           = banciyuan_home_dir + '\\' + create_user_folder_name(user_id)

	if not os.path.exists(user_dir):
		os.mkdir(user_dir)
		get_pics(account, password, user_id, user_dir)
	else:
		count = 0
		for fn in os.listdir(user_dir):
			count += 1
		get_pics(account, password, user_id, user_dir, count)