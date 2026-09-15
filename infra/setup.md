# Server Setup — For AI Sessions

This document is for AI sessions (Claude, Codex, etc.) that have SSH access to the user's server. Follow these steps to set up the LIMO infrastructure stack.

## Prerequisites

Before starting, confirm with the user:

1. **SSH access works** — You can connect to the server via SSH
2. **Server specs** — At least 2 CPU cores, 4GB RAM, 20GB disk (a t3.medium or equivalent)
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

## Step 2: Create Working Directory and Configure Secrets

```bash
mkdir -p ~/limo-infra
cd ~/limo-infra
```

Copy `docker-compose.yml`, `agent-bus-schema.sql`, and `.env.example` from this repo to the server.

Then create the `.env` file from the example and fill in all values:

```bash
cp .env.example .env

# Generate secure passwords
echo "POSTGRES_PASSWORD=$(openssl rand -base64 24)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -base64 24)" >> .env
echo "NEO4J_PASSWORD=$(openssl rand -base64 24)" >> .env
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env
```

Then manually set the remaining values:
- `OPENAI_API_KEY` — the user provides this
- `WEBHOOK_URL` — the server's public URL (set after TLS is configured, or use the IP for now)

**IMPORTANT:** The `.env` file is the single source of truth for all secrets. Never commit it to git. Never duplicate secrets in multiple places.

## Step 3: Deploy

```bash
cd ~/limo-infra

# Start all services
docker compose up -d

# Check status
docker compose ps

# Watch logs for errors (Ctrl+C to stop following)
docker compose logs -f --tail=50
```

## Step 4: Verify Services

### Postgres
```bash
docker exec limo-postgres pg_isready -U limo
# Should output: accepting connections
```

### Redis
```bash
docker exec limo-redis redis-cli -a "$(grep REDIS_PASSWORD .env | cut -d= -f2)" ping
# Should output: PONG
```

### mem0

**Note:** The mem0 Docker ecosystem is evolving. If the official `mem0ai/mem0` image doesn't work with the latest release, you have two options:

- **Option A:** Check mem0's documentation for the current recommended Docker setup
- **Option B:** Write a small FastAPI wrapper around the `mem0` Python library (more control, proven in production). The AI session can help you build this — it's about 50 lines of Python.

```bash
# Test mem0 health
curl -s http://localhost:8080/health

# Test storing a memory
curl -X POST http://localhost:8080/memories \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Test memory: LIMO infrastructure is running"}], "user_id": "test"}'

# Test searching
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is running?", "user_id": "test"}'
```

### Neo4j
```bash
# Check Neo4j is responding
curl -s http://localhost:7474

# Test a Cypher query
curl -X POST http://localhost:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -u neo4j:$(grep NEO4J_PASSWORD .env | cut -d= -f2) \
  -d '{"statements": [{"statement": "RETURN 1 AS test"}]}'
```

### n8n
```bash
curl -s http://localhost:5678/healthz
# Should return: {"status":"ok"}
```

### Agent Bus (Postgres tables)
```bash
docker exec limo-postgres psql -U limo -d limo -c "\dt agent_bus_*"
# Should list agent_bus_tasks and agent_bus_events tables
```

## Step 5: Security

### Bind to localhost only

The docker-compose.yml already binds all ports to `127.0.0.1`. This means services are NOT exposed to the internet directly. Access from outside the server goes through either:

- **SSH tunnel** (simplest, works immediately): `ssh -L 8080:127.0.0.1:8080 user@server`
- **Reverse proxy** (better for webhooks and browser access): see below

### Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp     # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp    # HTTPS (reverse proxy)
# Do NOT open individual service ports (5432, 6379, 7474, 7687, 5678, 8080)
# They're only accessible via localhost or the reverse proxy
sudo ufw enable
```

### Swap (recommended for 4GB RAM instances)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# Make persistent across reboots:
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Note: if you don't make swap persistent, it disappears on reboot.

## Step 6: Reverse Proxy with TLS

For n8n webhooks to work from the internet (Agent Bus, external triggers), you need a public URL with TLS. Options:

### Option A: Free domain with DuckDNS + Caddy

1. Go to https://www.duckdns.org, sign in, create a subdomain pointing to your server's IP
2. Install Caddy (auto-manages Let's Encrypt certificates):

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

3. Configure Caddy (`/etc/caddy/Caddyfile`):

```
your-subdomain.duckdns.org {
    # n8n (UI + webhooks) — the primary service needing public access
    reverse_proxy localhost:5678
}
```

4. Reload: `sudo systemctl reload caddy`

Now `https://your-subdomain.duckdns.org/` reaches n8n, and webhooks work at `https://your-subdomain.duckdns.org/webhook/*`.

### Option B: Apache (if already installed)

```bash
sudo apt install -y apache2 certbot python3-certbot-apache
sudo a2enmod proxy proxy_http proxy_wstunnel rewrite ssl headers
```

Create vhost, run certbot, enable WebSocket proxying. The AI session can generate the full Apache config for you.

### After setting up TLS

Update the `WEBHOOK_URL` in `.env` to your public HTTPS URL, then restart n8n:

```bash
cd ~/limo-infra
# Edit .env: WEBHOOK_URL=https://your-subdomain.duckdns.org/
docker compose restart n8n
```

## Step 7: Backups

```bash
# Create backup script
cat > ~/limo-infra/backup.sh << 'BACKUP'
#!/bin/bash
set -e
BACKUP_DIR=~/backups
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Postgres (includes mem0 vectors + Agent Bus state)
docker exec limo-postgres pg_dump -U limo limo > "$BACKUP_DIR/postgres-$TIMESTAMP.sql"

# Neo4j
docker exec limo-neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m" \
  > "$BACKUP_DIR/neo4j-$TIMESTAMP.cypher" 2>/dev/null || true

# Docker compose + env (config backup)
cp ~/limo-infra/docker-compose.yml "$BACKUP_DIR/docker-compose-$TIMESTAMP.yml"
cp ~/limo-infra/.env "$BACKUP_DIR/env-$TIMESTAMP"

# Tarball
tar -czf "$BACKUP_DIR/limo-backup-$TIMESTAMP.tar.gz" \
  -C "$BACKUP_DIR" \
  "postgres-$TIMESTAMP.sql" \
  "neo4j-$TIMESTAMP.cypher" \
  "docker-compose-$TIMESTAMP.yml" \
  "env-$TIMESTAMP"

# Cleanup individual files
rm -f "$BACKUP_DIR/postgres-$TIMESTAMP.sql" \
      "$BACKUP_DIR/neo4j-$TIMESTAMP.cypher" \
      "$BACKUP_DIR/docker-compose-$TIMESTAMP.yml" \
      "$BACKUP_DIR/env-$TIMESTAMP"

# Retain last 5 backups
ls -t "$BACKUP_DIR"/limo-backup-*.tar.gz | tail -n +6 | xargs rm -f 2>/dev/null

echo "Backup complete: $BACKUP_DIR/limo-backup-$TIMESTAMP.tar.gz"
BACKUP

chmod +x ~/limo-infra/backup.sh
```

Set up weekly cron:
```bash
# Run backup every Saturday at 3 AM UTC
(crontab -l 2>/dev/null; echo "0 3 * * 6 cd ~/limo-infra && source .env && ~/limo-infra/backup.sh") | crontab -
```

## Step 8: Connect LIMO to Infrastructure

Create an `INFRA_CONFIG.md` at your LIMO root (or in the domain's `core/` folder):

```markdown
## Infrastructure Endpoints (localhost — access via SSH tunnel or reverse proxy)

- **mem0 API:** http://127.0.0.1:8080
- **Neo4j Browser:** http://127.0.0.1:7474
- **Neo4j Bolt:** bolt://127.0.0.1:7687
- **n8n UI:** http://127.0.0.1:5678
- **Agent Bus webhook:** https://your-public-domain/webhook/agent-bus

## SSH Access
- Host: [server IP]
- User: [username]
- Key: [path to private key on your machine]
```

The AI session reads this file on boot and knows how to reach the infrastructure.

## Troubleshooting

| Symptom | Check |
|:--------|:------|
| Container won't start | `docker compose logs [service]` — look for config errors |
| mem0 can't connect to Postgres | Verify `.env` passwords match across services |
| Neo4j out of memory | Increase heap/pagecache in docker-compose.yml, add swap |
| n8n webhooks unreachable | Check reverse proxy config, verify WEBHOOK_URL in .env |
| Agent Bus tables missing | Check that agent-bus-schema.sql was loaded: `docker exec limo-postgres psql -U limo -d limo -c "\dt"` |
| Services unreachable from AI session | Use SSH tunnel: `ssh -L 8080:127.0.0.1:8080 user@server` |
| Swap disappeared after reboot | Re-create swap and add to /etc/fstab (see Step 5) |

## Partial Deployments

You don't need the full stack. Common subsets:

**mem0 only:** Start `postgres` and `mem0` services only. Comment out `neo4j`, `redis`, and `n8n` in docker-compose.yml.

**Neo4j only:** Start `neo4j` service only. It doesn't depend on Postgres.

**n8n + Agent Bus:** Start `postgres`, `redis`, and `n8n`. Good for workflow automation without semantic memory.

**mem0 + Neo4j (no n8n):** Start `postgres`, `mem0`, and `neo4j`. Semantic memory with graph-based relationship extraction, but no workflow automation.

## Lessons from Production

These lessons come from running this stack on a t3.medium for months:

1. **mem0 uses the OpenAI API** for embeddings and (optionally) LLM-powered entity extraction. This costs money. Budget roughly $0.002-0.005 per memory stored. Don't bulk-store thousands of memories without considering API costs.

2. **The custom n8n image tip** (adding curl/jq) is worth doing early. Many useful n8n workflows need to shell out to curl.

3. **Container names with Docker Compose v2** follow the pattern `[directory]-[service]-1` (e.g., `limo-infra-neo4j-1`), not the `container_name` you set. Use `docker ps` to check actual names, or use `docker compose exec neo4j ...` which always works.

4. **Don't modify mem0's Postgres tables directly.** The `memories` table schema is managed by mem0. Agent Bus tables are separate and safe to modify.

5. **All services binding to 127.0.0.1 is intentional.** Don't change this to `0.0.0.0` "to make it work" — use a reverse proxy instead. Exposing Postgres or Redis to the internet is a security incident waiting to happen.
