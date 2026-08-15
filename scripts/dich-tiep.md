# Dịch tiếp skill cộng đồng — bản bàn giao

**XONG 2.859/2.859** (15/08/2026). Việc dịch mô tả skill cộng đồng của
Tàng Thư Các sang tiếng Việt đã hoàn tất — **viết tay, không gọi API**,
448 mục có thêm phần "Với hệ thống của bạn".

Tệp này giữ lại làm hướng dẫn cho **skill mới**: mỗi lượt bot quét thêm kho
hoặc kho gốc thêm skill thì `node scripts/dich-con-lai.mjs` sẽ lại ra số
dương, và quy trình dưới đây vẫn dùng nguyên.

## Xem còn bao nhiêu

    node scripts/dich-con-lai.mjs            # thống kê + kho nào còn nhiều
    node scripts/dich-con-lai.mjs <kho> 60   # in 60 mô tả của một kho để dịch

## Cách ghi kết quả

Viết một tệp JSON tạm khoá theo **TÊN skill** (đoạn cuối đường dẫn), rồi:

    node scripts/dich-gop.mjs <kho> <tệp-tạm.json>

Script tự nối tên → id đầy đủ và gộp vào `tang-thu-cac/assets/data/dich/`.

**Đừng chép tay id.** Id dạng `kho/đường/dẫn/dài/dòng`; chép 60 cái là chắc
chắn sai một cái, và sai thì **im lặng** — bản dịch không hiện ra mà không
có lỗi nào báo.

## Khuôn mỗi mục

```json
"tên-skill": {
  "tom": "MỘT câu, nó là cái gì",
  "lam": ["2–4 việc cụ thể", "mỗi việc một mệnh đề ngắn"],
  "khi": "một câu, khi nào Claude tự bật nó",
  "ban": "CHỈ khi có liên hệ thật với hệ này — xem dưới"
}
```

Không gắn `may: 1` — cờ đó dành riêng cho bản do API dịch, và giao diện
dùng nó để hiện nhãn "máy dịch". Bản viết tay hiện nhãn "đã dịch".

## Mục `ban` — chỉ viết khi có liên hệ THẬT

Đây là mục duy nhất API không làm được, và cũng là mục dễ bịa nhất.
**Thà bỏ trống còn hơn cố nặn.** Khoảng 30% số skill xứng có mục này;
số còn lại là kỹ thuật chung chung (Android, Angular, Terraform) —
để trống.

Những sự thật về hệ này, dùng để nhận ra liên hệ thật:

- **Bảy cung** webapp tĩnh: `kinh-thanh` (số liệu blockchain),
  `do-sat-vien` (bảng xét L2), `cong-bo` (bộ đồ nghề), `tang-thu-cac`
  (kho skill này), `dai-quan-trac` (địa chính trị), `hoang-thanh`
  (văn hoá), `tao-bien-xu` (công xưởng AI). Tất cả **JS thuần, không
  build, không node_modules**, chạy offline được, hash routing vì IPFS.
- **Nhiều phiên Claude Code chạy song song**, mỗi phiên một git worktree,
  một cung, một nhánh. Không có kênh nhắn tin giữa các phiên — chỉ chạm
  nhau qua `.git/hooks` dùng chung.
- **CLAUDE.md hơn 400 dòng** là luật chung, có quy trình tự vá khi phát
  hiện lỗi trong chính nó. `npm run kiem` kiểm tài liệu còn khớp repo không.
- **Hook pre-commit** nhắc khi CLAUDE.md cũ hoặc đang dàn file bot sinh.
  Nó **luôn thoát 0** — chỉ nhắc, không chặn.
- **Nhà máy dữ liệu**: `scripts/nha-may.mjs` giữ sổ lịch, workflow
  `refresh-data.yml` hỏi sổ xem node nào đến hạn rồi chạy đúng node đó.
- **Sự cố 13–14/08/2026** (dùng nhiều nhất khi viết `ban`): đường ống bot
  chết hơn một ngày mà mọi phép kiểm đều xanh. Hai nguyên nhân cùng lúc —
  bước đóng dấu Pinata ngã kéo cả job, và job đụng trần 10 phút. Bài học:
  cảnh báo phải tới được mắt người, và một bước ngã không được giết cả lượt.
- **Hai khoá đã chết vì dán vào khung chat**: Anthropic và Pinata.
- **Đài Quan Trắc tắt lịch** vì chạy Opus kèm `web_search` tốn ~1,4 USD
  mỗi lượt, 4 lượt/ngày.

Ví dụ mục `ban` viết đúng (đã có trong `obra__superpowers.json`):

> `verification-before-completion` → "Nếu chỉ chọn một skill trong cả kho
> này thì chọn cái này. Nó là bài học xuyên suốt: cái ⚠ có mà không ai
> thấy, con số '24 tệp' hoá ra là mức cắt, đường ống chết hơn một ngày
> mà mọi phép kiểm đều xanh."

Ví dụ **không** nên viết: skill về Android hay Terraform mà cố nối vào
"bảy cung của bạn cũng có giao diện" — đó là bịa cho có.

## Giọng văn

Tiếng Việt tự nhiên, không dịch cứng. Giữ nguyên thuật ngữ không có từ
Việt phổ biến: MCP, hook, commit, API, repo, agent, skill, plugin, token,
webhook, worktree. Đừng dịch tên skill. Mô tả gốc nghèo thì viết ngắn —
đừng đắp thêm cho dài.

## Chỉ mục cho danh sách — `dich-tom.json`

Bản dịch đầy đủ nằm trong `dich/<kho>.json`, **nạp lười** khi mở hồ sơ một
skill. Màn danh mục không đợi được kiểu đó: nó phải biết ngay skill nào đã
dịch để đếm, để lọc, và để hiện câu công dụng tiếng Việt ngoài danh sách.
Nên có thêm `tang-thu-cac/assets/data/dich-tom.json` — chỉ `id → câu tom`.

`dich-gop.mjs` **tự sinh lại** chỉ mục sau mỗi lần gộp, nên không phải nhớ.
Sửa tay tệp trong `dich/` thì chạy `npm run dich-tom`.

Quên bước này thì bản dịch nằm trên đĩa mà trang vẫn báo "còn nguyên bản
gốc 2859" — đúng lỗi đã xảy ra ngày 15/08.

## Sau mỗi lô

    git add tang-thu-cac/assets/data/dich/
    git commit -m "Dịch tay thêm N skill <kho>"
    git push origin main

`dich/` là thư mục **viết tay**, không phải bot sinh — xem mục "File do
workflow tự sinh" trong CLAUDE.md, nơi đã tách riêng nó ra.

## Mục khuôn mẫu: `scripts/dich-composio.mjs`

Kho `ComposioHQ/awesome-claude-skills` có ~330 skill dùng **đúng một câu**
mô tả, chỉ đổi tên dịch vụ:

    Automate <Tên> tasks via Rube MCP (Composio). Always search tools first…

Dịch tay từng cái là chép lại cùng một câu 330 lần. Bản dịch của câu khuôn
đó viết **một lần** trong `scripts/dich-composio.mjs`, script chỉ thay tên
dịch vụ. Mục nào **không** khớp khuôn thì script bỏ qua và in ra để dịch tay.

Đây không phải dịch máy — câu tiếng Việt do người viết, script chỉ nhân bản.
Gặp kho khác cũng dùng khuôn cứng như vậy thì làm y hệt.

## Bẫy đã gặp

- **Trùng tên skill trong cùng một kho.** `ruvnet/ruflo` có hai
  `swarm-orchestration` ở hai đường dẫn khác nhau. `dich-gop.mjs` tra theo
  tên nên báo `✗ không khớp tên` rồi bỏ qua cả hai. Cách chữa: ghi thẳng vào
  `dich/<kho>.json` theo **id đầy đủ**.
- **Đẩy trượt.** Nhiều worktree cùng đẩy lên `main`. Trước mỗi lần đẩy:
  `git fetch -q && git -c rebase.autoStash=true rebase -q origin/main`.
  Có `autoStash` vì phiên khác có thể đang để dở file chưa commit trong cùng
  thư mục — **đừng** stash tay rồi quên pop.
- **Mô tả gốc bỏ trống.** Vài skill còn nguyên dòng mẫu ("Replace with
  description…"). Đừng bịa: ghi thẳng là mô tả gốc chưa điền, và bảo người
  đọc mở SKILL.md.
