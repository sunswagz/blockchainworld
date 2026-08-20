/* SINH TỰ ĐỘNG bởi scripts/nha-may.mjs — ĐỪNG SỬA TAY.
   Đây là bản chiếu của factory/state.json sang thứ trình duyệt đọc được.
   Sửa tay thì lượt bot kế tiếp ghi đè, không báo gì. */
window.VAN_HANH = {
 "generatedAt": "2026-08-20T07:09:14.935Z",
 "lan": 96,
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
   "luc": "2026-08-20T01:53:59.134Z",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T01:53:59.134Z",
   "lucDoi": "2026-08-20T01:53:59.134Z"
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
   "luc": "2026-08-20T01:55:04.790Z",
   "ket": "ok",
   "giay": 65,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T01:55:04.790Z",
   "lucDoi": "2026-08-20T01:55:04.790Z"
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
   "luc": "2026-08-20T01:55:08.898Z",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T01:55:08.898Z",
   "lucDoi": "2026-08-20T01:55:08.898Z"
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
   "luc": "2026-08-20T01:55:10.404Z",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T01:55:10.404Z",
   "lucDoi": "2026-08-20T01:55:10.404Z"
  },
  {
   "ma": "thai-boc-tu",
   "ten": "Đoàn tàu Thái Bộc Tự",
   "y": "Ba đường DefiLlama công khai. Không gọi AI, không khoá nào. Việc nặng nhất làm ở đây chứ không ở trình duyệt: xếp hơn 8.000 giao thức vào 18 toa và dựng quan hệ phụ thuộc oracle từ khai báo của từng cái.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-thaiboc.mjs",
   "ra": [
    "thai-boc-tu/assets/js/v/doan-tau.js"
   ],
   "cung": "thai-boc-tu",
   "cungTen": "Thái Bộc Tự",
   "wf": "refresh-data.yml",
   "luc": "2026-08-20T01:55:10.971Z",
   "ket": "ok",
   "giay": 0,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T01:55:10.971Z",
   "lucDoi": "2026-08-20T01:55:10.971Z"
  },
  {
   "ma": "thai-boc-tu-cong-truong",
   "ten": "Công trường Thái Bộc Tự",
   "y": "Hỏi GitHub 14 kho mã và lịch sử đề xuất ERC/EIP: nút thắt nào còn người xây, chuẩn nào vừa mở. Dùng GITHUB_TOKEN Actions tự cấp — không thêm secret nào, không gọi AI.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-congtruong.mjs",
   "ra": [
    "thai-boc-tu/assets/js/v/cong-truong.js"
   ],
   "cung": "thai-boc-tu",
   "cungTen": "Thái Bộc Tự",
   "wf": "refresh-data.yml",
   "luc": "2026-08-20T01:55:17.173Z",
   "ket": "ok",
   "giay": 7,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T01:55:17.173Z",
   "lucDoi": "2026-08-20T01:55:17.173Z"
  },
  {
   "ma": "thai-boc-tu-tin",
   "ten": "Tin tức Thái Bộc Tự",
   "y": "Sáu nguồn RSS công khai (CoinDesk, Cointelegraph, Decrypt, Bitcoin Magazine, blog Ethereum Foundation, Vitalik). Gắn nhãn toa bằng từ khoá. Ảnh TRỎ THẲNG sang CDN toà soạn, không tải về repo. Không khoá nào, không gọi AI.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-tintuc.mjs",
   "ra": [
    "thai-boc-tu/assets/js/v/tin-tuc.js"
   ],
   "cung": "thai-boc-tu",
   "cungTen": "Thái Bộc Tự",
   "wf": "refresh-data.yml",
   "luc": "2026-08-20T07:09:14.935Z",
   "ket": "ok",
   "giay": 0,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T07:09:14.935Z",
   "lucDoi": "2026-08-20T07:09:14.935Z"
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
   "luc": "2026-08-20T02:01:57.433Z",
   "ket": "ok",
   "giay": 400,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T02:01:57.433Z",
   "lucDoi": "2026-08-20T02:01:57.433Z"
  },
  {
   "ma": "quan-trac-do",
   "ten": "Bảng cảnh báo Quan Trắc",
   "y": "Bốn nguồn miễn phí không cần khoá (Yahoo Finance, open.er-api, Federal Register, GDELT), so ngưỡng số học rồi tự đặt đèn. KHÔNG gọi AI. Đo cho CẢ HAI chủ thể; bảng đo cái gì nằm ở DODAC trong data.js của cung.",
   "tram": "M12",
   "che": "script",
   "nhip": 6,
   "lenh": "node scripts/build-quantrac.mjs",
   "ra": [
    "dai-quan-trac/assets/js/do.js",
    "dai-quan-trac/assets/js/tq/do.js"
   ],
   "cung": "dai-quan-trac",
   "cungTen": "Đài Quan Trắc",
   "wf": "refresh-data.yml",
   "luc": "2026-08-20T02:03:32.235Z",
   "ket": "ok",
   "giay": 95,
   "doi": true,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T02:03:32.235Z",
   "lucDoi": "2026-08-20T02:03:32.235Z"
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
    "dai-quan-trac/assets/js/scan.js",
    "dai-quan-trac/assets/js/tq/scan.js"
   ],
   "cung": "dai-quan-trac",
   "cungTen": "Đài Quan Trắc",
   "wf": "refresh-data.yml",
   "luc": "2026-08-20T02:07:06.841Z",
   "ket": "ok",
   "giay": 214,
   "doi": true,
   "chuThich": "quét 214s · dựng 0s · haiku-4-5",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T02:07:06.841Z",
   "lucDoi": "2026-08-20T02:07:06.841Z"
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
   "luc": "2026-08-20T02:03:32.560Z",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T02:03:32.560Z",
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
   "luc": "2026-08-20T02:08:37.255Z",
   "ket": "ok",
   "giay": 90,
   "doi": true,
   "chuThich": "opus-5 · max-turns 8",
   "vi": null,
   "chuoiLoi": 0,
   "lucOk": "2026-08-20T02:08:37.255Z",
   "lucDoi": "2026-08-20T02:08:37.255Z"
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
   "luc": "2026-08-20T07:09:14.935Z",
   "ma": "thai-boc-tu-tin",
   "ket": "ok",
   "giay": 0,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T02:08:37.255Z",
   "ma": "bao-cao",
   "ket": "ok",
   "giay": 90,
   "doi": true,
   "chuThich": "opus-5 · max-turns 8",
   "vi": null
  },
  {
   "luc": "2026-08-20T02:07:06.841Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 214,
   "doi": true,
   "chuThich": "quét 214s · dựng 0s · haiku-4-5",
   "vi": null
  },
  {
   "luc": "2026-08-20T02:03:32.560Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T02:03:32.235Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 95,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T02:01:57.433Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 400,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T01:55:17.173Z",
   "ma": "thai-boc-tu-cong-truong",
   "ket": "ok",
   "giay": 7,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T01:55:10.971Z",
   "ma": "thai-boc-tu",
   "ket": "ok",
   "giay": 0,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T01:55:10.404Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T01:55:08.898Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T01:55:04.790Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 65,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-20T01:53:59.134Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T13:20:34.620Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T13:20:34.282Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 40,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T13:19:54.583Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 408,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T13:13:06.247Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T13:13:03.628Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T13:12:59.566Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 60,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T13:11:59.542Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T07:09:54.204Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 106,
   "doi": true,
   "chuThich": "quét 106s · dựng 0s · haiku-4-5",
   "vi": null
  },
  {
   "luc": "2026-08-19T02:09:17.224Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 1,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T02:09:16.697Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 27,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T02:08:49.818Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 766,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T01:56:03.006Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T01:55:59.295Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T01:55:56.359Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 65,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-19T01:54:50.850Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T19:01:22.496Z",
   "ma": "bao-cao",
   "ket": "ok",
   "giay": 56,
   "doi": true,
   "chuThich": "opus-5 · max-turns 8",
   "vi": null
  },
  {
   "luc": "2026-08-18T19:00:26.193Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 99,
   "doi": true,
   "chuThich": "quét 99s · dựng 0s · haiku-4-5",
   "vi": null
  },
  {
   "luc": "2026-08-18T13:20:28.069Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 1,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T13:20:27.614Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 13,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T13:20:14.573Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 459,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T13:12:35.150Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 7,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T13:12:28.185Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T13:12:24.328Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 68,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T13:11:16.168Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T07:08:34.588Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 94,
   "doi": false,
   "chuThich": "quét 94s · dựng 0s · haiku-4-5",
   "vi": null
  },
  {
   "luc": "2026-08-18T02:03:43.761Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T02:03:43.322Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 26,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T02:03:17.316Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 557,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T01:54:00.443Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 6,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T01:53:54.426Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 4,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T01:53:50.509Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 65,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-18T01:52:45.170Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T19:03:20.708Z",
   "ma": "bao-cao",
   "ket": "ok",
   "giay": 75,
   "doi": true,
   "chuThich": "opus-5 · max-turns 8",
   "vi": null
  },
  {
   "luc": "2026-08-17T19:02:05.906Z",
   "ma": "dai-quan-trac",
   "ket": "ok",
   "giay": 114,
   "doi": true,
   "chuThich": "quét 114s · dựng 0s · haiku-4-5",
   "vi": null
  },
  {
   "luc": "2026-08-17T19:00:11.688Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T13:17:44.023Z",
   "ma": "dong-dau",
   "ket": "ok",
   "giay": 0,
   "doi": false,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T13:17:43.623Z",
   "ma": "quan-trac-do",
   "ket": "ok",
   "giay": 26,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T13:17:17.210Z",
   "ma": "tang-thu-cac",
   "ket": "ok",
   "giay": 418,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T13:10:19.602Z",
   "ma": "ho-bo",
   "ket": "ok",
   "giay": 3,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T13:10:16.552Z",
   "ma": "cong-bo",
   "ket": "ok",
   "giay": 5,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T13:10:11.640Z",
   "ma": "do-sat-vien",
   "ket": "ok",
   "giay": 62,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
  {
   "luc": "2026-08-17T13:09:09.011Z",
   "ma": "kinh-thanh",
   "ket": "ok",
   "giay": 2,
   "doi": true,
   "chuThich": "",
   "vi": null
  },
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
  }
 ]
};
