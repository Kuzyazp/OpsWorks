#!/usr/bin/python3.5

import socket
import urllib.request
import boto3
from termcolor import colored
import datetime


hosts = []

hosts.append("down.kuzyazp.tk")
hosts.append("tcp.kuzyazp.tk")
hosts.append("http.kuzyazp.tk")

insts = []

insts.append("i-0523b84d70c4d34f3") #the one that should be stopped
insts.append("i-076f30fc7fc4f34c2") #the one that responds over port 22 only
insts.append("i-0e8ae3c67250eb59a") #the one that responds over HTTP and TCP


#HTTP/TCP checks
print("Checking instances using HTTP and TCP:\n")
for host in hosts:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        http_r = urllib.request.urlopen(("http://" + host), timeout=1).getcode()
        print("HTTP connect to ", host, ": \t{0}".format(colored("Connected!", 'green')))
    except Exception:
        print("HTTP connect to ", host, ": \t{0}".format(colored("Failed!", 'red')))
    try:
        s.connect((host, 22))
        print("TCP connect to ", host, ": \t{0}\n".format(colored("Connected!", 'green')))
    except socket.error as e:
        print("TCP connect to ", host, ": \t{0}\n".format(colored("Failed!", 'red')))
        s.close()

ec2 = boto3.resource('ec2')

#Creating AMI of stopped instance
print("\nCreating AMI of stopped instance:\n")

for i in ec2.instances.all():
    for inst in insts:
        if i.id == inst and i.state['Name'] == "stopped":
            to_be_terminated_id = i.id
            current_datetime = datetime.datetime.now()
            date_stamp = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            ami_name = "Kuzemko A._ID" + i.id + "_" + date_stamp
            ami_id = i.create_image(
            Name=ami_name,
            NoReboot=True,
            )
            print("\nAMI of stopped instance has been created. AMI name is:\t{0}".format(colored(ami_name, 'cyan')))


#Stopped instance termination
print("\nStopped instance termination")

ec2 = boto3.client('ec2')

reserv = ec2.describe_instances()

for i in reserv['Reservations']:
    for i1 in i['Instances']:
        if i1['InstanceId'] == to_be_terminated_id:
            try:
                ec2.terminate_instances(
                DryRun = False,
                InstanceIds = [to_be_terminated_id],
                )
                print("\nInstance with ID:", to_be_terminated_id, "has been terminated!\n")
            except:
                print("\nOOOps!!\n")

#AMIs cleanup

images_to_delete = []

timediff = datetime.datetime.now() - datetime.timedelta(days=7)
week = timediff.isoformat()

response = ec2.describe_images(Owners=["717986625066"])

for ami_details in response['Images']:
    image_created_time = ami_details['CreationDate']
    if image_created_time < week:
        images_to_delete.append(ami_details['ImageId'])
        image_id = ami_details['ImageId']
        try:
            response = ec2.deregister_image(
            ImageId=image_id,
            DryRun=True,
            )
        except:
            print(image_id, "Was created on", image_created_time,". It is older than 7 days. Deleting...")

#Checking Status of EC2 instances

print("\n Checking statuses of all instances")

ec2 = boto3.resource('ec2')

for i in ec2.instances.all():
    for inst in insts:
        if i.id == inst:
            print("Id: {0}\tState: {1}".format(
                colored(i.id, 'cyan'),
                colored(i.state['Name'], 'green'),
            ))