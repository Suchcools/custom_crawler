# coding: utf-8
import os
from pprint import pprint
from wechatarticles import ArticlesInfo

if __name__ == "__main__":
    # 登录微信PC端获取文章信息
    appmsg_token, cookie = "appmsg_token", "cookie"
    article_url = "http://mp.weixin.qq.com/s?__biz=MjM5NDU4ODI0NQ==&mid=2650949647&idx=1&sn=854714295ceee7943fe9426ab10453bf&chksm=bd739b358a041223833057cc3816f9562999e748904f39b166ee2178ce1a565e108fe364b920#rd'"
    test = ArticlesInfo(appmsg_token, cookie)
    comments = test.comments(article_url)
    read_num, like_num, old_like_num = test.read_like_nums(article_url)
    print("comments:")
    pprint(comments)
    print("read_like_num:", read_num, like_num, old_like_num)
