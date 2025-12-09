import os
import sys
from google.adk.agents import LlmAgent

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file

designer_agent = LlmAgent(
    name="designer_agent",
    model="gemini-2.5-flash",
    instruction=load_instructions_file("agents/designer/instructions.txt"),
    description=load_instructions_file("agents/designer/description.txt"),
    output_key="designer_output"
)