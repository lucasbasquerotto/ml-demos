# Math Agent Instructions for GitHub Copilot

## Project Overview
This project implements a simple, extensible agent that can process math and logical expressions using token trees. The agent can dynamically define new nodes/functions and use them in computations, with permissions controlling access to custom features. Only built-in Python packages are used.

## Extensibility
- Nodes and actions are represented as classes and registered in a central registry.
- The agent can define new nodes/functions when allowed, and use them in future computations.
- External tools/actions can be plugged in by registering new node types or functions.

## Permission System
- The agent has a permission flag to control whether it can create/use custom nodes/functions.
- When permission is revoked, custom nodes/functions are inaccessible.
- Built-in nodes/functions are always available.

## Guidelines for Improvement
- Add new node types by subclassing `Node` and registering them in the registry.
- Extend the agent to support more complex logic, introspection, or external actions.
- Improve the curriculum to unlock features adaptively based on agent performance.
- Keep all code compatible with built-in Python packages only.

## Examples
- See `main.py` for usage and demonstration.
- See `tokens.py` for node definitions and registry logic.
- See `agent.py` for agent implementation and permission control.
- See `curriculum.py` for adaptive progression and testing.

## Best Practices
- Keep the code simple and modular for easy extension.
- Document new features and update this instructions file as the project evolves.
