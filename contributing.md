# AI Agent Instructions & Coding Standards

## 1. Architectural Principles
- **Modularity:** Keep node-specific logic separate from the central orchestrator.
- **Fail-Safe Routing:** If a remote node is unreachable, the orchestrator must default to a local mock or a timeout.
- **JSON-Only Communication:** All inter-node communication must strictly follow the Ollama API schema.

## 2. Python Standards
- Use `pydantic` for data validation of node responses.
- All network calls must include a `timeout` parameter to prevent hanging the cluster.
- Use asynchronous programming (`asyncio`/`httpx`) for the orchestrator to manage multiple nodes simultaneously.

## 3. Documentation Requirements
- Every new function must include a docstring explaining its "Cognitive Role" (e.g., "Acts as a gating mechanism for logic verification").