from bcy_downloader import Downloader

if __name__ == '__main__':
    # account = input('Enter your banciyuan account (phone number/e-mail): ')
    # password = input('Enter your banciyuan password: ')
    # coser_id = input('Enter banciyuan coser id: ')
    # bcy_home_dir = input('Enter banciyuan home path (i.e. E:\\banciyuan): ')

    dl = Downloader(account='18926229838', password='banciyuan950820', coser_id='1016773', bcy_home_dir='/Users/yang/Pictures/banciyuan')
    dl.run()
