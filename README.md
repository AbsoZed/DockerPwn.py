# DockerPwn.py

Automation for abusing an exposed Docker TCP Socket.

This will automatically create a container on the Docker host with the host's root filesystem mounted,
allowing arbitrary read and write of the host filesystem (which is bad).

Once created, the script will employ the method of your choosing for obtaining a root shell. Currently,
shadow and useradd are working, with the less destructive method 'useradd' being default. 

### Methods:

- Useradd: Creates a 'DockerPwn' user, and adds them to /etc/sudoers with NOPASSWD. The handler automatically escalates to
         root using this privilege, and spawns a PTY.

- Shadow: Changes root and any valid user passwords to 'DockerPwn' in /etc/shadow, authenticates with Paramiko, 
        and sends a reverse shell. The handler automatically escalates to root utilzing 'su', and spawns a PTY.

         Shell I/O is logged for convenience and output to ./DockerPwn.log

## Roadmap:

- Implement chroot method. 
- Get packaged for pip3 installation.

## Usage:
```
DockerPwn.py [-h] [--target TARGET] [--port PORT] [--image IMAGE] [--method METHOD] [--c2 C2]

optional arguments:
  -h, --help       show this help message and exit
  --target TARGET  IP of Docker Host
  --port PORT      Docker API TCP Port
  --image IMAGE    Docker image to use. Default is Alpine Linux.
  --method METHOD  Method to use. Valid methods are shadow, chroot, useradd. Default is useradd.
  --c2 C2          Local IP and port in [IP]:[PORT] format to receive the shell.
