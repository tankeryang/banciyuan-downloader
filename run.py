from bcy_downloader import Downloader

if __name__ == '__main__':
    # account = input('Enter your banciyuan account (phone number/e-mail): ')
    # password = input('Enter your banciyuan password: ')
    coser_id = input('Enter banciyuan coser id: ')
    bcy_home_dir = input('Enter banciyuan home path (i.e. [WINDOWS]E:\\banciyuan | [MAC/LINUX]/home/username/Picture/banciyuan): ')

    dl = Downloader(coser_id=coser_id, bcy_home_dir=bcy_home_dir)
    dl.run()
