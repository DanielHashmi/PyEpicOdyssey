import os  
import asyncio  
import asyncpg  
from datetime import datetime  
from dataclasses import dataclass  
from pydantic import BaseModel, Field  
from open_router_config import config
from agents import Agent, Runner, function_tool, SQLiteSession, RunContextWrapper  
  
# Pydantic models for structured output  
class UserEvent(BaseModel):  
    uid: str  
    plan: str  
    timestamp: datetime = Field(default_factory=datetime.now)  
    action: str  
  
class PlanFeatures(BaseModel):  
    plan_name: str  
    api_calls_limit: int  
    support_level: str  
    features: list[str]  
  
class UsageInfo(BaseModel):  
    current_usage: int  
    limit: int  
    percentage_used: float  
  
@dataclass  
class UserContext:  
    uid: str  
    db_pool: asyncpg.Pool  
    session_id: str  
      
    async def get_plan(self) -> str:  
        """Get user's subscription plan from database"""  
        try:  
            async with self.db_pool.acquire() as conn:  
                result = await conn.fetchrow(  
                    "SELECT plan_type FROM user_subscriptions WHERE user_id = $1 AND active = true",   
                    self.uid  
                )  
                return result['plan_type'] if result else "No active plan"  
        except Exception as e:  
            print(f"Database error getting plan for user {self.uid}: {e}")  
            return "Error retrieving plan"  
      
    async def get_usage(self) -> dict:  
        """Get user's current API usage"""  
        try:  
            async with self.db_pool.acquire() as conn:  
                result = await conn.fetchrow(  
                    "SELECT current_usage, monthly_limit FROM user_usage WHERE user_id = $1",   
                    self.uid  
                )  
                if result:  
                    return {  
                        'current_usage': result['current_usage'],  
                        'limit': result['monthly_limit'],  
                        'percentage_used': (result['current_usage'] / result['monthly_limit']) * 100  
                    }  
                return {'current_usage': 0, 'limit': 0, 'percentage_used': 0}  
        except Exception as e:  
            print(f"Database error getting usage for user {self.uid}: {e}")  
            return {'current_usage': 0, 'limit': 0, 'percentage_used': 0}  
  
# Function tools with proper error handling  
@function_tool  
async def show_user_plan(context: RunContextWrapper[UserContext]) -> str:  
    """  
    Get the user's current subscription plan.  
      
    This tool checks the user's unique ID and returns their current plan from the database.  
    Always call this function when the response needs to be personalized based on the user's plan.  
      
    Args:  
        context: Automatically injected context with user data and database connection.  
          
    Returns:  
        A string indicating the user's current plan level.  
    """  
    plan = await context.context.get_plan()  
    print(f"Retrieved plan '{plan}' for user {context.context.uid}")  
    return f"Your current subscription plan is: {plan}"  
  
@function_tool  
async def get_plan_features(context: RunContextWrapper[UserContext]) -> str:
    """  
    Get detailed features available for the user's current plan.  
      
    Returns comprehensive information about what the user can access with their plan.  
      
    Args:  
        context: Automatically injected context with user data.  
          
    Returns:  
        Detailed feature information for the user's plan.  
    """  
    plan = await context.context.get_plan()  
      
    features_map = {  
        "Enterprise": {  
            "api_calls": "Unlimited",  
            "support": "24/7 Priority Support",  
            "features": ["Custom integrations", "Advanced analytics", "Dedicated account manager", "SLA guarantee"]  
        },  
        "Pro": {  
            "api_calls": "50,000/month",  
            "support": "Email support (24h response)",  
            "features": ["Advanced analytics", "API access", "Custom webhooks", "Priority processing"]  
        },  
        "Basic": {  
            "api_calls": "5,000/month",  
            "support": "Community support",  
            "features": ["Basic analytics", "Standard API access", "Email notifications"]  
        }  
    }  
      
    if plan in features_map:  
        features = features_map[plan]  
        return f"""  
Plan: {plan}  
API Calls: {features['api_calls']}  
Support: {features['support']}  
Features: {', '.join(features['features'])}  
        """.strip()  
    else:  
        return f"No feature information available for plan: {plan}"  
  
@function_tool  
async def check_usage_limits(context: RunContextWrapper[UserContext]) -> str:  
    """  
    Check current usage against plan limits.  
      
    Provides detailed information about the user's API usage and remaining quota.  
      
    Args:  
        context: Automatically injected context with user data.  
          
    Returns:  
        Current usage statistics and remaining quota information.  
    """  
    usage_data = await context.context.get_usage()  
      
    if usage_data['limit'] == 0:  
        return "No usage data available for your account."  
      
    percentage = usage_data['percentage_used']  
    status = "Good" if percentage < 80 else "Warning" if percentage < 95 else "Critical"  
      
    return f"""  
Current Usage: {usage_data['current_usage']:,} API calls  
Monthly Limit: {usage_data['limit']:,} API calls  
Usage: {percentage:.1f}% ({status})  
Remaining: {usage_data['limit'] - usage_data['current_usage']:,} API calls  
    """.strip()  
  
@function_tool  
async def upgrade_plan_info(context: RunContextWrapper[UserContext]) -> str:  
    """  
    Provide information about plan upgrades.  
      
    Shows available upgrade options and benefits for the user's current plan.  
      
    Args:  
        context: Automatically injected context with user data.  
          
    Returns:  
        Information about available plan upgrades.  
    """  
    current_plan = await context.context.get_plan()  
      
    upgrade_info = {  
        "Basic": "Upgrade to Pro for 10x more API calls and email support, or Enterprise for unlimited usage.",  
        "Pro": "Upgrade to Enterprise for unlimited API calls and 24/7 priority support.",  
        "Enterprise": "You're already on our highest tier plan!",  
        "No active plan": "Choose from Basic ($9/month), Pro ($49/month), or Enterprise ($199/month)."  
    }  
      
    return upgrade_info.get(current_plan, "Contact support for upgrade options.")  
  
# Database initialization  
async def init_database(db_pool: asyncpg.Pool):  
    """Initialize database tables if they don't exist"""  
    async with db_pool.acquire() as conn:  
        await conn.execute("""  
            CREATE TABLE IF NOT EXISTS user_subscriptions (  
                user_id TEXT PRIMARY KEY,  
                plan_type TEXT NOT NULL,  
                active BOOLEAN DEFAULT true,  
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
            )  
        """)  
          
        await conn.execute("""  
            CREATE TABLE IF NOT EXISTS user_usage (  
                user_id TEXT PRIMARY KEY,  
                current_usage INTEGER DEFAULT 0,  
                monthly_limit INTEGER NOT NULL,  
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
            )  
        """)  
          
        # Insert sample data  
        await conn.execute("""  
            INSERT INTO user_subscriptions (user_id, plan_type)   
            VALUES ('1', 'Enterprise'), ('2', 'Pro'), ('3', 'Basic')  
            ON CONFLICT (user_id) DO NOTHING  
        """)  
          
        await conn.execute("""  
            INSERT INTO user_usage (user_id, current_usage, monthly_limit)  
            VALUES ('1', 15000, 999999), ('2', 8500, 50000), ('3', 2100, 5000)  
            ON CONFLICT (user_id) DO NOTHING  
        """)  
  
# Authentication and validation  
async def authenticate_user(uid: str, db_pool: asyncpg.Pool) -> bool:  
    """Authenticate user exists in database"""  
    try:  
        async with db_pool.acquire() as conn:  
            result = await conn.fetchrow(  
                "SELECT user_id FROM user_subscriptions WHERE user_id = $1", uid  
            )  
            return result is not None  
    except Exception as e:  
        print(f"Authentication error for user {uid}: {e}")  
        return False  
  
def validate_input(query: str) -> bool:  
    """Validate user input"""  
    return len(query.strip()) > 0 and len(query) < 1000  
  
# Main application class  
class SubscriptionAssistantApp:  
    def __init__(self):  
        self.db_pool = None  
        self.config = config
          
        # Create agent with all tools  
        self.agent = Agent[UserContext](  
            name="Subscription Assistant",  
            instructions="""You are a helpful subscription management assistant.   
            Always use the available tools to get accurate, up-to-date information about the user's account.  
            Be friendly, informative, and proactive in helping users understand their subscription status.  
            If users ask about upgrades, provide clear information about benefits.""",  
            tools=[show_user_plan, get_plan_features, check_usage_limits, upgrade_plan_info],  
            # output_type=UserEvent  
        )  
      
    async def setup_database(self):  
        """Setup database connection and initialize tables"""  
        database_url = os.getenv("DATABASE_URL", "postgresql://localhost/subscription_app")  
        try:  
            self.db_pool = await asyncpg.create_pool(database_url, min_size=1, max_size=10)  
            await init_database(self.db_pool)  
            print("Database initialized successfully")  
        except Exception as e:  
            print(f"Database setup failed: {e}")  
            # Fallback to SQLite for demo  
            print("Falling back to in-memory demo mode")  
            self.db_pool = None  
      
    async def run_conversation(self, uid: str, query: str, session: SQLiteSession) -> str:  
        """Run a single conversation turn"""  
        if not validate_input(query):  
            return "Invalid input. Please provide a valid query."  
          
        # For demo purposes, create a mock pool if database setup failed  
        if self.db_pool is None:  
            # Create mock context for demo  
            user_context = UserContext(uid=uid, db_pool=None, session_id=session.session_id)  
            # Override get_plan method for demo  
            async def mock_get_plan():  
                plans = {'1': 'Enterprise', '2': 'Pro', '3': 'Basic'}  
                return plans.get(uid, 'No active plan')  
            user_context.get_plan = mock_get_plan  
              
            async def mock_get_usage():  
                usage_data = {  
                    '1': {'current_usage': 15000, 'limit': 999999, 'percentage_used': 1.5},  
                    '2': {'current_usage': 8500, 'limit': 50000, 'percentage_used': 17.0},  
                    '3': {'current_usage': 2100, 'limit': 5000, 'percentage_used': 42.0}  
                }  
                return usage_data.get(uid, {'current_usage': 0, 'limit': 0, 'percentage_used': 0})  
            user_context.get_usage = mock_get_usage  
        else:  
            # Authenticate user  
            if not await authenticate_user(uid, self.db_pool):  
                return "User authentication failed. Please check your user ID."  
              
            user_context = UserContext(uid=uid, db_pool=self.db_pool, session_id=session.session_id)  
          
        try:  
            result = await Runner.run(  
                self.agent,  
                input=query,  
                context=user_context,  
                run_config=self.config,  
                session=session,  
                max_turns=5  
            )  
            return result.final_output  
        except Exception as e:  
            print(f"Agent execution failed: {e}")  
            return f"Sorry, I encountered an error: {str(e)}"  
      
    async def start_interactive_session(self):  
        """Start interactive command-line session"""  
        await self.setup_database()  
          
        print("🚀 Subscription Assistant Started!")  
        print("Type 'quit' to exit, 'help' for commands")  
        print("-" * 50)  
          
        current_uid = None  
        session = None  
          
        try:  
            while True:  
                if current_uid is None:  
                    uid = input("\n👤 Enter your User ID (1, 2, or 3 for demo): ").strip()  
                    if uid.lower() == 'quit':  
                        break  
                    if uid in ['1', '2', '3']:  
                        current_uid = uid  
                        session = SQLiteSession(f"user_{uid}_session")  
                        print(f"✅ Logged in as User {uid}")  
                        continue  
                    else:  
                        print("❌ Invalid User ID. Use 1, 2, or 3 for demo.")  
                        continue  
                  
                query = input(f"\n💬 User {current_uid}: ").strip()  
                  
                if query.lower() == 'quit':  
                    break  
                elif query.lower() == 'help':  
                    print("""  
Available commands:  
- Ask about your subscription plan  
- Check usage limits    
- Get plan features  
- Ask about upgrades  
- 'logout' to switch users  
- 'quit' to exit  
                    """)  
                    continue  
                elif query.lower() == 'logout':  
                    current_uid = None  
                    session = None  
                    print("👋 Logged out")  
                    continue  
                elif not query:  
                    continue  
                  
                print("🤖 Assistant: ", end="")  
                response = await self.run_conversation(current_uid, query, session)  
                print(response)  
                  
        except KeyboardInterrupt:  
            print("\n👋 Goodbye!")  
        finally:  
            if self.db_pool:  
                await self.db_pool.close()  
  
# Entry point  
async def main():  
    """Main application entry point"""  
    app = SubscriptionAssistantApp()  
    await app.start_interactive_session()  
  
if __name__ == '__main__':      
    asyncio.run(main())