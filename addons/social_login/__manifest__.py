# -*- coding: utf-8 -*-
{
    'name': "Social Login",
    'summary': """微信公众号、企业微信等Oauth扫码及网页授权登录的实现""",
    'description': """""",
    'author': "Oejia",
    'website': "http://www.oejia.net/",
    'category': '',
    'version': '0.1',
    'depends': ['base', 'auth_oauth', 'oejia_wx'],
    'application': True,
    'data': [
        'views/wx_login.xml',
        'views/res_users_views.xml',
        #'views/signup.xml',
        'data/oauth_qywx.xml',
    ],
    'qweb': [],
    'demo': [],
}
