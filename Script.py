#!/usr/bin/python3.5

import socket
import urllib.request

hosts = []

hosts.append("google.com") #This host is for test purpose only
hosts.append("down.kuzyazp.tk")
hosts.append("tcp.kuzyazp.tk")
hosts.append("http.kuzyazp.tk")

instances = []

instances.append("i-0523b84d70c4d34f3") #the one that should be stopped
instances.append("i-076f30fc7fc4f34c2") #the one that responds over port 22 only
instances.append("i-0e8ae3c67250eb59a") #the one that responds over HTTP and TCP

for host in hosts:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        http_r = urllib.request.urlopen(("http://" + host), timeout=5).getcode()
        print("Succesess! Response code", http_r)
    except Exception:
        print ("HTTP connection Failed")
    try:
        s.connect((host, 22))
        print ("Port 22 reachable on host", host)
    except socket.error as e:
        print("Port 22 not reachable on host", host, "Error:", e)
        s.close()

