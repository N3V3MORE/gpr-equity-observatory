// Test server for the completed static artifact. Never starts Next's dev server.
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(process.env.GPR_ARTIFACT_DIR || path.join(__dirname, "../out"));
const basePath = (process.env.NEXT_PUBLIC_BASE_PATH || "").replace(/\/$/, "");
const port = Number(process.env.GPR_BROWSER_PORT || 4173);
if (!fs.existsSync(path.join(root, "index.html"))) throw new Error(`Build the static artifact first: ${root}`);
const types = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".csv": "text/csv", ".txt": "text/plain", ".woff2": "font/woff2" };

http.createServer((request, response) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname); }
  catch { response.writeHead(400).end(); return; }
  if (basePath && pathname !== basePath && !pathname.startsWith(`${basePath}/`)) {
    response.writeHead(404).end(); return;
  }
  const relative = pathname.slice(basePath.length).replace(/^\/+/, "");
  let file = path.resolve(root, relative);
  if (file !== root && !file.startsWith(`${root}${path.sep}`)) { response.writeHead(403).end(); return; }
  try {
    if (fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
    const body = fs.readFileSync(file);
    response.writeHead(200, { "Content-Type": `${types[path.extname(file)] || "application/octet-stream"}; charset=utf-8`, "Cache-Control": "no-store" });
    response.end(request.method === "HEAD" ? undefined : body);
  } catch { response.writeHead(404).end(); }
}).listen(port, "127.0.0.1", () => console.log(`Serving built artifact at http://127.0.0.1:${port}${basePath}/`));
