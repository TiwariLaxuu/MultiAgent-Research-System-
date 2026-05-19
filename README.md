# MultiAgent-Research-System-
Used Multiple Tools, Multiple Agents, Pipeline Create, Data Store 

Step 1: Install all the dependencies creating a virtual environment using uv which is very fast and easily accessible, so i prefer this. 

Step 2: Create tools.py We will build 2 custom tools using the @tool decorator. First web_search tool which talks to tavily api and fetches live search results from the internet. Second the scrape_url tool which takes a URL, visits that page and extracts clean readable text using BeautifulSoup. Using inspect in the web browser see all the html code, all the text or anything you want to extract it easily from bs4. 

Step 3: Create agents.py This is the heart of the project. We will build 4 things here. 
1. Search Agent using create_react_agent + AgentExecutor which will use the web_search tool. 
2. Reader agent using the same pattern but with the scrape_url tool. 
3. Writer Chain using the modern LCEL Pipe syntax - prompt | LLM | StrOutputParser() which takes all the research and writes a full report. 
4. Crtic Chain again using LCEL Pipe which reads the report and give a score and feedback.

Step 4: Create pipeline.py This is the supervisor.  
