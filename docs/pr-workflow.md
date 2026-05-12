# Sprints Workflow — Sequential Delivery via Feature Branches and Pull Requests

This workflow supports sprint delivery by requiring every team member to ship work through a feature branch and pull request, processing issues **one at a time** (no parallel execution).

## Prerequisite

Use the `superpowers` skill throughout the entire workflow — including research, brainstorming, planning, implementation, and review phases. Every phase below must be executed via the corresponding Superpowers subagent.

## Workflow

1. **Pick the next issue** from the sprint backlog. Issues are processed sequentially — do not start a new issue until the current one has been merged into `dev` and its evidence record updated.

2. **Start from `dev`** and pull the latest changes:

```bash
   git checkout dev
   git pull origin dev
```

3. **Create a feature branch** named `feat/<issue-number>`:

```bash
   git checkout -b feat/<issue-number>
```

4. **Implement the scoped change** on that branch using the Superpowers phased approach:
   - **Brainstorming phase:** explore the problem space using the Superpowers brainstorming subagent. **Always accept the recommendations produced in this phase** — do not deviate or override the suggested direction.
   - **Plan writing phase:** produce the implementation plan based on the brainstorming output. **Always accept the recommendations made during plan writing** — the plan, as recommended, becomes the source of truth for implementation.
   - **Implementation phase:** write the code **strictly following the recommended plan**, design patterns, and architectural decisions defined in the previous phases. No ad-hoc changes outside the recommended scope.

5. **Open a pull request** targeting `dev`, referencing the issue number in the PR description.

6. **Perform the review** and **post the review comments directly inside the open PR** as PR review comments (not in an external document, not in chat, not in Notion — they must live on the PR itself for traceability).

7. **Apply the adjustments recommended in the review before merging.** Push the fixes to the same feature branch so the PR is updated with the corrections. Re-request review if needed.

8. **Merge the pull request into `dev`** only after every review recommendation has been addressed and the PR is approved.

9. **Update the PR evidence record** after the merge is completed.
