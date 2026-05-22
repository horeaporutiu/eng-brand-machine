---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name:
description:
---

# My Agent

Describe what your agent does here.

connect to Miro's remote MCP Server with the following JSON.

Create me an architecture diagram on a miro board based on the code in this repo. 

```json
{
  "mcpServers": {
    "miro-mcp": {
      "url": "https://mcp.miro.com/", 
      "disabled": false,
      "autoApprove": []
    }
  }
}
```
