# Progress

## Sprint 1
- [x] feat(repo): bootstrap repository documentation — PR #48 merged into `dev`
- [ ] feat(project): configure delivery kanban workflow — PR #49 open
- [ ] feat(infra): scaffold docker compose foundation — PR #50 open
- [ ] feat(infra): validate local startup flow on docker compose — PR #51 open
- [ ] feat(auth): provision Supabase auth for v1 — PR #52 open
- [ ] feat(login): implement Supabase email/password sign-in — PR #53 open
- [ ] feat(auth): enforce JWT validation on backend endpoints — PR #54 open
- [ ] feat(api): expose public health check endpoint — PR #55 open
- [ ] feat(contrib): validate pull request workflow for every team member — PR #56 open

## Sprint 2
- [ ] feat(editor): integrate Monaco on the main route
- [ ] feat(editor): register the SIMPLES Monaco language
- [ ] feat(editor): apply dark theme for SIMPLES syntax
- [ ] feat(layout): build the three-panel IDE shell
- [ ] feat(layout): add resizable editor and NASM splitters
- [ ] feat(run): mock compile action from the toolbar
- [ ] feat(nasm): render NASM output in a read-only Monaco panel

## Sprint 3
- [ ] feat(build): package simplesc in the backend image
- [ ] feat(build): enable i386 linking toolchain in the backend container
- [ ] feat(compile): implement POST /api/compile endpoint
- [ ] feat(errors): normalize compiler errors by phase
- [ ] feat(editor): map compile errors to Monaco markers
- [ ] feat(nasm): sync generated assembly into the NASM panel
- [ ] feat(compile): enforce compile timeout safeguards

## Sprint 4
- [ ] feat(ws): implement authenticated /ws/run endpoint
- [ ] feat(terminal): integrate xterm.js into the terminal panel
- [ ] feat(sandbox): build the simples-runner execution image
- [ ] feat(executor): implement PtyExecutionStrategy for interactive runs
- [ ] feat(stream): bridge terminal I/O between WebSocket and PTY
- [ ] feat(interactive): support leia end-to-end in the IDE
- [ ] feat(protocol): implement the run-session WebSocket event contract

## Sprint 5
- [ ] feat(stop): wire the Stop action through the execution lifecycle
- [ ] feat(executor): enforce wall-clock execution timeout
- [ ] feat(sandbox): configure hard Docker stop timeout
- [ ] feat(security): harden sandbox runtime isolation defaults
- [ ] feat(security): rate-limit compile and run operations
- [ ] feat(observability): emit structured JSON logs
- [ ] feat(observability): expose Prometheus metrics internally
- [ ] feat(security): verify sandbox escape scenarios are blocked
- [ ] feat(docs): document sandbox incident response

## Sprint 6
- [ ] feat(e2e): automate the main IDE flow with Playwright
- [ ] feat(test): raise backend coverage to at least 70 percent
- [ ] feat(docs): publish the full project README with visuals
- [ ] feat(demo): produce the short project demo video
- [ ] feat(deploy): publish the OCI Ampere deployment path with valid TLS
- [ ] feat(deploy): configure a custom academic domain
- [ ] feat(presentation): prepare the final project presentation
- [ ] feat(retro): capture the team retrospective
