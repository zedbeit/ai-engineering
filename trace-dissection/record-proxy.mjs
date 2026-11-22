// Minimal recording proxy for Claude Code.
// Forwards http://localhost:PORT -> https://api.anthropic.com and saves each
// exchange as one JSON file. Headers are NOT saved (they carry your token).
//
// Usage: node record-proxy.mjs <out-dir> [port]
//        ANTHROPIC_BASE_URL=http://localhost:8000/ claude
import http from "node:http";
import https from "node:https";
import fs from "node:fs";
import path from "node:path";

const outDir = process.argv[2] ?? ".claude-trace/run";
const port = Number(process.argv[3] ?? 8000);
fs.mkdirSync(outDir, { recursive: true });
let n = 0;

function parse(text) {
  try { return JSON.parse(text); } catch { return text; }
}

http.createServer((req, res) => {
  const chunks = [];
  req.on("data", (c) => chunks.push(c));
  req.on("end", () => {
    const reqBody = Buffer.concat(chunks);
    const headers = { ...req.headers, host: "api.anthropic.com" };
    delete headers["accept-encoding"]; // ask for uncompressed so we can log it
    const started = new Date();
    const upstream = https.request(
      { host: "api.anthropic.com", port: 443, path: req.url, method: req.method, headers },
      (up) => {
        res.writeHead(up.statusCode ?? 502, up.headers);
        const out = [];
        up.on("data", (c) => { out.push(c); res.write(c); });
        up.on("end", () => {
          res.end();
          const id = String(++n).padStart(3, "0");
          const record = {
            id,
            started: started.toISOString(),
            ms: Date.now() - started.getTime(),
            method: req.method,
            url: req.url,
            status: up.statusCode,
            request: parse(reqBody.toString("utf8")),
            response: Buffer.concat(out).toString("utf8"), // SSE text when streamed
          };
          fs.writeFileSync(path.join(outDir, `${id}.json`), JSON.stringify(record, null, 2));
          console.log(`${id} ${req.method} ${req.url} -> ${up.statusCode} (${record.ms} ms)`);
        });
      },
    );
    upstream.on("error", (e) => { res.writeHead(502); res.end(String(e)); });
    upstream.end(reqBody);
  });
}).listen(port, () => console.log(`Recording to ${outDir} on http://localhost:${port}`));
