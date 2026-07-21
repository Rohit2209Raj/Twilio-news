from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from crewai_tools import TavilySearchTool
from crewai.tools import BaseTool
from twilio.rest import Client
import os
import asyncio

load_dotenv()

deepseek_llm=LLM(
    model="deepseek/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7

)

tavily_tool = TavilySearchTool(
    api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5
)


class WhatsAppSenderTool(BaseTool):
    name: str = "WhatsApp Sender"
    description: str = "Sends the given text message to a WhatsApp number via Twilio."

    def _run(self, message: str) -> str:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        client.messages.create(
            from_="whatsapp:+14155238886",  # Twilio sandbox number
            body=message,
            to=f"whatsapp:{os.getenv('MY_WHATSAPP_NUMBER')}"  # e.g. +91XXXXXXXXXX
        )
        return "Message sent successfully to WhatsApp."

whatsapp_tool = WhatsAppSenderTool()

search_agent = Agent(
    role="News Finder",
    goal="Given a topic,You need to find latest 5 news about it.",
    backstory="A news finder,who collects news only from trusted sources and collects only if verfied. ",
    llm=deepseek_llm,
    tools=[tavily_tool],
    # verbose=True,
    allow_delegation=False,
)

editor_agent = Agent(
    role="News Editor",
    goal="Rewrite the collected news about '{topic}' in simple, jargon-free English that anyone can understand.",
    backstory="An editor who takes raw or technical news and rewrites it in clear, beginner-friendly language without losing key facts. You are supposed to rewirte news in easier language but dont make it a one-liner summary.it must contain weight",
    llm=deepseek_llm,
    allow_delegation=False,
)


sender_agent = Agent(
    role="WhatsApp Notifier",
    goal="Send the exact, unaltered final note for '{topic}' to WhatsApp — never shorten or summarize it yourself.",
    backstory="A reliable delivery assistant that passes content through exactly as received, without editorializing or compressing.",
    llm=deepseek_llm,
    tools=[whatsapp_tool],
    allow_delegation=False,
)


search_task = Task(
    description="Search for the latest verified news about '{topic}' from trusted sources.",
    expected_output="A list of 3-5 recent news items with source and short detail.",
    agent=search_agent,
)

edit_task = Task(
    description="Rewrite the collected news about '{topic}' in simple, jargon-free English.",
    expected_output="Simplified, clean version of the news, same facts, beginner-friendly language.",
    agent=editor_agent,
    context=[search_task],
)

send_task = Task(
    description=(
        "Take the EXACT rewritten news text from the previous task (editor's output) "
        "and pass it AS-IS to the WhatsApp Sender tool's 'message' argument. "
        "Do NOT summarize, shorten, or rewrite it further. Send the full detailed version, word-for-word."
    ),
    expected_output="Confirmation that the full detailed message was sent successfully, unmodified.",
    agent=sender_agent,
    context=[edit_task],
)


# async def news(topic: str) -> str:
#     crew = Crew(
#       agents=[search_agent, editor_agent, sender_agent],
#       tasks=[search_task, edit_task, send_task],
#       process=Process.sequential,
#       verbose=True,
#     )
#     result =  crew.kickoff_async(inputs={"topic": topic})
#     return str(result)

async def news(topic: str) -> str:
    crew = Crew(
      agents=[search_agent, editor_agent, sender_agent],
      tasks=[search_task, edit_task, send_task],
      process=Process.sequential,
      verbose=True,
      llm=deepseek_llm
    )
    result = await crew.kickoff_async(inputs={"topic": topic})
    return str(result)

answer = asyncio.run(news("Indian Stock Market past 1 week performance" ))
print(answer)