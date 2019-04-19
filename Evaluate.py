# -*- coding: utf-8 -*-
import os
import func

os.system("title 集美大学教务系统自动评测 v20180111 - Author : https://blog.alexv525.com/")
temp_dir = (os.environ["TMP"])+'\\evaluateTemp'
try:
    func.cleanDir(temp_dir)
except FileNotFoundError:
    pass
os.mkdir(temp_dir)

# 登录过程

flag = func.userLogin(func.predictCheckCode(func.getCheckCode()))

# 登录后执行抓取评测列表，进行逐个评测
if flag == 1:
    print("获得评测课程列表中...")
    ev_url = 'http://jwgl3.jmu.edu.cn/Student/TeacherEvaluation/TeacherEvaluationList.aspx'
    ev_list = str(func.getPage(ev_url))
    courseCount = func.getEvaluateList(ev_list)
    print("共有%d门课程需要教学测评。" % courseCount)
    if courseCount != 0:
        try:
            file = open(temp_dir+"\\list", 'r+')
            hrefs = file.readlines()
        finally:
            file.close()
        print("正在开始评测进程...")
        print("*注：评测时间与当前教务系统服务器状态挂钩，如时间较长请耐心等待。")
        hrefs_num = len(hrefs)
        for i in range(0, hrefs_num):
            hrefs[i] = hrefs[i].replace("\n", "")
            viewstate, response = func.getEvaluateData(hrefs[i])
            if response == ev_list:
                print('课程id：'+hrefs[i]+' 已评测过，跳过')
            else:
                func.postEvaluateData(hrefs[i], viewstate)
        print('评测完成。')

os.system('pause')
