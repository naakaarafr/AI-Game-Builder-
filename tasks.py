from crewai import Task
from textwrap import dedent

class GameBuilderTasks:
    def code_task(self, agent, game_instructions):
        return Task(
            description=dedent(f"""
                You will create a game using python, these are the instructions:
                Instructions
                ------------
                {game_instructions}
                
                IMPORTANT: Keep your response concise to reduce API usage.
                Focus on creating functional, working code without excessive comments.
            """),
            expected_output="Your Final answer must be the full python code, only the python code and nothing else.",
            agent=agent
        )

    def review_task(self, agent, game_instructions):
        return Task(
            description=dedent(f"""
                You will create a game using python, these are the instructions:
                Instructions
                ------------
                {game_instructions}
                
                Using the code you got, check for errors. Check for logic errors,
                syntax errors, missing imports, variable declarations, mismatched brackets,
                and security vulnerabilities.
                
                IMPORTANT: Only fix actual errors. Do not make unnecessary changes.
                Keep your response concise to reduce API usage.
            """),
            expected_output="Your Final answer must be the full python code, only the python code and nothing else.",
            agent=agent
        )

    def evaluate_task(self, agent, game_instructions):
        return Task(
            description=dedent(f"""
                You are helping create a game using python, these are the instructions:
                Instructions
                ------------
                {game_instructions}
                
                You will look over the code to insure that it is complete and
                does the job that it is supposed to do.
                
                IMPORTANT: Only make changes if absolutely necessary for functionality.
                Keep your response concise to reduce API usage.
                The code should be working and complete.
            """),
            expected_output="Your Final answer must be the full python code, only the python code and nothing else.",
            agent=agent
        )