
# 测试环境部署方式，按步骤执行

1. 下载 centos7 镜像 [镜像地址](http://mirrors.aliyun.com/centos/7/isos/x86_64/) DVD版本

2. 虚拟机安装centos7, 安装完成后reboot首先尝试

    ```shell
        ping www.baidu.com
    ```

不能ping通的话，参照[方法](https://www.cnblogs.com/cindy-cindy/p/6784536.html)解决

能ping通之后，参照[ssh远程连接](https://www.cnblogs.com/maowenqiang/articles/7729246.html)完成远程连接

tips:

虚拟机网络采用NAT模式，远程连接工具：[mobaXterm](https://mobaxterm.mobatek.net/)

装完的centos查看ip的命令为 ip add, 主机 ping 虚拟机时会用到

ssh 连接方式:

    ```shell
        ssh root@<虚拟机ip>
    ```

3. [更换下载源站](https://www.cnblogs.com/mfyang/articles/6715811.html)

tips:我们下载的阿里的镜像源站本来就是阿里，不需要替换

4. 更换完源站后首先执行

    ```shell
        yum update
    ```

5. [安装 python3.5.2](https://blog.csdn.net/u010472499/article/details/53412411)

tips:

注意看一下版本，链接里面的版本是3.5.1, 要改成3.5.2

软连接命令 In -s 的时候文件路径有问题前一个路径/usr/local/python3应该为/usr/local/python3.5/bin/xxxx，两行命令都改

不会使用vi的建议使用gedit命令

vi /usr/libexec/urlgrabber-ext-down 这个文件第一行也要改成python2.7

6. [yum 安装 mongo](https://docs.mongodb.com/master/tutorial/install-mongodb-on-red-hat/) 只看第一种 yum install 的方式

7. [yum install influxDB](https://blog.csdn.net/sudaobo/article/details/52116668)

8. [更换 pip install 源站](https://blog.csdn.net/u013378306/article/details/69382500) 推荐用 pip.conf的方式

9. 还原python环境

    第一步: 在mobaXterm中切换到 /root 目录，把 requirements.txt 文件拖进该目录

    第二步:

    ```shell
        cd $HOME
        pip install -r requirements.txt
    ```

10. 关闭系统防火墙

```shell
service firewalld stop
setenforce 0
vim /etc/selinux/config
```

将SELINUX=enforcing改为SELINUX=disabled

11. 配置 nginx + uwsgi web后端测试环境

**tips:** 做以下操作之前，先用 python -V 命令，确保 python 版本为 3.5

```shell
yum install epel-release
yum install python-devel nginx gcc
curl http://uwsgi.it/install | bash -s default /tmp/uwsgi
ln -s /tmp/uwsgi /usr/bin/uwsgi
```

12. 测试 nginx + uwsgi + flask 可用

```shell
cd /home/<your_user_path>
mkdir test
cd test
vim test.py
```

粘贴测试用 flask app:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
```

```shell
vim wsgi.py
```

粘贴以下代码:

```python
from myproject import app

if __name__ == "__main__":
    app.run()
```

编辑 wsgi 配置文件:

```shell
vim test.ini
```

复制以下代码并修改 < your_user_path >:

```ini
[uwsgi]
# uwsgi 启动时所使用的地址与端口
socket = 127.0.0.1:8000
# 指向网站目录
chdir = /home/<your_user_path>/test
# python 启动程序文件
wsgi-file = wsgi.py
# python 程序内用以启动的 application 变量名
callable = app
# 处理器数
processes = 5
# 线程数
threads = 2
#状态检测地址
stats = 127.0.0.1:9191
```

编写 wsgi app 后台启动 service 文件

```shell
vim /etc/systemd/system/test.service
```

复制以下代码并修改 < your_user_path >:

```service
[Unit]
Description=uWSGI instance to serve myproject

[Service]
WorkingDirectory=/home/<your_user_path>/test
ExecStart=/usr/bin/uwsgi --ini test.ini

[Install]
WantedBy=multi-user.target
```

然后执行:

```shell
service test start
```

更改 nginx 配置

```shell
vim /etc/nginx/nginx.conf
```

在 http 属性下添加并修改 < your_user_path > 和 <虚拟机ip>:

```conf
    server {
        listen 8888;
        server_name <虚拟机ip>;

        location / {
            include uwsgi_params;
            uwsgi_pass 127.0.0.1:8000;
            uwsgi_param UWSGI_CHDIR  /home/<your_user_path>/test;
            uwsgi_param UWSGI_SCRIPT wsgi:app;
        }
    }
```

然后执行：

```shell
service nginx restart
```

最后用本机浏览器访问 <虚拟机ip地址:8888>, 最后显示 hello there 则 部署成功

mongo 基本使用资料:

[菜鸟教程](http://www.runoob.com/mongodb/mongodb-tutorial.html)

[mongo文档](https://docs.mongodb.com/manual/)

[mongo python client 菜鸟基础教程](http://www.runoob.com/python3/python-mongodb.html)

[PyMongo官方文档](http://api.mongodb.com/python/current/)

[influxDB介绍及使用样例](https://www.jianshu.com/p/a1344ca86e9b)

[influxDB Python client](https://influxdb-python.readthedocs.io/en/latest/include-readme.html)

[influxDB Python Flask extension](https://github.com/btashton/flask-influxdb)

[Mongo Python Flask extension](https://flask-pymongo.readthedocs.io/en/latest/)

[Nginx + uWSGI + Flask 参考](https://juejin.im/entry/58eb912c8d6d810061908b90)
