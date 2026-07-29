import json
import sys
from pathlib import Path

# 获取同级目录下的 mock.json
BASE_DIR = Path(__file__).parent
MOCK_FILE = BASE_DIR / "mock.json"

def read_mock_data():
    if not MOCK_FILE.exists():
        return []
    with open(MOCK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def handle_request(request):
    req_id = request.get("id")
    method = request.get("method")
    
    # 1. 响应初始化
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mock-data-server", "version": "1.0.0"}
            }
        }
    
    # 2. 注册工具列表
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "query_mock_data",
                        "description": "查询 mock.json 文件中的数据，支持通过关键词过滤。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "keyword": {
                                    "type": "string",
                                    "description": "搜索关键词（可选，例如：前端、张三）"
                                }
                            }
                        }
                    }
                ]
            }
        }
    
    # 3. 处理工具调用
    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "query_mock_data":
            keyword = args.get("keyword", "")
            data = read_mock_data()
            
            if keyword:
                keyword_lower = str(keyword).lower()
                filtered = [
                    item for item in data
                    if keyword_lower in json.dumps(item, ensure_ascii=False).lower()
                ]
                result_data = filtered
            else:
                result_data = data
                
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result_data, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            }

    return None

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = handle_request(request)
            if response:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception:
            break

if __name__ == "__main__":
    main()
