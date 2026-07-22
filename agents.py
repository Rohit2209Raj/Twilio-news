from crewai import Agent,Task,Crew,Process,LLM
from crewai_tools import TavilySearchTool
from tools import WhatsAppSenderTool
import os
from dotenv import load_dotenv

load_dotenv()


deepseek_llm = LLM(
    model="deepseek/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7
)

tavily_tool = TavilySearchTool(
    api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5
)

whatsapp_tool = WhatsAppSenderTool()

def create_agents():
    search_agent = Agent(
        role="News Finder",
        goal="Find latest 5 verified news about '{topic}' from trusted sources",
        backstory="Expert news researcher who finds accurate and verified news",
        llm=deepseek_llm,
        tools=[tavily_tool],
        allow_delegation=False,
        verbose=False
    )

    editor_agent = Agent(
        role="News Editor",
        goal="Rewrite news in simple, easy-to-understand language without losing key facts,do not summarize , just deliver content in easy language.",
        backstory="Skilled editor who simplifies complex news for everyone",
        llm=deepseek_llm,
        allow_delegation=False,
        verbose=False
    )

    sender_agent = Agent(
        role="WhatsApp Notifier",
        goal="Send the exact edited news to WhatsApp without any changes",
        backstory="Reliable assistant who delivers content as-is",
        llm=deepseek_llm,
        tools=[whatsapp_tool],
        allow_delegation=False,
        verbose=False
    )
    
    return search_agent, editor_agent, sender_agent


def process_news(topic:str,send_whatsapp:bool=True):
    """Process news for given topic"""
    try:
        search_agent, editor_agent, sender_agent = create_agents()
        
        # Define Tasks
        search_task = Task(
            description=f"Search latest 5 verified news about '{topic}' from trusted sources", # type: ignore
            expected_output="List of 5 recent news items with source and summary",
            agent=search_agent
        )

        edit_task = Task(
            description="Rewrite the collected news in simple, jargon-free English. Make it detailed but easy to understand",
            expected_output="Simplified news with same facts, formatted nicely",
            agent=editor_agent,
            context=[search_task]
        )
        
        tasks = [search_task, edit_task]
        
        # Add WhatsApp task if needed
        if send_whatsapp: # type: ignore
            send_task = Task(
                description="Send the EXACT edited news to WhatsApp without any changes",
                expected_output="Confirmation that message was sent",
                agent=sender_agent,
                context=[edit_task]
            )
            tasks.append(send_task)
        
        # Create and run Crew
        crew = Crew(
            agents=[search_agent, editor_agent, sender_agent] if send_whatsapp else [search_agent, editor_agent], # type: ignore
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff(inputs={"topic": topic}) # type: ignore
        return str(result)
        
    except Exception as e:
        raise Exception(f"News processing failed: {str(e)}")