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
	model="gemini/gemini-2.5-flash",
	api_key = os.getenv("GEMINI_API_KEY"),
	temperature=0.7
)


@CrewBase
class NatalAnalysisReviewCrew():
	"""NatalAnalysisReviewCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@agent
	def natal_interpretation_critic(self) -> Agent:
		return Agent(
			config=self.agents_config['natal_interpretation_critic'],
			llm=gemini_flash,
			verbose=True
		)

	@agent
	def natal_interpretation_enhancer(self) -> Agent:
		return Agent(
			config=self.agents_config['natal_interpretation_enhancer'],
			llm=gpt41,
			verbose=True
		)

	@task
	def natal_interpretation_critic_task(self) -> Task:
		return Task(
			config=self.tasks_config['natal_interpretation_critic_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/natal_interpretation_critic_task.md"
		)

	@task
	def natal_interpretation_enhancement_task(self) -> Task:
		return Task(
			config=self.tasks_config['natal_interpretation_enhancement_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/natal_interpretation_enhancement_task.md"
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the NatalAnalysisReviewCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
