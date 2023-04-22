# TinyAgents

TinyAgents is a tiny framework that simplifies the interaction between a LLM like GPT-3 and various external data sources. 
This is going to be a small playground for me to experiment with different ideas and approaches to the problem of building a LLM that can interact with the world.
TinyAgents also includes an "agent" abstraction that makes calls to the LLM in a loop and uses a chain of thought prompting approach.

## Design
TinyAgents is opinionated makes a few choices:
- openai for llm, openai for embeddings
- chromadb for storing data/embeddings
- llm calls are cheap, compute is cheap, memory is cheap


## Features
- Memory module for storing and retrieving information at different levels (L1, L2, L3).
- Connector abstraction to interact with external data sources like notes, and web searches.
- PromptComposer to create prompts for LLM using data from memory and connectors.
- Chain of thought prompting based on the following format:
  - Thought: What the LLM thinks is the user intention
  - Action: External executors that LLM can call and retrieve results from
  - Observation: The result we got
- Agent abstraction that interacts with the LLM in a loop until enough information is gathered to produce the final output.

## Note
Not a library, just a playground. Fork and play with it.

## Inspiration
- langchain
- babyagi
- gpt plugins
