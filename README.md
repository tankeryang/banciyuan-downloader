# banciyuan_downloader v1.0 --(Continuous updating 持续更新中)
<strong><center><font color="#ff0000">请勿用于商业用途 尊重coser的版权 转载图片请注明出处</font></center></strong>

此脚本实现了cos网站[半次元](https://bcy.net) __自定义coser__ 的 __高清无码__ 图片批量下载，并保存到 __自定义路径__ 下

## 实现功能
* [x] 根据```coser_id```批量下载某个coser发布的主题的所有图片
* [x] 图片保存在以 __coser名__ 命名的文件夹内
* [x] 图片按 __coser发布的主题__ 分文件夹保存，文件夹以主题标题命名
* [x] 若有相同标题的主题，则命名文件夹时会加上随机后缀防止文件名冲突
* [x] 图片命名格式为```%num%.jpg```/```%num%.png```，其中```%num%```为从```1```开始的 __编号__ 
* [x] 只下载 __最新__ 发布的图片，本地已有的 __不会__ 重复下载
* [x] 支持 __断点续传__ （从断连主题的下一个主题开始下载，若断连主题没下载完，则会丢失一部分断连主题的图片，其余均不影响）
* [ ] 不支持无半次元账号的下载，因为有 __只有粉丝可见__ 的限制，最好注册一个半次元账号
* [ ] 不支持下载指定主题
* [ ] 不支持智能下载 __未下载过的主题__ 
* [ ] 只有粉丝可见的主题需关注该coser后方可下载


## Environment and package version
* windows 10 1703-15063.674
* python 3.6.1
* beautifulsoup 4.5.3
* requests 2.13.0
* lxml 3.7.2

## Installation
```
git clone https://github.com/tankeryang/banciyuana-downloader.git
```

## Usage
以下载[coser犬神洛洛子](https://bcy.net/u/770554)发布的所有主题的cos图为例
* 图1：coser主页
![coser_page](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/coser_page.png)
* 图2：coser发布的主题页
![post_page](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/post_page.png)
* 获取```coser id```：```770554```（上图1箭头所指）
* 运行```download.py```脚本：```python download.py```
* ```input banciyuan account(phone number/e-mail): ```：输入半次元账号
* ```input banciyuan password: ```：输入登录密码
* ```input banciyuan coser id: ```：输入coser id```770554```
* ```input banciyuan home path (i.e. E:\\banciyuan): ```：输入半次元图片保存主目录（如```E:\banciyuan```）
* ```downloading...```：等待下载完成

图片会 __按发布的主题分类__ 保存在如下路径：```{banciyuan_home_path}/{coser_name}/{post_name}/```
其中：
* ```{banciyuan_home_path}```为图片保存的主目录名
* ```{coser_name}```为coser名
* ```{post_name}```为coser发布的主题名
如下图：
![home_folder](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/home_folder.png)
![coser_folder](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/coser_folder.png)
![post_folder](https://github.com/tankeryang/banciyuan-downloader/blob/master/README/post_folder.png)

## F&Q
有何疑问可发布 __issue__ ，本人会尽量及时查看