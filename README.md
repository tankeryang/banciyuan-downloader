# banciyuan-downloader v2.2

> 请勿用于商业用途 尊重coser的版权 转载图片请注明出处

此脚本实现了cos网站[半次元](https://bcy.net) __自定义coser__ 的 __高清无码__ 图片批量下载，并保存到 __自定义路径__ 下

## 实现功能

* [x] 根据`coser_id`批量下载某个coser发布的作品的所有图片
* [x] 图片保存在以 __coser名__ 命名的文件夹内
* [x] 图片按 __coser发布的作品__ 分文件夹保存，文件夹命名以 __作品标签__ 拼接而成
* [x] 若有相同标题的作品，则命名文件夹时会加上 __顺序编号后缀__ 防止文件名冲突
* [x] 图片命名格式为`%num%.jpg`/`%num%.png`，其中`%num%`为从`1`开始的 __编号__
* [x] 支持智能下载 __本地没有的作品__，本地已有的作品 __不会__ 重复下载
* [x] 支持 __断点续传__ （从断连作品的下一个作品开始下载，若断连作品没下载完，则会丢失一部分断连作品的图片，其余均不影响）
* [x] 支持超时自动重试
* [x] 支持下载指定作品
* [x] 根据频繁I/O进行 __多线程优化__
* [ ] 不支持无半次元账号的下载，因为有 __只有粉丝可见__ 的限制，最好注册一个半次元账号
* [ ] 只有粉丝可见的作品需关注该coser后方可下载
* [ ] 暂时不支持只下载`COS`类的作品，因为半次元改版后没有对`COS`和`绘画`之类的做分类，都在同一`url`下

## 依赖的库

我的测试环境:

* python 3.6.4
* beautifulsoup 4.5.3
* requests 2.13.0
* lxml 3.7.2

## 如何使用

* 先clone代码
    ```shell
    git clone https://github.com/tankeryang/banciyuana-downloader.git
    ```

* 直接运行`run.py`

    先执行:
    ```python
    python run.py
    ```

    后续步骤参考[Usage](#usage)

* 自定义实现

    因为进行了 __封装__，所以可以自行实例化一个`Downloader`对象来调用方法实现功能，下面给出简单例子:

    __分部执行__
    ```python
    from bcy_downloader import Downloader

    # 实例化Downloader对象
    # coser_id: 770554
    # 下载目录: E:\banciyuan (注意: windows下需按照windows特有的 <反斜杠 \> 来分隔路径，如 E:\xxx\pictures\banciyuan)
    dl = Downloader(coser_id='770554', bcy_home_dir='E:\\banciyuan')

    # 获取作品url列表
    dl.get_post_url_list()

    # 或者自定义下载作品列表
    dl.post_url_list = ["https://bcy.net/item/detail/6558754255610577155", "https://bcy.net/item/detail/6554677621064466692"]

    # 查看作品url列表
    print(dl.post_url_list)

    # 获取每个作品下所有图片url，得到download_data
    dl.get_pics_url_list()

    # 查看download_data
    # 格式如下
    # {
    #   '$(post_url)':
    #   {
    #     'post_name': $(post_name),
    #     'pics_url_list': $(pics_url_list)
    #   }
    # }
    # 例子:
    # {
    #   "https://bcy.net/item/detail/6558754255610577155":
    #   {
    #     'post_name': "碧蓝航线-COS-舰娘-场照-返图-cp22-三笠",
    #     'pics_url_list': [
    #       'https://img5.bcyimg.com/user/770554/item/c0je3/63y6vuq8hhgfmge7nrqcaqkpspyfszj5.jpg?1',
    #       'https://img9.bcyimg.com/user/770554/item/c0je3/esdrtvchzzkfzm74ezd8idx04ennjjfr.jpg?2',
    #       ......
    #       'https://img9.bcyimg.com/user/770554/item/c0je3/zfiyptpdcpasyz0itzh7ndtmpiysw8uy.jpg?9'
    #     ]
    #   }
    # }
    print(dl.download_data)

    # 根据download_data获取图片
    dl.get_pics()
    ```

    __一键执行__
    ```python
    from bcy_downloader import Downloader

    # 实例化Downloader对象
    # coser_id: 770554
    # 下载目录: E:\banciyuan (注意: windows下需按照windows特有的 <反斜杠 \> 来分隔路径，如 E:\xxx\pictures\banciyuan)
    dl = Downloader(coser_id='770554', bcy_home_dir='E:\\banciyuan')

    # 自动下载
    dl.run()
    ```

## 注意

下载时会在 __每个作品对应的文件夹__ 里建一个`url.local`文件，里面写入的是该作品对应的`url`。该文件主要用于 __判断本地是否已经下载过该`url`对应的作品，以实现智能无重复下载，请不要随意删除__

同时因为取消了登录的功能，所以 __只有粉丝可见的作品__ 会跳过不进行下载，但是也会在本地建一个 __xxx_粉丝可见__ 的文件夹，`xxx`为`作品url`后面的数字，文件夹下面一样会新建`url.local`文件，里面保存的是该作品对应的`url`

__Release__ 版本的`exe`可执行文件可直接运行

## Usage

以下载[coser犬神洛洛子](https://bcy.net/u/770554)发布的所有作品的cos图为例

* 图1：coser主页
    ![coser_page](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/coser_page.png)

* 图2：coser发布的作品页
    ![post_page](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/post_page.png)

* 获取`coser id`: `770554`(上图1箭头所指)

* 运行`run.py`脚本: `python run.py`

* `Enter banciyuan coser id:`: 输入coser id```770554```

* `Enter banciyuan home path (i.e. E:\banciyuan):`: 输入半次元图片保存主目录（如`E:\banciyuan`）

* `downloading...`：等待下载完成

图片会 __按发布的作品分类__ 保存在如下路径：`{banciyuan_home_path}/{coser_name}/{post_name}/`

其中:

* `{banciyuan_home_path}`为图片保存的主目录名

* `{coser_name}`为coser名

* `{post_name}`为coser发布的作品名

如下图:
![home_folder](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/home_folder.png)
![coser_folder](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/coser_folder.png)
![post_folder](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/post_folder.png)

## FAQ

有何疑问可发布 __issue__ ，本人会尽量及时查看