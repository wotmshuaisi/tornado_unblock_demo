# tornado_unblock_demo
tornado的同步、异步、多线程使用
## 建表
```
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
```
## 配置
HOST, DB, USER, PASSWD = 'your_host', 'your_db', 'your_user', 'your_passwd'
## 压测
>* 同步: ab -n 200 -c 50 http://127.0.0.1:8060/sync/name
>* 异步: ab -n 200 -c 50 http://127.0.0.1:8060/async/name
>* 多线程: ab -n 200 -c 50 http://127.0.0.1:8060/supersync/name
