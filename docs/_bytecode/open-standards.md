Agent Skills is the dominant open standard for packaging AI agent skills. Filesystem-based: a directory with `SKILL.md` (YAML frontmatter + markdown instructions), plus optional scripts/, references/, assets/. Progressive disclosure: metadata (~100 tokens) at startup, instructions (<5000 tokens) on activation, resources on reference.

Adopted by 27+ products: Claude Code, OpenAI Codex, GitHub Copilot, VS Code, Gemini CLI, Cursor, and others. Originated Anthropic Oct 2025, published as open standard Dec 2025. Discovery paths vary by platform (.claude/skills/, .agents/skills/, .github/skills/).

Governance under the Agentic AI Foundation (Linux Foundation, Dec 2025). AAIF also hosts MCP (tool/data connections) and AGENTS.md (project context). The three are complementary: MCP provides plumbing, AGENTS.md provides project context, Agent Skills provide domain procedures.

Limitations: instruction-only (no tool granting), no execution guarantees, fragmented discovery paths, no registry/distribution, no versioning mechanism.
