import streamlit as st
import os
from botocore.config import Config
from boto3.session import Session
import uuid
import json
from datetime import datetime


class BedrockAgent:
    """BedrockAgent class for invoking an Anthropic AI agent.

    This class provides a wrapper for invoking an AI agent hosted on Anthropic's
    Bedrock platform. It handles authentication, session management, and tracing
    to simplify interacting with a Bedrock agent.

    Usage:

    agent = BedrockAgent()
    response, trace = agent.invoke_agent(input_text)

    The invoke_agent() method sends the input text to the agent and returns
    the agent's response text and trace information.

    Trace information includes the agent's step-by-step reasoning and any errors.
    This allows visibility into how the agent came up with the response.

    The class initializes session state and authentication on first run. It
    reuses the session for subsequent calls for continuity.

    Requires streamlit and boto3. Authentication requires credentials configured
    in secrets management.
    """

    def __init__(self, environmentName, agent_id, agent_alias_id, region='us-east-1') -> None:
        # Allow region to be passed as parameter or get from environment
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        
        if "BEDROCK_RUNTIME_CLIENT" not in st.session_state:
            try:
                st.session_state["BEDROCK_RUNTIME_CLIENT"] = Session().client(
                    "bedrock-agent-runtime", 
                    config=Config(read_timeout=600, retries={'max_attempts': 3}),
                    region_name=self.region,
                )
                st.success(f"✅ Bedrock client initialized in region: {self.region}")
            except Exception as e:
                st.error(f"❌ Failed to initialize Bedrock client: {str(e)}")
                raise

        if "SESSION_ID" not in st.session_state:
            st.session_state["SESSION_ID"] = str(uuid.uuid1())

        self.agent_id = agent_id
        self.agent_alias_id = agent_alias_id
        
        # Validate agent configuration
        self._validate_agent()

    def _validate_agent(self):
        """Validate that the agent exists and is accessible"""
        try:
            # Test if we can access the agent (this will fail if agent doesn't exist)
            st.info(f"🔍 Validating agent: {self.agent_id} with alias: {self.agent_alias_id}")
            
        except Exception as e:
            st.error(f"❌ Agent validation failed: {str(e)}")
            st.error("Please check:")
            st.error("1. Agent ID is correct")
            st.error("2. Agent Alias ID is correct") 
            st.error("3. Agent is in the same region as your application")
            st.error("4. IAM permissions allow bedrock:InvokeAgent")
            raise

    def _serialize_trace_data(self, obj):
        """Custom JSON serializer for trace data that handles datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_trace_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_trace_data(item) for item in obj]
        else:
            return obj

    def new_session(self):
        st.session_state["SESSION_ID"] = str(uuid.uuid1())
        st.info(f"🔄 New session started: {st.session_state['SESSION_ID']}")

    def invoke_agent(self, input_text, trace):
        response_text = ""
        trace_text = ""
        step = 0

        try:
            st.info(f"🚀 Invoking agent {self.agent_id} with alias {self.agent_alias_id}")
            
            response = st.session_state["BEDROCK_RUNTIME_CLIENT"].invoke_agent(
                inputText=input_text,
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=st.session_state["SESSION_ID"],
                enableTrace=True,
            )

            for event in response["completion"]:
                if "chunk" in event:
                    data = event["chunk"]["bytes"]
                    response_text = data.decode("utf8")

                elif "trace" in event:
                    trace_obj = event["trace"]["trace"]

                    if "orchestrationTrace" in trace_obj:
                        # Clean trace data before JSON serialization
                        clean_trace = self._serialize_trace_data(trace_obj["orchestrationTrace"])
                        trace_dump = json.dumps(clean_trace, indent=2)

                        if "rationale" in trace_obj["orchestrationTrace"]:
                            step += 1
                            trace_text += f'\n\n\n---------- Step {step} ----------\n\n\n{trace_obj["orchestrationTrace"]["rationale"]["text"]}\n\n\n'
                            trace.markdown(
                                f'\n\n\n---------- Step {step} ----------\n\n\n{trace_obj["orchestrationTrace"]["rationale"]["text"]}\n\n\n'
                            )

                        elif (
                            "modelInvocationInput"
                            not in trace_obj["orchestrationTrace"]
                        ):
                            trace_text += "\n\n\n" + trace_dump + "\n\n\n"
                            trace.markdown("\n\n\n" + trace_dump + "\n\n\n")

                    elif "failureTrace" in trace_obj:
                        clean_trace = self._serialize_trace_data(trace_obj["failureTrace"])
                        trace_dump = json.dumps(clean_trace, indent=2)
                        trace_text += "\n\n\n" + trace_dump + "\n\n\n"
                        trace.markdown("\n\n\n" + trace_dump + "\n\n\n")

                    elif "postProcessingTrace" in trace_obj:
                        step += 1
                        clean_response = self._serialize_trace_data(trace_obj['postProcessingTrace']['modelInvocationOutput']['parsedResponse']['text'])
                        trace_text += f"\n\n\n---------- Step {step} ----------\n\n\n{json.dumps(clean_response, indent=2)}\n\n\n"
                        trace.markdown(
                            f"\n\n\n---------- Step {step} ----------\n\n\n{json.dumps(clean_response, indent=2)}\n\n\n"
                        )

        except Exception as e:
            error_msg = str(e)
            trace_text += f"❌ Error: {error_msg}"
            trace.error(f"❌ Error invoking agent: {error_msg}")
            
            # Provide specific troubleshooting based on error type
            if "ResourceNotFoundException" in error_msg:
                trace.error("🔍 **Troubleshooting ResourceNotFoundException:**")
                trace.error("1. Verify Agent ID is correct")
                trace.error("2. Verify Agent Alias ID is correct")
                trace.error("3. Check if agent is in the correct AWS region")
                trace.error("4. Ensure agent status is PREPARED")
                trace.error("5. Check IAM permissions for bedrock:InvokeAgent")
            elif "AccessDeniedException" in error_msg:
                trace.error("🔐 **Access Denied:** Check IAM permissions")
            
            raise Exception(f"Agent invocation failed: {error_msg}")

        return response_text, trace_text