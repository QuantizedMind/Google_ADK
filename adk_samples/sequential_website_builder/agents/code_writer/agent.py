import os
import sys
from google.adk.agents import LlmAgent

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file
from tools.file_writer_tool import write_to_file

code_writer_agent = LlmAgent(
    name="code_writer_agent",
    model="gemini-2.5-flash",
    instruction=load_instructions_file("agents/code_writer/instructions.txt"),
    description=load_instructions_file("agents/code_writer/description.txt"),
    tools=[write_to_file]
)