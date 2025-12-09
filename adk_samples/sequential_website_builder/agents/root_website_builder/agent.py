from google.adk.agents import SequentialAgent
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.file_loader import load_instructions_file
from agents.requirements_writer.agent import requirements_writer_agent
from agents.designer.agent import designer_agent
from agents.code_writer.agent import code_writer_agent

root_agent = SequentialAgent(
    name="root_website_builder_agent",
    sub_agents=[
        requirements_writer_agent,
        designer_agent,
        code_writer_agent
    ],
    description=load_instructions_file("agents/root_website_builder/description.txt"),
)