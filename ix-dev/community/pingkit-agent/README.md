# PingKit Agent

[PingKit Agent](https://pingkit.app/agent/docker/) watches your own network and alerts PingKit
on your iPhone when the internet goes down, a new device joins or a device goes offline.
Pair it with the code PingKit shows on your iPhone under Agents, Add an Agent, on the agent's
web page.

Ping is optional: without it the agent checks with TCP. To allow it, add System > Advanced
Settings > Sysctl: `net.ipv4.ping_group_range` with the value `0 2147483647`.
