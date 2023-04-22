import httpx
import inspect
import re
from typing import Callable, List, Dict
from dataclasses import dataclass
from duckduckgo_search import ddg


@dataclass
class Executor:
    name: str
    description: str
    funcs: Dict[Callable, str]


def run_executor(action_string, executors):
    match = re.search(r"`([\w_]+)\((.*)\)`", action_string)
    if match:
        function_name = match.group(1)
        params_str = match.group(2)
        params = eval(f"[{params_str}]")
        for cls in executors:
            if hasattr(cls, function_name):
                function = getattr(cls, function_name)
                return function(*params)
        return "No actions found"


def create_actions_prompt(executors):
    actions = []
    for executor in executors:
        actions.append("## {}".format(executor.name))
        actions.append(
            f"You have the tool `{executor.name}` for {executor.description} with these functions:"
        )
        for func, description in executor.funcs.items():
            signature_str = f"{func.__name__}{inspect.signature(func)}"
            actions.append(f"`{signature_str}` - {description}")
        actions.append("")
    return "\n".join(actions)


class SimpleEvaluator(Executor):
    def __init__(self):
        self.name = "eval"
        self.description = "Evaluate a simple expression"
        self.funcs = {self.eval: "returns the result of evaluating the expression"}

    def eval(self, exp):
        return eval(exp)


class DuckDuckGo(Executor):
    def __init__(self):
        self.name = "duckduckgo"
        self.description = "Search with duckduckgo(ddg)"
        self.funcs = {self.ddg: "returns a list of result snippets"}

    def ddg(self, q):
        results = ddg(q, region="wt-wt", safesearch="moderate", time="y", max_results=5)
        if len(results) == 0:
            return "No good DuckDuckGo Search Result was found"
        snippets = [result["body"] for result in results]
        return " ".join(snippets)


class Wikipedia(Executor):
    def __init__(self):
        self.name = "wikipedia"
        self.description = "Search with wikipedia"
        self.funcs = {self.wiki: "returns a summary from searching Wikipedia"}

    def wiki(self, q):
        return httpx.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": q,
                "format": "json",
            },
        ).json()["query"]["search"][0]["snippet"]
