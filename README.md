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

---

### 2. `mcp.json`（配置文件）

在根目录下创建 `mcp.json`，确保平台能够双重识别启动命令：

```json
{
  "mcpServers": {
    "mock-data-server": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
