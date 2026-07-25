# Lab 05: Isolated Docker Web Lab

## Objective

Launch a minimal local web service, verify its network exposure, inspect its
logs, and remove it cleanly.

## Safety boundary

The service binds to the loopback address so it is reachable only from the
host. Do not add secrets or personal files to the web directory. Use the
pinned image version in the included Compose file.

## Setup and run

Requirements:

- Docker Desktop or Docker Engine with Compose
- Port 8080 free on the local computer

From this folder:

```bash
docker compose config
docker compose up -d
docker compose ps
```

Open `http://127.0.0.1:8080` in a browser. You should see the included static
training page.

Inspect recent logs:

```bash
docker compose logs --tail 20
```

Confirm that the published port begins with `127.0.0.1`, not `0.0.0.0`.

## Defensive observations

Record:

- Image name and pinned version
- Host and container ports
- Bind address
- Container status
- One normal request from the access log
- Why least exposure matters

## Cleanup

Stop and remove only the resources defined by this Compose project:

```bash
docker compose down
```

Confirm with:

```bash
docker compose ps
```

## Deliverable

Submit a sanitized lab report showing the configuration, one normal log
event, verification of loopback-only exposure, and cleanup result.

