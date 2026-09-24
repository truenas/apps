# Hermes-Agent

[Hermes-Agent](https://hermes-agent.nousresearch.com/) is the self-improving AI agent built by Nous Research.

## A2A (Agent2Agent)

Set **A2A Port** to publish or expose the Hermes A2A server; it is disabled by default.
Hermes only accepts remote A2A peers when a token is configured, so also set `A2A_PEER_TOKENS` (or `A2A_BEARER_TOKEN`) under **Additional Environment Variables**; without a token the server stays bound to localhost inside the container.
