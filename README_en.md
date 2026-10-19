# SeqCode MCP Server

English | [中文](./README.md)

<div align="center">

**Version 0.1.0**

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for the [SeqCode Registry](https://registry.seqco.de/) database

</div>

---

## Table of Contents

- [Overview](#overview)
- [About the SeqCode Registry](#about-the-seqcode-registry)
- [Features](#features)
- [Installation](#installation)
- [Configuration & Usage](#configuration--usage)
- [Available Tools](#available-tools)
- [Tool Reference](#tool-reference)
- [API Data Models](#api-data-models)
- [Development Guide](#development-guide)
- [License](#license)

---

## Overview

> **⚠️ Disclaimer:** This is an **unofficial**, community-driven Model Context Protocol (MCP) server and is not affiliated with the SeqCode Registry organization. SeqCode and SeqCode Registry are trademarks/project names of their respective owners.

**SeqCode MCP** is a Model Context Protocol server that enables AI assistants (such as Claude) to query and retrieve microbial nomenclature information from the [SeqCode Registry](https://registry.seqco.de/) database.

The SeqCode Registry is the central repository for names of prokaryotes proposed under the SeqCode — a code of nomenclature for prokaryotes described from sequence data. This MCP server wraps all public REST API endpoints of the SeqCode Registry, providing **18 tool functions** covering name retrieval, genome queries, publication browsing, author/journal/subject browsing, register list queries, strain queries, and full-text search.

### How It Works

```
┌──────────────┐     stdio      ┌──────────────────┐     HTTPS     ┌─────────────────────┐
│  AI Assistant │ ◄──────────► │  SeqCode MCP     │ ◄──────────► │  SeqCode Registry   │
│  (Claude)    │               │  Server           │               │  REST API           │
└──────────────┘               └──────────────────┘               └─────────────────────┘
```

---

## About the SeqCode Registry

The SeqCode Registry is part of the [SeqCode initiative](https://isme-microbes.org/public/seqcode-initiative/), which provides a path forward for naming the uncultivated — prokaryotes (Bacteria and Archaea) described from genome sequence data.

### Key Statistics

| Data Type | Count (as of Oct 2026) |
|-----------|----------------------|
| Registered names | 48,431 |
| Validly published under SeqCode | 3,373 |
| Validated register lists | 264 |

### Data License

All information in the SeqCode Registry is released under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

---

## Features

- **18 MCP Tools**: Covering all public endpoints of the SeqCode Registry REST API
- **Async HTTP Client**: Built on `httpx` for high-performance async requests
- **Full-Text Search**: Search by names, genomes, publications, authors, or subjects
- **Pagination Support**: All list endpoints support pagination
- **Status Filtering**: Name lists can be filtered by `SeqCode`, `ICNP`, `valid`, etc.
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Zero Configuration**: Works out of the box — no authentication or API key required

---

## Installation

### Prerequisites

- Python ≥ 3.10
- pip or uv

### Install from Source

```bash
# Clone the project
git clone https://github.com/ZengZichao/SeqCode-MCP.git
cd SeqCode-MCP

# Install (virtual environment recommended)
pip install -e .

# Or using uv
uv pip install -e .
```

### Dependencies

| Dependency | Minimum Version | Description |
|------------|----------------|-------------|
| `mcp` | ≥ 1.0.0 | Model Context Protocol SDK |
| `httpx` | ≥ 0.27.0 | Async HTTP client |
| `anyio` | ≥ 4.0.0 | Async compatibility layer |

---

## Configuration & Usage

### Configure in Claude Desktop

Add the following to your Claude Desktop configuration file:

**Config file locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "seqcode": {
      "command": "python",
      "args": ["-m", "seqcode_mcp.server"],
      "cwd": "/path/to/seqcode-mcp"
    }
  }
}
```

> If installed via `pip install -e .`, you can use the entry point directly:
> ```json
> {
>   "mcpServers": {
>     "seqcode": {
>       "command": "seqcode-mcp"
>     }
>   }
> }
> ```

### Configure in Other MCP Clients

This server uses the standard **stdio** transport and is compatible with all MCP-supporting clients.

### Run Directly

```bash
# Option 1: Command-line entry point
seqcode-mcp

# Option 2: Python module
python -m seqcode_mcp.server
```

---

## Available Tools

The table below lists all 18 tools provided by this MCP server:

| # | Tool Name | Description | Category |
|---|-----------|-------------|----------|
| 1 | `check_api_status` | Check if the API is accessible | General |
| 2 | `list_names` | List names (with status filter & pagination) | Names |
| 3 | `get_name` | Get name details by ID | Names |
| 4 | `list_genomes` | List genomes | Genomes |
| 5 | `get_genome` | Get genome details by ID | Genomes |
| 6 | `list_type_genomes` | List type genomes of validly published names | Genomes |
| 7 | `list_registers` | List validated register lists | Registers |
| 8 | `get_register` | Get register list details by accession | Registers |
| 9 | `list_publications` | List publications | Publications |
| 10 | `get_publication` | Get publication details by ID | Publications |
| 11 | `list_authors` | List authors | Authors |
| 12 | `get_author` | Get author details and publications by ID | Authors |
| 13 | `list_journals` | List journals | Journals |
| 14 | `get_journal` | Get journal details and publications by name | Journals |
| 15 | `list_subjects` | List publication subjects | Subjects |
| 16 | `get_subject` | Get subject details and publications by ID | Subjects |
| 17 | `get_strain` | Get strain details by ID | Strains |
| 18 | `search_seqcode` | Full-text search (names/genomes/publications/authors/subjects) | Search |

---

## Tool Reference

### General

#### `check_api_status`
Check that the SeqCode REST API is accessible.

- **Parameters**: None
- **Example return**:
```json
{"status": "ok"}
```

### Names

#### `list_names`
Retrieve a paginated list of names, with optional status filtering.

- **Parameters**:
  - `page` (int, optional, default 1): Page number
  - `status` (str, optional): Filter by status — `public`, `automated`, `SeqCode`, `ICNP`, `ICNafp`, `valid`
- **Returns**: Paginated list of name items, each containing `id`, `name`, `url`, `uri`

#### `get_name`
Retrieve detailed information about a specific name by its numeric ID.

- **Parameters**:
  - `name_id` (int, required): Name ID
- **Returns**: Includes:
  - `rank`: Taxonomic rank (domain, phylum, class, order, family, genus, species, etc.)
  - `status_name`: Nomenclatural status (e.g., `Valid (SeqCode)`, `Valid (ICNP)`)
  - `syllabication`: Syllabification
  - `etymology`: Etymology
  - `description`: Description text (raw and html formats)
  - `formal_styling`: Formal citation styling
  - `nomenclatural_type`: Nomenclatural type (genome, name, or strain)
  - `classification`: Taxonomic classification (from domain to species)
  - `proposed_in`: Publication in which the name was proposed
  - `register`: Register list the name belongs to
  - `priority_date`: Priority date
  - `children`: Child names
  - `qc_warnings`: Quality check warnings

### Genomes

#### `get_genome`
Retrieve detailed information about a specific genome by its numeric ID.

- **Parameters**:
  - `genome_id` (int, required): Genome ID
- **Returns**: Includes:
  - `database` / `accession`: Database and accession (e.g., NCBI Assembly: GCA_988280555.1)
  - `kind`: Genome type (`isolate`, `mag`, `sag`, `enrichment`)
  - `genomic_features`: Genome features
    - Completeness, contamination, GC content
    - 16S/23S rRNA gene counts and completeness
    - tRNA count, coding density, codon table
    - N50, contigs, largest contig, assembly length
  - `names`: Associated names
  - `strain`: Associated strain info

### Registers

#### `get_register`
Retrieve detailed information about a register list by its accession.

- **Parameters**:
  - `acc` (str, required): Register accession (e.g., `r:0w5t6dud`; with or without `r:` prefix)
  - `page` (int, optional, default 1): Page number for the names list
- **Returns**:
  - Register list info (title, DOI, priority date)
  - Submitter and authors
  - Effective publication
  - List of names in the register

### Publications

#### `get_publication`
Retrieve detailed information about a publication by its numeric ID.

- **Parameters**:
  - `publication_id` (int, required): Publication ID
- **Returns**:
  - Citation, DOI, title, journal, journal location and date
  - Publication type, abstract
  - Authors list
  - Associated names
  - Subjects

### Search

#### `search_seqcode`
Full-text search the SeqCode Registry.

- **Parameters**:
  - `query` (str, required): Search query
  - `what` (str, optional, default `names`): Search type — `names`, `genomes`, `publications`, `authors`, `subjects`
- **Returns**: List of matching items, each containing:
  - `id`: Result ID
  - `name`: Result name/title
  - `url`: Registry page URL
  - `api_url`: API JSON endpoint

---

## API Data Models

This server wraps the SeqCode Registry REST API whose public endpoint is at `https://api.seqco.de/v1/`. Below is an overview of the primary data models:

### name_item
```json
{
  "id": 49702,
  "name": "Spongiamicus weybensis",
  "url": "https://api.seqco.de/v1/names/49702.json",
  "uri": "https://seqco.de/i:49702"
}
```

### genome_item
```json
{
  "id": 6326,
  "database": "assembly",
  "accession": "GCA_988280555.1",
  "kind": "mag",
  "url": "https://api.seqco.de/v1/genomes/6326.json",
  "uri": "https://seqco.de/g:6326"
}
```

### publication_item
```json
{
  "id": 3944,
  "citation": "Sun et al., 2025, Microbial Genomics",
  "doi": "10.1099/mgen.0.001351",
  "url": "https://api.seqco.de/v1/publications/3944.json"
}
```

### register_item
```json
{
  "acc_url": "seqco.de/r:0w5t6dud",
  "title": "Register list for Spongiamicus weybensis gen. nov. sp. nov. ...",
  "priority_date": "2026-09-23T09:58:21.630Z",
  "url": "https://api.seqco.de/v1/registers/r:0w5t6dud.json",
  "uri": "https://seqco.de/r:0w5t6dud"
}
```

### classification
The classification model is an array ordered from highest to lowest taxonomic rank, where the first value typically corresponds to a name with the rank of `domain`:

```json
[
  {"id": 753, "name": "Bacteria", "rank": "domain", "status_name": "Valid (ICNP)", ...},
  {"id": 49701, "name": "Spongiamicota", "rank": "phylum", ...},
  {"id": 49703, "name": "Spongiamicia", "rank": "class", ...},
  {"id": 49704, "name": "Spongiamicales", "rank": "order", ...},
  {"id": 49705, "name": "Spongiamicaceae", "rank": "family", ...},
  {"id": 49706, "name": "Spongiamicus", "rank": "genus", ...},
  {"id": 49702, "name": "Spongiamicus weybensis", "rank": "species", ...}
]
```

### Paginated Response

All list endpoints return a paginated structure:

```json
{
  "response": {
    "status": "ok",
    "message_type": "name",
    "count": 48431,
    "current_page": 1,
    "total_pages": 2422,
    "next": "https://api.seqco.de/v1/names.json?page=2"
  },
  "values": [...]
}
```

---

## Development Guide

### Project Structure

```
seqcode-mcp/
├── pyproject.toml              # Project config and dependencies
├── README.md                   # Chinese documentation
├── README_en.md                # English documentation (this file)
├── LICENSE                     # MIT License
├── .gitignore
└── src/
    └── seqcode_mcp/
        ├── __init__.py         # Package init
        ├── client.py           # SeqCode REST API async client
        └── server.py           # MCP server implementation
```

### Local Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check src/

# Run tests
pytest
```

### Adding New Tools

1. Add the corresponding API method in `client.py`
2. Add the tool definition to the `ALL_TOOLS` list in `server.py`
3. Add the routing branch in the `_dispatch_tool` function in `server.py`

### SeqCode REST API Reference

Full API documentation: [https://registry.seqco.de/page/api](https://registry.seqco.de/page/api)

API base URL: `https://api.seqco.de/v1/`

---

## License

This project is licensed under the [MIT License](./LICENSE).

SeqCode Registry data is released under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

---

<div align="center">

© 2026 SeqCode-MCP Contributors

</div>
