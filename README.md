🤖 Multi-Agent Research Studio

An elevated AI orchestration studio built with Streamlit and LangGraph designed for deep web intelligence gathering, technical compilation, and automated editorial verification.

This system leverages 4 cooperative autonomous agents and chains to scout, scrape, synthesize, and audit comprehensive research dossiers on any given topic.

📸 App UI Live Dashboard

Below is the live execution flow of the Multi-Agent Pipeline. The interface features real-time telemetry analytics, a dynamic node status tracker, and an interactive workspace editor.

💡 Replace the placeholder image path above (assets/dashboard_screenshot.png) with your actual screenshot file path once saved inside your repository.

🤝 System Orchestration Flow

[ User Input Topic ]
         │
         ▼
 1. 🔍 Search Agent (Scouts Tavily API & caches discovery links)
         │
         ▼
 2. 📖 Reader Agent (Scrapes high-yield URLs with BeautifulSoup)
         │
         ▼
 3. ✍️ Writer Chain (Synthesizes raw context into structured Markdown)
         │
         ▼
 4. 🧐 Critic Chain (Audits formatting, layout, and factual citations)


🛠️ Step-by-Step Architecture Guide

Step 1: Environment Setup

We utilize uv for lightning-fast package management. This isolated environment prevents dependency conflicts and ensures quick installations of deep-learning runtimes.

Step 2: Custom Tool Integrations (tools.py)

We build custom tools decorated with LangChain's @tool wrapper:

web_search: Connects directly to the Tavily API to pull up-to-the-minute web indices on our target topic.

scrape_url: Receives a target URL, fetches the document object model (DOM), parses out raw elements via BeautifulSoup, and extracts structural markdown and paragraphs.

Step 3: Core Agents Setup (agents.py)

This contains the processing layers of our system:

Search Agent: Built using create_react_agent and AgentExecutor to strategically run searches when queries are complex.

Reader Agent: Built using the same pattern but strictly bound to the scrape_url tool to ingest specific deep page context.

Writer Chain: Implements the modern LCEL (LangChain Expression Language) pipe design pattern:


$$\text{Prompt} \;\lvert\; \text{LLM} \;\lvert\; \text{StrOutputParser()}$$

Critic Chain: An independent LCEL verification unit that evaluates the compiled report and outputs a diagnostic review score and structured suggestions.

How the Agent Engine Handles Tool Invocation Under the Hood:

Tools are passed as native function definitions directly within the LLM API schemas.

The LLM outputs structured, machine-readable JSON arguments (e.g., tool_calls).

LangGraph's engine automatically captures these calls, executes the bound local Python code, and feeds the outputs back into the chat state natively.

Step 4: The Central Supervisor (pipeline.py)

The pipeline serves as the state orchestrator. It manages a shared dictionary state, running each agent sequentially and feeding outputs as message-based sequences:

# Sequential state injection example
search_results = search_agent.invoke({"messages": [("user", "Find info...")]})
state["search_results"] = search_results['messages'][-1].content


Terminal logging updates the developer on which node is currently processing.

Step 5: Command Line Validation

Run the programmatic pipeline to verify connection points and verify standard out operations before engaging the UI:

uv run pipeline.py


Step 6: Interactive Web Interface (app.py)

The Streamlit application provides a highly polished dashboard using custom CSS selectors, glassmorphic rendering, and a state-preserved workspace editor.

⚙️ Project Setup & Installation

1. Clone the Repository

git clone https://github.com/your-username/MultiAgent-Research-System.git
cd MultiAgent-Research-System


2. Environment Setup (Using uv)

Ensure your virtual environment is active and all required dependencies are installed:

uv pip install -r requirements.txt


3. API Key Configuration

Create a .env file in the root directory or export these keys in your active shell:

export GROQ_API_KEY="your_groq_api_key_here"
export TAVILY_API_KEY="your_tavily_api_key_here"


4. Run the Streamlit Dashboard

Launch your local web engine:

uv run streamlit run app.py
