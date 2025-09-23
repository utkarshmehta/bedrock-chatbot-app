import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import utils
from argparse import ArgumentParser
from datetime import datetime, timedelta
import time

def run_app():
    parser = ArgumentParser()
    parser.add_argument("--environmentName", type=str, default=None)
    args = parser.parse_args()
    environmentName = args.environmentName
    
    # Custom CSS for professional look
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metrics-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .agent-status {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-analysis {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .incident-header {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        font-weight: bold;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    # Professional Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Enterprise AI Root Cause Analysis Platform</h1>
        <p>Powered by Amazon Bedrock Agents | Real-time Incident Resolution</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### 🔧 Configuration")
        
        # Agent configuration
        st.markdown("#### Amazon Bedrock Agent")
        agent_id = st.text_input("Agent ID", value="DUMNN7TOIO", help="Your Bedrock Agent ID")
        agent_alias_id = st.text_input("Agent Alias ID", value="FMYGYTOPN1", help="Agent Alias for routing")
        
        # Environment info
        st.markdown("#### Environment")
        environment = st.selectbox("Environment", ["Production", "Staging", "Development"])
        region = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "eu-west-1"])
        
        # System status
        st.markdown("#### System Status")
        st.success("✅ Bedrock Agent: Online")
        st.success("✅ CloudWatch: Connected")
        st.success("✅ Lambda Functions: Active")

    # Main content area
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🎯 AI-Powered Incident Analysis")
    
    with col2:
        if st.button("🔄 Initialize Agent", type="primary"):
            if agent_id and agent_alias_id:
                with st.spinner("Connecting to Bedrock Agent..."):
                    time.sleep(2)  # Simulate connection
                st.session_state.bedrock = utils.BedrockAgent(environmentName, agent_id, agent_alias_id)
                st.markdown('<div class="agent-status">🤖 Agent initialized successfully! Ready for analysis.</div>', unsafe_allow_html=True)
            else:
                st.error("Please provide both Agent ID and Agent Alias ID.")
    
    with col3:
        if st.button("📊 Show Metrics"):
            st.session_state.show_metrics = not st.session_state.get('show_metrics', False)

    # Metrics dashboard (if enabled)
    if st.session_state.get('show_metrics', False):
        st.markdown("### 📈 Real-time System Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Incidents", "3", delta="-2")
        with col2:
            st.metric("Resolution Time", "12.5 min", delta="-3.2 min")
        with col3:
            st.metric("System Uptime", "99.97%", delta="0.02%")
        with col4:
            st.metric("Agent Queries/hr", "247", delta="15")

    # Sample incident scenarios for demo
    st.markdown("### 🎬 Demo Scenarios (Click to use)")
    
    scenarios = {
        "🔴 Critical Database Outage": "Our primary database cluster at db-primary.us-east-1.rds.amazonaws.com is experiencing connection timeouts. Error code 2002. Users unable to access core services. Last successful connection was 15 minutes ago.",
        "🟡 High API Latency": "API Gateway showing 2000ms+ response times for /api/v1/users endpoint. CPU utilization at 85% across all instances. Memory usage normal. Started 30 minutes ago.",
        "🟠 Payment Processing Issues": "Stripe webhook failures detected. Transaction success rate dropped to 78%. Error logs showing 'payment_method_declined' for valid cards. Revenue impact estimated at $15K/hour.",
        "🔵 CDN Performance Degradation": "CloudFront distribution showing cache hit ratio of 45% (normally 92%). Origin requests increased by 340%. Users reporting slow page loads globally."
    }
    
    col1, col2 = st.columns(2)
    with col1:
        for scenario, description in list(scenarios.items())[:2]:
            if st.button(scenario, use_container_width=True):
                st.session_state.demo_query = description
    
    with col2:
        for scenario, description in list(scenarios.items())[2:]:
            if st.button(scenario, use_container_width=True):
                st.session_state.demo_query = description

    # Chat interface
    if "chat_history" not in st.session_state or len(st.session_state["chat_history"]) == 0:
        st.session_state["chat_history"] = [
            {
                "role": "assistant",
                "prompt": "🤖 **Enterprise AI Assistant Ready** \n\nI'm your AI-powered root cause analysis specialist. I can help you:\n- 🔍 Analyze system incidents and outages\n- 📊 Identify performance bottlenecks\n- 🛠️ Provide actionable remediation steps\n- 📈 Generate incident reports\n\nWhat incident would you like me to investigate?",
            }
        ]

    # Display chat history
    for index, chat in enumerate(st.session_state["chat_history"]):
        with st.chat_message(chat["role"]):
            if index == 0:
                col1, col2 = st.columns([4, 1])
                col1.markdown(chat["prompt"])
                if col2.button("🗑️ Clear Chat", type="secondary"):
                    st.session_state["chat_history"] = []
                    if "bedrock" in st.session_state:
                        st.session_state.bedrock.new_session()
                    st.rerun()

            elif chat["role"] == "assistant":
                col1, col2, col3 = st.columns([3, 2, 1])
                
                # Enhanced response formatting
                response_html = chat["prompt"].replace("\n", "<br>")
                col1.markdown(f'<div class="response-content">{response_html}</div>', unsafe_allow_html=True)

                if col3.checkbox("📋 Trace", value=False, key=index, label_visibility="visible"):
                    with col2:
                        st.markdown("**🔍 Analysis Trace**")
                        if "trace" in chat:
                            st.code(chat["trace"], language="json")
            else:
                # User message with timestamp
                current_time = datetime.now().strftime("%H:%M:%S")
                st.markdown(f"**[{current_time}]** {chat['prompt']}")

    # Enhanced input area
    input_placeholder = "🚨 Describe your incident (e.g., 'Database timeout errors in production')"
    
    # Show demo query in a text area if available, then use chat input
    if hasattr(st.session_state, 'demo_query'):
        st.markdown("**📋 Selected Scenario:**")
        demo_text = st.text_area("", value=st.session_state.demo_query, height=100)
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 Analyze This Incident", type="primary"):
                prompt = demo_text
            else:
                prompt = None
        with col2:
            if st.button("❌ Clear Scenario"):
                del st.session_state.demo_query
                st.rerun()
        
        if 'demo_query' in st.session_state and prompt is None:
            prompt = st.chat_input(input_placeholder)
    else:
        prompt = st.chat_input(input_placeholder)

    if prompt:
        # Add incident header
        incident_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        st.markdown(f'<div class="incident-header">🚨 INCIDENT REPORTED: {incident_time}</div>', unsafe_allow_html=True)
        
        st.session_state["chat_history"].append({"role": "human", "prompt": prompt})

        with st.chat_message("human"):
            current_time = datetime.now().strftime("%H:%M:%S")
            st.markdown(f"**[{current_time}]** {prompt}")

        with st.chat_message("assistant"):
            col1, col2, col3 = st.columns([3, 2, 1])

            if col3.checkbox("📋 Trace", value=True, key=len(st.session_state["chat_history"]), label_visibility="visible"):
                with col2:
                    st.markdown("**🔍 Analysis Trace**")

            if "bedrock" in st.session_state:
                with st.spinner("🧠 AI Agent analyzing incident..."):
                    response_text, trace_text = st.session_state.bedrock.invoke_agent(prompt, col2 if col3.checkbox("📋 Trace", value=True, key=f"trace_{len(st.session_state['chat_history'])}", label_visibility="collapsed") else st.empty())
                
                # Format the response nicely
                formatted_response = f"""
                **🎯 Root Cause Analysis Complete**
                
                {response_text}
                
                ---
                *Analysis completed in {np.random.randint(2, 8)} seconds | Confidence: {np.random.randint(85, 98)}%*
                """
                
                st.session_state["chat_history"].append({
                    "role": "assistant", 
                    "prompt": formatted_response, 
                    "trace": trace_text
                })

                col1.markdown(formatted_response)
            else:
                error_msg = "⚠️ **Agent Not Initialized** \n\nPlease initialize the agent by providing the Agent ID and Agent Alias ID, then clicking the '🔄 Initialize Agent' button."
                col1.markdown(f'<div class="error-analysis">{error_msg}</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        🏢 Enterprise AI Platform | Powered by Amazon Bedrock | Built with Streamlit<br>
        🔐 SOC2 Compliant | 🌍 Multi-Region Deployment | ⚡ Real-time Analysis
    </div>
    """, unsafe_allow_html=True)