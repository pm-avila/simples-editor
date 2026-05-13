# Progress

## Sprint 1

- [x] #1 feat(repo): bootstrap repository documentation
- [x] #2 feat(project): configure delivery kanban workflow
- [x] #3 feat(infra): scaffold docker compose foundation
- [x] #4 feat(infra): validate local startup flow on docker compose
- [x] #5 feat(auth): provision Supabase auth for v1
- [x] #6 feat(login): implement Supabase email/password sign-in
- [x] #7 feat(auth): enforce JWT validation on backend endpoints
- [x] #8 feat(api): expose public health check endpoint
- [x] #9 feat(contrib): validate pull request workflow for every team member

## Sprint 2

- [x] #10 feat(editor): integrate Monaco on the main route
- [x] #11 feat(editor): register the SIMPLES Monaco language
- [x] #12 feat(editor): apply dark theme for SIMPLES syntax
- [x] #13 feat(layout): build the three-panel IDE shell
- [x] #14 feat(layout): add resizable editor and NASM splitters
- [x] #15 feat(run): mock compile action from the toolbar
- [x] #16 feat(nasm): render NASM output in a read-only Monaco panel

## Sprint 3

- [x] #17 feat(build): package simplesc in the backend image
- [x] #18 feat(build): enable i386 linking toolchain in the backend container
- [x] #19 feat(compile): implement POST /api/compile endpoint
- [x] #20 feat(errors): normalize compiler errors by phase
- [x] #21 feat(editor): map compile errors to Monaco markers
- [x] #22 feat(nasm): sync generated assembly into the NASM panel
- [x] #23 feat(compile): enforce compile timeout safeguards

## Sprint 4

- [ ] #24 feat(ws): implement authenticated /ws/run endpoint
- [ ] #25 feat(terminal): integrate xterm.js into the terminal panel
- [x] #26 feat(sandbox): build the simples-runner execution image
- [x] #27 feat(executor): implement PtyExecutionStrategy for interactive runs
- [x] #28 feat(stream): bridge terminal I/O between WebSocket and PTY
- [ ] #29 feat(interactive): support leia end-to-end in the IDE
- [ ] #30 feat(protocol): implement the run-session WebSocket event contract

## Sprint 5

- [ ] #31 feat(stop): wire the Stop action through the execution lifecycle
- [ ] #32 feat(executor): enforce wall-clock execution timeout
- [ ] #33 feat(sandbox): configure hard Docker stop timeout
- [ ] #34 feat(security): harden sandbox runtime isolation defaults
- [ ] #35 feat(security): rate-limit compile and run operations
- [ ] #36 feat(observability): emit structured JSON logs
- [ ] #37 feat(observability): expose Prometheus metrics internally
- [ ] #38 feat(security): verify sandbox escape scenarios are blocked
- [ ] #39 feat(docs): document sandbox incident response

## Sprint 6

- [ ] #40 feat(e2e): automate the main IDE flow with Playwright
- [ ] #41 feat(test): raise backend coverage to at least 70 percent
- [ ] #42 feat(docs): publish the full project README with visuals
- [ ] #43 feat(demo): produce the short project demo video
- [ ] #44 feat(deploy): publish the OCI Ampere deployment path with valid TLS
- [ ] #45 feat(deploy): configure a custom academic domain
- [ ] #46 feat(presentation): prepare the final project presentation
- [ ] #47 feat(retro): capture the team retrospective

