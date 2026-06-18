# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
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