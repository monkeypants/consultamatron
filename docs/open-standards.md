# Open Standards for AI Agent Skills

A summary of the open standard landscape for agent skills — modular,
reusable packages of knowledge and instructions that extend what AI agents
can do.

## The Agent Skills Standard

Agent Skills is the dominant open standard in this space. It defines a
simple, filesystem-based format for packaging procedural knowledge,
instructions, scripts, and resources that AI agents can discover and load
on demand.

- **Specification**: https://agentskills.io/specification
- **GitHub**: https://github.com/agentskills/agentskills
- **Example skills**: https://github.com/anthropics/skills
- **License**: Apache 2.0 (code), CC-BY-4.0 (docs)

### Origin and timeline

| Date | Event |
|------|-------|
| Oct 2025 | Anthropic introduces Agent Skills in Claude Code |
| Dec 9, 2025 | Linux Foundation announces the Agentic AI Foundation (AAIF) |
| Dec 18, 2025 | Anthropic publishes Agent Skills as an open standard |
| Jan 2026 | VS Code stable ships agent skills support |
| Feb 2026 | 27+ agent products list compatibility |

Source: [Anthropic engineering blog](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills),
[SiliconANGLE](https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/)

### How it works

A skill is a directory containing a `SKILL.md` file with YAML frontmatter
and Markdown instructions, plus optional supporting files:

```
skill-name/
├── SKILL.md              # Required — metadata + instructions
├── scripts/              # Optional — executable code
├── references/           # Optional — additional docs
└── assets/               # Optional — templates, data, schemas
```

The `SKILL.md` frontmatter requires two fields:

```yaml
---
name: skill-name          # lowercase, hyphens, max 64 chars
description: >
  What this skill does and when to use it. Max 1024 chars.
---
```

Optional frontmatter fields: `license`, `compatibility`, `metadata`
(arbitrary key-value pairs), and `allowed-tools` (experimental).

### Progressive disclosure

The standard is built around efficient context management:

1. **Metadata** (~100 tokens) — `name` and `description` loaded at startup
   for all available skills
2. **Instructions** (<5000 tokens recommended) — full `SKILL.md` body
   loaded when the agent decides the skill is relevant
3. **Resources** (as needed) — files in `scripts/`, `references/`, `assets/`
   loaded only when referenced during execution

This means agents can have many skills available without paying a context
cost until a skill is actually activated.

### Adopting platforms

The following agent products support the Agent Skills format:

**Major platforms**: Claude Code, Claude.ai, OpenAI Codex, GitHub Copilot,
VS Code, Gemini CLI, Cursor

**Other adopters**: Amp, Roo Code, Goose, Letta, Firebender, Factory,
Databricks, Spring AI, Mistral Vibe, Piebald, Qodo, TRAE, OpenCode, Mux,
Autohand, Agentman, Command Code, VT Code, Ona

Sources: [agentskills.io](https://agentskills.io/home),
[VS Code docs](https://code.visualstudio.com/docs/copilot/customization/agent-skills),
[OpenAI Codex docs](https://developers.openai.com/codex/skills),
[Gemini CLI docs](https://geminicli.com/docs/cli/skills/)

### Platform-specific discovery paths

Each platform scans for skills in slightly different locations:

- **Claude Code**: `.claude/skills/` in project or user config
- **OpenAI Codex**: `.agents/skills/` from cwd up to repo root
- **GitHub Copilot / VS Code**: `.github/skills/` in the repository
- **Gemini CLI**: tiered discovery with project and user-level skill dirs

The `SKILL.md` format itself is identical across all platforms.

## Governance: Agentic AI Foundation (AAIF)

The Agent Skills standard lives within the broader governance of the
Agentic AI Foundation, a Linux Foundation directed fund announced
December 9, 2025.

- **Website**: https://aaif.io/
- **Announcement**: [Linux Foundation press release](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)

**Platinum members**: AWS, Anthropic, Block, Bloomberg, Cloudflare, Google,
Microsoft, OpenAI

AAIF hosts three initial projects:

1. **Model Context Protocol (MCP)** — how agents connect to tools and data
2. **Goose** — open source extensible AI agent (from Block)
3. **AGENTS.md** — project-level context and instructions for agents

Agent Skills is maintained by Anthropic and open to community contributions
via the GitHub repository. Whether it formally joins the AAIF project
portfolio is not yet confirmed as of Feb 2026.

Source: [TechCrunch](https://techcrunch.com/2025/12/09/openai-anthropic-and-block-join-new-linux-foundation-effort-to-standardize-the-ai-agent-era/),
[OpenAI announcement](https://openai.com/index/agentic-ai-foundation/)

## Related standards and how they differ

### AGENTS.md

A file placed in a repository root that gives any AI agent project-level
context: coding conventions, architecture, test commands, etc.

- **Scope**: per-project instructions — "how to work on this codebase"
- **Relationship to Skills**: complementary. AGENTS.md tells agents about
  the project; Skills teach agents domain procedures.
- **Source**: https://github.com/anthropics/agents (now under AAIF)

### Model Context Protocol (MCP)

An open protocol for connecting agents to external tools and data sources.

- **Scope**: the "plumbing" — APIs, databases, file systems, services
- **Relationship to Skills**: complementary. MCP provides tool access;
  Skills provide the procedural knowledge for how to use those tools.
- **Source**: https://modelcontextprotocol.io/

### How they fit together

An agent using all three:
- **MCP** connects it to your data and services
- **AGENTS.md** tells it how your specific project is structured
- **Agent Skills** give it domain expertise and repeatable workflows

## Criticisms and limitations

- **Instruction-only**: Skills package knowledge, not capabilities. A skill
  can tell an agent what to do but cannot grant it new tool access (that is
  MCP's job).
- **No execution guarantees**: the agent decides whether and how to follow
  skill instructions. Compliance depends on the model and runtime.
- **Discovery fragmentation**: each platform uses different filesystem paths
  for skill discovery, despite the identical `SKILL.md` format.
- **No registry or distribution**: there is no official package manager or
  registry for skills. Distribution is via git repos and copy-paste.
- **No versioning in spec**: the `metadata.version` field is optional and
  informational. There is no dependency resolution or compatibility
  mechanism.

Sources:
[Akshay Kokane / Medium](https://medium.com/data-science-collective/skills-md-vs-agent-tools-are-we-reinventing-the-wheel-1eb0308110a2),
[eesel.ai comparison](https://www.eesel.ai/blog/skills-md-vs-agents-md)

## Community resources

- **awesome-agent-skills**: https://github.com/skillmatic-ai/awesome-agent-skills
- **OpenAI skills catalog**: https://github.com/openai/skills
- **Anthropic example skills**: https://github.com/anthropics/skills
- **Reference library / validator**: https://github.com/agentskills/agentskills/tree/main/skills-ref

## Summary

The Agent Skills standard is the only serious open standard specifically
for packaging AI agent skills. It has achieved rapid cross-vendor adoption
(Anthropic, OpenAI, Google, Microsoft/GitHub all support it) in under four
months. The format is intentionally simple — a directory with a Markdown
file — which has been both its strength (easy adoption) and its limitation
(no built-in distribution, versioning, or execution guarantees). It
occupies a distinct and complementary niche alongside MCP (tool access) and
AGENTS.md (project context).
