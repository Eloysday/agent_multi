import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY1'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL')
)

# 会话上下文
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
]
# 对话保存路径
SAVE_PATH = "chat_history.json"
# 退出指令
EXIT_CMD = ["exit", "quit", "退出"]

# 保存对话到本地文件
def save_chat_history():
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 对话已保存至 {SAVE_PATH}")
    except Exception as e:
        print(f"❌ 保存失败：{e}")

# 单轮对话逻辑
def chat(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model=os.environ.get('DEEPSEEK_MODEL2'),
        messages=messages,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    ans = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ans})
    return ans

if __name__ == "__main__":
    print("💬 开始对话，输入 exit/quit/退出 结束会话")
    while True:
        user_text = input("User: ").strip()
        # 1. 检测退出指令，跳出循环
        if user_text.lower() in EXIT_CMD:
            print("👋 会话结束...")
            save_chat_history()
            break
        
        # 空输入过滤
        if not user_text:
            print("请输入有效内容！")
            continue

        # 执行对话
        reply = chat(user_text)
        print(f"Assistant: {reply}")
        print("=" * 50)