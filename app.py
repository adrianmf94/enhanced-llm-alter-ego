"""
Enhanced LLM Alter Ego - AI-powered personal assistant chatbot.
Features real-time GitHub integration, modular data sources, and improved tool management.
"""
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import os

from utils import handle_tool_calls, DEFAULT_TOOLS
from data_sources import DataSourceManager, create_default_config
from prompts import get_prompt


load_dotenv(override=True)


class EnhancedMe:
    """Enhanced personal AI assistant with multi-source data integration."""

    def __init__(self, config=None):
        """
        Initialize the enhanced AI assistant.
        
        Args:
            config: Optional configuration dictionary
        """
        self.openai = OpenAI()
        
        # Use provided config or create default
        self.config = config or create_default_config()
        self.name = self.config.get("name", "Adrian Monge")
        self.prompt_style = self.config.get("prompt_style", "main")  # Allow prompt style configuration
        
        # Initialize data source manager
        self.data_manager = DataSourceManager(self.config)
        
        # Cache for profile data (refreshed periodically)
        self._profile_cache = None
        self._last_profile_update = None

    def get_profile_data(self, force_refresh: bool = False) -> str:
        """Get comprehensive profile data from all sources."""
        try:
            return self.data_manager.get_comprehensive_profile(include_github=True)
        except Exception as e:
            print(f"Error getting profile data: {e}")
            # Fallback to basic data if there's an error
            return self.data_manager.get_comprehensive_profile(include_github=False)

    def system_prompt(self) -> str:
        """Generate dynamic system prompt with current profile data."""
        # Get the base prompt from prompts.py
        base_prompt = get_prompt(self.name, self.prompt_style)
        
        # Get current profile data
        profile_data = self.get_profile_data()
        
        # Combine prompt with profile data
        return base_prompt + profile_data + f"\n\nWith this context, please chat with the user, always staying in character as {self.name}."

    def chat(self, message, history):
        """
        Main chat function that handles conversation flow.
        
        Args:
            message: User's current message
            history: Chat history in Gradio format
            
        Returns:
            AI assistant's response
        """
        # Build messages for OpenAI API
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        
        # Handle conversation with potential tool calls
        done = False
        while not done:
            try:
                response = self.openai.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=messages, 
                    tools=DEFAULT_TOOLS
                )
                
                if response.choices[0].finish_reason == "tool_calls":
                    # Handle tool calls
                    message_with_tools = response.choices[0].message
                    tool_calls = message_with_tools.tool_calls
                    tool_results = handle_tool_calls(tool_calls)
                    
                    # Add tool call and results to message history
                    messages.append(message_with_tools)
                    messages.extend(tool_results)
                else:
                    # No more tool calls, we're done
                    done = True
                    
            except Exception as e:
                print(f"Error in chat: {e}")
                return f"I apologize, but I'm experiencing some technical difficulties. Please try again in a moment."
        
        return response.choices[0].message.content

    def refresh_data(self):
        """Manually refresh all data sources."""
        print("Refreshing profile data...")
        self._profile_cache = None
        # Force refresh GitHub data
        self.data_manager.get_github_data(force_refresh=True)
        print("Profile data refreshed!")


def create_interface(enhanced_me: EnhancedMe):
    """Create the Gradio interface with additional controls."""
    
    with gr.Blocks(title=f"Chat with {enhanced_me.name}") as demo:
        gr.Markdown(f"# Chat with {enhanced_me.name}")
        gr.Markdown(f"Ask me about my background, experience, projects, or anything else! I have real-time access to my GitHub activity and comprehensive professional information.")
        
        # Main chat interface
        chatbot = gr.ChatInterface(
            enhanced_me.chat,
            type="messages",
            title=None,
            description=None
        )
        
        # Add refresh button
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh Profile Data", variant="secondary", size="sm")
            refresh_btn.click(
                fn=enhanced_me.refresh_data,
                inputs=[],
                outputs=[]
            )
    
    return demo


def main():
    """Main entry point for the application."""
    # Create default configuration (can be customized)
    config = create_default_config()
    
    # You can override specific settings here
    # config["github_username"] = "your-actual-username"
    # config["name"] = "Your Actual Name"
    
    # Initialize enhanced AI assistant
    enhanced_me = EnhancedMe(config)
    
    # Create and launch interface
    demo = create_interface(enhanced_me)
    
    print(f"Starting Enhanced LLM Alter Ego for {enhanced_me.name}")
    print(f"GitHub integration: {'✓' if config.get('github_username') else '✗'}")
    print("Navigate to the URL shown below to start chatting!")
    
    demo.launch()


if __name__ == "__main__":
    main() 