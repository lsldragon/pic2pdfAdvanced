import requests
from colorama import *
import time
import os
import fitz
import threading
import glob
from pyquery import PyQuery as pq

class Comic2PDF():

    # 构造函数
    def __init__(self):

        self.path = "./download/"
        self.file_name = ""
        self.label = "谨以此软件献给永远的神作----龙珠"

    # 获取当前时间戳,这个值无所谓,加上会更有爬虫的尊严。返回值:当前时间的时间戳long类型
    def getmsTime(self):

        t = time.time()
        mst = int(round(t * 1000))
        return mst

    # 获取图片链接地址，批量获取微博头条文章下的所有图片的url链接。返回值：url链接图片列表
    def generate_img_urls(self, id):

        tm = self.getmsTime()
        url = "https://card.weibo.com/article/m/aj/detail?id=%s&_t=%s" % (
            id, str(tm))

        refervalue = "https://card.weibo.com/article/m/show/id/%s" % id
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0".3809.100 Safari/537.36',
                   'Referer': refervalue}

        response = requests.get(url, headers=headers)

        text = response.json()
        self.file_name = text['data']['title']
        print("--------------------------------------")
        print("漫画: " + text['data']['title'])
        print("发布时间: " + text['data']['create_at'])
        print("阅读量: " + text['data']['read_count'])
        print("--------------------------------------")

        img_url_all = text['data']['content']
        pic_url = []
        doc = pq(img_url_all)
        lis = doc('p img').items()
        for li in lis:
            pic_url.append(li.attr('src'))
        return pic_url

    # 创建下载文件夹，建一个临时缓存文件夹用于储存下载图片的位置，最后会被删掉。返回值：文件夹的路径
    def create_down_dir(self):

        path = self.path
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    # 下载图片，获得到图片的url链接后就可下载图片。返回值：文件夹的路径。
    def download_imgs(self, img_urls):

        path = self.create_down_dir()

        count = 1
        for strimg in img_urls:
            response = requests.get(strimg)
            with open(path + str(count).zfill(3) + strimg[-4:], 'wb') as file:
                file.write(response.content)
                print(Fore.GREEN + "已下载 " + strimg)
            count += 1

        return path

    # 生成pdf文档，把下载的图片生成一个默认A4大小的PDF文档。PDF文件的路径是和软件的根路径一样的。
    def generatePDF(self, imgpath):
        doc = fitz.open()
        for img in sorted(glob.glob(imgpath + "*")):
            print(Fore.MAGENTA + "插入图片: " + img)
            imgdoc = fitz.open(img)
            pdfbytes = imgdoc.convertToPDF()
            imgpdf = fitz.open("pdf", pdfbytes)
            doc.insertPDF(imgpdf)

        file_name = self.file_name
        if file_name == "":
            doc.save(str(self.getmsTime()) + ".pdf")
        else:
            doc.save(file_name + ".pdf")

        self.file_name = ""

    # 删除图片文件，只保留pdf。PDF生成成功了，还要缓存的干啥，删掉图片，顺便把缓存的文件夹也删掉。
    def delete_imgs(self, imgpath):
        imgs = glob.glob(imgpath + "*")
        for img in imgs:
            os.remove(img)
            print(Fore.BLUE + "删除缓存 " + img)
        os.removedirs(imgpath)
        print("--------------------------------------")

    # 最后不能忘记再写个作者，我 ^_^
    def paint_author(self):
        about = """\n作者: Elliot Lee \n反馈：lsldragon@ouotlook.com"""
        print(Fore.BLACK + Back.WHITE + about)
        print(Style.RESET_ALL)

    # 从漫画id获取，即微博头条文章
    def get_from_id(self):
        print()
        value = input(Fore.YELLOW + "输入漫画id(微博网页头条文章): ")
        res = self.generate_img_urls(value)
        path = self.download_imgs(res)
        self.generatePDF(path)
        self.delete_imgs(path)
        print(Fore.RED + "生成pdf成功")
        self.paint_author()

    # 从长图的url链接获取,url可从浏览器直接复制，省去了解析链接的麻烦
    def get_from_longimg_url(self):
        print()
        value = input(Fore.YELLOW + "输入长图的url链接: ")
        # 因为download_imgs(value) 传入的value是一个列表，而输入的是一个字符串，所以要将字符转为列表
        path = self.download_imgs([value])
        self.generatePDF(path)
        self.delete_imgs(path)
        print(Fore.RED + "生成pdf成功")
        self.paint_author()

    # 启用进程下载
    def down_videos(self, url):

        print(Fore.GREEN + "正在下载.....")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0".3809.100 Safari/537.36'}
        response = requests.get(url, headers=headers)
        video_name = str(self.getmsTime()) + ".mp4"
        with open(video_name, 'wb') as f:
            f.write(response.content)

    def down_weibo_video(self):
        print()
        help = """获取视频真实地址操作方法:\n
        1. 右键微博视频, 点击视频地址选项，此时会出现该视频的url. Ctrl + C 复制url
        2. 将此url复制到浏览器的搜索框中, 回车. 即是该视频的播放页面
        3. 以谷歌浏览器为例, 按F12, 此时出现浏览器抓包的界面,F5刷新页面
        4. 点击网络(Network), 点击下方的媒体(Meida)
        5. 此时浏览器已经抓到了视频资源，点击出现的选项
        6. 在右侧的头文件(headers)中找到请求url(request url)
        7. 复制request url 后的链接，即使该视频的真实地址
        8. 将真实地址复制到该软件即可
        """
        print(Fore.CYAN + help)
        value = input(Fore.YELLOW + "输入微博视频的视频地址: ")
        print("--------------------------------------")
        print(Fore.GREEN + "正在解析.....\n")
        p = threading.Thread(target=self.down_videos, args=(value,))
        p.start()
        p.join()
        print()
        time.sleep(1.5)
        print(Fore.RED + "下载视频完成")
        print(Fore.YELLOW + "--------------------------------------")
        self.paint_author()

    # 启动程序
    def run(self):
        print()
        print(Fore.WHITE + Back.RED + self.label)
        print(Style.RESET_ALL)
        print()
        options = """选择:
        1. id,微博头条文章的图片转为PDF
        2. 长图,微博的长图链接转换为PDF
        3. 下载微博视频beta
        -> """
        while True:
            try:
                value = input(options)
                if value == "1":
                    self.get_from_id()
                elif value == "2":
                    self.get_from_longimg_url()
                elif value == "3":
                    self.down_weibo_video()
                else:
                    pass
            except:
                print(Fore.RED + "失败！可是我也不太清楚问题出在哪里，请重试")
                print(Style.RESET_ALL)

if __name__ == "__main__":

    c2f = Comic2PDF()
    c2f.run()

print(Style.RESET_ALL)