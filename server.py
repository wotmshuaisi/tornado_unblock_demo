#encoding: utf-8
__author__ = 'Jon'

import tornado.web
import tornado.ioloop
import tornado.escape
import torndb

from tornado import gen
from tornado.options import options, define
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado_mysql import pools


define('port')
tornado.options.parse_command_line()

##################################################################
# Setting
##################################################################
HOST, DB, USER, PASSWD = 'your_host', 'your_db', 'your_user', 'your_passwd'
APOOL_COUNT = POOL_COUNT = 10

DB_ARGS = [HOST, DB]
DB_KWARGS = dict(user=USER, password=PASSWD, time_zone='+8:00')

SQL='select * from user where name=%s'


##################################################################
# Service
##################################################################
class BaseService(object):
    executor = ThreadPoolExecutor(max_workers=POOL_COUNT)

    def __init__(self, db=None):
        self.db = db


class SyncService(BaseService):
    def find(self, name):
        result = self.db.query(SQL, name)

        return result


class AsyncService(BaseService):
    @gen.coroutine
    def find(self, name):
        result = yield self.db.execute(SQL, name)

        raise gen.Return(result.fetchall())


class SuperSyncService(BaseService):
    @run_on_executor
    def find(self, name):
        self.db = torndb.Connection(*DB_ARGS, **DB_KWARGS) # 线程池的每个线程对应一个数据库连接
        result = self.db.query(SQL, name)

        return result


##################################################################
# Handler
##################################################################
class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

        self.sync_service = SyncService(self.application.sdb)
        self.async_service = AsyncService(self.application.adb)
        self.super_sync_service = SuperSyncService()

    def write_json(self, data):
        self.write(tornado.escape.json_encode(data))


class SyncHandler(BaseHandler):
    def prepare(self):
        print 'into sync'

    def get(self, name):
        result = self.sync_service.find(name)

        self.write_json({'data': result})


class AsyncHandler(BaseHandler):
    def prepare(self):
        print 'into async'

    @gen.coroutine
    def get(self, name):
        result = yield self.async_service.find(name)

        self.write_json({'data': result})


class SuperSyncHandler(BaseHandler):
    def prepare(self):
        print 'into super sync'

    @gen.coroutine
    def get(self, name):
        result = yield self.super_sync_service.find(name)

        self.write_json({'data': result})


class FastHandler(BaseHandler):
    def prepare(self):
        print 'into fast'

    def get(self):
        self.write('fast')

##################################################################
# Application
##################################################################
class Application(tornado.web.Application):
    def __init__(self, handlers, **settings):
        self.sdb = torndb.Connection(*DB_ARGS, **DB_KWARGS)
        self.adb = pools.Pool(
            dict(host=HOST, db=DB, user=USER, passwd=PASSWD),
            max_idle_connections=APOOL_COUNT
        )

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    app = Application([
        (r'/sync/([\w\W]+)', SyncHandler),           # 同步
        (r'/async/([\w\W]+)', AsyncHandler),         # 异步
        (r'/supersync/([\w\W]+)', SuperSyncHandler), # 多线程
        (r'/fast', FastHandler)
    ], debug=True)
    port = options.port or 8060
    app.listen(port)
    print "listen %s..." % port
    tornado.ioloop.IOLoop.instance().start()
