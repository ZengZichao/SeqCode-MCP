"""Async HTTP client for the SeqCode Registry REST API."""

from __future__ import annotations

import re
from typing import Any

import httpx
from typing_extensions import Self

# Public API base URL (documented at https://registry.seqco.de/page/api)
API_BASE_URL = "https://api.seqco.de/v1"

# Fallback to the registry website JSON endpoints
REGISTRY_BASE_URL = "https://registry.seqco.de"

DEFAULT_TIMEOUT = 30.0


class SeqCodeAPIError(Exception):
    """Raised when the SeqCode API returns an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SeqCodeClient:
    """Lightweight async client wrapping all documented SeqCode REST endpoints.

    Every method returns the parsed JSON response (Python ``dict`` / ``list``)
    as-is, so callers can work with the full data returned by the API.
    """

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    # -- lifecycle -------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "seqcode-mcp/0.1.0",
                },
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    # -- internal helper -------------------------------------------------

    async def _request(self, path: str, **params: Any) -> Any:
        client = await self._get_client()
        try:
            resp = await client.get(path, params=params)
        except httpx.HTTPError as exc:
            raise SeqCodeAPIError(f"Network error contacting SeqCode API: {exc}") from exc

        if resp.status_code == 404:
            raise SeqCodeAPIError(
                f"SeqCode API returned 404 for '{path}' – resource not found.",
                status_code=404,
            )
        if resp.status_code >= 400:
            raise SeqCodeAPIError(
                f"SeqCode API error {resp.status_code}: {resp.text[:300]}",
                status_code=resp.status_code,
            )
        if not resp.text:
            raise SeqCodeAPIError("SeqCode API returned an empty response body.")
        try:
            return resp.json()
        except Exception as exc:
            raise SeqCodeAPIError(f"Failed to decode JSON response: {exc}") from exc

    # ------------------------------------------------------------------ #
    #  Generic                                                          #
    # ------------------------------------------------------------------ #

    async def get_status(self) -> dict:
        """GET /page/status.json – check that the API is accessible."""
        return await self._request("/page/status.json")

    # ------------------------------------------------------------------ #
    #  Names                                                            #
    # ------------------------------------------------------------------ #

    async def list_names(self, page: int = 1, status: str | None = None) -> dict:
        """GET /names.json – paginated list of names.

        Parameters
        ----------
        page:
            Page number (1-based).
        status:
            Filter by status: ``public``, ``automated``, ``SeqCode``,
            ``ICNP``, ``ICNafp``, or ``valid``.
        """
        params: dict[str, Any] = {"page": page}
        if status:
            params["status"] = status
        return await self._request("/names.json", **params)

    async def get_name(self, name_id: int) -> dict:
        """GET /names/(id).json – detailed data for a single name."""
        return await self._request(f"/names/{name_id}.json")

    # ------------------------------------------------------------------ #
    #  Genomes                                                          #
    # ------------------------------------------------------------------ #

    async def list_genomes(self, page: int = 1) -> dict:
        """GET /genomes.json – paginated list of genomes."""
        return await self._request("/genomes.json", page=page)

    async def get_genome(self, genome_id: int) -> dict:
        """GET /genomes/(id).json – detailed data for a single genome."""
        return await self._request(f"/genomes/{genome_id}.json")

    async def list_type_genomes(self, page: int = 1) -> dict:
        """GET /type-genomes.json – type genomes from validly published names."""
        return await self._request("/type-genomes.json", page=page)

    # ------------------------------------------------------------------ #
    #  Registers                                                        #
    # ------------------------------------------------------------------ #

    async def list_registers(self, page: int = 1) -> dict:
        """GET /registers.json – list of validated register lists."""
        return await self._request("/registers.json", page=page)

    async def get_register(self, acc: str, page: int = 1) -> dict:
        """GET /registers/(acc).json – data for a single register list.

        ``acc`` is the register accession, e.g. ``r:0w5t6dud``.
        """
        return await self._request(f"/registers/{acc}.json", page=page)

    # ------------------------------------------------------------------ #
    #  Publications                                                      #
    # ------------------------------------------------------------------ #

    async def list_publications(self, page: int = 1) -> dict:
        """GET /publications.json – paginated list of publications."""
        return await self._request("/publications.json", page=page)

    async def get_publication(self, pub_id: int) -> dict:
        """GET /publications/(id).json – detailed data for a publication."""
        return await self._request(f"/publications/{pub_id}.json")

    # ------------------------------------------------------------------ #
    #  Authors                                                           #
    # ------------------------------------------------------------------ #

    async def list_authors(self, page: int = 1) -> dict:
        """GET /authors.json – paginated list of authors."""
        return await self._request("/authors.json", page=page)

    async def get_author(self, author_id: int, page: int = 1) -> dict:
        """GET /authors/(id).json – data for an author with their publications."""
        return await self._request(f"/authors/{author_id}.json", page=page)

    # ------------------------------------------------------------------ #
    #  Journals                                                          #
    # ------------------------------------------------------------------ #

    async def list_journals(self, page: int = 1) -> dict:
        """GET /journals.json – paginated list of journals."""
        return await self._request("/journals.json", page=page)

    async def get_journal(self, name: str, page: int = 1) -> dict:
        """GET /journals/(name).json – data for a journal with its publications."""
        return await self._request(f"/journals/{name}.json", page=page)

    # ------------------------------------------------------------------ #
    #  Subjects                                                          #
    # ------------------------------------------------------------------ #

    async def list_subjects(self, page: int = 1) -> dict:
        """GET /subjects.json – paginated list of publication subjects."""
        return await self._request("/subjects.json", page=page)

    async def get_subject(self, subject_id: int, page: int = 1) -> dict:
        """GET /subjects/(id).json – data for a subject with its publications."""
        return await self._request(f"/subjects/{subject_id}.json", page=page)

    # ------------------------------------------------------------------ #
    #  Strains                                                           #
    # ------------------------------------------------------------------ #

    async def get_strain(self, strain_id: int) -> dict:
        """GET /strains/(id).json – data for a strain."""
        return await self._request(f"/strains/{strain_id}.json")

    # ------------------------------------------------------------------ #
    #  Search (website endpoint)                                         #
    # ------------------------------------------------------------------ #

    async def search(
        self,
        query: str,
        what: str = "names",
    ) -> list[dict]:
        """Search the SeqCode Registry website.

        Parameters
        ----------
        query:
            The search term.
        what:
            What to search for: ``names``, ``genomes``, ``publications``,
            ``authors``, or ``subjects``.
        """
        # The search endpoint is a website feature that returns HTML.
        # We use a separate httpx call without the API base_url.
        client = await self._get_client()
        url = "https://registry.seqco.de/search"
        try:
            resp = await client.get(
                url,
                params={"q": query, "what": what},
                headers={"Accept": "text/html"},
            )
        except httpx.HTTPError as exc:
            raise SeqCodeAPIError(f"Search request failed: {exc}") from exc

        if resp.status_code >= 400:
            raise SeqCodeAPIError(
                f"Search returned status {resp.status_code}",
                status_code=resp.status_code,
            )

        # The search results page lists matching items as links.
        # We do a lightweight extraction of links to names/genomes/etc.
        return _extract_search_results(resp.text, what)


# ------------------------------------------------------------------ #
#  Helpers                                                           #
# ------------------------------------------------------------------ #

_LINK_PATTERNS = {
    "names": re.compile(r'href="/names/(\d+)"[^>]*>([^<]*(?:<(?!/a>)[^<]*)*)', re.DOTALL),
    "genomes": re.compile(r'href="/genomes/(\d+)"[^>]*>([^<]*(?:<(?!/a>)[^<]*)*)', re.DOTALL),
    "publications": re.compile(r'href="/publications/(\d+)"[^>]*>([^<]*(?:<(?!/a>)[^<]*)*)', re.DOTALL),
    "authors": re.compile(r'href="/authors/(\d+)"[^>]*>([^<]*(?:<(?!/a>)[^<]*)*)', re.DOTALL),
    "subjects": re.compile(r'href="/subjects/(\d+)"[^>]*>([^<]*(?:<(?!/a>)[^<]*)*)', re.DOTALL),
}


def _strip_tags(text: str) -> str:
    """Remove HTML tags and decode common entities."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&#8220;", '"').replace("&#8221;", '"')
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&nbsp;", " ").strip()
    return text


def _extract_search_results(html: str, what: str) -> list[dict]:
    """Extract result items from the search results HTML page."""
    results: list[dict] = []
    pattern = _LINK_PATTERNS.get(what)
    if pattern is None:
        return results

    seen: set[str] = set()
    for match in pattern.finditer(html):
        item_id = match.group(1)
        if item_id in seen:
            continue
        seen.add(item_id)
        label = _strip_tags(match.group(2))
        results.append({
            "id": int(item_id),
            "name": label,
            "url": f"https://registry.seqco.de/{what}/{item_id}",
            "api_url": f"https://api.seqco.de/v1/{what}/{item_id}.json",
        })
    return results
