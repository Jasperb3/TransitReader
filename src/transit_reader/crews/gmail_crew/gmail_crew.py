from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from transit_reader.tools.gmail_tool_with_attachment import GmailAttachmentTool
from transit_reader.utils.models import Email
from transit_reader.utils.llm_manager import get_llm_for_agent
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class GmailCrew():
	"""GmailCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def email_writing_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['email_writing_agent'],
			llm=get_llm_for_agent('email_writer'),
			verbose=True
)

	@agent
	def gmail_draft_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['gmail_draft_agent'],
			tools=[GmailAttachmentTool()],
			llm=get_llm_for_agent('email_drafter'),
			verbose=True
)

	@task
	def email_writing_task(self) -> Task:
		return Task(
			config=self.tasks_config['email_writing_task'],
			output_pydantic=Email
		)

	@task
	def gmail_draft_task(self) -> Task:
		return Task(
			config=self.tasks_config['gmail_draft_task']
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the GmailCrew crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			cache=True
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
