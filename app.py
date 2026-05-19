import streamlit as st
import time
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# Premium Page Config
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Neon-Glassmorphic CSS Styles (Avoiding markdown indentation parser issues)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
}

.hero-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #311042 50%, #030712 100%);
    border-radius: 16px;
    padding: 35px;
    margin-bottom: 30px;
    border: 1px solid rgba(139, 92, 246, 0.2);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.hero-title {
    background: linear-gradient(90deg, #a78bfa 0%, #ec4899 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0 0 10px 0;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 400;
    margin: 0;
}

.agent-card {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.agent-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
    border-color: rgba(99, 102, 241, 0.3);
}

.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-search { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
.badge-reader { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-writer { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-critic { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 2px;
    letter-spacing: -0.03em;
}

.metric-label {
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

.pipeline-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 20px 0 35px 0;
    padding: 20px;
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
}

.pipeline-node {
    flex: 1;
    text-align: center;
    position: relative;
}

.pipeline-node:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 25%;
    right: -50%;
    width: 100%;
    height: 2px;
    background: rgba(255, 255, 255, 0.1);
    z-index: 1;
}

.node-bubble {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #334155;
    color: #94a3b8;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    z-index: 2;
    position: relative;
    border: 2px solid #1e293b;
    transition: all 0.3s ease;
}

.node-title {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-top: 8px;
    font-weight: 500;
}

.node-active .node-bubble {
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
    color: white;
    box-shadow: 0 0 15px rgba(236, 72, 153, 0.4);
    border-color: #f472b6;
}

.node-active .node-title {
    color: #f472b6;
    font-weight: 600;
}

.node-done .node-bubble {
    background: #10b981;
    color: white;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
    border-color: #34d399;
}

.node-done .node-title {
    color: #34d399;
}

.terminal-window {
    background: #020617;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 15px;
    font-family: 'JetBrains Mono', monospace;
    color: #38bdf8;
    font-size: 0.85rem;
    line-height: 1.6;
    max-height: 200px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

if "state" not in st.session_state:
    st.session_state.state = {
        "search_results": "",
        "reader_results": "",
        "report": "",
        "feedback": "",
        "logs": []
    }
if "is_researching" not in st.session_state:
    st.session_state.is_researching = False
if "execution_times" not in st.session_state:
    st.session_state.execution_times = {}
if "pipeline_step" not in st.session_state:
    st.session_state.pipeline_step = 0

def log_agent_activity(agent_name, message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.state["logs"].append(f"[{timestamp}] {agent_name}: {message}")

# Fixed: Compiling HTML inside a single line format to avoid leading space markdown parsing bug
def render_pipeline_tracker(step, placeholder=None):
    steps = [
        {"num": "1", "title": "Searcher"},
        {"num": "2", "title": "Reader"},
        {"num": "3", "title": "Writer"},
        {"num": "4", "title": "Critic"}
    ]
    
    html_out = '<div class="pipeline-wrapper">'
    for i, s in enumerate(steps, 1):
        status_class = ""
        if step == i:
            status_class = "node-active"
        elif step > i:
            status_class = "node-done"
            
        # Compile without newlines or tab indentations to prevent markdown code block escapes
        html_out += f'<div class="pipeline-node {status_class}"><div class="node-bubble">{s["num"]}</div><div class="node-title">{s["title"]}</div></div>'
    html_out += '</div>'
    
    if placeholder:
        placeholder.markdown(html_out, unsafe_allow_html=True)
    else:
        st.markdown(html_out, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://placehold.co/400x120/1e1b4b/a78bfa?text=AGENT+SYSTEMS+CONSOLE", use_container_width=True)
    st.markdown("### ⚙️ Engine Control")
    st.caption("Fine-tune model capabilities prior to runtime.")
    
    llm_provider = st.selectbox(
        "Autonomous LLM Engine", 
        ["Groq Cloud (Llama 3)", "Ollama Local (Mistral)", "OpenAI Client"],
        index=0
    )
    
    max_search_results = st.slider("Max Search Queries", min_value=2, max_value=12, value=6)
    deep_scrape_depth = st.radio("Deep Scrape Density", ["Standard Core Article", "High Intensive Parsing"], index=0)
    
    st.divider()
    st.markdown("### 🛠️ Execution Pipeline")
    st.info("The system automatically orchestrates 4 autonomous agents to gather, distill, synthesize, and audit critical inputs.")
    
    if st.button("🔄 Reset Environment", use_container_width=True, type="secondary"):
        st.session_state.state = {
            "search_results": "",
            "reader_results": "",
            "report": "",
            "feedback": "",
            "logs": []
        }
        st.session_state.execution_times = {}
        st.session_state.is_researching = False
        st.session_state.pipeline_step = 0
        st.rerun()

st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🤖 Multi-Agent Research System</h1>
    <p class="hero-subtitle">Elevated AI orchestration for deep intelligence gather, technical compilation, and editorial verification.</p>
</div>
""", unsafe_allow_html=True)

# Pre-populate unless already generated
default_val = "Traditional RAG vs Agentic RAG" if not st.session_state.state["report"] else ""
topic = st.text_input("Define Target Research Topic:", placeholder="e.g., Traditional RAG vs Agentic RAG", value=default_val)

start_research = st.button("🚀 Execute Autonomous Pipeline", type="primary", use_container_width=True)

if start_research and topic:
    st.session_state.is_researching = True
    st.session_state.state["logs"] = []
    start_total_time = time.time()
    
    # Active Deployment Section Container
    visual_container = st.container()
    
    with visual_container:
        st.markdown("### 🔄 Active Deployment")
        
        # Unified persistent status tracker placeholder
        tracker_placeholder = st.empty()
        
        # --- STAGE 1: SEARCH AGENT ---
        st.session_state.pipeline_step = 1
        render_pipeline_tracker(1, tracker_placeholder)
        t0 = time.time()
        
        with st.status("🔍 Active Agent: Google Search Orchestrator...", expanded=True) as status:
            log_agent_activity("Search Agent", f"Initiating web reconnaissance for: '{topic}'")
            st.write("Generating optimal query parameters...")
            
            search_agent = build_search_agent()
            search_results = search_agent.invoke(
                {
                    "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
                }
            )
            raw_content = search_results['messages'][-1].content
            # Guard against None values
            st.session_state.state["search_results"] = raw_content if raw_content is not None else "No search results retrieved."
            log_agent_activity("Search Agent", "Successfully queried targets and cached discovery metadata.")
            status.update(label="🔍 Search Agent: Phase Complete!", state="complete", expanded=False)
            
        st.session_state.execution_times["Search Agent"] = round(time.time() - t0, 2)
            
        # --- STAGE 2: READER AGENT ---
        st.session_state.pipeline_step = 2
        render_pipeline_tracker(2, tracker_placeholder)
        t0 = time.time()
        
        with st.status("📖 Active Agent: Raw HTML Markdown Scraper...", expanded=True) as status:
            log_agent_activity("Reader Agent", "Parsing discovered references...")
            st.write("Evaluating high-yield index sources and resolving HTML tables to text...")
            
            reader_agent = build_reader_agent()
            reader_results = reader_agent.invoke(
                {
                    "messages":[("user", 
                                 f"based on the following search result about '{topic}', "
                                 f"pick the most relevant url and scrape it for deeper content.\n\n "
                                 f"Search Result: \n{st.session_state.state['search_results'][:800]}"
                                 )]
                }
            )
            raw_reader = reader_results['messages'][-1].content
            st.session_state.state["reader_results"] = raw_reader if raw_reader is not None else "No scraping content extracted."
            log_agent_activity("Reader Agent", "Completed markdown extraction of source documents.")
            status.update(label="📖 Reader Agent: Phase Complete!", state="complete", expanded=False)
            
        st.session_state.execution_times["Reader Agent"] = round(time.time() - t0, 2)

        # --- STAGE 3: WRITER CHAIN ---
        st.session_state.pipeline_step = 3
        render_pipeline_tracker(3, tracker_placeholder)
        t0 = time.time()
        
        with st.status("✍️ Active Agent: Expert Intelligence Synthesizer...", expanded=True) as status:
            log_agent_activity("Writer Chain", "Constructing research synthesis matrix.")
            st.write("Integrating reader files with cached discoveries...")
            
            research_combined = (f"SEARCH RESULTS:\n{st.session_state.state['search_results']}\n\n"
                                 f"DETAILED SCRAPED CONTENT:\n{st.session_state.state['reader_results']}")
            
            writer_result = writer_chain.invoke(
                {
                    "topic": topic,
                    "research": research_combined
                }
            )
            st.session_state.state["report"] = writer_result if writer_result is not None else "Error generating report compilation."
            log_agent_activity("Writer Chain", "First draft compiled and formatted.")
            status.update(label="✍️ Writer Chain: Phase Complete!", state="complete", expanded=False)
            
        st.session_state.execution_times["Writer Chain"] = round(time.time() - t0, 2)

        # --- STAGE 4: CRITIC CHAIN ---
        st.session_state.pipeline_step = 4
        render_pipeline_tracker(4, tracker_placeholder)
        t0 = time.time()
        
        with st.status("🧐 Active Agent: Quality Assurance auditor...", expanded=True) as status:
            log_agent_activity("Critic Chain", "Running verification algorithms.")
            st.write("Validating citations, structural alignment, and clarity filters...")
            
            feedback_result = critic_chain.invoke({"report": st.session_state.state['report']})
            st.session_state.state["feedback"] = feedback_result if feedback_result is not None else "No feedback received."
            log_agent_activity("Critic Chain", "Auditing complete. Review finalized.")
            status.update(label="🧐 Critic Chain: Phase Complete!", state="complete", expanded=False)
            
        st.session_state.execution_times["Critic Chain"] = round(time.time() - t0, 2)
        
    st.session_state.execution_times["Total Duration"] = round(time.time() - start_total_time, 2)
    st.session_state.pipeline_step = 5
    st.session_state.is_researching = False
    
    # Complete state visual
    render_pipeline_tracker(5, tracker_placeholder)
    st.success("🎉 Multi-Agent Orchestration complete! Results mapped below.")

# ==========================================
# 7. PERFORMANCE & ANALYTICS VISUALS
# ==========================================
if st.session_state.state["report"]:
    st.markdown("### 📊 Engine Telemetry")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    
    with col_t1:
        st.markdown(f"""
        <div class="agent-card">
            <span class="badge badge-search">Search Phase</span>
            <div class="metric-value">{st.session_state.execution_times.get('Search Agent', 'N/A')}s</div>
            <div class="metric-label">Latency</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""
        <div class="agent-card">
            <span class="badge badge-reader">Scraper Phase</span>
            <div class="metric-value">{st.session_state.execution_times.get('Reader Agent', 'N/A')}s</div>
            <div class="metric-label">Latency</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown(f"""
        <div class="agent-card">
            <span class="badge badge-writer">Synthesizer Phase</span>
            <div class="metric-value">{st.session_state.execution_times.get('Writer Chain', 'N/A')}s</div>
            <div class="metric-label">Latency</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t4:
        st.markdown(f"""
        <div class="agent-card">
            <span class="badge badge-critic" style="background-color:rgba(139, 92, 246, 0.15); color:#a78bfa; border:1px solid rgba(139, 92, 246, 0.3)">Total Loop</span>
            <div class="metric-value">{st.session_state.execution_times.get('Total Duration', 'N/A')}s</div>
            <div class="metric-label">Elapsed Time</div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # 8. MULTI-TAB WORKSPACE INTERFACE
    # ==========================================
    res_tab1, res_tab2, res_tab3, res_tab4, res_tab5 = st.tabs([
        "📝 Compiled Research Report", 
        "🧐 Editorial Audit", 
        "🔍 Search Intelligence Cache", 
        "📖 Raw Scrape Data", 
        "📟 Kernel Event Logs"
    ])

    with res_tab1:
        st.markdown("### Workspace Document Editor")
        st.caption("Review output markdown, or enable manual correction mode inside the active text area.")
        
        enable_editor = st.checkbox("✍️ Activate Manual Document Editor")
        if enable_editor:
            corrected_input = st.text_area("Live Markdown Document Editor", st.session_state.state["report"], height=550)
            if corrected_input != st.session_state.state["report"]:
                st.session_state.state["report"] = corrected_input
                st.toast("Document updated in session state memory!")
        else:
            st.markdown('<div class="agent-card" style="background:rgba(15,23,42,0.25);">', unsafe_allow_html=True)
            st.markdown(st.session_state.state["report"])
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.divider()
        
        # Download utilities
        doc_topic = topic if topic else "Agentic_Research"
        st.download_button(
            label="💾 Download Generated Markdown Dossier",
            data=st.session_state.state["report"],
            file_name=f"{doc_topic.lower().replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True
        )

    with res_tab2:
        st.markdown("### Editorial Critique & Action Items")
        st.markdown('<div class="agent-card" style="border-left: 5px solid #ef4444;">', unsafe_allow_html=True)
        st.markdown(st.session_state.state["feedback"])
        st.markdown('</div>', unsafe_allow_html=True)

    with res_tab3:
        st.markdown("### Discoveries cached by Search Agent")
        st.text_area("Search Context Buffer", value=st.session_state.state["search_results"], height=450, disabled=True)

    with res_tab4:
        st.markdown("### Scraping Results retrieved by Reader Agent")
        st.text_area("HTML Scraping Buffer", value=st.session_state.state["reader_results"], height=450, disabled=True)

    with res_tab5:
        st.markdown("### Terminal Emulated Live Execution Stream")
        log_html = '<div class="terminal-window">'
        for entry in st.session_state.state["logs"]:
            log_html += f"<div>{entry}</div>"
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)

elif not start_research and not st.session_state.state["report"]:
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: rgba(30, 41, 59, 0.3); border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1); margin-top: 20px;">
        <h3 style="color: #94a3b8; font-weight: 500; margin-bottom: 8px;">System is Ready</h3>
        <p style="color: #64748b; margin: 0;">Specify a research topic in the text field above and click <b>Execute Autonomous Pipeline</b> to engage the agents.</p>
    </div>
    """, unsafe_allow_html=True)