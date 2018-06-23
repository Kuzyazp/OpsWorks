#!/usr/bin/python3.5

import socket
import urllib.request
import boto3
from termcolor import colored
import datetime


hosts = []

hosts.append("google.com") #This host is for test purpose only
hosts.append("down.kuzyazp.tk")
hosts.append("tcp.kuzyazp.tk")
hosts.append("http.kuzyazp.tk")

insts = []

insts.append("i-0523b84d70c4d34f3") #the one that should be stopped
insts.append("i-076f30fc7fc4f34c2") #the one that responds over port 22 only
insts.append("i-0e8ae3c67250eb59a") #the one that responds over HTTP and TCP


#HTTP/TCP checks
for host in hosts:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        http_r = urllib.request.urlopen(("http://" + host), timeout=1).getcode()
        print("Succesess! Response code", http_r)
    except Exception:
        print ("HTTP connection Failed")
    try:
        s.connect((host, 22))
        print("Port 22 reachable on host", host, "\n")
    except socket.error as e:
        print("Port 22 not reachable on host", host, "Error:", e, "\n")
        s.close()

ec2 = boto3.resource('ec2')

#Checking Status of EC2 instances (should be moved lower later)
for i in ec2.instances.all():
    for inst in insts:
        if i.id == inst:
            print("Id: {0}\tState: {1}".format(
                colored(i.id, 'cyan'),
                colored(i.state['Name'], 'green'),
            ))

#Creating AMI of stopped instance
for i in ec2.instances.all():
    for inst in insts:
        if i.id == inst and i.state['Name'] == "stopped":
            to_be_terminated_id = i.id
            current_datetime = datetime.datetime.now()
            date_stamp = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            ami_name = i.private_dns_name + "_" + date_stamp
            print(ami_name)
#            ami_id = i.create_image(
#            Name=ami_name,
#            NoReboot=True,
#            )



ec2 = boto3.client('ec2')

reserv = ec2.describe_instances()

for i in reserv['Reservations']:
    for i1 in i['Instances']:
        if i1['InstanceId'] == to_be_terminated_id:
            try:
                ec2.terminate_instances(
                DryRun = True, #Remove Dry_Run later
                InstanceIds = [to_be_terminated_id],
                )
                print("\nTermination Successfull!")
            except:
                print("\nTermination Successfull!\n")

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
