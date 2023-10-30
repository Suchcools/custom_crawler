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
driver.get('https://www.aminer.cn/ranks/aicity')
time.sleep(2)
# 提取页面标题
page_title = driver.title
print('页面标题:', page_title)


# 定位选项卡 
item_name = ['国外','国内']
cols = ['排名','城市','创新指数','论文指数','学者指数','机构指数','国际指数']
button_element = driver.find_elements_by_xpath('//div[@class="a-aminer-p-rankings-rank-city-index-radioBox"]//label')

for bt_idx in range(len(button_element)):
    if bt_idx == 0:
        elements = driver.find_elements_by_xpath("//tr[@class='ant-table-row ant-table-row-level-0']")

        res = []
        # 遍历匹配的元素并进行操作
        for element in elements:
            # 执行您需要的操作，例如打印文本
            temp = element.text.split("\n")[:2]
            temp.extend(element.text.split("\n")[-1].split(' '))
            res.append(temp)

        pd.DataFrame(res,columns =cols ).to_csv("国外创新城市排名.csv",index=False)
    elif bt_idx ==1 :
            button_element[bt_idx].click()
            time.sleep(10)
            elements = driver.find_elements_by_xpath("//tr[@class='ant-table-row ant-table-row-level-0']")

            res = []
            # 遍历匹配的元素并进行操作
            for element in elements:
                # 执行您需要的操作，例如打印文本
                temp = element.text.split("\n")[:2]
                temp.extend(element.text.split("\n")[-1].split(' '))
                res.append(temp)

            pd.DataFrame(res,columns =cols ).to_csv("国内创新城市排名.csv",index=False)

# 关闭浏览器窗口
driver.close()
