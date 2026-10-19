"""SeqCode MCP Server – exposes SeqCode Registry tools via the Model Context Protocol."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp import types
from mcp.server import NotificationOptions, Server

from .client import SeqCodeAPIError, SeqCodeClient

logger = logging.getLogger("seqcode-mcp")

SERVER_NAME = "seqcode-mcp"
SERVER_VERSION = "0.1.0"

# --------------------------------------------------------------------------- #
#  Tool definitions                                                           #
# --------------------------------------------------------------------------- #

ALL_TOOLS: list[types.Tool] = [
    # ---- Names --------------------------------------------------------
    types.Tool(
        name="list_names",
        description=(
            "Retrieve a paginated list of names from the SeqCode Registry. "
            "Each entry contains id, name, url and uri. "
            "Optionally filter by status: 'public', 'automated', 'SeqCode', "
            "'ICNP', 'ICNafp', or 'valid'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
                "status": {
                    "type": "string",
                    "description": (
                        "Filter names by status. One of: "
                        "'public', 'automated', 'SeqCode', 'ICNP', "
                        "'ICNafp', 'valid'."
                    ),
                    "enum": ["public", "automated", "SeqCode", "ICNP", "ICNafp", "valid"],
                },
            },
        },
    ),
    types.Tool(
        name="get_name",
        description=(
            "Retrieve detailed information about a specific name by its numeric ID. "
            "Returns rank, status, etymology, description, classification, "
            "nomenclatural type, proposed_in publication, and more."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name_id": {
                    "type": "integer",
                    "description": "The numeric ID of the name (e.g. 49702).",
                    "minimum": 1,
                },
            },
            "required": ["name_id"],
        },
    ),
    # ---- Genomes ------------------------------------------------------
    types.Tool(
        name="list_genomes",
        description="Retrieve a paginated list of genomes registered in the SeqCode Registry.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
        },
    ),
    types.Tool(
        name="get_genome",
        description=(
            "Retrieve detailed information about a specific genome by its numeric ID. "
            "Includes accession, kind (isolate/MAG/SAG/enrichment), "
            "genomic features (completeness, contamination, GC content, "
            "rRNA genes, tRNAs, N50, contigs, assembly length, etc.), "
            "associated names, and strain info."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "genome_id": {
                    "type": "integer",
                    "description": "The numeric ID of the genome (e.g. 6326).",
                    "minimum": 1,
                },
            },
            "required": ["genome_id"],
        },
    ),
    types.Tool(
        name="list_type_genomes",
        description=(
            "Retrieve a list of type genomes from validly published names "
            "and their corresponding names."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
        },
    ),
    # ---- Registers ----------------------------------------------------
    types.Tool(
        name="list_registers",
        description="Retrieve a paginated list of validated register lists from the SeqCode Registry.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
        },
    ),
    types.Tool(
        name="get_register",
        description=(
            "Retrieve detailed information about a specific register list by its accession. "
            "Includes submitter, authors, DOI, effective publication, "
            "and the list of names in the register."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "acc": {
                    "type": "string",
                    "description": (
                        "Register accession, e.g. 'r:0w5t6dud'. "
                        "Can be given with or without the 'r:' prefix."
                    ),
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for the names list (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
            "required": ["acc"],
        },
    ),
    # ---- Publications -------------------------------------------------
    types.Tool(
        name="list_publications",
        description="Retrieve a paginated list of publications referenced in the SeqCode Registry.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
        },
    ),
    types.Tool(
        name="get_publication",
        description=(
            "Retrieve detailed information about a specific publication by its numeric ID. "
            "Includes citation, DOI, title, journal, type, abstract, "
            "authors, associated names, and subjects."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "publication_id": {
                    "type": "integer",
                    "description": "The numeric ID of the publication (e.g. 3944).",
                    "minimum": 1,
                },
            },
            "required": ["publication_id"],
        },
    ),
    # ---- Authors ------------------------------------------------------
    types.Tool(
        name="list_authors",
        description="Retrieve a paginated list of publication authors from the SeqCode Registry.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
        },
    ),
    types.Tool(
        name="get_author",
        description=(
            "Retrieve detailed information about a specific author by their numeric ID, "
            "including their list of publications."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "author_id": {
                    "type": "integer",
                    "description": "The numeric ID of the author (e.g. 1).",
                    "minimum": 1,
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for the publications list (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
            "required": ["author_id"],
        },
    ),
    # ---- Journals -----------------------------------------------------
    types.Tool(
        name="list_journals",
        description="Retrieve a paginated list of publication journals from the SeqCode Registry.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
        },
    ),
    types.Tool(
        name="get_journal",
        description=(
            "Retrieve detailed information about a specific journal by name, "
            "including its list of publications."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The journal name (e.g. 'Microbial Genomics').",
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for the publications list (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
            "required": ["name"],
        },
    ),
    # ---- Subjects -----------------------------------------------------
    types.Tool(
        name="list_subjects",
        description="Retrieve a paginated list of publication subjects from the SeqCode Registry.",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "Page number (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
        },
    ),
    types.Tool(
        name="get_subject",
        description=(
            "Retrieve detailed information about a specific publication subject by its numeric ID, "
            "including associated publications."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "subject_id": {
                    "type": "integer",
                    "description": "The numeric ID of the subject (e.g. 1).",
                    "minimum": 1,
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for the publications list (1-based). Default: 1.",
                    "default": 1,
                    "minimum": 1,
                },
            },
            "required": ["subject_id"],
        },
    ),
    # ---- Strains ------------------------------------------------------
    types.Tool(
        name="get_strain",
        description=(
            "Retrieve detailed information about a specific strain by its numeric ID. "
            "Includes strain numbers, typified names, genomes, and strain info DOIs."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "strain_id": {
                    "type": "integer",
                    "description": "The numeric ID of the strain (e.g. 42239).",
                    "minimum": 1,
                },
            },
            "required": ["strain_id"],
        },
    ),
    # ---- Search -------------------------------------------------------
    types.Tool(
        name="search_seqcode",
        description=(
            "Search the SeqCode Registry for names, genomes, publications, authors, "
            "or subjects. Returns a list of matching items with id, name, url, "
            "and api_url for each result. Use the specific 'get_*' tools for "
            "detailed information about individual results."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string.",
                },
                "what": {
                    "type": "string",
                    "description": "What to search for. Default: 'names'.",
                    "enum": ["names", "genomes", "publications", "authors", "subjects"],
                    "default": "names",
                },
            },
            "required": ["query"],
        },
    ),
    # ---- API Status ---------------------------------------------------
    types.Tool(
        name="check_api_status",
        description="Check that the SeqCode Registry REST API is accessible.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


# --------------------------------------------------------------------------- #
#  Server factory                                                              #
# --------------------------------------------------------------------------- #


def create_server() -> Server:
    """Create and configure the MCP server with all SeqCode tools."""
    client = SeqCodeClient()

    async def handle_list_tools(ctx, params):
        return types.ListToolsResult(tools=ALL_TOOLS)

    async def handle_call_tool(ctx, params):
        """Dispatch a tool call and return a CallToolResult."""
        name = params.name
        arguments = params.arguments if params.arguments is not None else {}

        try:
            result = await _dispatch_tool(client, name, arguments)
        except SeqCodeAPIError as exc:
            error_msg = f"SeqCode API error: {exc}"
            if exc.status_code:
                error_msg += f" (HTTP {exc.status_code})"
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_msg)],
                isError=True,
            )
        except ValueError as exc:
            logger.warning("Invalid argument for tool '%s': %s", name, exc)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Invalid argument: {exc}")],
                isError=True,
            )
        except Exception as exc:
            logger.exception("Unexpected error in tool '%s'", name)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Unexpected error: {exc}")],
                isError=True,
            )

        # Format result as readable JSON text
        text = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=text)],
        )

    server = Server(
        SERVER_NAME,
        version=SERVER_VERSION,
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )
    return server


async def _dispatch_tool(
    client: SeqCodeClient, name: str, args: dict[str, Any]
) -> Any:
    """Route a tool call to the appropriate client method."""

    if name == "check_api_status":
        return await client.get_status()

    elif name == "list_names":
        return await client.list_names(
            page=args.get("page", 1),
            status=args.get("status"),
        )

    elif name == "get_name":
        name_id = args.get("name_id")
        if name_id is None:
            raise ValueError("'name_id' is required")
        try:
            name_id = int(name_id)
        except (TypeError, ValueError):
            raise ValueError(f"'name_id' must be an integer, got: {name_id!r}")
        return await client.get_name(name_id)

    elif name == "list_genomes":
        return await client.list_genomes(page=args.get("page", 1))

    elif name == "get_genome":
        genome_id = args.get("genome_id")
        if genome_id is None:
            raise ValueError("'genome_id' is required")
        try:
            genome_id = int(genome_id)
        except (TypeError, ValueError):
            raise ValueError(f"'genome_id' must be an integer, got: {genome_id!r}")
        return await client.get_genome(genome_id)

    elif name == "list_type_genomes":
        return await client.list_type_genomes(page=args.get("page", 1))

    elif name == "list_registers":
        return await client.list_registers(page=args.get("page", 1))

    elif name == "get_register":
        acc = args.get("acc", "")
        if not acc:
            raise ValueError("'acc' is required")
        # Ensure the accession has the 'r:' prefix
        if not acc.startswith("r:"):
            acc = f"r:{acc}"
        return await client.get_register(acc, page=args.get("page", 1))

    elif name == "list_publications":
        return await client.list_publications(page=args.get("page", 1))

    elif name == "get_publication":
        pub_id = args.get("publication_id")
        if pub_id is None:
            raise ValueError("'publication_id' is required")
        try:
            pub_id = int(pub_id)
        except (TypeError, ValueError):
            raise ValueError(f"'publication_id' must be an integer, got: {pub_id!r}")
        return await client.get_publication(pub_id)

    elif name == "list_authors":
        return await client.list_authors(page=args.get("page", 1))

    elif name == "get_author":
        author_id = args.get("author_id")
        if author_id is None:
            raise ValueError("'author_id' is required")
        try:
            author_id = int(author_id)
        except (TypeError, ValueError):
            raise ValueError(f"'author_id' must be an integer, got: {author_id!r}")
        return await client.get_author(author_id, page=args.get("page", 1))

    elif name == "list_journals":
        return await client.list_journals(page=args.get("page", 1))

    elif name == "get_journal":
        journal_name = args.get("name")
        if not journal_name:
            raise ValueError("'name' is required")
        return await client.get_journal(journal_name, page=args.get("page", 1))

    elif name == "list_subjects":
        return await client.list_subjects(page=args.get("page", 1))

    elif name == "get_subject":
        subject_id = args.get("subject_id")
        if subject_id is None:
            raise ValueError("'subject_id' is required")
        try:
            subject_id = int(subject_id)
        except (TypeError, ValueError):
            raise ValueError(f"'subject_id' must be an integer, got: {subject_id!r}")
        return await client.get_subject(subject_id, page=args.get("page", 1))

    elif name == "get_strain":
        strain_id = args.get("strain_id")
        if strain_id is None:
            raise ValueError("'strain_id' is required")
        try:
            strain_id = int(strain_id)
        except (TypeError, ValueError):
            raise ValueError(f"'strain_id' must be an integer, got: {strain_id!r}")
        return await client.get_strain(strain_id)

    elif name == "search_seqcode":
        query = args.get("query", "")
        if not query:
            raise ValueError("'query' is required")
        what = args.get("what", "names")
        return await client.search(query, what)

    else:
        raise ValueError(f"Unknown tool: {name}")


# --------------------------------------------------------------------------- #
#  Entry point (stdio transport)                                              #
# --------------------------------------------------------------------------- #


def main() -> None:
    """Run the SeqCode MCP server using stdio transport."""
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    async def _run() -> None:
        server = create_server()
        from mcp.server.stdio import stdio_server

        init_options = server.create_initialization_options(
            notification_options=NotificationOptions(),
        )

        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, init_options)

    asyncio.run(_run())


if __name__ == "__main__":
    main()
