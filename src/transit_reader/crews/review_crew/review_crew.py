import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from transit_reader.tools.google_search_tool import GoogleSearchTool
from transit_reader.tools.gemini_search_tool import GeminiSearchTool
from transit_reader.tools.qdrant_search_tool import QdrantSearchTool
from transit_reader.tools.linkup_search_tool import LinkUpSearchTool
from transit_reader.utils.constants import TIMESTAMP
from dotenv import load_dotenv

load_dotenv()

google_search_tool = GoogleSearchTool(api_key=os.getenv("GOOGLE_SEARCH_API_KEY"), cx=os.getenv("SEARCH_ENGINE_ID"))

gpt41 = LLM(
	model="gpt-4.1",
	api_key = os.getenv("OPENAI_API_KEY"),
	temperature=0.7
)

gpt41mini = LLM(
	model="gpt-4.1-mini",
	api_key = os.getenv("OPENAI_API_KEY"),
	temperature=0.7
)

gemini_flash = LLM(
	model="gemini/gemini-2.5-flash-preview-04-17",
	api_key = os.getenv("GEMINI_API_KEY"),
	temperature=0.7
)


@CrewBase
class ReviewCrew():
	"""ReviewCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def report_critic(self) -> Agent:
		return Agent(
			config=self.agents_config['report_critic'],
			llm=gemini_flash,
			verbose=True
		)

	@agent
	def report_enhancer(self) -> Agent:
		return Agent(
			config=self.agents_config['report_enhancer'],
			llm=gpt41,
			tools=[google_search_tool, GeminiSearchTool(), QdrantSearchTool(), LinkUpSearchTool()],
			verbose=True
		)

	@task
	def report_review_task(self) -> Task:
		return Task(
			config=self.tasks_config['report_review_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/report_review_task.md"
		)

	@task
	def report_enhancement_task(self) -> Task:
		return Task(
			config=self.tasks_config['report_enhancement_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/report_enhancement_task.md"
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ReviewCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
