import asyncio
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# ─── Configure Gemini ─────────────────────────────────────────
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"


# ─── Convert MCP tools → Gemini function declarations ─────────
def convert_tools_for_gemini(mcp_tools):
    """
    Converts MCP tool definitions into Gemini function declarations format.
    """
    gemini_tools = []

    for tool in mcp_tools:
        properties = {}
        required = []

        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema_props = tool.inputSchema.get("properties", {})
            required = tool.inputSchema.get("required", [])

            for prop_name, prop_info in schema_props.items():
                prop_type = prop_info.get("type", "string")

                type_mapping = {
                    "string": "STRING",
                    "integer": "INTEGER",
                    "number": "NUMBER",
                    "boolean": "BOOLEAN",
                    "array": "ARRAY",
                    "object": "OBJECT"
                }

                properties[prop_name] = {
                    "type": type_mapping.get(prop_type, "STRING"),
                    "description": prop_info.get("description", prop_name)
                }

        gemini_tools.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or "",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        k: types.Schema(
                            type=getattr(types.Type, v["type"]),
                            description=v["description"]
                        )
                        for k, v in properties.items()
                    },
                    required=required
                )
            )
        )

    return gemini_tools


# ─── Execute a tool call via MCP ──────────────────────────────
async def execute_tool(session: ClientSession, tool_name: str, tool_args: dict):
    """
    Execute a tool call through the MCP session and return the result.
    """
    print(f"\n  🔧 Calling tool: {tool_name}")
    print(f"  📥 With args: {json.dumps(tool_args, indent=2)}")

    result = await session.call_tool(tool_name, tool_args)

    if result.content and len(result.content) > 0:
        tool_output = result.content[0].text
        print(f"  📤 Tool returned: {tool_output[:200]}...")
        return tool_output

    return "{}"


# ─── Main chat function ───────────────────────────────────────
async def chat(user_message: str):
    """
    Connects to MCP server, gets tools, sends message to Gemini,
    handles tool calls in agentic loop, returns final response.
    """
    server_params = StdioServerParameters(
        command="python",
        args=[os.path.join(os.path.dirname(__file__), "server.py")],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # ── Initialize MCP session ─────────────────────────
            await session.initialize()
            print("✅ Connected to MCP Server")

            # ── Get tools from MCP server ──────────────────────
            tools_response = await session.list_tools()
            mcp_tools = tools_response.tools
            print(f"📋 Found {len(mcp_tools)} tools: {[t.name for t in mcp_tools]}")

            # Convert to Gemini format
            gemini_functions = convert_tools_for_gemini(mcp_tools)
            gemini_tools = [types.Tool(function_declarations=gemini_functions)]

            # ── Build conversation history ─────────────────────
            conversation_history = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_message)]
                )
            ]

            print(f"\n💬 User: {user_message}")
            print("🤔 Gemini is thinking...\n")

            # ── Agentic loop ───────────────────────────────────
            while True:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=conversation_history,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        temperature=0.7
                    )
                )

                candidate = response.candidates[0]
                content = candidate.content

                # Add Gemini response to history
                conversation_history.append(content)

                # Check if Gemini wants to call tools
                tool_calls = [
                    part for part in content.parts
                    if part.function_call is not None
                ]

                # No tool calls = Gemini has final answer
                if not tool_calls:
                    final_response = ""
                    for part in content.parts:
                        if part.text:
                            final_response += part.text
                    return final_response

                # ── Execute all tool calls ─────────────────────
                tool_results = []
                for part in tool_calls:
                    tool_name = part.function_call.name
                    tool_args = dict(part.function_call.args)

                    tool_output = await execute_tool(session, tool_name, tool_args)

                    tool_results.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_output}
                            )
                        )
                    )

                # Add tool results to history so Gemini can use them
                conversation_history.append(
                    types.Content(
                        role="user",
                        parts=tool_results
                    )
                )
                # Loop again — Gemini will now either
                # call more tools or give final answer


# ─── Interactive terminal chat loop ───────────────────────────
async def main():
    print("=" * 50)
    print("💰 Finance MCP Assistant")
    print("=" * 50)
    print("Type your question or 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break

        try:
            response = await chat(user_input)
            print(f"\n🤖 Assistant: {response}\n")
            print("-" * 50)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())