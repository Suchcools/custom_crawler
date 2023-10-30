# 导入必要的库
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import csv
import pandas as pd
# 创建一个WebDriver实例，选择使用Chrome浏览器
driver = webdriver.Chrome()

# 打开网站
driver.get('https://www.aminer.cn/ranks/org?domain_ids=624521982faec9f93681e73b&search=&metric=h5_index&region=all&type=all')
time.sleep(2)
# 提取页面标题
page_title = driver.title
print('页面标题:', page_title)

time.sleep(30)
cols = ['排名','机构','头衔','H5指数','H5中位数']
elements = driver.find_elements_by_xpath("//tr[@class='ant-table-row ant-table-row-level-0']")
res = []
# 遍历匹配的元素并进行操作
for element in elements:
    # 执行您需要的操作，例如打印文本
    res.append(element.text.split("\n"))

pd.DataFrame(res,columns =cols ).to_csv("人工智能机构排名.csv",index=False)

# 关闭浏览器窗口
driver.close()
