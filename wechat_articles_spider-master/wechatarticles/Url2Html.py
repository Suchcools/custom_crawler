# coding: utf-8
import os
import re
import time

import requests
from bs4 import BeautifulSoup as bs


class Url2Html(object):
    """根据微信文章链接下载为本地HTML文件"""

    def __init__(self, img_path=None):
        """
        Parameters
        ----------
        img_path: str
            本地存储图片的路径，采用绝对路径的方式引用图片。可不下载图片
        """
        self.data_src_re = re.compile(r'data-src="(.*?)"')
        self.data_croporisrc_re = re.compile(r'data-croporisrc="(.*?)"')
        self.src_re = re.compile(r'src="(.*?)"')

    @staticmethod
    def replace_name(title):
        """
        对进行标题替换，确保标题符合windows的命名规则

        Parameters
        ----------
        title: str
            文章标题

        Returns
        ----------
        str: 替换后的文章标题
        """
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        title = re.sub(rstr, "", title).replace("|", "").replace("\n", "")
        return title

    def download_img(self, url):
        """
        Parameters
        ----------
        url: str
            图片链接

        Returns
        ----------
        str: 下载图片的本地路径
        """
        # 根据链接提取图片名
        name = "{}.{}".format(url.split("/")[-2], url.split("/")[3].split("_")[-1])
        save_path = os.path.join(self.account, "imgs", name)
        # 如果该图片已被下载，可以无需再下载，直接返回路径即可
        if os.path.isfile(save_path):
            with open(save_path, "rb") as f:
                img = f.read()
            return os.path.join("imgs", name), img

        response = requests.get(url, proxies=self.proxies)
        img = response.content
        with open(save_path, "wb") as f:
            f.write(img)
        return os.path.join("imgs", name), img

    def replace_img(self, html):
        """
        根据提供的html源码找出其中的图片链接，并对其进行替换

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        str: 替换html中在线图片链接为本地图片路径
        """
        data_croporisrc_lst = self.data_croporisrc_re.findall(html)
        data_src_lst = self.data_src_re.findall(html)
        src_lst = self.src_re.findall(html)

        img_url_lst = data_croporisrc_lst + data_src_lst + src_lst
        img_lst = []
        for img_url in img_url_lst:
            if "mmbiz.qpic.cn" in img_url:
                data_src, img = self.download_img(img_url)
                img_lst.append([data_src, img])
                # 以绝对路径的方式替换图片
                html = html.replace(img_url, data_src).replace("data-src=", "src=")
        return html, img_lst

    @staticmethod
    def get_title(html):
        """
        根据提供的html源码提取文章中的标题

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        str: 根据HTML获取文章标题
        """
        try:
            # title = html.split('activity-name">')[1].split('</h2')[0].strip()
            title = html.split("<h2")[1].split("</h2")[0].split(">")[1].strip()
            return title
        except Exception as e:
            try:
                title = html.split("<h1")[1].split("</h1")[0].split(">")[1].strip()
                return title
            except Exception as e:
                return ""
        # if "var msg_title = " in s.text:
        #     ct = s.text.split('var ct = "')[1].split('"')[0]
        #     msg_title = s.text.split("var msg_title = '")[1].split("'")[0]
        # elif "window.msg_title" in s.text:
        #     ct = s.text.split("window.ct = '")[1].split("'")[0]
        #     msg_title = s.text.split("window.msg_title = '")[1].split("'")[0]
        # else:
        #     print(url)


    @staticmethod
    def article_info(html):
        """
        根据提供的html源码提取文章中的公众号和作者

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        (str, str): 公众号名字和作者名字
        """
        # account = (
        #     html.split('rich_media_meta rich_media_meta_text">')[1]
        #     .split("</span")[0]
        #     .strip()
        # )
        account = html.split('nickname = "')[1].split('"')[0]
        author = html.split('id="js_name">')[1].split("</a")[0].strip()
        return account, author

    @staticmethod
    def get_timestamp(html):
        """
        根据提供的html源码提取文章发表的时间戳

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        int: 文章发表的时间戳
        """
        timestamp = int(html.split('ct = "')[1].split('";')[0].strip())
        return timestamp

    @staticmethod
    def timestamp2date(timestamp):
        """
        时间戳转日期

        Parameters
        ----------
        timestamp: int
                时间戳

        Returns
        ----------
        str: 文章发表的日期，yyyy-mm-dd
        """
        ymd = time.localtime(timestamp)
        date = "{}-{}-{}".format(ymd.tm_year, ymd.tm_mon, ymd.tm_mday)
        return date

    def rename_title(self, title, html):
        # 自动获取文章标题
        if title == None:
            title = self.get_title(html)
        if title == "":
            return ""
        title = self.replace_name(title)

        if self.account == None:
            try:
                account_name = self.article_info(html)[0]
            except:
                account_name = "未分类"
            self.account = account_name
        else:
            account_name = self.account
        try:
            date = self.timestamp2date(self.get_timestamp(html))
        except:
            date = ""
        # try:
        if not os.path.isdir(account_name):
            os.mkdir(account_name)
        # except:
        #     account_name = '未分类'
        #     if not os.path.isdir(account_name):
        #         os.mkdir(account_name)

        title = os.path.join(
            account_name, "[{}]-{}-{}".format(account_name, date, title)
        )
        return title

    @staticmethod
    def download_media(html, title):
        soup = bs(html, "lxml")
        # mp3
        mpvoice_item_lst = soup.find_all("mpvoice")
        base_url = "https://res.wx.qq.com/voice/getvoice?mediaid="
        for i, item in enumerate(mpvoice_item_lst, 1):
            if os.path.isfile("{}-{}.mp3".format(title, i)):
                continue
            doc = requests.get(base_url + item["voice_encode_fileid"])
            with open("{}-{}.mp3".format(title, i), "wb") as f:
                f.write(doc.content)

        # video
        if os.path.isfile("{}.mp4".format(title)):
            return ""
        video_url = re.findall(r"url: \'(.+)\',\n", html)
        if video_url:
            video_url = [url for url in video_url if "videoplayer" not in url]
            if video_url:
                video_url = video_url[0].replace(r"\x26", "&")
                doc = requests.get(video_url)
                with open("{}.mp4".format(title), "wb") as f:
                    f.write(doc.content)

    @staticmethod
    def test_replace_img(html):
        return html.replace("data-src=", "src=").replace("wx_fmt=jpeg", "wx_fmt=web")

    def run(self, url, mode, proxies={"http": None, "https": None}, **kwargs):
        """
        Parameters
        ----------
        url: str
             微信文章链接
        mode: int
            运行模式
            1: 返回html源码，不下载图片
            2: 返回html源码，下载图片但不替换图片路径
            3: 返回html源码，下载图片且替换图片路径
            4: 保存html源码，下载图片且替换图片路径
            5: 保存html源码，下载图片且替换图片路径，并下载视频与音频
            6: 返回html源码，不下载图片，替换src和图片为web
        kwargs:
            account: 公众号名
            title: 文章名
            date: 日期
            proxies: 代理

        Returns
        ----------
        str: HTML源码或消息
        """
        self.proxies = proxies
        if mode == 1:
            return requests.get(url, proxies=proxies).text
        elif mode == 6:
            return self.test_replace_img(requests.get(url, proxies=proxies).text)
        elif mode in [2, 3, 4, 5]:
            if mode == 2:
                return requests.get(url, proxies=proxies).text
            elif mode == 3:
                html = requests.get(url, proxies=proxies).text
                html_img, _ = self.replace_img(html)
                return html_img
            else:
                account = kwargs["account"] if "account" in kwargs.keys() else None
                self.account = account
                title = kwargs["title"] if "title" in kwargs.keys() else None
                date = kwargs["date"] if "date" in kwargs.keys() else None
                proxies = kwargs["proxies"] if "proxies" in kwargs.keys() else None
                if self.account and title and date:
                    title = os.path.join(
                        self.account,
                        "[{}]-{}-{}".format(
                            self.account, date, self.replace_name(title)
                        ),
                    )
                    if os.path.isfile("{}.html".format(title)):
                        return 0
                    html = requests.get(url, proxies=proxies).text
                else:
                    html = requests.get(url, proxies=proxies).text
                    title = self.rename_title(title, html)

                if not os.path.isdir(os.path.join(self.account, "imgs")):
                    os.makedirs(os.path.join(self.account, "imgs"))
                if mode == 5:
                    try:
                        self.download_media(html, title)
                    except Exception as e:
                        print(e)
                        print(title)
                html_img, _ = self.replace_img(html)
                with open("{}.html".format(title), "w", encoding="utf-8") as f:
                    f.write(html_img)
                return "{} success!".format(url)
        else:
            print("please input correct mode num")
            return "failed!"


if __name__ == "__main__":

    url_lst = [
        "http://mp.weixin.qq.com/s?__biz=MTc5MTU3NTYyMQ==&mid=2650742058&idx=2&sn=1da6e9ddd1a0281e8c548fb30f8387f0&chksm=5afd0c006d8a851648e91e8cdaebfc2ab61d2518cbba369749b0a29cccb4781c622f966e6b04#rd"
    ]
    uh = Url2Html()
    for url in url_lst:
        s = uh.run(url, mode=4)
        print(s)
