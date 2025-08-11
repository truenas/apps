# Elastic Agent

Elastic Agent is a single, unified agent that you can deploy to hosts or containers to collect data and send it to the Elastic Stack. It provides a simple way to add monitoring for logs, metrics, and other types of data to each host, and scales from a handful of hosts to thousands.

## Features

- **Unified Agent**: Single agent for logs, metrics, and security data collection
- **Fleet Management**: Centrally manage and configure agents through Fleet Server
- **Multiple Flavors**: Basic, Server, and Complete editions available
- **Security Options**: Run privileged or with limited capabilities
- **Hardened Images**: Optional Wolfi-based hardened images for enhanced security

## Configuration

### Agent Flavor

Choose from three agent flavors:

- **Basic**: Lightweight agent for basic data collection
- **Server**: Standard agent with full capabilities (recommended)
- **Complete**: Full agent with Synthetics Browser monitoring support

### Security Settings

- **Privileged Mode**: Most use cases require privileged access for system monitoring
- **Hardened Images**: Use Wolfi-based images for reduced CVE exposure
- **Custom Capabilities**: When not running privileged, specify required Linux capabilities

### Fleet Configuration

For Fleet-managed agents:

1. **Fleet Server URL**: The URL of your Fleet Server (e.g., https://fleet-server:8220)
2. **Enrollment Token**: Obtain from Kibana → Management → Fleet → Enrollment tokens
3. **Service Token**: Required if running Fleet Server on this agent

### Storage

- **State Storage**: Persistent storage for agent state and configuration
- **Additional Storage**: Mount additional volumes as needed for data collection

## Getting Started

1. Configure the Fleet Server URL and enrollment token
2. Choose the appropriate agent flavor for your use case
3. Set security options based on your requirements
4. Configure storage for agent state persistence
5. Deploy the agent

## Documentation

For more information, visit:

- [Elastic Agent Container Documentation](https://www.elastic.co/docs/reference/fleet/elastic-agent-container)
- [Fleet and Elastic Agent Guide](https://www.elastic.co/docs/reference/fleet)
- [Elastic Agent Installation](https://www.elastic.co/docs/reference/fleet/install-elastic-agents)
