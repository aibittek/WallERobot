# -*- coding:utf-8 -*-

def consumer():
    r = ''
    while True:
        n = yield r
        print("[Consumer] n = %d" %n)
        if not n:
            return
        print("[Consumer] consuming %s..." %n)
        r = '200 OK'

def produce(c):
    c.send(None)
    h = 0
    while h < 5:
        h = h + 1
        print("[Producer] producing %d..." %h)
        s = c.send(h)
        print("[Producer] consumer return: %s" %s)
    c.close()

c = consumer() #创建一个生成器
produce(c) #在该函数中，调用生成器的send()方法