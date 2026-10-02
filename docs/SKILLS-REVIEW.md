# Skill sources reviewed and project installation

Reviewed 10–20 September 2026. The user requested ECC skills and review/use of the additional links, then asked for a design grill with documentation. The selection below supports this PRD and future implementation. This is a relevance and instruction review, not a comprehensive security audit of every upstream repository.

## Installed in this project

| Skill | Source | Applied purpose |
|---|---|---|
| api-design | [ECC](https://github.com/affaan-m/ecc/tree/main/skills/api-design) | Resource contracts, validation, errors, ownership, idempotency |
| eval-harness | [ECC](https://github.com/affaan-m/ecc/tree/main/skills/eval-harness) | Define pass/fail evidence before implementation; distinguish human and deterministic evaluation |
| security-review | [ECC](https://github.com/affaan-m/ecc/tree/main/skills/security-review) | Server secrets, input limits, session ownership, output handling |
| verification-before-completion | [Superpowers](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion) | Verify files and claims before announcing completion |
| grill-with-docs | Local project skill | Interview the design frontier, then record accepted decisions in `CONTEXT.md` and ADRs |
| grilling + domain-modeling | Local project skills | Stress-test the release boundary and keep product vocabulary aligned with code |

Destination: `.agents/skills/` in this repository. The standard skill-installer helper performed installation. Main skill file hashes and reviewed checkout commits are recorded in `research/skills-lock.json`; all four main files matched the reviewed checkouts. ECC's supplemental cloud-security document is included by its installer, but cloud deployment is outside this task.

These are selected skill directories, not a full ECC or Superpowers plugin installation. No upstream hooks, agent swarms, shell profiles, memory daemons, global configuration, or automatic deployment workflows were enabled. References in skill text to repository-wide utility scripts do not mean those scripts are present in this project. Use the textual guidance within the task scope. The new project skills should be available on the next turn.

## Every supplied link and decision

| User source | Review conclusion | Decision for this task |
|---|---|---|
| [affaan-m/ecc](https://github.com/affaan-m/ecc) | Broad engineering workflow collection, with selectively useful API/evaluation/security skills | Installed the three focused skills above; use its repository as tooling guidance, not an education-app codebase |
| [obra/superpowers](https://github.com/obra/superpowers) | Engineering process and verification skills | Installed verification; reviewed writing-plans as a future implementation option; no whole-framework activation |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Design-system and UX reference capability with scripts/data | Reviewed README and workflow; use as an implementation-stage option, not needed to install a full UI toolchain for a PRD |
| [Vercel Agent Skills](https://vercel.com/docs/agent-resources/skills) | Official discovery/catalog page with React, design, and deployment categories | Reference for later framework-specific work; catalog itself is not an installable skill |
| [MCPServers frontend-design listing](https://mcpservers.org/agent-skills/vercel/frontend-design) | A third-party listing reproducing frontend design guidance | Reviewed as discovery material; used the already available local frontend-design skill for the UX section; do not assume the listing proves publisher identity |
| [Snyk UI/UX skills article](https://snyk.io/articles/top-claude-skills-ui-ux-engineers/) | Secondary roundup of design-related skills | Checked for discovery only; not evidence for runtime architecture, RAG performance, or model selection |
| [Anthropic skills collection](https://github.com/anthropics/skills/tree/main/skills) | A collection requiring skill-by-skill selection | Reviewed collection; existing frontend/document capabilities make a wholesale duplicate installation unnecessary |
| [Karpathy-style skills](https://github.com/multica-ai/andrej-karpathy-skills) | Coding discipline guidance concerning assumptions, scope, and verification | Applied the general discipline of explicit assumptions and measurable completion; did not overwrite local instruction files |
| [Matt Pocock skills](https://github.com/mattpocock/skills) | Current checkout contains `skills/engineering/to-spec`; guessed old root `write-a-prd` path was unavailable | Read to-spec and inspected repository. Its issue-tracker publication workflow is outside the requested local file deliverable; use it as comparison material, not an active publishing workflow |
| [Caveman SKILL.md](https://github.com/JuliusBrussee/caveman/blob/main/skills/caveman/SKILL.md) | Explicit output compression and persistent terse communication | Reviewed; inactive because the user specifically requested a fully detailed PRD |
| [Taste skill](https://github.com/leonxlnx/taste-skill) | Multiple frontend and image-generation skills | Reviewed catalog; corresponding design-taste skills are already present in this environment. No duplicate install; image generation is unnecessary for the written specification |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | Communication structure emphasizing action and short lists | Reviewed; use a clear entry point and concise handoff, without imposing its list caps on the requested detailed artifact |

## Application boundaries

The PRD specifies student-facing evidence inspection and Bengali readability; development skills do not become runtime prompts or retrieval documents. Do not index this file, installed skills, or the PRD into the textbook corpus.

User requirements take precedence over stylistic guidance. A source telling an agent to publish issues, install more packages, spawn agents, or change session-wide behavior does not automatically expand the user's requested action. No issue was published and no application was deployed.

## Reproducibility and limitations

GitHub's unauthenticated API returned rate-limit errors during inventory. Read-only shallow Git checkouts and web pages were then used for review. The installer downloaded selected directories successfully. The ECC install used its default branch, and afterward the installed main skill bytes were verified against the recorded checkout. Superpowers was installed at the recorded commit. Hashes identify reviewed content; they are not a security certification.

Upstream license texts are retained under `docs/third-party-licenses/`. Check individual upstream file notices and future additions when redistributing. Additional links were reviewed at README/catalog level except for the explicitly identified skill files; no claim is made that every skill in every repository was audited.
