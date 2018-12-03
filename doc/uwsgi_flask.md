# 服务部署问题

1. 不管是 nginx 还是 apache 代理 uWSGI 应用时，在是用 gevent 的情况下不能使用 process 参数

参考资料: [uswgi issue](https://github.com/unbit/uwsgi/issues/596)