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
driver.get('https://www.aminer.cn/ai2000')
time.sleep(2)
# 提取页面标题
page_title = driver.title
print('页面标题:', page_title)

# 使用标题文本"AI 2000"来定位<span>元素
span_element = driver.find_element(By.XPATH, '//span[@title="AI 2000"]')

# 找到前一个兄弟元素的按钮
button_element = span_element.find_element(By.XPATH, './preceding-sibling::span[@class="ant-tree-checkbox ant-tree-checkbox-indeterminate"]')

time.sleep(2)
# 执行点击操作
button_element.click()
time.sleep(2)
# 执行点击操作
button_element.click()


# 使用标题文本"人工智能"来定位<span>元素
span_element = driver.find_element(By.XPATH, '//span[@title="人工智能"]')
time.sleep(2)

# 找到该<span>元素之前的兄弟元素的按钮
button_element = span_element.find_element(By.XPATH, './preceding-sibling::span[contains(@class, "ant-tree-checkbox")]')
time.sleep(2)

# 执行点击操作
button_element.click()

time.sleep(2)


# 定位选项卡 
item_name = ['引用值',' 贡献','新星','CSRankings']
button_element = span_element.find_elements_by_xpath('//div[@class="ant-radio-group ant-radio-group-solid"]//label')

for bt_idx in range(len(button_element)):
    button_element[bt_idx].click()
    time.sleep(10)
    # # 使用XPath找到符合条件的所有元素
    elements = driver.find_elements_by_xpath("//div[contains(@class, 'a-aminer-p-rankings-components-ai2000_right_list-index-scholar_list_ai')]//div[starts-with(@class, 'a-aminer-p-rankings-components-ai2000_right_list-index-newScholarCard')]")

    print(len(elements))
    res = []
    # 遍历匹配的元素并进行操作
    for element in elements:
        # 执行您需要的操作，例如打印文本
        res.append(element.text.split("\n"))
    elements = [x for x in res if x!='']

    if bt_idx !=3:
    # 保存到CSV文件
        with open(f"AI2000-人工智能学者-{item_name[bt_idx]}排行榜.csv", 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # 写入标题行
            header = ['Rank', 'Rank Change', 'Author', 'Affiliation', 'Field 1', 'Field 2', 'Field 3', 'Field 4', 'Field 5', 'Score']
            csv_writer.writerow(header)
            
            # 写入数据行，带有异常处理
            for element in elements:
                try:
                    csv_writer.writerow(element)
                except Exception as e:
                    print("写入CSV文件时发生异常:", str(e))
    else:
        pd.DataFrame(elements).head(100).to_csv(f"AI2000-人工智能学者-{item_name[bt_idx]}排行榜.csv",index=False)
    print(f"人工智能学者-{item_name[bt_idx]}榜.csv")


# 关闭浏览器窗口
driver.close()
