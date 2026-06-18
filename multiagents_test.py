import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ========== 1. 原生 DeepSeek 客户端（零 LangChain 依赖） ==========
llm_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY1"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
)
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")

# ========== 2. 自定义状态（完全透明，不用黑盒 MessagesState） ==========
class AgentState(TypedDict):
    messages: List[Dict]  # 统一用 OpenAI 原生格式：{"role": "...", "content": "..."}

# ========== 3. LLM 意图分类（替代关键词匹配） ==========
def classify_intent(state: AgentState) -> str:
    """用大模型做结构化意图判断，准确率远高于关键词"""
    user_query = state["messages"][-1]["content"]
    
    prompt = f"""
    用户问题：{user_query}
    
    请判断用户意图，只能返回以下选项中的一个：
    - weather_agent：询问天气、温度、气候相关
    - code_agent：询问编程、代码、技术开发相关
    - farewell：用户说再见、退出、结束对话
    - general_agent：其他所有问题
    
    只返回选项字符串，不要任何其他内容。
    """
    
    try:
        resp = llm_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=20
        )
        intent = resp.choices[0].message.content.strip()
        # 兜底校验，防止模型乱输出
        valid_intents = {"weather_agent", "code_agent", "farewell", "general_agent"}
        return intent if intent in valid_intents else "general_agent"
    except Exception as e:
        print(f"意图分类失败: {e}")
        return "general_agent"

# ========== 4. 各个业务节点 ==========
def weather_agent(state: AgentState) -> Dict:
    system_prompt = "你是一个天气助手，友好地回答天气相关问题。如果没有实时数据，可以给出一般性建议。"
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    
    resp = llm_client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=0.7
    )
    return {"messages": [{"role": "assistant", "content": resp.choices[0].message.content}]}

def code_agent(state: AgentState) -> Dict:
    system_prompt = "你是一个编程助手，擅长解答代码问题并给出清晰的代码示例。"
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    
    resp = llm_client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=0.7
    )
    return {"messages": [{"role": "assistant", "content": resp.choices[0].message.content}]}

def general_agent(state: AgentState) -> Dict:
    system_prompt = "你是一个友善的 AI 助手，可以回答各种问题。"
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    
    resp = llm_client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=0.7
    )
    return {"messages": [{"role": "assistant", "content": resp.choices[0].message.content}]}

def farewell_agent(state: AgentState) -> Dict:
    return {"messages": [{"role": "assistant", "content": "再见！期待下次与你交流。"}]}

# ========== 5. 构建图（去掉冗余 router 节点） ==========
builder = StateGraph(AgentState)

# 只加业务节点，不需要空路由节点
builder.add_node("weather_agent", weather_agent)
builder.add_node("code_agent", code_agent)
builder.add_node("general_agent", general_agent)
builder.add_node("farewell", farewell_agent)

# 直接从 START 出发做条件路由，省掉中间节点
builder.add_conditional_edges(
    START,
    classify_intent,
    {
        "weather_agent": "weather_agent",
        "code_agent": "code_agent",
        "general_agent": "general_agent",
        "farewell": "farewell",
    }
)

# 所有节点执行完结束
for node in ["weather_agent", "code_agent", "general_agent", "farewell"]:
    builder.add_edge(node, END)

# 编译图
graph = builder.compile()

# ========== 测试 ==========
if __name__ == "__main__":
    test_inputs = [
        "北京今天天气怎么样？",
        "帮我写一个 Python 快速排序",
        "你好，介绍一下你自己",
        "再见啦！"
    ]

    for user_input in test_inputs:
        print(f"\n用户: {user_input}")
        result = graph.invoke({"messages": [{"role": "user", "content": user_input}]})
        print(f"助手: {result['messages'][-1]['content'][:100]}...")
        print("-" * 50)