"""
Base agent tools & infrastructure: AgentResult and run_specialist_agent
"""
import json
import time
from dataclasses import dataclass, field
from config import client, ACTIVE_MODEL



@dataclass
class AgentResult:
    agent_name: str
    answer: str
    tools_called: list = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)
    confidence: float = 0.0
    issues_found: list = field(default_factory=list)
    reasoning: str = ""

    def summary(self):
        print(f"\n{'─'*54}")
        print(f"Agent      : {self.agent_name}")
        print(f"Tools used : {', '.join(self.tools_called) or 'none'}")
        print(f"Confidence : {self.confidence:.0%}")
        if self.issues_found:
            print(f"Issues     : {'; '.join(self.issues_found)}")
        print(f"Answer     :\n  {self.answer[:500]}")


# Lazy import to avoid circular dependency
def _get_tool_functions():
    """Lazy import of tool functions to avoid circular imports."""
    import tools
    return {
        "get_tickers_by_sector": tools.get_tickers_by_sector,
        "get_price_performance": tools.get_price_performance,
        "get_company_overview": tools.get_company_overview,
        "get_market_status": tools.get_market_status,
        "get_top_gainers_losers": tools.get_top_gainers_losers,
        "get_news_sentiment": tools.get_news_sentiment,
        "query_local_db": tools.query_local_db,
    }




def run_specialist_agent(
    agent_name: str,
    system_prompt: str,
    task: str,
    tool_schemas: list,
    max_iters: int = 8,
    verbose: bool = True,
) -> AgentResult:
    """Core agentic loop used by every agent."""
    
    ALL_TOOL_FUNCTIONS = _get_tool_functions()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task}
    ]
    
    tools_called = []
    raw_data = {}
    
    for iteration in range(max_iters):
        if verbose:
            print(f"  🔄 Iteration {iteration + 1}/{max_iters}")
        
        # Call OpenAI API
        try:
            if tool_schemas:
                response = client.chat.completions.create(
                    model=ACTIVE_MODEL,
                    messages=messages,
                    tools=tool_schemas
                )
            else:
                response = client.chat.completions.create(
                    model=ACTIVE_MODEL,
                    messages=messages
                )
        except Exception as e:
            return AgentResult(
                agent_name=agent_name,
                answer=f"API call failed: {str(e)}",
                tools_called=tools_called,
                raw_data=raw_data
            )
        
        message = response.choices[0].message
        
        if not message.tool_calls:
            # No tool calls = final answer
            if verbose:
                print(f"  ✅ Done! Called {len(tools_called)} tools")
            
            return AgentResult(
                agent_name=agent_name,
                answer=message.content or "No answer",
                tools_called=tools_called,
                raw_data=raw_data
            )
        
        # Has tool calls
        messages.append(message)
        
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                tool_args = {}
                if verbose:
                    print(f"    ⚠️  JSON parse error: {e}")
            
            if verbose:
                args_display = str(tool_args)[:60]
                print(f"    🔧 {tool_name}({args_display}...)")
            
            try:
                if tool_name in ALL_TOOL_FUNCTIONS:
                    func = ALL_TOOL_FUNCTIONS[tool_name]
                    result = func(**tool_args)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                tools_called.append(tool_name)
                raw_data[f"{tool_name}_{len(tools_called)}"] = result
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
                
                if verbose:
                    print(f"       ✓ Returned {len(str(result))} chars")
                
            except Exception as e:
                error_msg = f"Tool execution error: {str(e)}"
                if verbose:
                    print(f"       ✗ {error_msg}")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": error_msg})
                })
    
    if verbose:
        print(f"  ⚠️  Reached max iterations")
    
    return AgentResult(
        agent_name=agent_name,
        answer="Failed to complete task within iteration limit",
        tools_called=tools_called,
        raw_data=raw_data
    )