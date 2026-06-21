import asyncio
import threading
import concurrent.futures
from fastmcp.client import Client
from fastmcp.client import Client as FastMCPClient
from fastmcp.client import Client as _ClientType
from fastmcp.client import Client as _Unused
import traceback
import sys

# Local fallback tools
try:
    from app.tools import dataset_tools as _local_dataset_tools
except Exception:
    try:
        import tools.dataset_tools as _local_dataset_tools
    except Exception:
        _local_dataset_tools = None

# Prefer an in-process transport when the local MCP server module is available.
try:
    # import the FastMCP server instance defined in mcp_server/server.py
    from mcp_server import server as _mcp_server_module
    # Prefer a module-level `mcp` if present, otherwise try a `make_server()` factory.
    _IN_PROCESS_MCP = getattr(_mcp_server_module, "mcp", None)
    if _IN_PROCESS_MCP is None and hasattr(_mcp_server_module, "make_server"):
        try:
            _IN_PROCESS_MCP = _mcp_server_module.make_server()
        except Exception:
            _IN_PROCESS_MCP = None
except Exception:
    _IN_PROCESS_MCP = None


def _run_coro_in_thread(coro):
    """Run an async coroutine in a new event loop inside a background thread and return result."""
    fut = concurrent.futures.Future()

    def _thread_target():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro)
            fut.set_result(res)
        except Exception as e:
            fut.set_exception(e)
        finally:
            try:
                loop.close()
            except Exception:
                pass

    t = threading.Thread(target=_thread_target, daemon=True)
    t.start()
    return fut.result()


def _call_mcp_tool(name: str, arguments: dict | None = None):
    async def _inner():
        if _IN_PROCESS_MCP is not None:
            async with Client(_IN_PROCESS_MCP) as client:
                return await client.call_tool(name, arguments or {})
        else:
            # FastMCP HTTP app exposes the MCP endpoint under /mcp by default.
            # Use the correct path to avoid 404 on POST /
            MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"
            async with Client(MCP_SERVER_URL) as client:
                return await client.call_tool(name, arguments or {})
    def _call_inner_sync():
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # no running loop
            return asyncio.run(_inner())
        else:
            return _run_coro_in_thread(_inner())

    # Try MCP transports, fallback to local functions if MCP fails
    try:
        res = _call_inner_sync()
        return res
    except Exception as e:
        # Log the error for visibility and attempt fallback
        print("[mcp_tools] MCP call failed:", file=sys.stderr)
        traceback.print_exc()

        # Fallback to local dataset tools if available
        if _local_dataset_tools is not None:
            try:
                if name == "get_metadata":
                    return _local_dataset_tools.get_metadata()
                if name == "quality_check":
                    return _local_dataset_tools.quality_check()
                if name == "pii_check":
                    # best-effort PII via simple heuristics using the dataframe
                    import pandas as pd
                    df = pd.read_csv("data/sample.csv", dtype=str).fillna("")
                    email_re = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                    phone_re = r"\+?\d[\d\-() ]{6,}\d"
                    email_counts = {c: int(df[c].str.count(email_re).sum()) for c in df.columns}
                    phone_counts = {c: int(df[c].str.count(phone_re).sum()) for c in df.columns}
                    return {"email_counts": email_counts, "phone_counts": phone_counts, "total_emails": sum(email_counts.values()), "total_phones": sum(phone_counts.values())}
            except Exception:
                print("[mcp_tools] local fallback failed:", file=sys.stderr)
                traceback.print_exc()

        # Re-raise original error if no fallback succeeded
        raise


def get_metadata():
    return _call_mcp_tool("get_metadata", {"file_path": "data/sample.csv"})


def quality_check():
    return _call_mcp_tool("quality_check", {"file_path": "data/sample.csv"})


def pii_check():
    return _call_mcp_tool("pii_check", {"file_path": "data/sample.csv"})