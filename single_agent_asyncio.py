import os
from openai import AsyncOpenAI  # 改用异步客户端
from dotenv import load_dotenv
import asyncio

load_dotenv()

# 初始化 异步客户端 AsyncOpenAI
client = AsyncOpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY1'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL')
)

async def chat(user_input: str):
    response = await client.chat.completions.create(
        model=os.environ.get('DEEPSEEK_MODEL2'),
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"计算{user_input+10}的结果并判断是否为质数，如果不是输出所有可能的因数："},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    print(response.choices[0].message.content)
    # 如需获取思考过程：response.choices[0].message.thinking

async def main():
    task_list = []
    for i in range(10):
        task_list.append(chat(i))
    # 并发执行所有任务
    await asyncio.gather(*task_list)

if __name__ == "__main__":
    asyncio.run(main())