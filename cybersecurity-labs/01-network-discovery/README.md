# Lab 01: Network Discovery in a Private Lab

## Objective

Identify active systems on a network you own, create a device inventory, and
explain why an accurate inventory supports defense.

## Safety boundary

Scan only the isolated subnet assigned to your own virtual machines. Do not
scan a school, workplace, hotel, public Wi-Fi, VPN, or internet address range.
This lab uses host discovery only; it does not exploit or log in to anything.

## Setup

1. Create two local VMs on a host-only/internal network.
2. Record their assigned private addresses from the VM consoles.
3. Install Nmap on the analyst machine.
4. Complete the authorization section of a copied lab report.

Example lab scope:

```text
Network: 192.168.56.0/24
Targets: LAB-LINUX-01 and LAB-WIN-01
Allowed activity: ICMP/ARP host discovery
```

Replace this example with your actual private, authorized lab subnet.

## Procedure

Confirm your own IP and subnet first:

```bash
ipconfig getifaddr en0           # macOS; interface may differ
ip address                       # Linux
ipconfig                         # Windows
```

Run host discovery against only the documented lab subnet:

```bash
nmap -sn 192.168.56.0/24
```

Record active addresses, hostnames, and roles. Do not publish real MAC
addresses; they can identify a device vendor or interface.

## Expected observations

Compare your format with `../samples/network-discovery.txt`. A host may not
reply because of a firewall or sleep state, so absence from the scan does not
prove that no device exists.

## Deliverable

Create a sanitized table:

| Asset ID | Role | Address | Observed status | Owner |
| --- | --- | --- | --- | --- |
| LAB-LINUX-01 | Log server | 192.168.56.10 | Up | Lab owner |

Explain one limitation of discovery and one way an inventory helps incident
response.

## Cleanup

Stop the VMs and disconnect the host-only network if it is no longer needed.

