import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

print("🚀 Starting CrewAI + Qutato Integration Test...")

# 1. Point CrewAI to Qutato
# Note: We use a dummy API key since we're using Ollama locally via the gateway,
# or we just rely on Qutato's admin key.
os.environ["OPENAI_API_BASE"] = "http://localhost:8000/v1"
os.environ["OPENAI_API_KEY"] = "qutato_admin_secret_key"

qutato_llm = ChatOpenAI(
    model="gpt-3.5-turbo", # Qutato will route this or handle it
    temperature=0.7
)

# 2. Define a simple researcher agent
researcher = Agent(
    role="Senior AI Researcher",
    goal="Discover interesting facts about large language models",
    backstory="You are an expert AI researcher who loves explaining concepts simply.",
    llm=qutato_llm,
    verbose=True,
    allow_delegation=False
)

# 3. Define a basic task
task1 = Task(
    description="Write exactly one sentence explaining what a transformer architecture is. Do not output anything else.",
    expected_output="A single sentence explaining transformers.",
    agent=researcher
)

# 4. Form the crew and kick it off
crew = Crew(
    agents=[researcher],
    tasks=[task1],
    process=Process.sequential,
    verbose=True
)

print("\n🤖 Kicking off the CrewAI agents...")
result = crew.kickoff()

print("\n✅ CREW AI RESULT:")
print(result)
