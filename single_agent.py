# Please install required dependencies first:
# pip install openai python-dotenv
# 该agent使用deepseek v4 flash模型
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 环境变量文件
load_dotenv()

# 获取环境变量，带默认值兜底
api_key = os.environ.get('DEEPSEEK_API_KEY1')
base_url = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
model = os.environ.get('DEEPSEEK_MODEL2', 'deepseek-chat')

if not api_key:
    raise ValueError("❌ 环境变量 DEEPSEEK_API_KEY1 未设置，请检查 .env 文件！")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 判断是否为推理模型（deepseek-reasoner），如果是则启用 thinking 参数
is_reasoner = 'reasoner' in model.lower()

request_params = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    "stream": False,
}

# DeepSeek 推理模型专用参数
if is_reasoner:
    request_params["extra_body"] = {"thinking": {"type": "enabled"}}

response = client.chat.completions.create(**request_params)

print("🤖 模型回复：")
print(response.choices[0].message.content)

# 如果是推理模型，额外打印推理过程（如果有）
if is_reasoner and hasattr(response.choices[0].message, 'reasoning_content'):
    print("\n🧠 推理过程：")
    print(response.choices[0].message.reasoning_content)
