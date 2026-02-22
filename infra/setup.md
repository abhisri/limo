# Server Setup — For AI Sessions

This document is for AI sessions (Claude, Codex, etc.) that have SSH access to the user's server. Follow these steps to set up the LIMO infrastructure stack.

## Prerequisites

Before starting, confirm with the user:

1. **SSH access works** — You can connect to the server via SSH
2. **Server specs** — At least 2 CPU cores, 4GB RAM, 20GB disk
3. **OS** — Ubuntu 22.04 (or similar Debian-based Linux)
4. **OpenAI API key** — Needed for mem0 embeddings (user provides this)
5. **Which components** — Ask: "Do you want the full stack (mem0 + Neo4j + n8n + Agent Bus), or just specific components?"

## Step 1: Install Docker

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Add current user to docker group (avoids needing sudo for docker commands)
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install -y docker-compose-plugin

# Verify
docker --version
docker compose version
```

If the user's session disconnects after the `usermod` command, they may need to reconnect for the group change to take effect.

## Step 2: Create Working Directory

```bash
mkdir -p ~/limo-infra
cd ~/limo-infra
```

## Step 3: Deploy Docker Compose

Copy the `docker-compose.yml` from this repo to the server. Before deploying:

1. **Change all passwords** — Replace every `CHANGE_ME_*` value
2. **Set the OpenAI API key** — Replace `CHANGE_ME_your_openai_api_key`
3. **Set the webhook URL** — Replace `your-server-domain` with the server's IP or domain

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# Watch logs for errors
docker compose logs -f --tail=50
```

## Step 4: Verify Services

### Postgres
```bash
docker exec limo-postgres pg_isready -U limo
# Should output: /var/run/postgresql:5432 - accepting connections
```

### mem0
```bash
curl -s http://localhost:8080/health
# Should return a health status

# Test storing a memory
curl -X POST http://localhost:8080/memories \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Test memory: LIMO infrastructure is running"}], "user_id": "test"}'
```

### Neo4j
```bash
# Check Neo4j is responding
curl -s http://localhost:7474

# Test a Cypher query via HTTP API
curl -X POST http://localhost:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -u neo4j:YOUR_PASSWORD \
  -d '{"statements": [{"statement": "RETURN 1 AS test"}]}'
```

### n8n
```bash
curl -s http://localhost:5678/healthz
# Should return: {"status":"ok"}
```

### Agent Bus (Postgres tables)
```bash
docker exec limo-postgres psql -U limo -c "\dt agent_bus_*"
# Should list agent_bus_tasks and agent_bus_events tables
```

## Step 5: Firewall (Recommended)

Only expose the ports you actually need from outside the server:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8080/tcp    # mem0 API
sudo ufw allow 7474/tcp    # Neo4j browser (optional — can keep internal only)
sudo ufw allow 7687/tcp    # Neo4j bolt
sudo ufw allow 5678/tcp    # n8n UI + webhooks
# Do NOT expose 5432 (Postgres) externally unless you have a specific reason
sudo ufw enable
```

## Step 6: TLS (Optional, Recommended for Production)

If the server has a domain name, set up Let's Encrypt:

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d your-domain.com
```

Then configure a reverse proxy (nginx or Caddy) to terminate TLS and forward to the Docker services. Caddy is simpler:

```bash
sudo apt install -y caddy
```

Caddy configuration for all services:

```
your-domain.com {
    handle /mem0/* {
        reverse_proxy localhost:8080
    }
    handle /neo4j/* {
        reverse_proxy localhost:7474
    }
    handle /* {
        reverse_proxy localhost:5678
    }
}
```

## Step 7: Backups (Recommended)

```bash
# Postgres backup (includes mem0 vectors and Agent Bus state)
docker exec limo-postgres pg_dump -U limo limo > ~/limo-infra/backup-$(date +%Y%m%d).sql

# Neo4j backup
docker exec limo-neo4j neo4j-admin database dump neo4j --to-stdout > ~/limo-infra/neo4j-backup-$(date +%Y%m%d).dump
```

Set up a cron job for daily backups:
```bash
crontab -e
# Add: 0 3 * * * docker exec limo-postgres pg_dump -U limo limo > ~/limo-infra/backup-$(date +\%Y\%m\%d).sql
```

## Troubleshooting

| Symptom | Check |
|:--------|:------|
| Container won't start | `docker compose logs [service]` — look for config errors |
| mem0 can't connect to Postgres | Verify password matches in both mem0 and postgres environment vars |
| Neo4j out of memory | Increase heap/pagecache in docker-compose.yml environment vars |
| n8n webhooks unreachable | Check firewall (port 5678), check WEBHOOK_URL in docker-compose.yml |
| Agent Bus tables missing | Check that agent-bus-schema.sql was loaded: `docker exec limo-postgres psql -U limo -c "\dt"` |

## Partial Deployments

You don't need the full stack. Common subsets:

**mem0 only:** Start `postgres` and `mem0` services. Comment out or remove `neo4j` and `n8n` from docker-compose.yml.

**Neo4j only:** Start `neo4j` service only. It doesn't depend on Postgres.

**n8n only:** Start `postgres` and `n8n`. Useful if you just want workflow automation without semantic memory or graph.
