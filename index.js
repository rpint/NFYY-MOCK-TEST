import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import path from "path";

const server = new Server(
  { name: "mock-json-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// 注册查询工具
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "query_mock_data",
        description: "查询 mock.json 文件中的数据",
        inputSchema: {
          type: "object",
          properties: {
            key: { type: "string", description: "需要查找的字段名或关键字（可选）" }
          }
        }
      }
    ]
  };
});

// 处理查询逻辑
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "query_mock_data") {
    try {
      const filePath = path.resolve(process.cwd(), "mock.json");
      const rawData = fs.readFileSync(filePath, "utf-8");
      const data = JSON.parse(rawData);

      const key = request.params.arguments?.key;
      let result = data;

      // 如果传了 key，可做简单的筛选处理
      if (key) {
        result = data.filter(item => 
          JSON.stringify(item).toLowerCase().includes(key.toLowerCase())
        );
      }

      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
      };
    } catch (err) {
      return {
        isError: true,
        content: [{ type: "text", text: `读取 mock.json 失败: ${err.message}` }]
      };
    }
  }
  throw new Error("未找到对应工具");
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main();
