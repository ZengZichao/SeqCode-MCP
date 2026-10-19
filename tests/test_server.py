"""Tests for the SeqCode MCP server and client."""

from unittest.mock import AsyncMock, patch

import pytest

from seqcode_mcp.client import SeqCodeAPIError, SeqCodeClient
from seqcode_mcp.server import ALL_TOOLS, _dispatch_tool, create_server

# --------------------------------------------------------------------------- #
#  Client tests                                                               #
# --------------------------------------------------------------------------- #


@pytest.fixture
def client():
    return SeqCodeClient()


def test_client_base_url():
    """The client should strip trailing slashes from the base URL."""
    c = SeqCodeClient(base_url="https://api.seqco.de/v1/")
    assert c._base_url == "https://api.seqco.de/v1"


def test_client_default_timeout():
    """The client should have a sensible default timeout."""
    c = SeqCodeClient()
    assert c._timeout == 30.0


@pytest.mark.asyncio
async def test_client_get_name(client):
    """get_name should call the correct endpoint."""
    mock_response = {"response": {"status": "ok"}, "id": 1, "name": "Test"}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_name(1)
        mock_req.assert_called_once_with("/names/1.json")
        assert result == mock_response


@pytest.mark.asyncio
async def test_client_list_names(client):
    """list_names should pass page and status parameters."""
    mock_response = {"response": {"status": "ok"}, "values": []}

    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.list_names(page=2, status="SeqCode")
        mock_req.assert_called_once_with("/names.json", page=2, status="SeqCode")
        assert result == mock_response


@pytest.mark.asyncio
async def test_client_get_genome(client):
    """get_genome should call the correct endpoint."""
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"response": {"status": "ok"}}
        await client.get_genome(6326)
        mock_req.assert_called_once_with("/genomes/6326.json")


@pytest.mark.asyncio
async def test_client_get_register(client):
    """get_register should call the correct endpoint."""
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"response": {"status": "ok"}}
        await client.get_register("r:0w5t6dud", page=1)
        mock_req.assert_called_once_with("/registers/r:0w5t6dud.json", page=1)


@pytest.mark.asyncio
async def test_client_get_publication(client):
    """get_publication should call the correct endpoint."""
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"response": {"status": "ok"}}
        await client.get_publication(3944)
        mock_req.assert_called_once_with("/publications/3944.json")


@pytest.mark.asyncio
async def test_client_get_strain(client):
    """get_strain should call the correct endpoint."""
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"response": {"status": "ok"}}
        await client.get_strain(42239)
        mock_req.assert_called_once_with("/strains/42239.json")


@pytest.mark.asyncio
async def test_client_get_journal(client):
    """get_journal should call the correct endpoint."""
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"response": {"status": "ok"}}
        await client.get_journal("Microbial Genomics", page=1)
        mock_req.assert_called_once_with(
            "/journals/Microbial Genomics.json", page=1
        )


# --------------------------------------------------------------------------- #
#  Server tests                                                               #
# --------------------------------------------------------------------------- #


def test_all_tools_count():
    """The server should expose exactly 18 tools."""
    assert len(ALL_TOOLS) == 18


def test_tool_names():
    """All expected tool names should be present."""
    expected_names = {
        "check_api_status",
        "list_names",
        "get_name",
        "list_genomes",
        "get_genome",
        "list_type_genomes",
        "list_registers",
        "get_register",
        "list_publications",
        "get_publication",
        "list_authors",
        "get_author",
        "list_journals",
        "get_journal",
        "list_subjects",
        "get_subject",
        "get_strain",
        "search_seqcode",
    }
    actual_names = {t.name for t in ALL_TOOLS}
    assert actual_names == expected_names


def test_tools_have_input_schema():
    """Every tool should have an input_schema."""
    for tool in ALL_TOOLS:
        assert tool.input_schema is not None
        assert "type" in tool.input_schema
        assert tool.input_schema["type"] == "object"


def test_tools_have_descriptions():
    """Every tool should have a non-empty description."""
    for tool in ALL_TOOLS:
        assert tool.description
        assert len(tool.description) > 20


def test_required_params_are_declared():
    """Tools with required params should declare them in inputSchema."""
    tools_with_required = {
        "get_name": ["name_id"],
        "get_genome": ["genome_id"],
        "get_publication": ["publication_id"],
        "get_author": ["author_id"],
        "get_journal": ["name"],
        "get_subject": ["subject_id"],
        "get_strain": ["strain_id"],
        "get_register": ["acc"],
        "search_seqcode": ["query"],
    }
    for tool in ALL_TOOLS:
        if tool.name in tools_with_required:
            required = tools_with_required[tool.name]
            assert set(required).issubset(
                set(tool.input_schema.get("required", []))
            ), f"Tool '{tool.name}' should declare required params: {required}"


def test_create_server():
    """create_server should return a Server instance."""
    server = create_server()
    assert server is not None
    assert server.name == "seqcode-mcp"


# --------------------------------------------------------------------------- #
#  Dispatch tests                                                             #
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_dispatch_get_name():
    """Dispatching get_name should call client.get_name."""
    client = SeqCodeClient()
    mock_data = {"id": 49702, "name": "Spongiamicus weybensis"}

    with patch.object(client, "get_name", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "get_name", {"name_id": 49702})
        mock_method.assert_called_once_with(49702)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_names():
    """Dispatching list_names should call client.list_names."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}

    with patch.object(client, "list_names", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(
            client, "list_names", {"page": 2, "status": "SeqCode"}
        )
        mock_method.assert_called_once_with(page=2, status="SeqCode")
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_get_register_adds_prefix():
    """Dispatching get_register should add 'r:' prefix if missing."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}}

    with patch.object(client, "get_register", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        await _dispatch_tool(client, "get_register", {"acc": "0w5t6dud"})
        mock_method.assert_called_once_with("r:0w5t6dud", page=1)


@pytest.mark.asyncio
async def test_dispatch_get_register_keeps_prefix():
    """Dispatching get_register should keep the 'r:' prefix if present."""
    client = SeqCodeClient()

    with patch.object(client, "get_register", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = {"response": {"status": "ok"}}
        await _dispatch_tool(client, "get_register", {"acc": "r:0w5t6dud"})
        mock_method.assert_called_once_with("r:0w5t6dud", page=1)


@pytest.mark.asyncio
async def test_dispatch_unknown_tool():
    """Dispatching an unknown tool should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="Unknown tool"):
        await _dispatch_tool(client, "nonexistent_tool", {})


@pytest.mark.asyncio
async def test_dispatch_missing_required_param():
    """Dispatching a tool without required params should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'name_id' is required"):
        await _dispatch_tool(client, "get_name", {})


@pytest.mark.asyncio
async def test_dispatch_api_error_propagates():
    """SeqCodeAPIError should propagate through dispatch."""
    client = SeqCodeClient()
    with patch.object(client, "get_name", new_callable=AsyncMock) as mock_method:
        mock_method.side_effect = SeqCodeAPIError("Not found", status_code=404)
        with pytest.raises(SeqCodeAPIError):
            await _dispatch_tool(client, "get_name", {"name_id": 999999})


# --------------------------------------------------------------------------- #
#  Additional dispatch tests (parameter validation)                            #
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_dispatch_get_name_invalid_id():
    """Dispatching get_name with a non-integer ID should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="must be an integer"):
        await _dispatch_tool(client, "get_name", {"name_id": "abc"})


@pytest.mark.asyncio
async def test_dispatch_get_genome_invalid_id():
    """Dispatching get_genome with a non-integer ID should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="must be an integer"):
        await _dispatch_tool(client, "get_genome", {"genome_id": "xyz"})


@pytest.mark.asyncio
async def test_dispatch_get_publication_invalid_id():
    """Dispatching get_publication with a non-integer ID should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="must be an integer"):
        await _dispatch_tool(client, "get_publication", {"publication_id": "not-a-number"})


@pytest.mark.asyncio
async def test_dispatch_get_author_invalid_id():
    """Dispatching get_author with a non-integer ID should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="must be an integer"):
        await _dispatch_tool(client, "get_author", {"author_id": "not-a-number"})


@pytest.mark.asyncio
async def test_dispatch_get_subject_invalid_id():
    """Dispatching get_subject with a non-integer ID should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="must be an integer"):
        await _dispatch_tool(client, "get_subject", {"subject_id": "bad"})


@pytest.mark.asyncio
async def test_dispatch_get_strain_invalid_id():
    """Dispatching get_strain with a non-integer ID should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="must be an integer"):
        await _dispatch_tool(client, "get_strain", {"strain_id": "abc"})


@pytest.mark.asyncio
async def test_dispatch_get_genome_missing_required_param():
    """Dispatching get_genome without genome_id should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'genome_id' is required"):
        await _dispatch_tool(client, "get_genome", {})


@pytest.mark.asyncio
async def test_dispatch_get_publication_missing_required_param():
    """Dispatching get_publication without publication_id should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'publication_id' is required"):
        await _dispatch_tool(client, "get_publication", {})


@pytest.mark.asyncio
async def test_dispatch_get_author_missing_required_param():
    """Dispatching get_author without author_id should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'author_id' is required"):
        await _dispatch_tool(client, "get_author", {})


@pytest.mark.asyncio
async def test_dispatch_get_subject_missing_required_param():
    """Dispatching get_subject without subject_id should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'subject_id' is required"):
        await _dispatch_tool(client, "get_subject", {})


@pytest.mark.asyncio
async def test_dispatch_get_strain_missing_required_param():
    """Dispatching get_strain without strain_id should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'strain_id' is required"):
        await _dispatch_tool(client, "get_strain", {})


@pytest.mark.asyncio
async def test_dispatch_get_journal_missing_required_param():
    """Dispatching get_journal without name should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'name' is required"):
        await _dispatch_tool(client, "get_journal", {})


@pytest.mark.asyncio
async def test_dispatch_search_missing_query():
    """Dispatching search_seqcode without query should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'query' is required"):
        await _dispatch_tool(client, "search_seqcode", {})


@pytest.mark.asyncio
async def test_dispatch_get_register_missing_acc():
    """Dispatching get_register without acc should raise ValueError."""
    client = SeqCodeClient()
    with pytest.raises(ValueError, match="'acc' is required"):
        await _dispatch_tool(client, "get_register", {})


# --------------------------------------------------------------------------- #
#  Dispatch tests for remaining tools                                         #
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_dispatch_check_api_status():
    """Dispatching check_api_status should call client.get_status."""
    client = SeqCodeClient()
    mock_data = {"status": "ok"}
    with patch.object(client, "get_status", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "check_api_status", {})
        mock_method.assert_called_once()
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_genomes():
    """Dispatching list_genomes should call client.list_genomes."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}
    with patch.object(client, "list_genomes", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "list_genomes", {"page": 3})
        mock_method.assert_called_once_with(page=3)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_type_genomes():
    """Dispatching list_type_genomes should call client.list_type_genomes."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}
    with patch.object(client, "list_type_genomes", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "list_type_genomes", {"page": 1})
        mock_method.assert_called_once_with(page=1)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_registers():
    """Dispatching list_registers should call client.list_registers."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}
    with patch.object(client, "list_registers", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "list_registers", {"page": 1})
        mock_method.assert_called_once_with(page=1)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_publications():
    """Dispatching list_publications should call client.list_publications."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}
    with patch.object(client, "list_publications", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "list_publications", {"page": 1})
        mock_method.assert_called_once_with(page=1)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_authors():
    """Dispatching list_authors should call client.list_authors."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}
    with patch.object(client, "list_authors", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "list_authors", {"page": 1})
        mock_method.assert_called_once_with(page=1)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_journals():
    """Dispatching list_journals should call client.list_journals."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}
    with patch.object(client, "list_journals", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "list_journals", {"page": 1})
        mock_method.assert_called_once_with(page=1)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_list_subjects():
    """Dispatching list_subjects should call client.list_subjects."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}, "values": []}
    with patch.object(client, "list_subjects", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "list_subjects", {"page": 1})
        mock_method.assert_called_once_with(page=1)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_get_journal():
    """Dispatching get_journal should call client.get_journal."""
    client = SeqCodeClient()
    mock_data = {"response": {"status": "ok"}}
    with patch.object(client, "get_journal", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(client, "get_journal", {"name": "Nature", "page": 2})
        mock_method.assert_called_once_with("Nature", page=2)
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_search_seqcode():
    """Dispatching search_seqcode should call client.search."""
    client = SeqCodeClient()
    mock_data = [{"id": 1, "name": "Test", "url": "...", "api_url": "..."}]
    with patch.object(client, "search", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        result = await _dispatch_tool(
            client, "search_seqcode", {"query": "Bacillus", "what": "genomes"}
        )
        mock_method.assert_called_once_with("Bacillus", "genomes")
        assert result == mock_data


@pytest.mark.asyncio
async def test_dispatch_search_seqcode_default_what():
    """Dispatching search_seqcode without 'what' should default to 'names'."""
    client = SeqCodeClient()
    mock_data = []
    with patch.object(client, "search", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_data
        await _dispatch_tool(client, "search_seqcode", {"query": "test"})
        mock_method.assert_called_once_with("test", "names")


# --------------------------------------------------------------------------- #
#  Search extraction helper tests                                             #
# --------------------------------------------------------------------------- #


def test_extract_search_results_names():
    """_extract_search_results should parse name links from HTML."""
    from seqcode_mcp.client import _extract_search_results

    html = """
    <html>
    <body>
        <a href="/names/49702"><span>Spongiamicus weybensis</span></a>
        <a href="/names/49703"><span>Spongiamicus other</span></a>
        <a href="/genomes/6326"><span>Some genome</span></a>
    </body>
    </html>
    """
    results = _extract_search_results(html, "names")
    assert len(results) == 2
    assert results[0]["id"] == 49702
    assert "Spongiamicus" in results[0]["name"]
    assert results[0]["url"] == "https://registry.seqco.de/names/49702"
    assert results[0]["api_url"] == "https://api.seqco.de/v1/names/49702.json"


def test_extract_search_results_dedup():
    """_extract_search_results should deduplicate by ID."""
    from seqcode_mcp.client import _extract_search_results

    html = """
    <a href="/names/42">Name A</a>
    <a href="/names/42">Name A duplicate</a>
    <a href="/names/43">Name B</a>
    """
    results = _extract_search_results(html, "names")
    assert len(results) == 2
    ids = [r["id"] for r in results]
    assert ids == [42, 43]


def test_extract_search_results_unknown_what():
    """_extract_search_results should return empty list for unknown type."""
    from seqcode_mcp.client import _extract_search_results

    results = _extract_search_results("<html></html>", "unknown_type")
    assert results == []


def test_extract_search_results_empty_html():
    """_extract_search_results should return empty list for HTML without matches."""
    from seqcode_mcp.client import _extract_search_results

    results = _extract_search_results("<html><body>no links here</body></html>", "names")
    assert results == []


def test_strip_tags():
    """_strip_tags should remove HTML tags and decode entities."""
    from seqcode_mcp.client import _strip_tags

    assert _strip_tags("<b>Hello</b>") == "Hello"
    assert _strip_tags("a &amp; b") == "a & b"
    assert _strip_tags("&lt;tag&gt;") == "<tag>"
    assert _strip_tags("&quot;quoted&quot;") == '"quoted"'
    assert _strip_tags("&#39;apostrophe&#39;") == "'apostrophe'"
    assert _strip_tags("&nbsp;spaces&nbsp;") == "spaces"


# --------------------------------------------------------------------------- #
#  Client request error handling tests                                        #
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_client_request_404():
    """_request should raise SeqCodeAPIError for 404 responses."""
    import httpx

    from seqcode_mcp.client import SeqCodeAPIError, SeqCodeClient

    client = SeqCodeClient()
    mock_resp = httpx.Response(404, text="Not Found", request=httpx.Request("GET", "https://test"))

    with patch.object(client, "_get_client", new_callable=AsyncMock) as mock_get:
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_resp)
        mock_http_client.is_closed = False
        mock_get.return_value = mock_http_client

        with pytest.raises(SeqCodeAPIError, match="404"):
            await client._request("/names/999999.json")


@pytest.mark.asyncio
async def test_client_request_500():
    """_request should raise SeqCodeAPIError for 500 responses."""
    import httpx

    from seqcode_mcp.client import SeqCodeAPIError, SeqCodeClient

    client = SeqCodeClient()
    mock_resp = httpx.Response(500, text="Internal Server Error", request=httpx.Request("GET", "https://test"))

    with patch.object(client, "_get_client", new_callable=AsyncMock) as mock_get:
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_resp)
        mock_http_client.is_closed = False
        mock_get.return_value = mock_http_client

        with pytest.raises(SeqCodeAPIError, match="500"):
            await client._request("/names.json")


@pytest.mark.asyncio
async def test_client_request_empty_response():
    """_request should raise SeqCodeAPIError for empty response body."""
    import httpx

    from seqcode_mcp.client import SeqCodeAPIError, SeqCodeClient

    client = SeqCodeClient()
    mock_resp = httpx.Response(200, text="", request=httpx.Request("GET", "https://test"))

    with patch.object(client, "_get_client", new_callable=AsyncMock) as mock_get:
        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_resp)
        mock_http_client.is_closed = False
        mock_get.return_value = mock_http_client

        with pytest.raises(SeqCodeAPIError, match="empty response"):
            await client._request("/names.json")
