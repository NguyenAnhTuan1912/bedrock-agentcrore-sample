# Bedrock AgentCore Code Sample

Đây là repo code mẫu đơn giản cho AgentCore.

## Requirements

Cần một số package sau để chạy:

1. Python >= 3.12
2. Các packages trong requirements.txt

## Installation

1. Đầu tiên thì cài môi trường ảo cho Python.

```bash
python3 -m venv venv
```

2. Sau đó là trỏ về môi trường ảo này.

```bash
source venv/bin/activate
```

3. Cài đặt các packages python cần thiết (Cài toàn bộ)

```bash
pip install -r requirements.txt
```

Nếu như bạn sử dụng Strands Agents thì chỉ cần cài

```bash
pip install ".[strands_agents]"
```

## Run

1. Đầu tiên là chạy MCP Server trước.

```bash
python ./mcp/calculator/main.py
```

2. Chạy Agent Server.

```bash
python ./src/strands_agent_server.py
```
