#encoding: utf-8
__author__ = 'Jon'

import tornado.web
import tornado.ioloop
import tornado.escape
import requests

from tornado import gen
from tornado.options import options, define
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from pprint import pprint
from tornadohttpclient import TornadoHTTPClient

define('port')
tornado.options.parse_command_line()

##################################################################
# Setting
##################################################################
POOL_COUNT = 10
URL = 'http://www.baidu.com'


##################################################################
# Service
##################################################################
class BaseService(object):
    executor = ThreadPoolExecutor(max_workers=POOL_COUNT)


class SyncService(BaseService):
    '''requests 登录51job
    '''
    def find(self):
        pprint('Into requests')
        s = requests.session()

        pprint('Start login')
        f = s.get('http://ehire.51job.com')
        soup = BeautifulSoup(f.text, "html.parser")
        hidAccessKey = soup.find('input', {'name': 'hidAccessKey'})['value']
        fksc = soup.find('input', {'name': 'fksc'})['value']
        hidEhireGuid = soup.find('input', {'name': 'hidEhireGuid'})['value']

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://ehire.51job.com',
            'Referer': 'http://ehire.51job.com/MainLogin.aspx',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        }
        data = {'ctmName': '大岂网络',
                'userName': 'dqwl805',
                'password': '64079603sj',
                'oldAccessKey': hidAccessKey,
                'langtype': 'Lang=&Flag=1',
                'sc': fksc,
                'ec': hidEhireGuid,
                'isRememberMe': 'True'
                }
        res = s.post('https://ehirelogin.51job.com/Member/UserLogin.aspx', data=data, headers=headers)
        pprint('End login')

        pprint('Start force')
        try:
            soup = BeautifulSoup(res.text, "html.parser")
            viewState = soup.find('input', {'name': '__VIEWSTATE'})['value']
            partURL = soup.find('form', {'id': 'form1'})['action']

            URL = 'http://ehire.51job.com/Member/' + partURL
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'http://ehire.51job.com',
                'Referer': URL,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
            }
            data = {'__EVENTTARGET': 'gvOnLineUser',
                    '__EVENTARGUMENT': 'KickOut$0',
                    '__VIEWSTATE': viewState
                    }
            res = s.post(URL, data=data, headers=headers)
        except: pass # 有时不需要下线
        pprint('End force')

        pprint('Start fetch remain')
        resp = s.get('http://ehire.51job.com/CommonPage/JobsPostNumbList.aspx')
        pprint('End   fetch remain')
        bs = BeautifulSoup(resp.text, "html.parser")
        print(bs.find('b', {'class': 'info_att'}).text)


class AsyncService(BaseService):
    '''使用tornadohttpclient 登录51job
       特点:
           * 携带cookie
           * requests风格
    '''
    @gen.coroutine
    def find(self):
        pprint('Into tornadohttpclient')
        s = TornadoHTTPClient(force_instance = True)

        pprint('Start login')
        f = yield s.get('http://ehire.51job.com')
        soup = BeautifulSoup(f.body, "html.parser")
        hidAccessKey = soup.find('input', {'name': 'hidAccessKey'})['value']
        fksc = soup.find('input', {'name': 'fksc'})['value']
        hidEhireGuid = soup.find('input', {'name': 'hidEhireGuid'})['value']

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://ehire.51job.com',
            'Referer': 'http://ehire.51job.com/MainLogin.aspx',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        }
        data = {'ctmName': '大岂网络',
                'userName': 'dqwl805',
                'password': '64079603sj',
                'oldAccessKey': hidAccessKey,
                'langtype': 'Lang=&Flag=1',
                'sc': fksc,
                'ec': hidEhireGuid,
                'isRememberMe': 'True'
                }
        res = yield s.post('https://ehirelogin.51job.com/Member/UserLogin.aspx', data=data, headers=headers)
        pprint('End login')

        pprint('Start force')
        try:
            soup = BeautifulSoup(res.body, "html.parser")
            viewState = soup.find('input', {'name': '__VIEWSTATE'})['value']
            partURL = soup.find('form', {'id': 'form1'})['action']
    
            URL = 'http://ehire.51job.com/Member/' + partURL
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'http://ehire.51job.com',
                'Referer': URL,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
            }
            data = {'__EVENTTARGET': 'gvOnLineUser',
                    '__EVENTARGUMENT': 'KickOut$0',
                    '__VIEWSTATE': viewState
                    }
            res = yield s.post(URL, data=data, headers=headers)
        except: pass # 有时不需要下线
        pprint('End force')

        pprint('Start fetch remain')
        resp = yield s.get('http://ehire.51job.com/CommonPage/JobsPostNumbList.aspx')
        pprint('End   fetch remain')

        bs = BeautifulSoup(resp.body, "html.parser")
        pprint(bs.find('b', {'class': 'info_att'}).text)

        pprint('###Cookie###')
        pprint(s.cookie)

        with open('cookie.txt', 'w') as f:
            f.write(s.cookie)

    @gen.coroutine
    def find_next(self):
        pprint('Start recover cookie')
        s = TornadoHTTPClient(force_instance = True)

        with open('cookie.txt') as f:
            cookie_str = f.read()

        s.set_global_headers({ 'Cookie': cookie_str })

        resp = yield s.get('http://ehire.51job.com/CommonPage/JobsPostNumbList.aspx')
        pprint('End   recover cookie')

        bs = BeautifulSoup(resp.body, "html.parser")
        pprint(bs.find('b', {'class': 'info_att'}).text)


class SuperSyncService(BaseService):
    @run_on_executor
    def find(self):
        r = requests.get(URL)

        return r.status_code


##################################################################
# Handler
##################################################################
class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

        self.sync_service = SyncService()
        self.async_service = AsyncService()
        self.super_sync_service = SuperSyncService()

    def write_json(self, data):
        self.write(tornado.escape.json_encode(data))


class SyncHandler(BaseHandler):
    def prepare(self):
        print('into sync')

    def get(self):
        result = self.sync_service.find()

        self.write_json({'data': result})


class AsyncHandler(BaseHandler):
    def prepare(self):
        print('into async')

    @gen.coroutine
    def get(self, n):
        if n:
            result = yield self.async_service.find_next()
        else:
            result = yield self.async_service.find()

        self.write_json({'data': result})


class SuperSyncHandler(BaseHandler):
    def prepare(self):
        print('into super sync')

    @gen.coroutine
    def get(self):
        result = yield self.super_sync_service.find()

        self.write_json({'data': result})


class FastHandler(BaseHandler):
    def prepare(self):
        print('into fast')

    def get(self):
        self.write('fast')


##################################################################
# Application
##################################################################
class Application(tornado.web.Application):
    def __init__(self, handlers, **settings):
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    app = Application([
        (r'/sync', SyncHandler),           # 同步IO
        (r'/async/?(\d*)', AsyncHandler),  # 异步IO
        (r'/supersync', SuperSyncHandler), # 多线程

        (r'/fast', FastHandler)
    ], debug=True)
    port = options.port or 8060
    app.listen(port)
    print('listen %s...' % port)
    tornado.ioloop.IOLoop.instance().start()