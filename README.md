# Mock Data MCP Server

这是一个用于查询指定 `mock.json` 数据的 MCP 服务。

## MCP 服务配置

```json
{
  "mcpServers": {
    "mock-data-server": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
