# Sandbox Runner Image Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `simples-runner` Docker image contract for x86 32-bit execution in an isolated non-root sandbox.

**Architecture:** Add a dedicated `runner/Dockerfile` with Debian slim runtime and qemu-user-static support. Enforce runtime isolation by dropping root privileges and setting `/sandbox` as owned working directory. Verify the contract through focused repository tests.

**Tech Stack:** Dockerfile, Python unittest (static contract checks)

---

### Task 1: Add runner image contract test first

**Files:**
- Test: `tests/test_runner_dockerfile.py`

- [ ] **Step 1: Write the failing test**

```python
class RunnerDockerfileContractTest(unittest.TestCase):
    def test_base_image_is_debian_slim(self):
        text = _dockerfile_text()
        self.assertRegex(text, r"^FROM\\s+debian:[^\\s]*slim", re.MULTILINE)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_runner_dockerfile.py -v`
Expected: FAIL because `runner/Dockerfile` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `runner/Dockerfile` with:
- `FROM debian:bookworm-slim`
- `apt-get install ... qemu-user-static ...`
- non-root `sandbox` user setup
- `WORKDIR /sandbox` and `USER sandbox`

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_runner_dockerfile.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add runner/Dockerfile tests/test_runner_dockerfile.py
git commit -m "feat(sandbox): add simples-runner docker image contract"
```

### Task 2: Validate regression scope

**Files:**
- Test: `tests/test_compose_startup.py` (existing)
- Test: `tests/test_backend_dockerfile.py` (existing)

- [ ] **Step 1: Run focused existing tests**

Run: `python3 -m unittest tests/test_backend_dockerfile.py tests/test_compose_startup.py -v`
Expected: PASS or known unrelated baseline failures.

- [ ] **Step 2: Commit test evidence-only updates if needed**

No code changes expected in this task.
