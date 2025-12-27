# Neuro-Distributed-Network (NDN)

A research framework for distributed metacognitive orchestration across heterogeneous hardware.

## Research Thesis
NDN explores "System 1 vs. System 2" thinking by routing cognitive tasks across an asymmetric hardware cluster. By mimicking the functional separation of the human brain, we aim to optimize for both inference speed and reasoning depth in agentic systems.

## Hardware Topology
- **Orchestrator:** MacBook Air (M-series) - *The Frontal Lobe*
- **Primary Cortex:** RTX A4000 Workstation - *The Slow-Thinking Reasoning Node*
- **Cerebellum:** GTX 1660 Ti (Lenovo Legion) - *The Fast-Thinking Reactive Node*

## Connectivity
- **Network:** Tailscale Mesh VPN
- **Inference Server:** Ollama (Port 11434)
- **Binding:** `OLLAMA_HOST=0.0.0.0`

## Repository Structure
- `/orchestrator`: Node management and routing logic.
- `/reasoning_engine`: Implementation of MCTS and cognitive search.
- `/nodes`: Node-specific configuration and health checks.
- `/experiments`: Benchmarking scripts for ICML reproducibility.