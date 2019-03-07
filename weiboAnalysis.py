#-*- coding:utf-8 -*-

"""
爬取新浪微博的用户信息
功能：用户ID 用户名 粉丝数 关注数 微博数 微博内容
网址：www.weibo.cn 数据量更少相对于 www.weibo.cn
"""
import  time
import re
import codecs
from selenium import webdriver
import selenium.webdriver.support.ui as ui

import config as cf

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import shutil
import urllib
import  os
import  sys
#先调用无界面浏览的浏览器 PhantomJS 或Firefox

driver=webdriver.Chrome()

wait=ui.WebDriverWait(driver,10)


#全局变量 文件操作的读写信息
inforead=codecs.open("SinaWeibo_List.txt",'r','utf-8')
infofile=codecs.open("SinaWeibo_Info.txt",'a','utf-8')
followfile=codecs.open("SinaWeibo_Follow_Info.txt",'a','utf-8')

# 登陆函数
def LoginWeibo(username,password):
    try:
        print(u'准备登陆weibop.cn网站..')
        driver.get("http://weibo.cn/3985356869")
        # driver.get("http://login.weibo.cn/login/")
        #
        time.sleep(3)
        #
        # login_button = driver.find_element_by_css_selector('body > div > div > a.btn.btnWhite')
        # login_button.click()

        elem_user=driver.find_element_by_id("loginName") # find_element_by_name("mobile")
        elem_user.send_keys(username) #用户名
        elem_pwd=driver.find_element_by_id("loginPassword")           #("/html/body/div[2]/form/div/input[2]")
        elem_pwd.send_keys(password) #密码
        #elem_rem=driver.find_element_by_name("remember")
        #elem_rem.click()

        #重点：暂停时间输入验证码
        # time.sleep(30)

        elem_sub=driver.find_element_by_id("loginAction")
        elem_sub.click() # 点击登陆
        time.sleep(3)

        # 获取Coockie 推荐 http://www.cnblogs.com/fnng/p/3269450.html
        #print driver.current_url
        """
        print driver.get_cookies() #获得cookie信息dict 存储
        print u'输出cookie对应的键值信息:'
        for cookie in driver.get_cookies():
            for key in cookie:
                print key,cookie[key]
        """
        print(u'登陆成功...')
    except Exception as e:
        print("Error:",e)
    finally:
        print(u'End loginWeibo!\n\n')

##第二步访问 个人页面 http://weibo.cn/userId
def VisitPersonPage(user_id):
    try:
        global  infofile
        print(u'准备访问个人网站...')
        driver.get("http://weibo.cn/"+user_id)
        ##第一步直接获取用户昵称 微博数 关注数 粉丝数
        #str_name.text 是unicode 编码类型

        #用户id
        print(u'个人详细信息')
        print('*****************')
        print(u'用户id:'+user_id)

        #昵称
        str_name=driver.find_element_by_xpath("//div[@class='ut']")#/html/body/div[4]/div[1]
        str_t=str_name.text.split(" ")
        num_name=str_t[0]
        print(u'昵称:'+num_name)

        #微博数 除了个人主页外 它默认直接显示微博数 无超链接
        str_wb=driver.find_element_by_xpath("//div[@class='tip2']")
        pattern=r"\d+\.?\d*"  #正则提取"微博[0]" 但r"(\[.*?\])"总含[]
        guid=re.findall(pattern,str_wb.text,re.S|re.M)
        print(str_wb.text)
        for value in guid:
            num_wb=int(value)
            break
        print('微博数:'+str(num_wb))

        #关注数目
        str_gz=driver.find_element_by_xpath("//div[@class='tip2']/a[1]")
        num_gz_temp=re.findall(pattern,str_gz.text,re.S|re.M)
        num_gz=int(num_gz_temp[0])
        print('关注数目:'+str(num_gz))

        #粉丝数目
        str_fs = driver.find_element_by_xpath("//div[@class='tip2']/a[2]")
        num_fs_temp = re.findall(pattern, str_fs.text, re.S | re.M)
        num_fs = int(num_fs_temp[0])
        print('粉丝数目:' + str(num_fs))
        # ***************************************************************************
        # No.2 文件操作写入信息
        # ***************************************************************************

        infofile.write('=====================================================================\r\n')
        infofile.write(u'用户: ' + user_id + '\r\n')
        infofile.write(u'昵称: ' + num_name + '\r\n')
        infofile.write(u'微博数: ' + str(num_wb) + '\r\n')
        infofile.write(u'关注数: ' + str(num_gz) + '\r\n')
        infofile.write(u'粉丝数: ' + str(num_fs) + '\r\n')
        infofile.write(u'微博内容: ' + '\r\n\r\n')

        #获取微博内容
        #http://weibo.cn/+ user_id +?filter=0&page=1
        # 其中 filter=0 表示全部 filter=1 表示原创

        print('\n')
        print(u'获取微博的内容信息')
        num=1
        while num<=5:
            url_wb='http://weibo.cn/'+user_id+"?filter=0&page="+str(num)
            driver.get(url_wb)
            info_temp="//div[@class='c'][{0}]"
            # // *[ @ id = "M_H1pCdbLMo"]
            num_temp=1
            while True:
                print(num_temp)
                info_temp = "//div[@class='c'][%d]"%num_temp
                print(info_temp)
                print(info_temp.format(num_temp))
                info = driver.find_element_by_xpath(info_temp).text
                # info = driver.find_element_by_xpath(info_temp.format(num_temp)).text
                print(info)
                try:
                    # 设置:皮肤.图片
                    if u'广场.游戏.找人.更多' not in info:
                        if info.find(u'转发') != -1: #startswith
                            print(u'转发微博')
                            infofile.write(u'转发微博\r\n')
                        else:
                            print(u'原创微博')
                            infofile.write(u'原创微博\r\n')

                        # 获取最后一个点赞数 因为转发是后有个点赞数
                        str1 = info.split(u"赞")[-1]
                        if str1:
                            val1 = re.match(r'\[(.*?)\]', str1).groups()[0]
                            print(re.match(r'\[(.*?)\]', str1).groups())
                            print(u'点赞数: ' + val1)
                            infofile.write(u'点赞数: ' + str(val1) + '\r\n')

                        str2 = info.split(u"转发")[-1]
                        if str2:
                            val2 = re.match(r'\[(.*?)\]', str2).groups()[0]
                            print(u'转发数: ' + val2)
                            infofile.write(u'转发数: ' + str(val2) + '\r\n')

                        str3 = info.split(u"评论")[-1]
                        if str3:
                            val3 = re.match(r'\[(.*?)\]', str3).groups()[0]
                            print(u'评论数: ' + val3)
                            infofile.write(u'评论数: ' + str(val3) + '\r\n')

                        str4 = info.split(u"收藏 ")[-1]
                        flag = str4.find(u"来自")
                        print(u'时间: ' + str4[:flag])
                        infofile.write(u'时间: ' + str4[:flag] + '\r\n')

                        print(u'微博内容:')
                        print(info[:info.rindex(u" 赞")])  # 后去最后一个赞位置
                        infofile.write(info[:info.rindex(u" 赞")] + '\r\n')
                        infofile.write('\r\n')
                        print('\n')
                    else:
                        print(u'跳过', '\n')
                        # break
                    num_temp+=1
                except Exception as e:
                    print("解析出错",e)
                    break
            num+=1

    except Exception as e:
        print("Error: ", e)
    finally:
        print(u'VisitPersonPage!\n')
        print('**********************************************\n')

# 爬去用户的关注
def getFollow(user_id):
    try:
        global  followfile
        print(u'准备爬取用户的粉丝...')
        driver.get("http://weibo.cn/"+user_id+"/follow")
        ##第一步直接获取用户昵称 微博数 关注数 粉丝数
        #str_name.text 是unicode 编码类型

        #用户id
        print(u'个人详细信息')
        print('*****************')
        print(u'用户id:'+user_id)

        # 昵称
        str_name = driver.find_element_by_xpath("//div[@class='ut']")  # /html/body/div[4]/div[1]
        str_t = str_name.text.split(" ")
        num_name = str_t[0]
        print(u'昵称:' + num_name)

        # 微博数 除了个人主页外 它默认直接显示微博数 无超链接
        str_wb = driver.find_element_by_xpath("//div[@class='tip2']")
        pattern = r"\d+\.?\d*"  # 正则提取"微博[0]" 但r"(\[.*?\])"总含[]
        guid = re.findall(pattern, str_wb.text, re.S | re.M)
        print(str_wb.text)
        for value in guid:
            num_wb = int(value)
            break
        print('微博数:' + str(num_wb))

        # 关注数目
        str_gz = driver.find_element_by_xpath("//div[@class='tip2']/a[1]")
        num_gz_temp = re.findall(pattern, str_gz.text, re.S | re.M)
        num_gz = int(num_gz_temp[0])
        print('关注数目:' + str(num_gz))

        # 粉丝数目
        str_fs = driver.find_element_by_xpath("//div[@class='tip2']/a[2]")
        num_fs_temp = re.findall(pattern, str_fs.text, re.S | re.M)
        num_fs = int(num_fs_temp[0])
        print('粉丝数目:' + str(num_fs))
        # ***************************************************************************
        # No.2 文件操作写入信息
        # ***************************************************************************

        followfile.write('=====================================================================\r\n')
        followfile.write(u'用户: ' + user_id + '\r\n')
        followfile.write(u'昵称: ' + num_name + '\r\n')
        followfile.write(u'微博数: ' + str(num_wb) + '\r\n')
        followfile.write(u'关注数: ' + str(num_gz) + '\r\n')
        followfile.write(u'粉丝数: ' + str(num_fs) + '\r\n')
        followfile.write(u'关注的人: ' + '\r\n\r\n')


        pageNum = 1
        while pageNum < 20:
            # https://weibo.cn/userId/follow?page=20
            url_wb = 'http://weibo.cn/' + user_id + "/follow?page=" + str(pageNum)
            driver.get(url_wb)

            num_temp = 1
            while True:
                print(num_temp)
                # /html/body/table[1]
                info_temp = "//table[%d]" % num_temp
                print(info_temp)
                print(info_temp.format(num_temp))
                info = driver.find_element_by_xpath(info_temp).text
                # info = driver.find_element_by_xpath(info_temp.format(num_temp)).text
                print(info)


    except Exception as e:
        print("Error: ", e)
    finally:
        print(u'getFollow End!\n')
        print('**********************************************\n')

if __name__ == '__main__':

    #定义变量
    username = cf.USERNAME             #输入你的用户名
    password = cf.PASSWORD               #输入你的密码
    #操作函数
    LoginWeibo(username, password)      #登陆微博
    # user_id=inforead.readline()
    user_id = cf.USERID
    while user_id!="":
        user_id=user_id.rstrip('\r\n')
        VisitPersonPage(user_id)
        # user_id=inforead.readline()
    infofile.close()
    inforead.close()