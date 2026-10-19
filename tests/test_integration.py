"""Quick integration test against the live SeqCode API."""
import asyncio

from seqcode_mcp.client import SeqCodeClient


async def main():
    async with SeqCodeClient() as c:
        # 1. Check API status
        status = await c.get_status()
        print("API status:", status)

        # 2. Get a name by ID
        name = await c.get_name(49702)
        print(f"\nName: {name.get('name')}")
        print(f"  Rank: {name.get('rank')}")
        print(f"  Status: {name.get('status_name')}")
        print(f"  Etymology: {name.get('etymology', 'N/A')[:80]}...")

        # 3. Get a genome by ID
        genome = await c.get_genome(6326)
        print(f"\nGenome: {genome.get('accession')}")
        print(f"  Kind: {genome.get('kind')}")
        gf = genome.get("genomic_features", {})
        print(f"  GC content: {gf.get('gc_content')}")

        # 4. List some names (first page)
        names_list = await c.list_names(page=1, status="SeqCode")
        resp = names_list.get("response", {})
        values = names_list.get("values", [])
        print(f"\nNames list: {resp.get('count')} total, page 1 has {len(values)} items")
        if values:
            print(f"  First: {values[0].get('name')}")

        # 5. Search
        results = await c.search("Spongiamicus", what="names")
        print(f"\nSearch 'Spongiamicus': {len(results)} results")
        for r in results[:3]:
            print(f"  - {r['name']} (id: {r['id']})")

        print("\nAll integration tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
