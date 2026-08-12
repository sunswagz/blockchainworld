/* Máy chủ tĩnh tối giản — không cần cài gói nào.
   Dùng: node server.js [cổng]     mặc định http://localhost:5173
   Service worker chỉ chạy trên http/https, nên đừng mở index.html
   bằng file:// nếu muốn thử chế độ offline. */

const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const PORT = Number(process.argv[2] || process.env.PORT || 5173);

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".md": "text/markdown; charset=utf-8"
};

const server = http.createServer((req, res) => {
  let rel = decodeURIComponent(req.url.split("?")[0]);
  if (rel.endsWith("/")) rel += "index.html";

  const file = path.join(ROOT, path.normalize(rel));
  if (!file.startsWith(ROOT)) {
    res.writeHead(403).end("Forbidden");
    return;
  }

  fs.readFile(file, (err, buf) => {
    if (err) {
      res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
      res.end("404 · " + rel);
      return;
    }
    res.writeHead(200, {
      "content-type": TYPES[path.extname(file).toLowerCase()] || "application/octet-stream",
      // tắt cache của trình duyệt để service worker là thứ duy nhất quyết định
      "cache-control": "no-cache"
    });
    res.end(buf);
  });
});

server.listen(PORT, () => {
  console.log("Kinh Thành đang chạy tại  http://localhost:" + PORT);
  console.log("Ctrl+C để dừng.");
});
