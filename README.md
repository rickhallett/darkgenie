# Dark Genie (First Circle): Voice-Activated Deep Research Engine

## 1. Project Overview

**[Dark Genie](https://youtu.be/Qx91ff77yzM?si=Rm9mEomU89bcDwmK)** is a project focused on enabling powerful, voice-activated deep research by programmatically orchestrating AI agents. The Minimum Viable Product (MVP) will allow a user to issue a voice query, which is then processed and delegated to Anthropic's Claude (via its API and web search tool) to conduct in-depth, iterative research by spawning multiple "research instances" or "agents." The resulting research reports will then undergo an AI-driven verification step for accuracy and to identify potential hallucinations before being automatically aggregated, named, and stored in the user's Google Drive.

This project combines a custom orchestration layer with the advanced capabilities of Claude's API and a secondary evaluator LLM to deliver comprehensive and verified research reports from simple voice commands.

Find the [initial PRD](docs/initial_prd.md) here.

Project status is available in the [tasks.md](docs/tasks.md) file.

A number of helper utilities are already in development:
- "[Maximised v0.1](explorer/maximized.py) | [o3 v0.1](explorer/o3.py)" - a set of tools for analysing folder structures, providing detailed statistics and suggestions for organisation improvement, heading towards a "search first" approach to file management. v1.0 will also provide the means to voice activate folder transmutation for automatic file management.

## 2. Purpose & Problem Solved

In a world of information overload, conducting truly deep research is time-consuming and often requires sifting through vast amounts of data from various sources. Standard web searches provide surface-level information, and while advanced AI web UIs offer impressive depth, they lack direct, programmatic API access to replicate that same extensive automated research process and often lack a transparent, secondary verification layer.

**Dark Genie aims to solve this by:**

*   **Automating Deep Research:** Allowing users to initiate complex research tasks through simple voice commands.
*   **Programmatic Control:** Providing a framework to spawn and manage multiple research "agents" (leveraging Claude's iterative web search) to achieve a specified depth and breadth.
*   **Bridging the API Gap:** Creating a practical solution for accessing deep, iterative AI research capabilities that are not currently available as a simple, direct API call from other major vendors for this specific, intensive use case.
*   **Enhancing Reliability:** Incorporating an AI-powered verification step to scrutinize initial research outputs for accuracy and potential hallucinations.
*   **Efficient Output Management:** Organizing and storing the comprehensive, verified research outputs directly into the user's Google Drive for easy access and use.

## 3. How It Works (MVP Workflow)

The core process flow for the Dark Genie MVP is envisioned as follows:

1.  **Voice Input:** The user issues a research query via a voice input mechanism.
2.  **Query Parsing & Parameterization (Custom Orchestration Layer):**
    *   The custom code layer receives the voice input.
    *   It parses the user's query to identify the core research topic, desired depth/scope (e.g., number of "agents" or iterations), any constraints, and the overall goal.
3.  **Query Optimization for Claude (Intermediary LLM):**
    *   The structured query and parameters are passed to an intermediary LLM.
    *   This LLM is pre-loaded with instructions on how to best formulate or "translate" the user's request into an optimal prompt for Claude's deep research (web search tool) capabilities.
4.  **Invoking Claude for Deep Research (Claude API):**
    *   The Claude-optimized query, along with parameters like the number of "agents" to spawn (which translates to the `max_uses` for the web search tool or separate, parallel invocations), is passed to the Claude API, specifically utilizing its `web_search` tool.
5.  **Iterative Research by Claude "Agents":**
    *   One or more instances of Claude perform the deep research. This involves autonomously generating search queries, accessing web information, analyzing results, and potentially performing multiple progressive searches to achieve the desired depth, producing initial research reports.
6.  **Report Aggregation & AI-Powered Verification (Custom Orchestration Layer & Evaluator LLM):**
    *   The custom orchestration layer collects the initial research reports from Claude.
    *   **Each report (or a consolidated report) is then passed to a separate "Evaluator LLM."**
    *   This Evaluator LLM is specifically prompted to:
        *   Verify the factual accuracy of the information presented against known sources (if possible, or flag claims that are difficult to verify).
        *   Identify potential hallucinations, inconsistencies, or biases in the research.
        *   Check the coherence and logical flow of the report.
    *   The output of this verification step might include annotations, a confidence score, or a summary of potential issues.
7.  **Output Naming & Formatting:**
    *   The (now verified or annotated) aggregated research is given a relevant name, likely based on the initial user query.
8.  **Output Formatting:**
    * A high-level, initially generic, executive summary of the research will be produced in the same document folder. 
8.  **Storage (Google Drive API):**
    *   The final research output, along with any verification notes, is programmatically uploaded and stored in a designated folder within the user's Google Drive.
9.  **User Review & Correction:**
    *   The user can review the research output and identity particularly useful information via comments. In Phase-2, a seperate "Reviewer" agent will be used to collate, store and analyse the users experience for further refinement of the research process.
10. **Alternative Research Strategy**
    *   After the initial research process has been demonstrated with initial functionality, I will create a lightweight custom deep research process and provide its results within the subdirectory of that document to check the degree to which Claude Max subscription is going to be required on an ongoing basis. This is unlikely to be as good as what Claude's tooling can offer, but it's worth checking in the name of long-term fiscal prudence.

## 4. Key Features (MVP)

*   Voice-activated research queries.
*   Programmatic initiation and management of multiple deep research instances (via Claude's API and web search tool).
*   User-definable parameters for research depth and scope.
*   **AI-driven verification of research reports for accuracy and hallucination detection.**
*   Automated collation of research findings.
*   Seamless integration with Google Drive for organized storage of research outputs.

## 5. Technical Overview (High-Level)

*   **Voice Input Module:** Apple Watch, Just Press Record, cloud-sync.
*   **Custom Orchestration Layer:** Likely Python-based, responsible for:
    *   Managing the overall workflow.
    *   Interfacing with voice input.
    *   Parsing and parameterizing user queries.
    *   Interacting with the intermediary LLM for query optimization.
    *   Making controlled API calls to Anthropic's Claude for research.
    *   **Interfacing with the Evaluator LLM for verification.**
    *   Managing the number of "agents"/research iterations.
    *   Collecting and organizing results.
    *   Interfacing with the Google Drive API.
*   **Query Optimization LLM:** An LLM instance for prompt optimization.
*   **Core Research Engine:** Anthropic's Claude API (specifically leveraging the `web_search` tool).
*   **Evaluator LLM:** A separate LLM instance (could be another Claude model, GPT, or a specialized model) tasked with report verification.
*   **Storage Backend:** Google Drive (accessed via Google Drive API).

## 6. Technology Choices & Rationale

*   **Anthropic's Claude (with Web Search Tool) for Research:**
    *   **Why:** As of current offerings (May 2024/2025), Anthropic's API is the most promising for programmatically achieving deep, iterative web research. Their `web_search` tool allows Claude to autonomously conduct multiple progressive searches and synthesize comprehensive answers with citations.
    *   **Compared to Others:** Remains the most direct current path for the *initial* deep research phase compared to building this layer from scratch with OpenAI or Google.
*   **Evaluator LLM (Vendor TBD, could be Claude, GPT, etc.):**
    *   **Why:** To introduce a layer of critical review and enhance the trustworthiness of the generated research. Different LLMs may have different strengths in fact-checking or identifying subtle inconsistencies. This modularity allows for choosing the best tool for verification.
*   **Custom Orchestration Layer:**
    *   **Why:** Essential for managing the multi-step process: voice input, query optimization, invoking Claude for research, then invoking the Evaluator LLM, and finally handling storage.
*   **Google Drive:**
    *   **Why:** Ubiquitous, user-friendly, and offers a robust API for programmatic file management.

## 7. Current Status

*   Conceptualization and MVP definition phase, including the addition of an AI verification step.
*   Core technologies identified.
*   High-level architecture and workflow outlined.
*   This project is a priority, and development of the MVP is to commence immediately.

## 8. Future Considerations

*   Developing sophisticated prompting strategies for the Evaluator LLM to maximize verification effectiveness.
*   Mechanisms for user review and correction of the AI's verification.
*   More advanced agent coordination and task decomposition.
*   Advanced output formatting and summarization options post-verification.
*   Integration with other data sources beyond web search.

---

This revision now clearly incorporates the crucial verification step, making the "Dark Genie" project even more robust in its aims.