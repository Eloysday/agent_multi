# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

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
    



client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY1'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL')
)

response = client.chat.completions.create(
    model=os.environ.get('DEEPSEEK_MODEL2'),
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}}
)

print(response.choices[0].message.content)