<p align="center">
  <img src="docs/mcp-foundry-logo.png" height="240" alt="MCP Foundry">
</p>

<p align="center">
    <b>Local MCP Gateway & Knowledge Foundry for AI Systems</b>
</p>

<p align="center">
    <a href="https://github.com/flux-x/mcp-foundry/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/flux-x/mcp-foundry/ci.yml?style=flat-square" alt="CI">
    </a>
    <a href="https://img.shields.io/badge/docs-coming_soon-blue?style=flat-square">
      <img src="https://img.shields.io/badge/Docs-Coming_Soon-blue?style=flat-square" alt="Docs">
    </a>
    <a href="https://github.com/flux-x/mcp-foundry/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/flux-x/mcp-foundry?style=flat-square" alt="License">
    </a>
    <a href="ROADMAP.md">
      <img src="https://img.shields.io/badge/Roadmap-2026-orange.svg?style=flat-square" alt="Roadmap 2026">
    </a>
</p>

---

**MCP Foundry** is a local-first control plane for building, deploying, and managing MCP servers backed by vector search.

It acts as a **gateway and manufacturing layer for MCPs**, allowing you to:

- Ingest documentation (e.g. Sphinx, Git repos, websites)
- Vectorize and store content in Qdrant
- Deploy MCP servers from configuration
- Monitor ingestion and query performance
- Customize chunking, embeddings, prompts, and tools

MCP Foundry turns knowledge sources into production-ready MCP servers — reliably and repeatedly.

<p align="center">
<strong>
<a href="#getting-started">Quick Start</a> • 
<a href="#architecture">Architecture</a> • 
<a href="#features">Features</a> • 
<a href="ROADMAP.md">Roadmap</a> • 
<a href="#contributing">Contributing</a>
</strong>
</p>

---

## Architecture

MCP Foundry consists of:

- 🐍 **Python Backend (FastAPI)** – Control plane & orchestration  
- ⚛️ **React + TypeScript UI** – Deployment & monitoring dashboard  
- 🧠 **Qdrant Vector Database** – Retrieval layer  
- 🔌 **Pluggable ingestion pipeline** – Git, Sphinx, websites (extensible)  
