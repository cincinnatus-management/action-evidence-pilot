"""Request artifact digests over MCP stdio; print one receipt per call."""
import argparse
import asyncio
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(args):
    command = [str(Path(__file__).with_name("server.py").resolve()), "--out", str(args.out.resolve())]
    if args.policy:
        command.extend(["--policy", str(args.policy.resolve())])
    async with stdio_client(StdioServerParameters(command=sys.executable, args=command)) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            hello = await client.initialize()
            tools = await client.list_tools()
            print("Connected:", hello.serverInfo.name, hello.protocolVersion, "(stdio)")
            print("Tools:", ", ".join(tool.name for tool in tools.tools))
            for artifact in args.artifacts:
                response = await client.call_tool("artifact_digest", {"artifact": artifact})
                receipt = json.loads(response.content[0].text)
                print(json.dumps({"artifact": artifact, "isError": response.isError, **receipt}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("artifacts", nargs="+")
    asyncio.run(main(parser.parse_args()))
