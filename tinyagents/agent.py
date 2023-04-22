import openai
import os
import re

from executor import (
    run_executor,
    create_actions_prompt,
    DuckDuckGo,
    Wikipedia,
    SimpleEvaluator,
)


openai.api_key = os.environ.get("OPENAI_API_KEY")


class Stats:
    def __init__(self):
        self.usage = {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}

    def __call__(self, completion):
        self.usage["completion_tokens"] += completion.usage.completion_tokens
        self.usage["prompt_tokens"] += completion.usage.prompt_tokens
        self.usage["total_tokens"] += completion.usage.total_tokens
        return completion


class LLM:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
        self.stats = Stats()

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )
        self.stats(completion)
        return completion.choices[0].message.content


SYSTEM_PROMPT_PREAMBLE = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

# Available actions
""".strip()


EXAMPLE_SESSION = """
Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: `wikipedia('France')`
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris
""".strip()


action_re = re.compile("^Action: (.*)$")


class Agent:
    def __init__(self, supported_executors):
        self.executors = supported_executors
        self.max_turns = 5
        init_prompt = self.initial_prompt()
        self.llm = LLM(init_prompt)

    def initial_prompt(self):
        return (
            SYSTEM_PROMPT_PREAMBLE
            + create_actions_prompt(self.executors)
            + EXAMPLE_SESSION
        )

    def __call__(self, query):
        i = 0
        next_prompt = query
        while i < self.max_turns:
            i += 1
            result = self.llm(next_prompt)
            print(f"{result} \n")
            actions = [
                action_re.match(a) for a in result.split("\n") if action_re.match(a)
            ]
            if actions:
                # There is an action to run
                action = actions[0].groups(0)
                observation = run_executor(action[0], self.executors)
                print(f"Observation: {observation} \n")
                next_prompt = f"Observation: {observation}"
            else:
                return


if __name__ == "__main__":
    executors = [DuckDuckGo(), Wikipedia(), SimpleEvaluator()]
    agent = Agent(executors)
    # agent("what is the height of the 2nd tallest building in the world?")
    agent(
        "what is the height of the 2nd tallest building in the world? and what does wikipedia say about it?"
    )
