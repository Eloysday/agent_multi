import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY1'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL')
)

# ---------------------- 1. 工具函数（读写分离） ----------------------
def read_file(file_path: str) -> str:
    try:
        if not os.path.isfile(file_path):
            return f"[读取失败] 文件不存在：{file_path}"
        with open(file_path, "r", encoding="utf-8") as f:
            return f"[读取成功]\n{f.read()}"
    except Exception as e:
        return f"[读取异常] {str(e)}"

def write_file(file_path: str, content: str) -> str:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[写入成功] 内容已保存至：{file_path}"
    except Exception as e:
        return f"[写入异常] {str(e)}"

# ---------------------- 2. 工具注册（只做一次） ----------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文本文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "文件路径"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入/覆写本地文本文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "写入内容"}
                },
                "required": ["file_path", "content"]
            }
        }
    }
]

# ---------------------- 3. 简洁 system prompt ----------------------
system_prompt = """
你可以使用 read_file（读取文件）和 write_file（写入文件）两个工具。
需要读写文件时，直接调用对应工具即可，不要编造内容。
工具执行结果会自动返回给你，基于结果给出回答。
"""

# ---------------------- 4. 多轮对话循环（Trae 核心） ----------------------
def run_chat():
    messages = [{"role": "system", "content": system_prompt}]
    print("💬 已启动（Trae 式：工具自动调用），输入 exit 退出")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("exit", "quit", "退出"):
            print("👋 结束会话")
            break
        if not user_input:
            print("请输入有效内容")
            continue

        # 用户消息入上下文
        messages.append({"role": "user", "content": user_input})

        # ---------- 工具调用闭环（自动循环） ----------
        while True:
            resp = client.chat.completions.create(
                model=os.environ.get('DEEPSEEK_MODEL2'),
                messages=messages,
                tools=tools,
                tool_choice="auto",
                stream=False,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}}
            )
            msg = resp.choices[0].message

            # 无工具调用 → 输出回答，跳出工具循环，回到等用户输入
            if not msg.tool_calls:
                print(f"\nAssistant: {msg.content}")
                messages.append(msg)
                break

            # 有工具调用 → 执行并回传
            print(f"\n🔧 调用工具：{msg.tool_calls[0].function.name}")
            messages.append(msg)
            print(msg.tool_calls)
            for tool_call in msg.tool_calls:
                fname = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                cid = tool_call.id
                
                print(f"🔧 调用工具：{fname}，参数：{args}，ID：{cid}")
                if fname == "read_file":
                    res = read_file(args["file_path"])
                elif fname == "write_file":
                    res = write_file(args["file_path"], args["content"])
                else:
                    res = f"未知工具：{fname}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": cid,
                    "name": fname,
                    "content": res
                })
            # 继续内层循环，让模型基于工具结果再生成

if __name__ == "__main__":
    run_chat()