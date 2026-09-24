# Hermes-Agent

[Hermes-Agent](https://hermes-agent.nousresearch.com/) is the self-improving AI agent built by Nous Research.

## Additional Ports

Use **Additional Ports** to publish or expose listeners that have no dedicated port field, such as the A2A (Agent2Agent) server (port 9900 by default).
`Container Port` must be the port the listener binds to inside the container; a published extra port usually also needs matching environment variables (for A2A: `A2A_PORT`, `A2A_HOST=0.0.0.0`, `A2A_PEER_TOKENS`) set under **Additional Environment Variables**.
