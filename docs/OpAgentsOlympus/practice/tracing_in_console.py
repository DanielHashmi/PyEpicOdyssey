import asyncio
import json
from datetime import datetime
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner
from config import config
from agents.tracing import set_trace_processors
from agents.tracing.processors import BatchTraceProcessor, TracingExporter
from agents.tracing.spans import Span
from agents.tracing.traces import Trace
from typing import Any


class ComprehensiveRichConsoleSpanExporter(TracingExporter):
    """Prints traces and spans to console with rich formatting, showing all data like the OpenAI dashboard."""

    def __init__(self):
        self.console = Console()
        self.span_hierarchy = {}  # Track parent-child relationships

    def export(self, items: list[Trace | Span[Any]]) -> None:
        for item in items:
            if isinstance(item, Trace):
                self._export_trace(item)
            else:
                self._export_span(item)

    def _export_trace(self, trace: Trace):
        trace_data = trace.export()
        if not trace_data:
            return

        # Format trace information like the dashboard
        trace_info = []
        trace_info.append(
            f"[bold blue]Trace ID:[/bold blue] {trace_data.get('id', 'N/A')}"
        )
        trace_info.append(
            f"[bold blue]Name:[/bold blue] {trace_data.get('workflow_name', 'N/A')}"
        )

        if trace_data.get("group_id"):
            trace_info.append(
                f"[bold blue]Group ID:[/bold blue] {trace_data['group_id']}"
            )

        if trace_data.get("metadata"):
            trace_info.append(
                f"[bold blue]Metadata:[/bold blue] {json.dumps(trace_data['metadata'], indent=2)}"
            )

        panel = Panel(
            "\n".join(trace_info), title="🔍 Trace Started", border_style="blue"
        )
        self.console.print(panel)

    def _export_span(self, span: Span[Any]):
        span_data = span.export()
        if not span_data:
            return

        # Extract all span information
        span_id = span_data.get("id", "N/A")
        parent_id = span_data.get("parent_id")
        trace_id = span_data.get("trace_id", "N/A")
        started_at = span_data.get("started_at")
        ended_at = span_data.get("ended_at")

        # Calculate duration
        duration = None
        if started_at and ended_at:
            try:
                start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
                duration = (end_time - start_time).total_seconds()
            except:
                duration = None

        # Get span type and data
        span_details = span_data.get("span_data", {})
        span_type = span_details.get("type", "unknown")

        # Create main tree with span type
        tree = Tree(f"[bold green]Span:[/bold green] {span_type}")

        # Add core span metadata
        tree.add(f"[cyan]Span ID:[/cyan] {span_id}")
        tree.add(f"[cyan]Trace ID:[/cyan] {trace_id}")
        if parent_id:
            tree.add(f"[cyan]Parent ID:[/cyan] {parent_id}")

        # Add timing information
        if started_at:
            tree.add(f"[cyan]Started At:[/cyan] {started_at}")
        if ended_at:
            tree.add(f"[cyan]Ended At:[/cyan] {ended_at}")
        if duration is not None:
            tree.add(f"[cyan]Duration:[/cyan] {duration:.3f}s")

        # Add error information if present
        if span_data.get("error"):
            error_info = span_data["error"]
            error_tree = tree.add("[red]Error:[/red]")
            error_tree.add(f"[red]Message:[/red] {error_info.get('message', 'N/A')}")
            if error_info.get("data"):
                error_tree.add(
                    f"[red]Data:[/red] {json.dumps(error_info['data'], indent=2)}"
                )

        # Add span-specific data based on type
        self._add_span_type_data(tree, span_type, span_details)

        self.console.print(tree)
        self.console.print()  # Add spacing between spans

    def _add_span_type_data(self, tree: Tree, span_type: str, span_details: dict):
        """Add type-specific span data like the OpenAI dashboard shows."""

        if span_type == "generation":
            self._add_generation_data(tree, span_details)
        elif span_type == "agent":
            self._add_agent_data(tree, span_details)
        elif span_type == "function":
            self._add_function_data(tree, span_details)
        elif span_type == "handoff":
            self._add_handoff_data(tree, span_details)
        elif span_type == "guardrail":
            self._add_guardrail_data(tree, span_details)
        elif span_type == "transcription":
            self._add_transcription_data(tree, span_details)
        elif span_type == "speech":
            self._add_speech_data(tree, span_details)
        elif span_type == "custom":
            self._add_custom_data(tree, span_details)
        else:
            # Generic data display for unknown types
            for key, value in span_details.items():
                if key != "type":
                    tree.add(f"[yellow]{key}:[/yellow] {self._format_value(value)}")

    def _add_generation_data(self, tree: Tree, data: dict):
        """Add generation span data."""
        if data.get("model"):
            tree.add(f"[yellow]Model:[/yellow] {data['model']}")

        if data.get("input"):
            input_tree = tree.add("[yellow]Input Messages:[/yellow]")
            for i, msg in enumerate(data["input"]):
                msg_tree = input_tree.add(f"Message {i + 1}")
                msg_tree.add(f"Role: {msg.get('role', 'N/A')}")
                content = msg.get("content", "")
                if len(content) > 100:
                    content = content[:100] + "..."
                msg_tree.add(f"Content: {content}")

        if data.get("output"):
            output_tree = tree.add("[yellow]Output Messages:[/yellow]")
            for i, msg in enumerate(data["output"]):
                msg_tree = output_tree.add(f"Message {i + 1}")
                if isinstance(msg, dict):
                    for key, value in msg.items():
                        if key == "content" and len(str(value)) > 100:
                            value = str(value)[:100] + "..."
                        msg_tree.add(f"{key}: {value}")

        if data.get("model_config"):
            config_tree = tree.add("[yellow]Model Config:[/yellow]")
            for key, value in data["model_config"].items():
                config_tree.add(f"{key}: {value}")

        if data.get("usage"):
            usage_tree = tree.add("[yellow]Usage:[/yellow]")
            for key, value in data["usage"].items():
                usage_tree.add(f"{key}: {value}")

    def _add_agent_data(self, tree: Tree, data: dict):
        """Add agent span data."""
        if data.get("name"):
            tree.add(f"[yellow]Agent Name:[/yellow] {data['name']}")

        if data.get("handoffs"):
            handoffs_tree = tree.add("[yellow]Available Handoffs:[/yellow]")
            for handoff in data["handoffs"]:
                handoffs_tree.add(f"• {handoff}")

        if data.get("tools"):
            tools_tree = tree.add("[yellow]Available Tools:[/yellow]")
            for tool in data["tools"]:
                tools_tree.add(f"• {tool}")

        if data.get("output_type"):
            tree.add(f"[yellow]Output Type:[/yellow] {data['output_type']}")

    def _add_function_data(self, tree: Tree, data: dict):
        """Add function span data."""
        if data.get("name"):
            tree.add(f"[yellow]Function Name:[/yellow] {data['name']}")

        if data.get("input"):
            tree.add(f"[yellow]Input:[/yellow] {self._format_value(data['input'])}")

        if data.get("output"):
            tree.add(f"[yellow]Output:[/yellow] {self._format_value(data['output'])}")

        if data.get("mcp_data"):
            mcp_tree = tree.add("[yellow]MCP Data:[/yellow]")
            for key, value in data["mcp_data"].items():
                mcp_tree.add(f"{key}: {self._format_value(value)}")

    def _add_handoff_data(self, tree: Tree, data: dict):
        """Add handoff span data."""
        if data.get("from_agent"):
            tree.add(f"[yellow]From Agent:[/yellow] {data['from_agent']}")
        if data.get("to_agent"):
            tree.add(f"[yellow]To Agent:[/yellow] {data['to_agent']}")

    def _add_guardrail_data(self, tree: Tree, data: dict):
        """Add guardrail span data."""
        if data.get("name"):
            tree.add(f"[yellow]Guardrail Name:[/yellow] {data['name']}")
        if "triggered" in data:
            status = "🚨 TRIGGERED" if data["triggered"] else "✅ PASSED"
            tree.add(f"[yellow]Status:[/yellow] {status}")

    def _add_transcription_data(self, tree: Tree, data: dict):
        """Add transcription span data."""
        if data.get("model"):
            tree.add(f"[yellow]Model:[/yellow] {data['model']}")

        if data.get("input"):
            input_info = data["input"]
            if isinstance(input_info, dict):
                tree.add(
                    f"[yellow]Input Format:[/yellow] {input_info.get('format', 'N/A')}"
                )
                if input_info.get("data"):
                    tree.add("[yellow]Input Data:[/yellow] [Audio data present]")

        if data.get("output"):
            tree.add(f"[yellow]Transcription:[/yellow] {data['output']}")

    def _add_speech_data(self, tree: Tree, data: dict):
        """Add speech span data."""
        if data.get("model"):
            tree.add(f"[yellow]Model:[/yellow] {data['model']}")

        if data.get("input"):
            tree.add(f"[yellow]Text Input:[/yellow] {data['input']}")

        if data.get("output"):
            output_info = data["output"]
            if isinstance(output_info, dict):
                tree.add(
                    f"[yellow]Output Format:[/yellow] {output_info.get('format', 'N/A')}"
                )
                if output_info.get("data"):
                    tree.add("[yellow]Audio Output:[/yellow] [Audio data present]")

        if data.get("first_content_at"):
            tree.add(f"[yellow]First Content At:[/yellow] {data['first_content_at']}")

    def _add_custom_data(self, tree: Tree, data: dict):
        """Add custom span data."""
        if data.get("name"):
            tree.add(f"[yellow]Custom Span Name:[/yellow] {data['name']}")

        if data.get("data"):
            custom_tree = tree.add("[yellow]Custom Data:[/yellow]")
            for key, value in data["data"].items():
                custom_tree.add(f"{key}: {self._format_value(value)}")

    def _format_value(self, value: Any) -> str:
        """Format a value for display, truncating if too long."""
        if value is None:
            return "None"

        str_value = str(value)
        if len(str_value) > 200:
            return str_value[:200] + "..."
        return str_value


# Use the comprehensive rich exporter
comprehensive_processor = BatchTraceProcessor(ComprehensiveRichConsoleSpanExporter())
set_trace_processors([comprehensive_processor])


async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    config.tracing_disabled = False

    result = Runner.run_streamed(
        agent, input="Please tell me 5 jokes.", run_config=config
    )
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
