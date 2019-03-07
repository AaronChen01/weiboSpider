# weiboSpider
登陆微博后，以某个用户为种子，爬取关注的人以及粉丝，及其发布的微博和基本信息

在config.py文件中填写基本信息：  
USERNAME = "xxx" --> 登陆微博的账号  
PASSWORD = "xxx" --> 登陆微博的密码  
USERID = "xxx" --> 要作为爬取种子的userid号

文件使用selenium框架模拟浏览器操作进行登陆爬取  
未使用动态ip代理池，大量爬取可能会被封ip。。