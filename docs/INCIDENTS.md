# Sandbox Incident Response

## When to use this

Use this when you suspect sandbox escape, unexpected network access, filesystem writes outside `/tmp`, fork bomb behavior, or any execution that ignores Stop/timeout controls.

## 1. Containment

1. Stop new executions by disabling the backend container or removing the `/ws/run` route from traffic.
2. Preserve the current backend logs and `/metrics` snapshot.
3. Keep the affected user session isolated until the investigation is complete.

## 2. Diagnosis

1. Find the `request_id`, `user_id`, and `client_ip` in the structured logs.
2. Check whether the event was `execution_timeout`, `execution_finished`, or `execution_rate_limited`.
3. Inspect the sandbox flags in `backend/ws/pty_execution.py` and confirm the container was started with `--network=none`, `--read-only`, `tmpfs=/tmp`, `pids_limit=64`, `cap_drop=["ALL"]`, and a non-root user.
4. Review `/metrics` for active sandboxes and execution counts.

## 3. Communication

1. Notify the team that execution is paused.
2. Share the `request_id`, approximate timestamp, and observed behavior.
3. Do not restart the service until the likely cause is understood.

## 4. Recovery

1. Restore the service only after the sandbox configuration is verified.
2. Re-run the sandbox audit tests.
3. Document the incident and any mitigation changes in the next sprint note.
