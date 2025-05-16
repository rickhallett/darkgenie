# Project Overview: Programmable Claude Code

This repository serves as a comprehensive demonstration and toolkit for leveraging "Claude Code," Anthropic's programmable AI coding assistant. It showcases how to interact with Claude Code programmatically using various languages (Shell, Python, JavaScript) and contrasts its capabilities with Aider, another AI coding tool. The core idea is to illustrate the power of using natural language to instruct AI tools to perform complex coding tasks, including file manipulation, command execution, and even integration with external services like Notion.

## High-Level Understanding

The project aims to:

1.  **Educate:** Show users how to go beyond simple chat interactions with AI coding assistants and use them as programmable tools within automated workflows.
2.  **Demonstrate:** Provide concrete examples of Claude Code's capabilities, such as creating scripts, building small applications (e.g., a CLI todo app), and interacting with APIs.
3.  **Compare:** Offer parallel examples using Aider to highlight different approaches to AI-assisted development.
4.  **Explore Advanced Use Cases:** Showcase more complex scenarios like voice control for Claude Code and integration with Notion for task management.

## Most Important Bits for Newcomers

If you're new to this codebase, here's where to start:

1.  **`README.md`**: This is your primary guide. It explains the project's purpose, setup instructions, and provides a description of each key file. Pay close attention to the "Quick Start" and "File Descriptions" sections.
2.  **Simple Examples (the `_1` scripts):**
    *   `claude_code_is_programmable_1.sh`: A very basic shell script showing how to call the Claude Code CLI to generate a "hello.js" file. This demonstrates the fundamental concept.
    *   `aider_is_programmable_1.sh`: The Aider equivalent to the above, useful for comparison.
3.  **Core Demonstrations (the `_2` scripts):**
    *   `claude_code_is_programmable_2.py` (Python) and `claude_code_is_programmable_2.js` (JavaScript): These scripts demonstrate a more practical use case – creating a TypeScript CLI todo application using Claude Code. They showcase the use of more tools like `Edit`, `Replace`, `Bash`, and `Create`.
    *   `aider_is_programmable_2.py` and `aider_is_programmable_2.js`: Aider equivalents for creating the TypeScript todo app, often including git operations.
4.  **`anthropic_search.py`**: A standalone Python script that demonstrates Claude AI's web search capabilities. This is a useful utility in itself.

## Experimental or Demonstrable Parts

These parts showcase more advanced or proof-of-concept functionalities:

1.  **`voice_to_claude_code.py`**: This is a significant feature that enables voice interaction with Claude Code. It uses RealtimeSTT for speech recognition and OpenAI TTS for voice output. While powerful, it involves more dependencies and setup, positioning it as a more advanced demonstration.
2.  **Notion Integration (`claude_code_is_programmable_3.py` and scripts in `bonus/`):**
    *   `claude_code_is_programmable_3.py`: Integrates Claude Code with the Notion API for todo management. This shows how Claude Code can be used to interact with external services.
    *   `bonus/starter_notion_agent.py`: A template for building a Notion agent with the OpenAI Agent SDK.
    *   `bonus/claude_code_inside_openai_agent_sdk_4_bonus.py`: A more complex example embedding Claude Code within the OpenAI Agent SDK for Notion tasks. These are more experimental and geared towards developers looking to build sophisticated agentic systems.
3.  **MCP (Multi-call Protocol) Configuration (`.mcp.sample.json`):** This is related to the Notion integration and represents a more advanced setup for enabling Claude Code to work with specific APIs through a standardized protocol.

## Main Workflow

The "main workflow" depends on what you're trying to achieve, but generally follows these patterns:

1.  **Direct CLI Interaction (Demonstrated by `.sh` scripts):**
    *   Formulate a natural language prompt describing the coding task.
    *   Use the `claude` CLI tool, specifying the prompt and allowed tools.
    *   Claude Code processes the request and (typically) creates or modifies files.

2.  **Programmatic Control (Demonstrated by `.py` and `.js` scripts):**
    *   Write a script (Python or JavaScript) that defines a task for Claude Code.
    *   This script constructs a prompt (often incorporating context or variables).
    *   It then calls the `claude` CLI as a subprocess.
    *   The script can then process Claude Code's output or observe its effects (e.g., new files created).

3.  **Voice-Driven Workflow (`voice_to_claude_code.py`):**
    *   Run the `voice_to_claude_code.py` script.
    *   Speak your command, including a trigger word (e.g., "Claude, create a Python script...").
    *   The script transcribes your speech to text.
    *   The transcribed text is passed to Claude Code (similar to the programmatic control workflow).
    *   Claude Code's textual response is converted back to speech and played.

4.  **Web Search (`anthropic_search.py`):**
    *   Run the script with a search query.
    *   The script uses Claude AI with its web search tool to find information.
    *   Results are displayed in the console.

**Setup is Crucial:** Regardless of the workflow, ensure you've followed the setup instructions in `README.md`, especially regarding API keys (`.env` file) and potentially the MCP configuration (`.mcp.json`) if you're exploring Notion integration.

This repository is rich with examples. Start with the simpler ones and gradually explore the more complex demonstrations to fully grasp the potential of programmable AI coding assistants. 