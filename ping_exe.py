import os
from multiprocessing.pool import ThreadPool
from tkinter import *
import threading
from tkinter import messagebox
import socket
import ping3

import paramiko

one_ip = []
two_ip = []

def one():
    if strvar_1.get() == "正在采集":
        messagebox.showinfo(title='提示', message="请等待采集完成")
        return
    global one_ip
    strvar_1.set("正在采集")
    btn_2["state"] = DISABLED
    d_2["state"] = DISABLED
    btn_["state"] = DISABLED
    one_ip = ping()
    strvar_1.set("采集完成")
    print("第一次采集:" + str(one_ip))
    btn_2["state"] = NORMAL
    d_2["state"] = NORMAL
    btn_["state"] = NORMAL


def two():
    if strvar_2.get() == "正在采集":
        messagebox.showinfo(title='提示', message="请等待采集完成")
        return
    global two_ip
    strvar_2.set("正在采集")
    btn_1["state"] = DISABLED
    d_2["state"] = DISABLED
    btn_["state"] = DISABLED
    two_ip = ping()
    strvar_2.set("采集完成")
    print("第二次采集:" + str(two_ip))
    btn_3["state"] = NORMAL
    btn_1["state"] = NORMAL
    d_2["state"] = NORMAL
    btn_["state"] = NORMAL


def duibi():
    if strvar_1.get() != "采集完成":
        messagebox.showinfo(title='提示', message="请进行第一次采集")
    elif strvar_2.get() != "采集完成":
        messagebox.showinfo(title='提示', message="请进行第二次采集")
    elif strvar_1.get() == "采集完成" and strvar_2.get() == "采集完成":
        ip_list = []
        for i in two_ip:
            if i not in one_ip:
                ip_list.append(i)
        if len(ip_list) == 0:
            print("对比结果：未找到第二次采集前接入的设备，请检查设备网络")
            messagebox.showinfo(title='提示', message="未找到第二次采集前接入的设备，请检查设备网络")
        else:
            print("正在获取hostname，请稍等")
            _password["state"] = DISABLED
            _username["state"] = DISABLED
            btn_3["state"] = DISABLED
            pool = ThreadPool(50)
            result = pool.map(cat_hostname, ip_list)
            pool.close()
            pool.join()
            print("对比结果如下：")
            print("----------------------------------")
            print("    ip            hostname")
            for i in result:
                print(i[0], "  ", i[1])
            print("----------------------------------")
            messagebox.showinfo(title='提示', message="结果请看输出区")
            btn_3["state"] = NORMAL
            _password["state"] = NORMAL
            _username["state"] = NORMAL


def cat_hostname(ip):
    # 实例化SSHClient
    client = paramiko.SSHClient()
    # 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接SSH服务端，以用户名和密码进行认证
    try:
        client.connect(hostname=ip, port=22, username=username.get(), password=password.get(), banner_timeout=30)
        # 打开一个Channel并执行命令
        stdin, stdout, stderr = client.exec_command('cat /etc/hostname')
        hostname = stdout.read()
        client.close()
        return [ip, hostname.decode().strip()]
    except:
        return [ip, "获取hostname失败"]


def run(func):
    t = threading.Thread(target=func)
    # t.setDaemon(True)
    t.start()


def ping():
    data_ip = []  # 256个ip
    normal_ip = []  # 能ping通的ip
    network = c_2.get()  # 网段输入框
    split_ip = localhost[0][0:localhost[0].rfind(".") - 1]  # 拼接后的ip，如10.55.

    for i in range(256):
        data_ip.append(split_ip + "%s.%d" % (network, i))

    def ping_ip(ip):
        result = ping3.ping(ip, timeout=1)
        if result:
            normal_ip.append(ip)

    pool = ThreadPool(256)
    pool.map(ping_ip, data_ip)
    pool.close()
    pool.join()

    return normal_ip


def netword():
    netword_list = socket.gethostbyname_ex(socket.gethostname())[2]  # 本机ip
    if len(netword_list) == 0 or (len(netword_list) == 1 and netword_list[0] == "127.0.0.1"):
        messagebox.showinfo(title='提示', message="没有可用的网卡")
        return
    window = Toplevel(root, width=20)
    window.title("选择网卡")
    # window.geometry('{}x{}+{}+{}'.format(320, (len(netword_list)+1) * 40, 10, 10))
    setCenter(window, 320, (len(netword_list) + 1) * 40)
    for index, value in enumerate(netword_list):
        Button(window, text=value, command=lambda window=window, ip=value: localhost_ip(window, ip)).grid(row=index,
                                                                                                          column=0,
                                                                                                          padx=10,
                                                                                                          pady=5)
    Label(window, text="手动输入ip:").grid(row=index + 1, column=0)
    ip = StringVar()
    d_2 = Entry(window, textvariable=ip).grid(row=index + 1, column=1)
    Button(window, text="确定", command=lambda window=window: localhost_ip(window, ip.get())).grid(row=index + 1,
                                                                                                 column=2, padx=10,
                                                                                                 pady=5)


def setCenter(window, w=0, h=0):
    ws = window.winfo_screenwidth()  # 获取屏幕宽度（单位：像素）
    hs = window.winfo_screenheight()  # 获取屏幕高度（单位：像素）
    # 获取顶层窗口宽度异常
    # if (w==0  or  h==0):
    #     w = window.winfo_width()   #获取窗口宽度（单位：像素）
    #     h = window.winfo_height()  #获取窗口高度（单位：像素）
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    window.geometry('{}x{}+{}+{}'.format(w, h, x, y))


def localhost_ip(window, ip):
    localhost[0] = ip
    print("选择网卡ip为：" + ip)
    a = localhost[0].split(".")
    c_2.set(a[2])
    btn_1["state"] = NORMAL
    btn_4["state"] = NORMAL
    window.destroy()


def cat_all():
    print("正在获取hostname，请稍等")
    _password["state"] = DISABLED
    _username["state"] = DISABLED
    btn_3["state"] = DISABLED
    btn_4["state"] = DISABLED
    d_2["state"] = DISABLED
    btn_["state"] = DISABLED
    ip = ping()
    pool = ThreadPool(50)
    result = pool.map(cat_hostname, ip)
    pool.close()
    pool.join()
    if len(result) > 0:
        print("----------------------------------")
        print("    ip            hostname")
        for i in result:
            print(i[0], "  ", i[1])
        print("----------------------------------")
        messagebox.showinfo(title='提示', message="结果请看输出区")
        btn_3["state"] = NORMAL
        d_2["state"] = NORMAL
        btn_4["state"] = NORMAL
        _password["state"] = NORMAL
        _username["state"] = NORMAL
        btn_["state"] = NORMAL


if __name__ == "__main__":
    root = Tk()
    root.title("寻找ip")
    setCenter(root, 600, 200)
    Label(root, text="账号:").grid(row=0, column=0)
    username = StringVar(value="root")
    _username = Entry(root, textvariable=username, width=10, state=NORMAL)
    _username.grid(row=0, column=1)
    Label(root, text="密码:").grid(row=0, column=2)
    password = StringVar(value="root")
    _password = Entry(root, textvariable=password, width=10, state=NORMAL)
    _password.grid(row=0, column=3)
    b1 = Label(root, text="网段:").grid(row=1, column=0)
    c_2 = StringVar(value="1")
    d_2 = Entry(root, textvariable=c_2, width=5)
    d_2.grid(row=1, column=1)
    localhost = [""]
    strvar_1 = StringVar(value="第一次采集")
    strvar_2 = StringVar(value="第二次采集")
    strvar_3 = StringVar(value="对比ip")

    btn_ = Button(root, text="选择网卡", state=NORMAL, command=lambda: netword())
    btn_.grid(row=1, column=2, padx=10, pady=20)
    btn_1 = Button(root, textvariable=strvar_1, state=DISABLED, command=lambda: run(one))
    btn_1.grid(row=1, column=3, padx=10, pady=20)
    btn_2 = Button(root, textvariable=strvar_2, state=DISABLED, command=lambda: run(two))
    btn_2.grid(row=1, column=4, padx=10, pady=20)
    btn_3 = Button(root, textvariable=strvar_3, state=DISABLED, command=lambda: run(duibi))
    btn_3.grid(row=1, column=5, padx=10, pady=20)
    btn_4 = Button(root, text="查看所有设备的hostname", state=DISABLED, command=lambda: run(cat_all))
    btn_4.grid(row=1, column=6, padx=10, pady=20)
    print("网段说明：网段是指192.168.1.100中的第三段，也就是1")
    print("网卡说明：选择网卡是为了寻找这个网卡同网段的设备，手动输入ip时需输入全部ip（最后一段可随意填写）")
    print(
        "使用说明：\n        第一次采集时为设备未接入网络\n        第二次采集时应设备接入网络\n        对比结果如果为：未找到第二次采集前接入的设备，则当前没找出差异的设备ip，请检查设备网络\n"
        "        账号密码是指SSH的登录账号密码\n        如获取hostname失败，则可能是设备无法连接或者账号密码错误")
    root.mainloop()
