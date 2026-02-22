# LIMO Infrastructure Guide

**What this is:** An optional add-on for LIMO that adds persistent memory services beyond the filesystem. Works with single-domain (Tier 1) or multi-domain (Tier 2) setups.

**When you need this:** When your LIMO usage outgrows what files alone can do — you want semantic search across memories, a knowledge graph of people and relationships, or automated workflows between agents.

**When you don't need this:** If you're running 1-3 domains and file-based LIMO is working fine, you don't need any of this. Markdown files are the right answer for most users. Come back when you feel the pain.

---

## What Each Component Does

### mem0 — Semantic Memory

**The problem it solves:** LIMO files are great for structured knowledge (decisions, goals, learnings). But some knowledge is better found by *meaning* than by location. "What did we figure out about sleep and medication interactions?" is a semantic question — grepping SESSION_DIARY won't reliably find the answer.

**What it is:** A vector database (pgvector + OpenAI embeddings) with a simple API. You store text with metadata, and later search by meaning. It returns the most semantically similar memories.

**When you'd want it:**
- You accumulate insights across many sessions and domains
- You want to ask "what do we know about X?" and get answers from anywhere in your history
- You have 10+ domains and cross-domain knowledge discovery matters

**How it works with LIMO:** The AI session stores key insights in mem0 as it writes them to LIMO files. On boot, it can search mem0 for relevant context beyond what's in the current domain's files. The LIMO files remain the source of truth — mem0 is a search layer on top.

---

### Neo4j — Knowledge Graph

**The problem it solves:** People, places, relationships, and facts form a graph. "Who co-owns the house?" "What's the connection between the lawyer and the mediator?" These are graph queries. Storing this in flat markdown works until the web of relationships gets complex.

**What it is:** A graph database where nodes are people, properties, organizations, and edges are relationships (MARRIED_TO, CO_OWNS, WORKS_FOR, etc.). You query it with Cypher (a graph query language).

**When you'd want it:**
- Your domains involve many people with complex relationships
- You need to trace connections: "Who knows who?" "What's linked to what?"
- Legal, family, or business contexts where relationship mapping matters

**How it works with LIMO:** KEY_PEOPLE.md stays as the quick-reference. Neo4j holds the deeper graph — all the people, all the relationships, queryable. The AI session can check the graph when it needs relationship context beyond what's in the local files.

---

### n8n — Workflow Automation

**The problem it solves:** Some tasks should happen automatically or on a schedule. "Check my inbox and process messages every morning." "When an agent drops a high-priority message, notify me." "Run a memory cleanup every Sunday."

**What it is:** A visual workflow automation tool (like Zapier, but self-hosted and free). You build workflows with a drag-and-drop UI that connect triggers to actions.

**When you'd want it:**
- You want scheduled tasks (cron-driven inbox polling, memory maintenance)
- You want webhook-triggered workflows (Agent Bus pattern)
- You want to connect LIMO to external services (email, Slack, calendars)

**How it works with LIMO:** n8n runs on your server and executes workflows. The most powerful pattern is the Agent Bus — a webhook-driven task dispatch system where agents can submit tasks and get results back asynchronously.

---

### Agent Bus — Cross-Agent Task Dispatch

**The problem it solves:** The `_messages/` bus in Tier 2 is asynchronous and file-based — an agent drops a message, and the recipient processes it whenever it next boots. The Agent Bus adds real-time, webhook-driven task dispatch with state tracking.

**What it is:** An n8n workflow backed by a Postgres database. An agent submits a task via webhook, the bus validates and routes it, tracks state (pending → claimed → done/failed), and returns results.

**When you'd want it:**
- You want agents to trigger work in other agents in real-time
- You need task state tracking (what's pending, what's done, what failed)
- You want retry logic, dead-letter queues, or leased task claims

**How it works with LIMO:** The Agent Bus complements `_messages/`. Use `_messages/` for FYI-level cross-domain communication. Use the Agent Bus for tasks that need tracking, confirmation, or real-time dispatch.

---

## Do You Need This?

| Situation | Recommendation |
|:----------|:---------------|
| 1-3 domains, files working fine | **No.** Stay with Tier 1/2. |
| Many domains, hard to find old insights | **mem0** only. Start there. |
| Complex people/relationship tracking | **Neo4j** only. Start there. |
| Want automated maintenance or scheduling | **n8n** only. Start there. |
| All of the above, plus real-time agent coordination | **Full stack.** |

You don't have to deploy everything at once. Each component is independent. Start with the one that solves your most pressing pain.

---

## What You Need: A Linux Server

All of these services run as Docker containers on a Linux server. You need a machine that:

- Runs Linux (Ubuntu 22.04 recommended)
- Has a public IP address (so your AI sessions can reach it)
- Has SSH access (so the AI can connect and manage it)
- Has at least 2 CPU cores and 4GB RAM (a modest cloud instance)
- Has Docker and Docker Compose installed

**If you've never done this before, that's fine.** Your AI session (Claude, Codex, etc.) can walk you through the entire process:

1. **Pick a cloud provider** — AWS, DigitalOcean, Hetzner, Linode, Vultr, or any provider that offers Linux VMs. Hetzner and DigitalOcean are often the simplest for beginners. Budget roughly $10-20/month for a suitable instance.

2. **Create an account and provision a server** — The AI can tell you exactly what to click, but you'll need to do the clicking yourself (account creation, payment, etc.).

3. **Set up SSH access** — You'll get a private key file (`.pem` or similar). Save it somewhere safe on your computer. This is how the AI will connect to your server.

4. **Give the AI SSH access** — Provide the AI session with:
   - The server's public IP address
   - The SSH username (usually `ubuntu` or `root`)
   - The path to your private key file

5. **Let the AI do the rest** — Once the AI can SSH into the server, it can install Docker, pull the container images, configure the services, set up DNS/TLS if you want, and verify everything works.

The AI should offer to guide you through steps 1-4 and then handle step 5 directly via SSH.

---

## Architecture Overview

The full stack runs as Docker containers on your server:

```
┌─────────────────────────────────────────────┐
│                Linux Server                  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  mem0     │  │  Neo4j   │  │   n8n    │  │
│  │  API      │  │  (graph  │  │  (work-  │  │
│  │  server   │  │  DB +    │  │  flows)  │  │
│  │          │  │  browser) │  │          │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
│  ┌────┴──────────────┴──────────────┴────┐  │
│  │           Postgres + pgvector          │  │
│  │     (shared database for all state)    │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │           Agent Bus (n8n workflow)      │  │
│  │     (webhook → validate → dispatch     │  │
│  │      → track state → respond)          │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         ▲
         │ SSH + HTTPS
         │
    AI Sessions (Claude, Codex, etc.)
```

Each container is independent. You can run just mem0 + Postgres, or just Neo4j, or the full stack.

---

## Starter Configs

The `infra/` directory in this repo contains starter configurations:

- **`docker-compose.yml`** — A template Docker Compose file that defines all services. Customize the environment variables (passwords, API keys) before deploying.
- **`agent-bus-schema.sql`** — The Postgres schema for the Agent Bus state machine (tasks table, events table, indexes).
- **`setup.md`** — Step-by-step instructions for an AI session to follow when setting up the server.

These are starting points, not turnkey solutions. Your AI session should read them, adapt them to your server's specifics, and configure them for your needs.

---

## Connecting LIMO to Infrastructure

Once services are running, the AI session needs to know how to reach them. Add a configuration section to the domain's `SESSION_PROMPT.md` or create a shared `INFRA_CONFIG.md` at root:

```markdown
## Infrastructure Endpoints

- **mem0 API:** https://your-server:8080
- **Neo4j Browser:** https://your-server:7474
- **Neo4j Bolt:** bolt://your-server:7687
- **n8n:** https://your-server:5678
- **Agent Bus webhook:** https://your-server:5678/webhook/agent-bus

## SSH Access
- Host: your-server-ip
- User: ubuntu
- Key: [path to private key on your machine]
```

The AI session reads this on boot and knows how to reach the infrastructure.

---

## Security Notes

- **SSH keys:** Never commit private keys to this repo or any repo. Store them locally.
- **API keys:** If you use OpenAI embeddings for mem0, the API key goes in the server's environment variables, not in LIMO files.
- **Passwords:** Neo4j and Postgres passwords go in the docker-compose environment variables on the server.
- **TLS:** If your server has a domain name, set up Let's Encrypt for HTTPS. The AI can help with this via SSH.
- **Firewall:** Only expose the ports you need. The AI can configure `ufw` on the server.

---

## What This Guide Does NOT Cover

- **Your specific implementation.** This guide describes the architecture and gets you started. Your domains, your data, your workflows are yours to build.
- **Managed services.** This assumes self-hosted Docker containers. If you prefer managed services (mem0 Cloud, Neo4j Aura, n8n Cloud), the concepts are the same but the setup is different — your AI session can help with those too.
- **Cost optimization.** A small cloud instance running this stack costs $10-20/month. If cost is a concern, start with just one component.
