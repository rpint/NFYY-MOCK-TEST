import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mock-data-server")
BASE_DIR = Path(__file__).parent
MOCK_FILE = BASE_DIR / "mock.json"

def read_mock_data():
    if not MOCK_FILE.exists():
        return []
    with open(MOCK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def query_mock_data(keyword: str = "") -> str:
    """查询 mock.json 文件中的数据，支持通过关键词过滤。"""
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
    return json.dumps(result_data, ensure_ascii=False, indent=2)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
