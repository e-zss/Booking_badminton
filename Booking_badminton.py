import time
import pytesseract
from PIL import Image
from selenium import webdriver
import datetime
import random
import os
from selenium.webdriver.common.by import By


def main(reserverdic):
    Dstate = 0  # 0 for start,1 for select which game,2 for select which day,3 for select which time
    ErrorCnt = 0
    # 隐藏浏览器界面
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--no-sandbox')
    bro = webdriver.Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe',options=option)

    print("Chrome 已启动")
    url = 'https://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal'
    bro.get(url)
    # 登录信息门户
    id = reserverdic["idpwd"]["ssid"]
    pwd = reserverdic["idpwd"]["pwd"]
    time.sleep(1)
    while (Dstate == 0):
        try:
            bro.implicitly_wait(3)
            input_username = bro.find_element(By.ID,"username")
            input_password = bro.find_element(By.ID,"password")
            input_username.send_keys(id)
            input_password.send_keys(pwd)
            # 多个class 要用下面的形式 不能直接find_element_by_class
            botton_login = bro.find_element(By.CSS_SELECTOR,"[class='auth_login_btn primary full_width']")
            botton_login.click()
            print("登录成功")
            ErrorCnt = 0
            Dstate = 1
        except Exception:
            print("登录失败，重新登录")
            ErrorCnt = ErrorCnt + 1;
            if (ErrorCnt > 3):
                bro.refresh()
                time.sleep(1)
            if (ErrorCnt > 5):
                print("预约失败")
                bro.quit()
                return 0
    # 进入预约系统
    url2 = "http://yuyue.seu.edu.cn/eduplus/order/initOrderIndex.do?sclId=1"
    bro.get(url2)
    # 选择羽毛球
    time.sleep(1)
    BallPath = '//*[@id="container"]/div/div/table/tbody/tr/td[2]/div[1]/ul/li[' + reserverdic["info"][
        "Ball"] + ']/input'
    while (Dstate == 1):
        try:
            bro.implicitly_wait(2)  # 等待页面刷新
            botton1 = bro.find_element(By.XPATH,BallPath)
            botton1.click()
            print("球类已选择")
            ErrorCnt = 0
            Dstate = 2
        except Exception:
            print("球类选择失败，重新选择中")
            ErrorCnt = ErrorCnt + 1;
            if (ErrorCnt > 3):
                bro.refresh()
                time.sleep(1)
            if (ErrorCnt > 5):
                print("预约失败")
                bro.quit()
                return 0
    # 选择第三天
    time.sleep(1)
    DatePath = '//*[@id="container"]/div/div/table/tbody/tr/td[1]/ul/li[' + reserverdic["info"]["Date"] + ']'
    while (Dstate == 2):
        try:
            bro.implicitly_wait(2)  # 等待页面刷新
            botton1 = bro.find_element(By.XPATH,DatePath)
            botton1.click()
            print("日期已选择")
            ErrorCnt = 0
            Dstate = 3
        except Exception:
            print("日期选择失败，重新选择中")
            ErrorCnt = ErrorCnt + 1;
            if (ErrorCnt > 5):
                print("预约失败")
                bro.quit()
                return 0
    time.sleep(1)
    # 选择15-16点
    TimePath = '//*[@id="orderInfo"]/div[1]/div[1]/div[' + reserverdic["info"]["Time"] + ']/a'
    while (Dstate == 3):
        try:
            bro.implicitly_wait(4)  # 等待帧刷新
            botton1 = bro.find_element(By.XPATH,TimePath)
            botton1.click()
            print("时间已选择")
            Dstate = 4
            ErrorCnt = 0
        except Exception:
            print("时间选择失败，重新选择中")
            ErrorCnt = ErrorCnt + 1;
            bro.get_screenshot_as_file(str(ErrorCnt) + 'D3.png')
            if (ErrorCnt > 10):
                print("预约失败")
                bro.quit()
                return 0
    # 处理验证码

    screenshot = str(random.randint(1, 100000)) + 'screenshot.png'
    validcodeshot = str(random.randint(1, 100000)) + 'validateimage.png'
    time.sleep(3)
    while (Dstate == 4):
        try:
            bro.implicitly_wait(6)  # 等待帧刷新
            nextf = bro.find_element(By.TAG_NAME,"iframe")
            print("预约窗口已选中")
            Dstate = 5
            ErrorCnt = 0
        except Exception:
            print("预约窗口未选中，重新选择中")
            ErrorCnt = ErrorCnt + 1;
            if (ErrorCnt > 5):
                print("预约失败")
                bro.quit()
                return 0
    offsetx = nextf.location['x']  # 帧的偏移位置
    offsety = nextf.location['y']
    bro.switch_to.frame(nextf)
    while (Dstate == 5):
        try:
            img = bro.find_element(By.XPATH,'//*[@id="fm"]/table/tbody/tr[6]/td[2]/img')
            bro.get_screenshot_as_file(screenshot)
            print("验证码已采集")
            ErrorCnt = 0
            Dstate = 6
        except Exception:
            ErrorCnt = ErrorCnt + 1;
            if (ErrorCnt > 5):
                print("预约失败")
                bro.quit()
                return 0
    # 通过Image处理图像
    im = Image.open(screenshot)
    left = int(img.location['x'] + offsetx)
    top = int(img.location['y'] + offsety)
    right = int(img.location['x'] + img.size['width'] + offsetx)
    bottom = int(img.location['y'] + img.size['height'] + offsety)
    im = im.crop((left, top, right, bottom))
    # im = im.crop((676, 497, 767, 525))#显示测试用
    im.save(validcodeshot)

    img = Image.open(validcodeshot)
    validcode = pytesseract.image_to_string(img)
    print(validcode)
    input_validcode = bro.find_element(By.ID,"validateCode")
    input_validcode.send_keys(validcode)
    button_reserve = bro.find_element(By.ID,"do-submit")
    button_reserve.click()

    os.remove(screenshot)
    os.remove(validcodeshot)
    time.sleep(1)

    try:
        bro.implicitly_wait(10)
        alertcontent = bro.find_element(By.CSS_SELECTOR,"[class='xubox_msg xubox_text']")
        if alertcontent.get_attribute("textContent"):
            print(alertcontent.get_attribute("textContent"), "预约失败")
            bro.quit()
            return 0
    except Exception:
        bro.quit()
        print("预约成功")
    return 1


def mmain():
    # 测试用例
    reserverdic1 = {
        "idpwd": {
            'ssid': "220202864",
            'pwd': "zhang66600"
        },
        "info": {
            'Ball': '4',  # 1是乒乓球，4是羽毛球
            'Date': '3',  # 3是后天,1是今天，2是明天
            'Time': '7'  # 7是周末15-16点，周内16-17点
        },
        "phonemate": {
            "phone": 18795880295,
            "mateid": [],  # list 所有好友id
            "halffull": 1  # 1表示全场，2表示半场，非蓝球默认位1，或者空
        }
    }

    state = 0
    ErC = 0
    while (1):
        if (state == 0):
            now_time = datetime.datetime.now()
            now_time_hour = int(datetime.datetime.strftime(now_time, '%H'))
            now_time_minute = int(datetime.datetime.strftime(now_time, '%M'))
            if (now_time_hour == 8 and now_time_minute == 00):
                state = 1
        if (state == 1):
            response = main(reserverdic1)
            if (response == 0):
                ErC = ErC + 1
            if (response == 1):
                state = 0
                return 0
            if (ErC >= 10):
                print("网络状态不佳，无法预约")
                ErC = 0
                state = 0
                return 0


if __name__ == '__main__':
    # mmain()

    mmain()