import asyncio  
from agents import trace  
from agents.tracing import agent_span, function_span, generation_span  
from agents.tracing.scope import Scope
import dotenv

dotenv.load_dotenv()

async def demonstrate_span_hierarchy():  
    print("=== Demonstrating Span Hierarchy ===")  
      
    # This will create the main trace that Runner uses  
    with trace("span_hierarchy_demo") as main_trace:  
        print(f"Main trace started: {main_trace.trace_id}")  
          
        # Create spans manually within the Runner context  
        parent_span = agent_span("parent_agent")  
        parent_span.start(mark_as_current=True)  
        print(f"Parent span started: {parent_span.span_id}")  
        print(f"Current span after parent start: {Scope.get_current_span()}")  
          
        child_span = function_span("tool_call")  
        child_span.start(mark_as_current=True)  
        print(f"Child span started: {child_span.span_id}")  
        print(f"Current span after child start: {Scope.get_current_span()}")  
          
        # Create another span that becomes current  
        other_span = generation_span(  
            input=[{"role": "user", "content": "manual test"}],  
            model="gpt-4o-mini"  
        )
        
        other_span.start(mark_as_current=True)  
        print(f"Other span started: {other_span.span_id}")  
        print(f"Current span after other start: {Scope.get_current_span()}")  
          
        # Finish child_span while other_span is current  
        print(f"About to finish child_span while other_span is current")  
        child_span.finish()  
        print(f"Child span finished. Current span: {Scope.get_current_span()}")  
          
        # Verify the hierarchy is preserved  
        print(f"Child span parent_id: {child_span.parent_id}")  
        print(f"Parent span span_id: {parent_span.span_id}")  
        print(f"Other span parent_id: {other_span.parent_id}")  
          
        # Clean up remaining spans  
        other_span.finish()  
        parent_span.finish()  
  
# Run the demonstration  
asyncio.run(demonstrate_span_hierarchy())

# Output:
# === Demonstrating Span Hierarchy ===
# Main trace started: trace_9244edff272d4532ad02c1ccf777ac29
# Parent span started: span_810c48d032ee4fcab115520a
# Current span after parent start: <agents.tracing.spans.SpanImpl object at 0x0000029C9E592DD0>
# Child span started: span_0ff1add6b7e043f899883cac
# Current span after child start: <agents.tracing.spans.SpanImpl object at 0x0000029C9E592E50>
# Other span started: span_6e3091714f894fb38a34b1e7
# Current span after other start: <agents.tracing.spans.SpanImpl object at 0x0000029C9E592ED0>
# About to finish child_span while other_span is current
# Child span finished. Current span: <agents.tracing.spans.SpanImpl object at 0x0000029C9E592ED0>
# Child span parent_id: span_810c48d032ee4fcab115520a
# Parent span span_id: span_810c48d032ee4fcab115520a
# Other span parent_id: span_0ff1add6b7e043f899883cac