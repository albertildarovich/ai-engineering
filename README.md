# AI Engineering & Agent Development

A hands-on learning project focused on understanding and building AI-powered applications and autonomous agents using Python and Large Language Models (LLMs).

The project explores the core concepts of AI Engineering, from basic LLM integration to stateful agents capable of executing tools, managing conversation history, and recovering from interruptions.

## 🎯 Project Goals

- Understand how Large Language Models work through API integration.
- Learn prompt engineering and structured LLM outputs.
- Build AI agents with tool-calling capabilities.
- Implement multi-step agent execution loops.
- Manage agent state and conversation history.
- Implement state persistence and recovery mechanisms.
- Explore the architecture behind reliable AI agent applications.

## 🛠 Tech Stack

- **Python** — application logic and agent implementation
- **Ollama** — local LLM inference
- **Qwen 3 (1.7B)** — language model
- **FastAPI** — planned backend integration
- **Pydantic** — data validation and structured outputs
- **HTTPX** — asynchronous HTTP requests
- **JSON** — initial agent state persistence

## 📚 Learning Progress

### 1. LLM Integration
- Connecting Python applications to local LLMs through Ollama.
- Sending messages and processing model responses.
- Understanding system, user, and assistant roles.

### 2. Prompt Engineering
- Designing system prompts.
- Managing conversation history.
- Controlling model behavior through instructions.

### 3. Structured Outputs
- Generating structured JSON responses.
- Defining data schemas with Pydantic.
- Validating LLM-generated data.

### 4. Tool Calling
- Defining tools using function schemas.
- Executing Python functions requested by an LLM.
- Processing tool results and returning them to the model.

### 5. Multi-step Agent Loop
- Implementing iterative agent execution.
- Supporting multiple tool calls.
- Managing interactions between the LLM and external tools.

### 6. Agent State Management
- Designing a structured agent state.
- Tracking messages, iterations, tool results, and execution status.
- Managing state transitions.

### 7. Persistence & Recovery
- Saving and loading agent state.
- Implementing execution checkpoints.
- Tracking completed tool calls.
- Recovering interrupted agent execution.
- Resuming agents from saved state.

### 8. Upcoming Topics
- Idempotency and duplicate execution prevention.
- Agent architecture and modular design.
- Planning and reasoning.
- Short-term and long-term memory.
- Embeddings and vector databases.
- Retrieval-Augmented Generation (RAG).
- LangGraph and multi-agent systems.

## 📁 Project Structure

```text
ai-engineering/
├── app/
│   ├── main.py
│   ├── agent_state.py
│   ├── state_storage.py
│   └── multi_step_agent.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

*The project structure will evolve as new concepts and components are implemented.*

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Ollama installed
- Git

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-engineering
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the language model

```bash
ollama pull qwen3:1.7b
```

### 5. Run the application

```bash
python -m app.main
```

## 🧠 Learning Approach

This repository is developed incrementally through practical implementation.

Each topic focuses on understanding the underlying concepts, implementing them in Python, testing the behavior, and gradually improving the architecture.

The goal is to build a solid foundation for developing production-ready AI applications and autonomous agents.

## 📌 Project Status

**In active development.**

This