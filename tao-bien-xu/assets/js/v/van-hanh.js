/* SINH TỰ ĐỘNG bởi scripts/nha-may.mjs — ĐỪNG SỬA TAY.
   Đây là bản chiếu của factory/state.json sang thứ trình duyệt đọc được.
   Sửa tay thì lượt bot kế tiếp ghi đè, không báo gì. */
window.VAN_HANH = {
 "generatedAt": "2026-08-17T02:10:04.982Z",
 "lan": 42,
 "repo": "sunswagz/blockchainworld",
 "node": [
  {
   "ma": "kinh-thanh",
   "ten": "Số liệu Kinh Thành",
   "y": "TVL và số on-chain 9 quốc gia L1, lấy từ DefiLlama.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-live.mjs",
   "ra": [
    "kinh-thanh/assets/js/data/live.js",
    "kinh-thanh/assets/js/data/provenance.js",
    "kinh-thanh/assets/data/history.json"
   ],
   "cung": "kinh-thanh",
   "cungTen": "Kinh Thành",
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T01:56:57.765Z",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T01:56:57.765Z",
   "lucDoi": "2026-08-17T01:56:57.765Z"
  },
  {
   "ma": "do-sat-vien",
   "ten": "Bảng xét Đô Sát Viện",
   "y": "Xếp hạng Layer 2 theo L2BEAT, kèm logo tải về.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-l2beat.mjs",
   "ra": [
    "do-sat-vien/assets/js/data.js",
    "do-sat-vien/assets/logos/"
   ],
   "cung": "do-sat-vien",
   "cungTen": "Đô Sát Viện",
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T01:58:04.743Z",
   "ket": "ok",
   "giay": 66,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T01:58:04.743Z",
   "lucDoi": "2026-08-17T01:58:04.743Z"
  },
  {
   "ma": "cong-bo",
   "ten": "Đồ nghề Công Bộ",
   "y": "Bộ công cụ onchain. Nguồn có một phần là host staging của L2BEAT nên hay ngã.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-congbo.mjs",
   "ra": [
    "cong-bo/assets/js/data.js",
    "cong-bo/assets/js/logos.js",
    "cong-bo/assets/js/v/nhat-ky.js",
    "cong-bo/assets/logos/"
   ],
   "cung": "cong-bo",
   "cungTen": "Công Bộ",
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T01:58:08.524Z",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T01:58:08.524Z",
   "lucDoi": "2026-08-17T01:58:08.524Z"
  },
  {
   "ma": "ho-bo",
   "ten": "Dòng tiền Hộ Bộ",
   "y": "Mười một đường DefiLlama công khai (TVL, phí, DEX, stablecoin, vụ mất tiền, lợi suất) cộng lịch sử 20 chuỗi, gộp thành một file. KHÔNG gọi AI, không khoá nào.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-hobu.mjs",
   "ra": [
    "ho-bo/assets/js/v/dong-tien.js"
   ],
   "cung": "ho-bo",
   "cungTen": "Hộ Bộ",
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T01:58:11.260Z",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T01:58:11.260Z",
   "lucDoi": "2026-08-17T01:58:11.260Z"
  },
  {
   "ma": "tang-thu-cac",
   "ten": "Kho skill Tàng Thư Các",
   "y": "Quét kho Claude Skills trên GitHub. Bước chậm nhất — có lượt 532 giây.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-tangthu.mjs",
   "ra": [
    "tang-thu-cac/assets/js/data.js",
    "tang-thu-cac/assets/data/"
   ],
   "cung": "tang-thu-cac",
   "cungTen": "Tàng Thư Các",
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T02:06:51.968Z",
   "ket": "ok",
   "giay": 520,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T02:06:51.968Z",
   "lucDoi": "2026-08-17T02:06:51.968Z"
  },
  {
   "ma": "quan-trac-do",
   "ten": "Bảng cảnh báo Quan Trắc",
   "y": "Ba nguồn miễn phí không cần khoá (Yahoo Finance, open.er-api, GDELT), so ngưỡng số học rồi tự đặt đèn. KHÔNG gọi AI.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-quantrac.mjs",
   "ra": [
    "dai-quan-trac/assets/js/do.js"
   ],
   "cung": "dai-quan-trac",
   "cungTen": "Đài Quan Trắc",
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T02:07:23.519Z",
   "ket": "ok",
   "giay": 31,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T02:07:23.519Z",
   "lucDoi": "2026-08-17T02:07:23.519Z"
  },
  {
   "ma": "dai-quan-trac",
   "ten": "Bản quét Đài Quan Trắc",
   "y": "Việc DUY NHẤT trong xưởng thật sự cần phán đoán: đọc tin 7 ngày rồi viết một câu tiếng Việt + phân loại xanh/vàng/đỏ. Trả bằng quota gói, không còn khoá API.",
   "tram": "M07",
   "che": "claude",
   "nhip": 12,
   "lenh": "claude-code-action + node scripts/build-scan.mjs",
   "ra": [
    "dai-quan-trac/assets/js/scan.js"
   ],
   "cung": "dai-quan-trac",
   "cungTen": "Đài Quan Trắc",
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T02:10:04.982Z",
   "ket": "ok",
   "giay": 161,
   "doi": true,
   "chuThich": "quét 160s · dựng 0s · haiku-4-5",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T02:10:04.982Z",
   "lucDoi": "2026-08-17T02:10:04.982Z"
  },
  {
   "ma": "dong-dau",
   "ten": "Đóng dấu bản số liệu",
   "y": "Pin bản số liệu 1,8 KB lên IPFS. Tự bỏ qua nếu sha256 trùng bản trước.",
   "tram": "M16",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/pin-snapshot.mjs",
   "ra": [],
   "cung": null,
   "cungTen": null,
   "wf": "refresh-data.yml",
   "luc": "2026-08-17T02:07:23.977Z",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-17T02:07:23.977Z",
   "lucDoi": null
  },
  {
   "ma": "bao-cao",
   "ten": "Báo cáo sức khoẻ xưởng",
   "y": "Claude Code Action đọc state.json rồi viết vài dòng tiếng Việt: node nào đang ốm, ốm từ bao giờ, nên xem chỗ nào trước.",
   "tram": "M18",
   "che": "claude",
   "nhip": 24,
   "lenh": "anthropics/claude-code-action",
   "ra": [
    "factory/bao-cao.md"
   ],
   "cung": null,
   "cungTen": null,
   "wf": "refresh-data.yml",
   "luc": "2026-08-16T18:49:46.086Z",
   "ket": "ok",
   "giay": 70,
   "doi": true,
   "chuThich": "opus-5 · max-turns 8",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-16T18:49:46.086Z",
   "lucDoi": "2026-08-16T18:49:46.086Z"
  },
  {
   "ma": "hoang-thanh",
   "ten": "Rừng văn hoá Hoàng Thành",
   "y": "Nguồn nằm NGOÀI repo (sunswagz-hub/08_world_culture_forest) nên Actions không quét được. Chạy tay rồi commit là cách duy nhất.",
   "tram": "M12",
   "che": "tay",
   "nhip": 0,
   "lenh": "npm run hoangthanh",
   "ra": [
    "hoang-thanh/assets/js/data.js",
    "hoang-thanh/assets/js/v/"
   ],
   "cung": "hoang-thanh",
   "cungTen": "Hoàng Thành",
   "wf": null,
   "luc": "2026-08-14T09:16:24.800Z",
   "ket": "ok",
   "giay": null,
   "doi": false,
   "chuThich": "mồi từ dấu generatedAt sẵn có trong file",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-14T09:16:24.800Z",
   "lucDoi": "2026-08-14T09:16:24.800Z"
  },
  {
   "ma": "tu-cam-thanh",
   "ten": "Phiên Tử Cấm Thành",
   "y": "Runtime là tiến trình Python chạy dài, cần ANTHROPIC_API_KEY và quyền ghi đĩa — Actions không chạy được. Chạy tay rồi commit lát cắt, cùng kiểu Hoàng Thành.",
   "tram": "M12",
   "che": "tay",
   "nhip": 0,
   "lenh": "cd tu-cam-thanh-runtime && python -m trader.snapshot",
   "ra": [
    "tu-cam-thanh/assets/js/v/phien.js"
   ],
   "cung": "tu-cam-thanh",
   "cungTen": "Tử Cấm Thành",
   "wf": null,
   "luc": null,
   "ket": null,
   "giay": null,
   "doi": false,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": null,
   "lucDoi": null
  },
  {
   "ma": "giao-hang",
   "ten": "Giao hàng lên Pages",
   "y": "Không có nhịp riêng — chạy khi có commit số liệu. 27/27 lượt thành công.",
   "tram": "M16",
   "che": "theo",
   "nhip": 0,
   "lenh": ".github/workflows/deploy-pages.yml",
   "ra": [],
   "cung": null,
   "cungTen": null,
   "wf": "deploy-pages.yml",
   "luc": null,
   "ket": null,
   "giay": null,
   "doi": false,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": null,
   "lucDoi": null
  }
 ],
 "nk": [
  {
   "luc": "2026-08-17T02:10:04.982Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 161,
   "doi": true,
   "chuThich": "quét 160s · dựng 0s · haiku-4-5",
   "vi": null
  },
  {
   "luc": "2026-08-17T02:07:23.977Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T02:07:23.519Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 31,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T02:06:51.968Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 520,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T01:58:11.260Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T01:58:08.524Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T01:58:04.743Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 66,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T01:56:57.765Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T18:49:46.086Z",
   "ma": "bao-cao",
   "ket": "ok",
   "giay": 70,
   "doi": true,
   "chuThich": "opus-5 · max-turns 8",
   "vi": null
  },
  {
   "luc": "2026-08-16T13:16:31.575Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T13:16:31.098Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 16,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T13:16:15.757Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 696,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T13:04:39.324Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 7,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T13:04:32.407Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 5,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T13:04:27.586Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 69,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T13:03:17.821Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T07:03:18.060Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 1,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T02:06:33.304Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 1,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T02:06:32.802Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 13,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T02:06:19.918Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 375,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T02:00:04.178Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T02:00:02.491Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T01:59:58.707Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 65,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-16T01:58:52.809Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 1,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T18:49:23.800Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:18:35.358Z",
   "ma": "bao-cao",
   "ket": "ok",
   "giay": null,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:17:36.335Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 0,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:16:09.873Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:16:09.326Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 40,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:15:29.055Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 700,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:03:49.567Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 5,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:03:44.523Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 69,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T14:02:35.771Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:14:45.657Z",
   "ma": "dai-quan-trac",
   "ket": "loi",
   "giay": null,
   "doi": false,
   "chuThich": "kiểm không qua: dai-quan-trac/assets/js/scan.js — teo đột ngột: 3886 byte, bản cũ 10188 byte",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:14:45.507Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 0,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:12:53.505Z",
   "ma": "bao-cao",
   "ket": "ok",
   "giay": null,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:11:47.088Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 1,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:11:46.676Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 42,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:11:04.083Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 494,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:02:50.367Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 19,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:02:31.714Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 62,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-15T13:01:29.158Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-14T13:54:17.370Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": null,
   "doi": false,
   "chuThich": "mồi từ dấu generatedAt sẵn có trong file"
  },
  {
   "luc": "2026-08-14T13:47:47.836Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": null,
   "doi": false,
   "chuThich": "mồi từ dấu generatedAt sẵn có trong file"
  },
  {
   "luc": "2026-08-14T13:47:43.854Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": null,
   "doi": false,
   "chuThich": "mồi từ dấu generatedAt sẵn có trong file"
  },
  {
   "luc": "2026-08-14T13:46:40.331Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": null,
   "doi": false,
   "chuThich": "mồi từ dấu generatedAt sẵn có trong file"
  },
  {
   "luc": "2026-08-14T09:16:24.800Z",
   "ma": "hoang-thanh",
   "ket": "ok",
   "giay": null,
   "doi": false,
   "chuThich": "mồi từ dấu generatedAt sẵn có trong file"
  },
  {
   "luc": "2026-08-13T08:53:22.949Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": null,
   "doi": false,
   "chuThich": "mồi từ dấu generatedAt sẵn có trong file"
  }
 ]
};
