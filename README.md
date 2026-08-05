# Brain-Worker Architecture Plugin for Agent Zero

A Brain-Worker architecture plugin for [Agent Zero](https://github.com/frdel/agent-zero). Agent 0 acts as a pure **orchestrator** that plans, delegates, and synthesizes — while all actual work is executed by **worker** subordinates running on a cost-effective model (the model configured in the Model Config plugin UI (active preset) by default).

## What It Does

- **Agent 0 (Orchestrator)** — Receives tasks from the user, breaks them into subtasks, delegates each to a worker subordinate, collects results, and presents the final answer. The orchestrator is **enforced** via system prompt injection to never execute code, write files, or use terminal tools directly.
- **Worker Subordinates** — Spawned via `call_subordinate` with `profile: "worker"`. Their chat model is automatically swapped to the model configured in the Model Config plugin UI (active preset) (or whatever you configure), and their utility model is swapped to a configurable utility endpoint.

This lets you run a powerful reasoning model as the brain (orchestrator) while keeping execution costs low by routing all coding/terminal/file operations through cheaper worker models.

## Installation

1. Copy the entire `brain_worker` folder into your Agent Zero plugins directory:
   ```bash
   cp -r brain_worker/ /a0/usr/plugins/brain_worker/
   ```
2. Copy the worker agent profile:
   ```bash
   cp -r agents/worker/ /a0/usr/agents/worker/
   ```
3. Restart Agent Zero (or reload plugins from the UI).
4. The plugin appears in **Settings → Plugins**. Enable it if not already enabled.

## How It Works

The plugin uses three framework extension hooks:

### 1. `get_chat_model/start` — Swap Worker Chat Model

**File:** `extensions/python/_functions/agent/Agent/get_chat_model/start/_20_swap_worker_model.py`

Intercepts model creation for subordinate agents (agent number > 0). Instead of using the default model, it builds a fresh the model configured in the Model Config plugin UI (active preset) model from the plugin's `config.json` settings and returns it as the chat model.

### 2. `get_utility_model/start` — Swap Worker Utility Model

**File:** `extensions/python/_functions/agent/Agent/get_utility_model/start/_20_swap_worker_utility.py`

Same concept as above, but for the utility model (used for background tasks like summaries and embeddings). Swaps subordinates to a configurable utility endpoint.

### 3. `system_prompt` — Enforce Orchestrator Behavior

**File:** `extensions/python/system_prompt/_20_orchestrator_enforce.py`

Appends a mandatory orchestrator-only system prompt to Agent 0 (agent number 0). This prompt enforces strict rules:

- Never execute code, write files, or use terminal tools directly
- Always delegate via `call_subordinate` with `profile: "worker"`
- Only use planning/research tools (`search_engine`, `memory_load`, `goal`, etc.)
- Break tasks into subtasks, delegate, collect, synthesize

## Configuration

All configuration lives in `config.json` at the plugin root. You can edit it directly or via the **Settings → Agent → Brain-Worker Architecture** panel in the WebUI.

```json
{
    "worker_chat_model": {
        "provider": "zai_coding",
        "name": "glm-5.2",
        "api_base": "https://api.z.ai/api/coding/paas/v4",
        "ctx_length": 1000000,
        "ctx_history": 0.7,
        "vision": false,
        "rl_requests": 0,
        "rl_input": 0,
        "rl_output": 0
    },
    "worker_utility_model": {
        "provider": "other",
        "name": "free-stack-Utility",
        "api_base": "https://omniroute.onekindpromo.com",
        "ctx_length": 128000,
        "ctx_input": 0.7
    },
    "orchestrator_enforce": true
}
```

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `worker_chat_model.provider` | Model provider key | `zai_coding` |
| `worker_chat_model.name` | Model name | `glm-5.2` |
| `worker_chat_model.api_base` | API endpoint URL | Z.AI coding endpoint |
| `worker_chat_model.ctx_length` | Context window size | `1000000` |
| `worker_chat_model.vision` | Enable vision capability | `false` |
| `worker_chat_model.rl_requests` | Rate limit: requests per minute (0 = unlimited) | `0` |
| `worker_chat_model.rl_input` | Rate limit: input tokens per minute (0 = unlimited) | `0` |
| `worker_chat_model.rl_output` | Rate limit: output tokens per minute (0 = unlimited) | `0` |
| `worker_utility_model.*` | Same fields as above, for utility model | Omniroute endpoint |
| `orchestrator_enforce` | Whether to inject orchestrator-only system prompt for Agent 0 | `true` |

> **Note:** The orchestrator (Agent 0) model is **not** controlled by this plugin. Configure it normally via **Settings → Model Configuration** in the Agent Zero UI.

## Worker Agent Profile

The `agents/worker/agent.yaml` file defines the worker subordinate profile:

```yaml
title: Worker
description: Worker agent for the Brain-Worker architecture. Executes tasks delegated by the orchestrator using the model configured in the Model Config plugin UI (active preset).
context: |
  You are a WORKER agent in the Brain-Worker architecture.
  You receive tasks from the orchestrator (Agent 0) and EXECUTE them.
  Your model is the model configured in the Model Config plugin UI (active preset) — optimized for coding, terminal operations, and implementation.

  Rules:
  1. Execute tasks efficiently using code_execution_tool, text_editor, and other tools.
  2. Return clear, structured results to the orchestrator.
  3. If a task is ambiguous, make reasonable assumptions and proceed.
  4. Focus on completing the assigned task — do not delegate further.
  5. Report what you did, what succeeded, and what failed.
```

This profile is activated when the orchestrator calls `call_subordinate` with `profile: "worker"`.

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Agent 0 (Orchestrator)          │
│  Model: Configured in Settings (e.g. Kimi K3)│
│  Role: Plan → Delegate → Synthesize          │
│  Tools: call_subordinate, search, memory...  │
└──────────────────┬──────────────────────────┘
                   │ call_subordinate(profile: "worker")
                   ▼
┌─────────────────────────────────────────────┐
│           Worker Subordinates (the model configured in the Model Config plugin UI (active preset))      │
│  Role: Execute code, terminal, file ops      │
│  Tools: code_execution_tool, text_editor...  │
└─────────────────────────────────────────────┘
```

## License

MIT
