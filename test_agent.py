from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import asyncio
# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent

# Load environment variables early
load_dotenv()

# Initialize the MCP MultiServer Client 

client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            "args": ["sqlitemcp.py"],
            "transport": "stdio"
        }
    }
)


# 1. We group structural routing functions outside the async block
AGENT_NODE = 'agent'
TOOL_NODE = 'tools'

def should_continue(state):
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return TOOL_NODE
    return END

# 2. Main async entrypoint to handle all 'await' calls safely
async def main():
    print("🤖 Connecting to MCP Client & fetching math tools...")
    
    # Resolving 'await' for the client tools initialization
    tools = await client.get_tools()
    print(f"Discovered Tools: {[tool.name for tool in tools]}\n")

    # Connect tools to model
    model = init_chat_model('gpt-4o')
    agent = create_agent(
    model=model, 
    tools=tools,
    system_prompt="You are a data assistant. Use the query tools to analyze SQLite database data."
)
    # model_with_tool = model.bind_tools(tools)

    # Define the worker model node asynchronously 
    # async def call_model(state: MessagesState):
    #     messages = state['messages']
    #     response = await agent.ainvoke(messages)
    #     return {"messages": [response]}

    async def call_model(state):
        messages = state["messages"]
        response = await agent.ainvoke({"messages": messages})

        # Ensure you return a dict mapping to the state key!
        if isinstance(response, dict) and "messages" in response:
            return {"messages": response["messages"]}

        # If ainvoke returns the raw message list or object directly:
        return {"messages": response}


    # 3. Correctly instantiate the Prebuilt ToolNode passing tools
    tools_executor_node = ToolNode(tools)

    # 4. Build the State Graph Workflow Pipeline
    builder = StateGraph(MessagesState)
    builder.add_node(AGENT_NODE, call_model)
    builder.add_node(TOOL_NODE, tools_executor_node) # Fixed parameter reference

    builder.add_edge(START, AGENT_NODE)
    builder.add_conditional_edges(
        AGENT_NODE,
        should_continue,
        {
            TOOL_NODE: TOOL_NODE,
            END: END
        }
    )
    builder.add_edge(TOOL_NODE, AGENT_NODE)

    # Compile the runnable graph structure
    graph = builder.compile()
    builder.compile()
    print("📊 Executing LangGraph workflow session...")
    
    # Resolving 'await' for invocation execution loop
    # response1 = await graph.ainvoke(
    #     {"messages": [{"role": "user", "content": "What is 3 + 5?"}]}
    # )

    input = {"messages": [{"role": "user", "content": "how many users did not make any purchase, please give the user ids as well"}]} 
    result = await graph.ainvoke(input) 
    print(result["messages"][-1].content)


    print("\n--- Final Graph Output ---")

    # print(response1["messages"][-1].content)

    # Clean up and close connection channel streams
    await client.aclose()

if __name__ == "__main__":
    # 5. Hand over control flow execution safely to asyncio event loops
    asyncio.run(main())
