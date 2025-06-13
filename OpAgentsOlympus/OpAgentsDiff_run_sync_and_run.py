import asyncio
import os
import time
import dotenv
import threading
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled # type: ignore

dotenv.load_dotenv()
set_tracing_disabled(True)

api_key = os.environ.get("GEMINI_API_KEY")
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
llm = OpenAIChatCompletionsModel(model='gemini-1.5-flash', openai_client=client)

@function_tool
def echo(text: str) -> str:
    return text

def spin_blocking():
    """A blocking spinner that runs in the main thread - this WON'T work with run_sync"""
    while True:
        print("⟳", end="", flush=True)
        time.sleep(0.1)
        # This loop blocks the entire thread

def spin_threaded():
    """A spinner that runs in a separate thread - the only way to get concurrency with run_sync"""
    while not stop_spinner:
        print("⟳", end="", flush=True)
        time.sleep(0.1)

def main_with_run_sync():
    global stop_spinner
    stop_spinner = False
    
    # Start spinner in a separate thread (only way to get concurrency with run_sync)
    spinner_thread = threading.Thread(target=spin_threaded, daemon=True)
    spinner_thread.start()
    
    agent = Agent(
        name="EchoAgent",
        instructions="Echo whatever the user says.",
        tools=[echo],
        model=llm,
    )
    
    print("Starting agent (run_sync)…", end="")
    start_time = time.time()
    
    # This blocks the entire thread until completion
    result = Runner.run_sync(agent, "Hello, world!")
    
    end_time = time.time()
    stop_spinner = True
    
    print("\nAgent done!")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print("Final output:", result.final_output)

async def main_with_async():
    """For comparison - the original async version"""
    async def spin():
        while True:
            print("⟳", end="", flush=True)
            await asyncio.sleep(0.1)
    
    spinner = asyncio.create_task(spin())
    
    agent = Agent(
        name="EchoAgent",
        instructions="Echo whatever the user says.",
        tools=[echo],
        model=llm,
    )
    
    print("Starting agent (async)…", end="")
    start_time = time.time()
    result = await Runner.run(agent, "Hello, world!")
    end_time = time.time()
    spinner.cancel()
    print("\nAgent done!")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print("Final output:", result.final_output)

def demonstrate_blocking_issue():
    """This demonstrates why run_sync blocks everything"""
    print("=== DEMONSTRATING run_sync BLOCKING ISSUE ===")
    print("This will NOT show a spinner because run_sync blocks the thread:")
    
    agent = Agent(
        name="EchoAgent",
        instructions="Echo whatever the user says.",
        tools=[echo],
        model=llm,
    )
    
    print("Starting agent…", end="")
    
    # Try to start a spinner - this won't work because run_sync will block
    # spin_blocking()  # If you uncomment this, it will block before run_sync even starts
    
    start_time = time.time()
    result = Runner.run_sync(agent, "Hello, world!")  # This blocks everything
    end_time = time.time()
    
    # We can't start both spinner and the agent with run_sync at the same time!
    print("Agent done! (no spinner was shown)")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print("Final output:", result.final_output)

if __name__ == "__main__":
    choice = input("Choose demo:\n1. run_sync with threading workaround\n2. async version (original)\n3. demonstrate blocking issue\nEnter 1, 2, or 3: ")
    
    if choice == "1":
        main_with_run_sync()
    elif choice == "2":
        asyncio.run(main_with_async())
    elif choice == "3":
        demonstrate_blocking_issue()
    else:
        print("Invalid choice, running blocking demonstration:")
        demonstrate_blocking_issue()
