# -*- coding: utf-8 -*-
from PIL import Image
from bs4 import BeautifulSoup
from keras.models import *
import urllib
import urllib.request
import http.cookiejar
import shutil
import string
import os
import cv2
import numpy as np

temp_dir = (os.environ["TMP"])+'\\evaluateTemp'


def getCheckCode():
    # 携带Cookie获取验证码并保留在CookieJar中管理
    captcha_url = "http://jwgl3.jmu.edu.cn/Common/CheckCode.aspx"
    captcha_path = temp_dir+'\\captcha.gif'
    cookie = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie), urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    captcha = opener.open(captcha_url).read()
    captcha1 = open('./captcha.gif', 'wb')
    captcha1.write(captcha)
    captcha1.close()
    captcha2 = open(captcha_path, 'wb')
    captcha2.write(captcha)
    captcha2.close()
    os.remove('./captcha.gif')

    return captcha_path


def predictCheckCode(captcha_path):
    def color_range(color):
        c_range = 50
        r, g, b = color
        color = [b, g, r]
        return np.clip([i - c_range for i in color], 0, 255), \
               np.clip([i + c_range for i in color], 0, 255)

    colors = [
        color_range([255, 0, 0]),
        color_range([153, 43, 51]),
        color_range([204, 43, 51]),
        color_range([0, 0, 153]),
        color_range([0, 0, 102]),
        color_range([0, 128, 153]),
        color_range([0, 170, 153]),
        color_range([255, 170, 0]),
        color_range([255, 128, 0]),
        color_range([0, 0, 0]),
        color_range([0, 128, 0]),
        color_range([0, 85, 0])
    ]

    def process_image(path):
        code_pic = Image.open(path).convert('RGB').crop((8, 5, 72, 21))
        cv_image = cv2.cvtColor(np.array(code_pic), cv2.COLOR_RGB2BGR)
        pics = []
        center = [6, 18, 30, 42, 54]
        for (lower, upper) in colors:
            # 创建NumPy数组
            lower = np.array(lower, dtype="uint8")  # 颜色下限
            upper = np.array(upper, dtype="uint8")  # 颜色上限

            # 根据阈值找到对应颜色
            mask = cv2.inRange(cv_image, lower, upper)
            if np.sum(mask) > 14000:
                break
        for a in range(5):
            size = (12, 16)
            cropped = cv2.getRectSubPix(mask, size, (center[a], 8))
            pics.append(cropped)
        return pics

    characters = string.digits

    def vec2word(vec):
        char_idxs = np.argmax(vec, axis=1)
        return ''.join([characters[idx] for idx in char_idxs])

    model = load_model('gmu_jw_captcha_break_splited.h5')
    width, height = 12, 16

    images = process_image(captcha_path)
    X = np.zeros((len(images), height, width, 1), dtype=np.uint8)
    for idx, im in enumerate(images):
        X[idx, :, :, 0] = im[:, :]
    y = model.predict(X)
    predict_word = vec2word(y)

    print("Predict: "+predict_word)
    return predict_word


def userLogin(captcha):
    home_url = "http://jwgl3.jmu.edu.cn/Login.aspx"
    home_page = BeautifulSoup(urllib.request.urlopen(home_url), "html.parser", from_encoding="gb2312")
    get_viewstate = (home_page.find_all("input", id="__VIEWSTATE")[0])["value"]

    username = input('输入用户名： ')
    password = input('输入密码： ')
    os.system('cls')

    post_data = urllib.parse.urlencode({
        '__VIEWSTATE': get_viewstate,
        'TxtUserName': username,
        'TxtPassword': password,
        'TxtVerifCode': captcha,
        'BtnLoginImage.x': '0',
        'BtnLoginImage.y': '0'
    })
    post_data = post_data.encode('utf-8')

    # 禁止gzip压缩
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://jwgl3.jmu.edu.cn/Login.aspx',
        'Connection': 'Keep-Alive'
    }

    # 构建请求，模拟登录post
    login_request = urllib.request.Request(home_url, data=post_data, headers=headers)
    login_response = urllib.request.urlopen(login_request)
    login_status = login_response.read()

    # 解析post后页面，判断是否登录
    login_page = BeautifulSoup(login_status, "html.parser", from_encoding='utf-8')
    get_title = str(login_page.find_all("title")[0].get_text(strip=True))
    if get_title == "集美大学综合教务管理系统":
        i = os.system('cls')
        print("你已成功登录！")
        flag = 1
    else:
        print("登录失败。")
        print("请检查用户名密码或验证码是否正确后再次尝试。")
        flag = 0

    return flag


def getPage(href):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'Keep-Alive',
        'DNT': '1',
        'Origin': 'http://jwgl3.jmu.edu.cn',
        'Referer': 'http://jwgl3.jmu.edu.cn/Student/TeacherEvaluation/Main.htm',
        'Upgrade-Insecure-Requests': '1'
    }
    ev_request = urllib.request.Request(href, headers=headers)
    ev_response = urllib.request.urlopen(ev_request)
    ev_status = ev_response.read()
    ev_page = BeautifulSoup(ev_status, "html.parser")
    return ev_page


def getEvaluateList(ev_content):
    bs = BeautifulSoup(ev_content, "html.parser")
    hrefs = bs.find_all("a")
    hrefs_len = len(hrefs)
    print(hrefs_len)
    if hrefs_len != 0:
        for i in range(0, hrefs_len):
            hrefs[i] = hrefs[i].get('href')[26:]+"\n"
        try:
            file = open(temp_dir+"\list", 'w')
            file.writelines(hrefs)
        finally:
            file.close()
    return hrefs_len


def getEvaluateData(courseNum):
    courseUrl = 'http://jwgl3.jmu.edu.cn/Student/TeacherEvaluation/TeacherEvaluate.aspx?Code='+courseNum
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'Keep-Alive',
        'DNT': '1',
        'Origin': 'http://jwgl3.jmu.edu.cn',
        'Referer': 'http://jwgl3.jmu.edu.cn/Student/TeacherEvaluation/TeacherEvaluationList.aspx',
        'Upgrade-Insecure-Requests': '1'
    }
    get_request = urllib.request.Request(courseUrl, headers=headers)
    get_response = BeautifulSoup(urllib.request.urlopen(get_request), "html.parser", from_encoding='utf-8')
    response = str(get_response)
    viewstate = (get_response.find_all("input", id="__VIEWSTATE")[0])["value"]
    return viewstate, response


def postEvaluateData(courseNum, viewstate):
    courseUrl = 'http://jwgl3.jmu.edu.cn/Student/TeacherEvaluation/TeacherEvaluate.aspx?Code='+courseNum
    # 创建post数据
    post_data = urllib.parse.urlencode({
        'ctl00_ToolkitScriptManager1_HiddenField': '',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': viewstate,
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl02$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl03$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl04$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl05$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl06$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl07$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl08$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl09$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl10$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl11$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl12$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl13$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl14$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl15$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$GVTeacherEvaluation$ctl16$AAA': 'RadioButton1',
        'ctl00$ContentPlaceHolder3$TextBoxSumScore': '100',
        'ctl00$ContentPlaceHolder3$TextBoxSuggestion': ' ',
        'ctl00$ContentPlaceHolder3$ButtonSubmit': '提交'
    })
    post_data = post_data.encode('utf-8')
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'Keep-Alive',
        'DNT': '1',
        'Origin': 'http://jwgl3.jmu.edu.cn',
        'Referer': courseUrl,
        'Upgrade-Insecure-Requests': '1'
    }
    post_request = urllib.request.Request(courseUrl, data=post_data, headers=headers)
    post_response = urllib.request.urlopen(post_request)
    print("课程id："+courseNum+" 已完成评测")


def cleanDir(dir_path):
    if os.path.isdir(dir_path):
        paths = os.listdir(dir_path)
        for path in paths:
            filePath = os.path.join(dir_path, path)
            if os.path.isfile(filePath):
                try:
                    os.remove(filePath)
                except os.error:
                    pass
            elif os.path.isdir(filePath):
                if filePath[-4:].lower() == ".svn".lower():
                    continue
                shutil.rmtree(filePath, True)
    os.rmdir(dir_path)
    return True
