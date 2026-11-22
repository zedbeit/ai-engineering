"""Summarize recordings made by record-proxy.mjs.

Usage: python3 summarize.py <run-dir> [<run-dir> ...]
"""

import glob
import json
import sys
from pathlib import Path


def events(sse: str):
    for line in sse.splitlines():
        if line.startswith("data: "):
            try:
                yield json.loads(line[6:])
            except json.JSONDecodeError:
                pass


def turn(record: dict) -> dict | None:
    req = record["request"]
    if not isinstance(req, dict) or "messages" not in req:
        return None
    calls, stop, usage = [], None, {}
    for e in events(record["response"]):
        kind = e.get("type")
        if kind == "message_start":
            usage.update(e["message"].get("usage", {}))
        elif kind == "content_block_start" and e["content_block"]["type"] == "tool_use":
            calls.append(e["content_block"]["name"])
        elif kind == "message_delta":
            stop = e["delta"].get("stop_reason")
            usage.update(e.get("usage", {}))
    system = req.get("system") or []
    sys_chars = sum(len(b.get("text", "")) for b in system) if isinstance(system, list) else len(system)
    return {
        "id": record["id"],
        "status": record["status"],
        "messages": len(req["messages"]),
        "tools": len(req.get("tools", [])),
        "sys_chars": sys_chars,
        "in": usage.get("input_tokens", 0),
        "cache_write": usage.get("cache_creation_input_tokens", 0),
        "cache_read": usage.get("cache_read_input_tokens", 0),
        "out": usage.get("output_tokens", 0),
        "stop": stop,
        "calls": calls,
    }


def summarize(run_dir: str) -> None:
    print(f"\n== {run_dir}")
    rows = []
    for f in sorted(glob.glob(f"{run_dir}/*.json")):
        r = json.loads(Path(f).read_text())
        t = turn(r)
        if t is None:
            print(f"{r['id']} {r['method']} {r['url']} -> {r['status']} (not a model call)")
            continue
        rows.append(t)
        print(
            f"{t['id']} {t['status']} msgs={t['messages']:>3} tools={t['tools']:>2} sys={t['sys_chars']:>6} "
            f"in={t['in']:>5} cw={t['cache_write']:>6} cr={t['cache_read']:>6} out={t['out']:>5} "
            f"{t['stop']} {t['calls']}"
        )
    loop = [t for t in rows if t["tools"] > 0 and t["status"] == 200]
    total = lambda k: sum(t[k] for t in loop)  # noqa: E731
    print(
        f"main loop: turns={len(loop)} tool_calls={sum(len(t['calls']) for t in loop)} "
        f"in={total('in')} cache_write={total('cache_write')} cache_read={total('cache_read')} out={total('out')}"
    )
    from collections import Counter
    print("tool mix:", dict(Counter(c for t in loop for c in t["calls"])))


if __name__ == "__main__":
    for d in sys.argv[1:]:
        summarize(d)
