# DockerPwn.py

Exploit for exposed Docker TCP Socket.

This will automatically create a container on the Docker host with the root filesystem mounted,
allowing arbitrary read and write of the root filesystem (which is bad).

Once created, the script will empty the password requirement for 'root', and will alter any user
with a valid Unix password to have a password of 'DockerPwn'

Once this is done, the script will attempt to use Paramiko to login to all users enumerated from 
/etc/passwd using the password 'DockerPwn', and a shell will be spawned. 

# Roadmap:

Utilize the limited command execution via Paramiko to get a better shell, and automatically escalate to root.


# Usage:

DockerPwn.py [-h] [--target TARGET] [--port PORT]

optional arguments:
  -h, --help       show this help message and exit
  --target TARGET  IP of Docker Host
  --port PORT      Docker API TCP Port
