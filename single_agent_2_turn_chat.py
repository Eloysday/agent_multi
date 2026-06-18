import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY1'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL')
)

# 初始化上下文（全局/会话内保存）
chat_history = [
    {"role": "system", "content": "You are a helpful assistant"}
]

# 第一轮对话
chat_history.append({"role": "user", "content": "Hello"})
response = client.chat.completions.create(
    model=os.environ.get('DEEPSEEK_MODEL2'),
    messages=chat_history,
    stream=False,
    reasoning_effort="high",
    #extra_body={"thinking": {"type": "enabled"}}
)
# 把模型回复加入历史
chat_history.append(response.choices[0].message.model_dump())
print(response.choices[0].message.content)

# 第二轮对话（自动带上全部历史）
chat_history.append({"role": "user", "content": "再介绍下你自己"})
response2 = client.chat.completions.create(
    model=os.environ.get('DEEPSEEK_MODEL2'),
    messages=chat_history,
    stream=False,
    reasoning_effort="high",
    #extra_body={"thinking": {"type": "enabled"}}
)
chat_history.append(response2.choices[0].message.model_dump())
print(response2.choices[0].message.content)