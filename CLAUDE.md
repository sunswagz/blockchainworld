# blockchainworld

Repo chứa Cổng Thành (`index.html` ở gốc) và mười hai cung, mỗi cung là một
webapp tĩnh độc lập có `index.html` riêng:

    cong-bo/  dai-quan-trac/  do-sat-vien/  hoang-thanh/  ho-bo/
    kham-thien-giam/  kinh-thanh/  tang-thu-cac/  tao-bien-xu/
    thai-boc-tu/  thi-bac-ty/  tu-cam-thanh/

Có đúng **bốn** thư mục ở gốc **không** phải cung. Ba đầu là runtime
Python chạy tay, không lên site:

    tu-cam-thanh-runtime/       giao dịch crypto có hướng
    kham-thien-giam-runtime/    thị trường tiên đoán Polymarket
    thi-bac-ty-runtime/         Thị Bạc Ty — bộ máy quản lý vốn;
                                CHÍN ty, năm họ: chênh funding perp,
                                cash-and-carry, ngang giá quyền chọn
                                (phái sinh) · xoay lãi cho vay, Pendle PT
                                (tín dụng) · chênh stablecoin, vòng đổi
                                DEX (chênh lệch) · cấp thanh khoản AMM
                                (thanh khoản) · Polymarket (tiên đoán —
                                đọc từ Khâm Thiên Giám, không đặt lệnh)

Cái thứ tư là dữ liệu, không phải mã chạy:

    knowledge-os/               lớp tri thức nền dùng chung

Xem mục "Ba runtime Python là ngoại lệ" và mục "knowledge-os" bên dưới.
Ba runtime theo cùng một luật, nên mục đó nói chung cho cả ba chứ không
chép làm ba bản.

Cả bốn đều ngoài `dist/` vì `HALLS` trong `build-dist.mjs` là danh sách
tường minh, và cả bốn đều không bị `npm run kiem` nhầm là cung vì bộ kiểm
chỉ tính thư mục có `index.html` **ngay tại gốc** thư mục đó.

## Chạy song song nhiều phiên

Repo này thường có 2–4 phiên Claude Code chạy cùng lúc, mỗi phiên một
git worktree riêng, mỗi phiên lo một cung:

    claude --worktree cong-bo

Các cung tách thư mục hẳn nên file nguồn không đụng nhau. Ba thứ còn dùng
chung, và toàn bộ luật dưới đây chỉ để chia ba thứ đó:

- `.git` — chung index, chung branch `main`
- các file ở gốc repo, và `.github/workflows/`
- cổng localhost — worktree cô lập file, không cô lập runtime

### Cây chính không phải chỗ làm việc

Thư mục gốc `kinh-thanh-app/` chỉ để gộp và chạy lệnh toàn site. **Mọi
việc sửa code phải làm trong worktree**, kể cả khi dựng một cung hoàn
toàn mới.

Làm thẳng trong cây chính thì file mới của bạn hiện ra dưới dạng chưa
theo dõi trong cây của **mọi** phiên khác. Phiên nào lỡ `git add -A` là
nuốt trọn việc dở của bạn vào commit của họ — đã suýt xảy ra một lần với
`hoang-thanh/` khi nó đang thiếu 5 file và chưa nối vào đâu.

Một cung = một nhánh = một worktree, và **nhánh đặt đúng tên cung**. Nhờ
quy ước đó, `git worktree list` là sổ ghi việc duy nhất cần có; không
phiên nào phải đoán ai đang làm gì.

### Trước khi bắt đầu

Năm lệnh, chạy từ cây chính, mất vài giây:

    git fetch -q
    git worktree list                 # ai đang giữ cung nào
    git status --short                # có file lạ chưa theo dõi không
    git branch -r --sort=-committerdate | head
    npm run kiem                      # tài liệu này có còn khớp repo không,
                                      # và bản bạn đang giữ có cũ không

`git status --short` mà thấy thư mục lạ (`?? hoang-thanh/`) thì **có phiên
khác đang dựng dở trong cây chính**. Đừng đụng, đừng add, đừng chạy
`npm run dist` — bản dựng sẽ dính nửa cung chưa xong.

`npm run kiem` báo lệch thì xem mục **"Khi phát hiện lỗi trong chính file
này"** ở cuối — sửa trước khi làm việc khác, vì mọi luật ở đây chỉ đúng
khi tài liệu còn khớp thực tế.

Phép kiểm đầu tiên của nó là **bản bạn đang giữ có cũ không**. Bảy phép
còn lại so tài liệu cục bộ với repo cục bộ, nên worktree cũ có cả hai đều
cũ mà khớp nhau sẽ in ✓ — xanh trong khi bạn làm theo luật đã bị thay.
Phải chạy `git fetch -q` trước, không thì nó đọc ref cũ trên đĩa.

Chuyện lỗi thời được canh ở **hai lớp**, và chúng bù nhau chứ không thừa:
hook pre-commit (mục dưới) nhắc phiên đang chạy dở mà không nhớ chạy lệnh
nào — nó luôn thoát 0, chỉ nhắc; còn `npm run kiem` thoát 1, nên chặn được
và cắm CI được. Lớp thứ nhất tới được người không tìm nó; lớp thứ hai có
răng.

Phiên mở từ worktree cũ đang giữ bản `CLAUDE.md` cũ. Xem **đúng phần đã
đổi** kể từ lúc worktree được tạo:

    git fetch -q
    git diff HEAD origin/main -- CLAUDE.md

Không in ra gì là bản của bạn còn mới. In ra thì đọc hết phần đó trước
khi làm gì, rồi `git merge --ff-only origin/main` để bắt kịp.

(Đừng dùng `git show origin/main:CLAUDE.md | head -60` — file này đã dài
hơn 350 dòng, `head -60` cắt mất cả chương "Khi phát hiện lỗi trong chính
file này" ở cuối, tức là giấu đi đúng phần mà phiên đang bắt kịp cần nhất.)

### Hook nhắc — cách duy nhất chạm tới phiên đang chạy

Mọi lệnh ở trên chỉ chạy khi phiên **tự nhớ mà chạy**. Phiên mở từ hôm
qua, đang làm dở, sẽ không tự nhiên chạy `git fetch`. Không có kênh nhắn
tin nào giữa các phiên — chúng là tiến trình riêng.

Chỗ hở duy nhất: **worktree dùng chung `.git/hooks`**. Worktree chỉ tách
`.git/worktrees/<tên>`, còn hooks thì không. Nên hook cài một lần sẽ chạy
trong **mọi** phiên, kể cả phiên đang mở dở.

    npm run hook        # cài, chạy một lần cho cả kho

Từ đó mỗi lần commit, nếu `CLAUDE.md` của bạn cũ hơn `origin/main`, hoặc
bạn đang dàn file bot tự sinh, hook in một khối nhắc. Nó **luôn thoát 0** —
chỉ báo, không chặn. Cố ý: một hook chặn do phiên khác cài mà phiên đang
chạy không hay biết thì chính là kiểu va chạm cả quy trình này muốn tránh.

Danh sách file bot hook đọc thẳng từ mục "File do workflow tự sinh" bên
dưới, không chép lại — hai bản sao thì sẽ lệch. Gỡ hook: xoá
`.git/hooks/pre-commit`.

### Phạm vi sửa

- Chỉ sửa file bên trong thư mục cung được giao cho phiên này.
- **Không bao giờ `git add -A` hay `git add .`** — chỉ add đúng thư mục
  cung. Phiên khác có thể đang viết dở file của nó; `git add -A` sẽ nuốt
  luôn nửa việc chưa xong của họ vào commit của bạn.

  Luôn add theo đường dẫn, rồi soát lại trước khi commit:

      git add tang-thu-cac/
      git status --short          # mọi dòng phải bắt đầu bằng tên cung
      git diff --staged --name-only | grep -v '^tang-thu-cac/'
      #  ↑ phải KHÔNG in ra gì. In ra dòng nào là đang ôm file của người khác.
- Không đụng file dùng chung ở gốc repo: `index.html`, `sw.js`,
  `manifest.webmanifest`, `assets/`, `scripts/`, `package.json`,
  `server.js`, `CLAUDE.md`, `.github/workflows/`. Cần sửa thì dừng lại
  hỏi trước.
- Không merge, không rebase vào nhánh khác. Commit và push lên đúng nhánh
  worktree hiện tại. Người dùng vẫn là người quyết định **khi nào** gộp;
  bảo gộp rồi thì làm theo mục "Gộp về `main`", đứng nguyên trong worktree.

### File do workflow tự sinh — đừng sửa tay

Workflow chạy theo lịch và commit thẳng vào `main`. Chúng ghi đè đúng
những đường dẫn dưới đây; sửa tay là chắc chắn conflict lúc merge.

`refresh-data.yml` (17 phút sau 0, 3, 6, 9, 12, 15, 18, 21 giờ UTC —
tám mốc, nhưng node nào chạy thì sổ đăng ký quyết, xem mục dưới):

    kinh-thanh/assets/js/data/live.js
    kinh-thanh/assets/js/data/provenance.js
    kinh-thanh/assets/data/history.json
    do-sat-vien/assets/js/data.js
    do-sat-vien/assets/logos/
    cong-bo/assets/js/data.js
    cong-bo/assets/js/logos.js
    cong-bo/assets/js/v/nhat-ky.js
    cong-bo/assets/logos/
    ho-bo/assets/js/v/dong-tien.js
    thai-boc-tu/assets/js/v/doan-tau.js
    thai-boc-tu/assets/js/v/cong-truong.js
    thai-boc-tu/assets/js/v/tin-tuc.js
    thai-boc-tu/assets/js/v/tin-phan-tich.js
    tang-thu-cac/assets/js/data.js
    tang-thu-cac/assets/data/lich-su.json
    tang-thu-cac/assets/data/kb/
    dai-quan-trac/assets/js/do.js
    dai-quan-trac/assets/js/scan.js
    dai-quan-trac/assets/js/tq/do.js
    dai-quan-trac/assets/js/tq/scan.js
    dai-quan-trac/assets/js/tin.js
    .claude/skills/
    factory/skills.json
    factory/tien-hoa.jsonl
    factory/kho-de-xuat.json
    factory/phieu.json
    factory/state.json
    factory/bao-cao.md
    tao-bien-xu/assets/js/v/van-hanh.js
    cong-bo/assets/js/v/tri-thuc.js
    dai-quan-trac/assets/js/v/tri-thuc.js
    do-sat-vien/assets/js/v/tri-thuc.js
    ho-bo/assets/js/v/tri-thuc.js
    hoang-thanh/assets/js/v/tri-thuc.js
    kham-thien-giam/assets/js/v/tri-thuc.js
    tang-thu-cac/assets/js/v/tri-thuc.js
    tao-bien-xu/assets/js/v/tri-thuc.js
    thai-boc-tu/assets/js/v/tri-thuc.js
    thi-bac-ty/assets/js/v/tri-thuc.js
    tu-cam-thanh/assets/js/v/tri-thuc.js

### File bot ĐỒNG SỬA — vẫn sửa tay được, nhưng đọc mục này trước

    ho-bo/assets/css/app.css
    ho-bo/assets/js/app.js
    ho-bo/index.html
    ho-bo/sw.js
    thai-boc-tu/assets/css/app.css
    thai-boc-tu/assets/js/app.js
    thai-boc-tu/index.html
    thai-boc-tu/sw.js
    dai-quan-trac/index.html
    dai-quan-trac/assets/css/app.css
    dai-quan-trac/assets/css/halls.css
    dai-quan-trac/assets/js/app.js
    dai-quan-trac/assets/js/trang/dong.js
    dai-quan-trac/assets/js/trang/bang.js
    dai-quan-trac/assets/js/trang/soi.js
    dai-quan-trac/assets/js/trang/nen.js
    dai-quan-trac/sw.js
    kham-thien-giam/assets/css/app.css
    kham-thien-giam/assets/js/app.js
    kham-thien-giam/index.html
    kham-thien-giam/sw.js
    tao-bien-xu/assets/css/app.css
    tao-bien-xu/assets/js/app.js
    tao-bien-xu/index.html
    tao-bien-xu/sw.js
    knowledge-os/data/bridges/repo.json
    knowledge-os/data/2026/concepts.json
    knowledge-os/data/2026/relations.json

Đây là một loại thứ **ba**, đừng lẫn với hai loại trên:

| loại | ai ghi | sửa tay được không |
|---|---|---|
| bot tự sinh (`v/dong-tien.js`…) | chỉ bot | **không** — lượt sau đè |
| sinh tay (`hoang-thanh/data.js`…) | chỉ người | có, đó là cách duy nhất |
| **đồng sửa** (bảng trên) | **cả hai** | **có** — nhưng xem dưới |

Đài Quan Trắc **từng** hẹp hơn hai cung kia: lời nhắc chỉ cho model
sửa `app.css` và `app.js`. Điều đó đúng vào ngày `app.js` còn giữ cả
16 hàm vẽ. Sau khi 16 hàm ấy tách sang `assets/js/trang/`, phần lớn
giao diện nằm NGOÀI phạm vi của chính vòng sửa giao diện — và vì cổng
chặn `exit 1` khi thấy file ngoài danh sách, model sửa đúng chỗ cần
sửa lại làm hỏng cả lượt. Nay phạm vi gồm `index.html`, hai file CSS,
`app.js` và bốn file `assets/js/trang/`.

Ba nơi khai phạm vi ấy phải TRÙNG nhau: lời nhắc trong `refresh-data.yml`,
biến `CHO` của bước cổng chặn, và `ra` của node trong
`scripts/node/dai-quan-trac.mjs` — `ra` là chỗ `duong-ra` sinh `git add`,
nên thiếu một đường thì bản vá biến mất mà mọi log đều xanh.

Vẫn ở ngoài, có lý do: `halls.js` và `v/tri-thuc.js` do máy sinh nên sửa
tay là mất ở lượt sinh sau; `khung.js` là lớp phương pháp chứ không phải
lớp vẽ; `pwa.js` đụng vòng đời service worker, hỏng ở đó thì người dùng
kẹt bản cũ mà cổng chặn không thấy.

`sw.js` có mặt vì bước nâng CACHE_VERSION ghi vào nó sau khi bản vá
được nhận, chứ không phải thứ model sửa.

Node `ho-bo-tien-hoa` (nhịp 24 giờ) để model đề xuất sửa giao diện,
rồi `scripts/tien-hoa.mjs cong --so` quyết định nhận hay trả lại. Nên
bốn file đó vừa là mã viết tay, vừa là thứ bot chạm vào mỗi ngày.

Ba đường `knowledge-os/data/` ở cuối bảng cũng là đồng sửa, nhưng do
node `tri-thuc-tien-hoa` chứ không phải vòng giao diện. Model **chỉ**
được chạm ba đường đó; lớp sách (`data/concepts/`, `data/relations/`,
`data/chapters/`, `data/sources/`) là **người viết, tuyệt đối không có
bot** — xem mục knowledge-os bên dưới để biết vì sao.

Hệ quả khi bạn sửa tay chúng:

- **Cứ sửa.** Đây là mã nguồn thật, không phải file sinh ra. Không có
  lượt nào "đè" bạn: model chỉ sửa *thêm* trên bản mới nhất trong repo.
- **Chạy `node scripts/tien-hoa.mjs do ho-bo` trước khi commit.** Không
  thước nào được tụt. Sửa tay làm tụt điểm thì lượt tiến hoá kế tiếp
  sẽ thấy đó là điểm yếu và đi vá — tốn một lượt cho việc bạn vừa làm.

  Đừng ghi cứng con số ở đây. Số thước đã đổi một lần (bảy → mười, khi
  ba luật của `baseline-ui` và `frontend-design` được dịch thành phép
  canh), và mọi chỗ ghi "bảy thước" trong workflow lúc ấy thành nói sai
  cùng lúc — model đọc lời nhắc rồi tưởng mình đã xem hết bảng.
- **Xung đột lúc gộp là có thật**, khác hẳn hai loại kia. Bot commit
  thẳng vào `main` nên nhánh worktree đụng bốn file này phải rebase
  như với bất kỳ file dùng chung nào.

Không gộp bốn đường này vào danh sách "bot tự sinh — đừng sửa tay" ở
trên, dù `npm run kiem` cũng chấp nhận. Làm vậy là nói sai sự thật, và
hook pre-commit sẽ nhắc nhầm mỗi lần có người sửa `app.js` một cách
hoàn toàn hợp lệ — đúng cái bẫy mà mục `cong-bo/assets/js/` đã cắn.

Ba đường cuối là **sổ nhà máy** — xem mục "Nhịp chạy nằm ở sổ đăng ký"
ngay dưới. `van-hanh.js` là bản chiếu của `state.json` cho trình duyệt,
nên hai file đó luôn đi cùng nhau trong một commit.

Danh sách này liệt kê **từng file**, không gom cả thư mục. Trước đây nó
ghi `cong-bo/assets/js/` và điều đó sai theo cả hai hướng:

- **Rộng quá.** Thư mục ấy còn chứa `halls.js`, `app.js`, `decoder.js`,
  `glossary.js`, `pwa.js` — toàn file viết tay. Hook pre-commit đọc danh
  sách này để nhắc, nên nó báo nhầm mỗi lần ai đó sửa `halls.js` một
  cách hợp lệ, tức là mỗi lần thêm cung mới. Cảnh báo báo nhầm mãi thì
  người ta bỏ qua cảnh báo, và lần nó đúng cũng bị bỏ qua nốt.
- **Hẹp quá.** Hai thư mục logo bị sót hẳn: `build-l2beat.mjs` và
  `build-congbo.mjs` tải ảnh về `assets/logos/`, mà `git add` không phủ.
  `logos.js` thì được commit và trỏ tới những ảnh chưa bao giờ được
  commit — ảnh vỡ trên site, không lỗi nào báo. Chưa nổ vì lần thêm logo
  gần nhất làm bằng tay; sẽ nổ đúng lần L2BEAT thêm dự án mới.

Nên khi thêm một script sinh dữ liệu, hỏi đúng một câu: **script này
`writeFile` vào những đường nào?** Mọi đường đó phải có ở đây và trong
`git add`, không thừa không thiếu.

Đúng lỗi đó vừa lặp lại một lần nữa với `tang-thu-cac/assets/data/`.
Thư mục ấy còn chứa `dich/` — **bản dịch tiếng Việt VIẾT TAY** cho skill
cộng đồng, bot không hề ghi. Gom cả thư mục thì hook báo nhầm mỗi lần
sửa bản dịch, và tệ hơn: một phiên sau đọc mục này sẽ tưởng cả thư mục
là bot sinh mà xoá đi. Nay liệt kê đúng hai đường bot thật sự ghi —
`lich-su.json` và `kb/`.

    tang-thu-cac/assets/data/dich/   ← VIẾT TAY, commit như mã nguồn

### Repo này KHÔNG dùng `ANTHROPIC_API_KEY` nữa

Từ **15/08/2026**, mọi lời gọi model trong xưởng đều trả bằng **quota gói**
qua `CLAUDE_CODE_OAUTH_TOKEN`. Không còn secret tính tiền theo token nào.

Chuyện đã xảy ra, ghi lại để đừng ai dựng lại đường cũ: bản quét Đài Quan
Trắc từng có workflow riêng gọi thẳng `api.anthropic.com`. Bảng điều khiển
Anthropic ghi **610K token và 4,30 USD** cho đúng **ba lượt** — khoảng
**1,4 USD một lượt**, ở nhịp 4 lượt/ngày là cỡ **170 USD/tháng**. Lịch
phải tắt sáng 14/08, và cung sống bằng bản quét cũ suốt từ đó.

Vặn ba núm (Opus→Haiku, `max_uses: 3`, nhịp 4→1 lượt/ngày) chỉ hạ được
xuống vài USD/tháng. Thứ giải quyết hẳn là **đổi đường trả tiền**, không
phải vặn núm: `anthropics/claude-code-action` + token OAuth.

`scan-observatory.yml` đã **xoá**. Bản quét nay là ba bước trong
`refresh-data.yml`, và tách ba bước là có chủ ý:

| bước | ai làm | ra cái gì |
|---|---|---|
| Ra đề | `build-scan.mjs --de-bai` | `assets/data/de-bai.json` từ `THEATERS` trong data.js |
| Quét | Claude Code Action + WebSearch | `assets/data/quet.json` — JSON **thô** |
| Dựng | `build-scan.mjs` | `assets/js/scan.js`, sau khi kiểm |

**Đừng cho model ghi thẳng `scan.js`.** Đó là file JS trình duyệt nạp —
một lỗi cú pháp của model thành một trang trắng cho người xem. Bước dựng
còn chặn id chiến trường bịa, mức ngoài bảng `g/y/r`, và ngày sai khuôn;
không nhận được chiến trường nào thì **giữ bản cũ** chứ không ghi đè bằng
bảng trống — bảng trống người ta đọc thành "thế giới không có tin gì".

Hai file `de-bai.json` và `quet.json` nằm trong `.gitignore`: chúng chỉ
sống trong một lượt chạy, thứ đáng giữ là `scan.js` đã qua kiểm.

(`scripts/dich-skill.mjs` vẫn đọc `ANTHROPIC_API_KEY` — đó là công cụ
dịch **chạy tay**, không nằm trong vòng tự động, và không có secret nào
trong repo cho nó.)

### Nhịp chạy nằm ở sổ đăng ký, không nằm ở cron

Trước 14/08/2026, "bao lâu chạy một lượt" nằm rải ở **ba** chỗ không chỗ
nào biết chỗ nào: `cron` trong workflow, thứ tự các bước trong workflow,
và ngưỡng "bao lâu là cũ" trong `scripts/tuoi-du-lieu.mjs`. Ba chỗ phải
khớp nhau mà không có gì bắt chúng khớp — sót một chỗ thì bot vẫn chạy,
`npm run kiem` vẫn xanh, chỉ có dữ liệu là sai nhịp.

Giờ nhịp nằm ở sổ đăng ký, một chỗ:

    node scripts/nha-may.mjs bang         xem cả nhà máy trong một bảng
    node scripts/nha-may.mjs den-han      node nào đến hạn (workflow đọc)
    node scripts/nha-may.mjs duong-ra     đường nào đáng commit (workflow đọc)
    node scripts/nha-may.mjs so-dang-ky   sinh lại factory/registry.json
    node scripts/nha-may.mjs chieu        sinh lại van-hanh.js cho webapp

#### Một cung một file: `scripts/node/<cung>.mjs`

Sổ đăng ký **không** nằm trong `nha-may.mjs` nữa. Mỗi cung khai node của
mình trong `scripts/node/<cung>.mjs`; `nha-may.mjs` đọc cả thư mục theo
thứ tự tên file rồi gộp lại. Node của chính nhà máy (đóng dấu, báo cáo,
giao hàng) nằm ở `scripts/node/xuong.mjs`.

Vì sao tách, và đây là chuyện đã cắn thật ngày 20/08: khi cả 18 node
khai chung một mảng, **hai phiên thêm hai cung là hai người sửa cùng vài
dòng của cùng một file**. Worktree tách được file theo cung, nhưng không
tách được mảng dùng chung ấy — nên xung đột mỗi lần, không trừ lần nào.

Nay **thêm một cung = thêm MỘT file mới**. Hai file khác nhau thì git
không có gì để mà đụng: hết xung đột do cấu trúc, không phải do ai đó
nhớ giỏi hơn.

Hệ quả kèm theo: `factory/registry.json` mang thêm trường `khai` — file
nào khai node đó. Lỗi ném ra từ phép kiểm cũng chỉ thẳng file phải sửa,
thay vì bắt đi tìm trong một mảng dài.

`cron` trong hai workflow chỉ còn là **TRẦN** — "cứ 3 giờ ngó một lần xem
có gì đến hạn không". Đến hạn hay chưa thì sổ quyết. Hệ quả: **đổi nhịp
một cung là sửa đúng một con số**, không đụng YAML. Muốn nhịp mịn hơn 3
giờ thì mới phải sửa cron.

**Tám mốc chứ không bốn, và đó là chuyện GitHub chứ không phải chuyện
nhịp.** Đo ngày 28/08 trên 56 lượt: từ 14/08 tới 26/08 chạy đúng 4
lượt/ngày, mười ba ngày liền; từ 26/08 20:05 tụt còn 2 lượt/ngày. Không
phải hai lượt chồng nhau (lượt dài nhất 38 phút) — thứ đổi là **độ trễ
so với giờ cron**, từ 35 phút–1,6 giờ lên 3,6–5,2 giờ. Trễ quá khoảng
cách giữa hai mốc thì GitHub bỏ hẳn mốc kế.

Mốc gãy trùng đúng lượt 38 phút đầu tiên, tức lúc các node tiến hoá lên:
xưởng nặng lên thì GitHub giãn lịch ra. Thêm mốc là cách duy nhất ta
điều khiển được từ phía mình, và nó gần như miễn phí — lượt không có
node nào đến hạn chạy hết **0,8 phút** (đo lượt 20/08 07:09).

Thêm một node thì `npm run kiem` bắt ba thứ phải khớp, và cả ba đều hỏng
im lặng nếu sai:

- node có `nhip` mà không workflow nào gọi tới → **không bao giờ chạy**,
  còn Bảng vận hành thì mãi báo "đến hạn"
- node khai `ra` mà `git add` không phủ → **chạy rồi mất**
- `factory/registry.json` lệch `NODE` → sổ đăng ký nói dối

Nhìn thấy nhà máy đang chạy: mở **Tạo Biện Xứ → Bảng vận hành**. Trang đó
đọc `van-hanh.js` nên nó hiện lượt chạy thật, không phải mô phỏng.

#### Hai node gọi model, hai bài toán chi phí khác nhau

Đừng chọn model theo cảm giác "to thì đắt" — chọn theo **khối lượng có
chặn được không**, và **trả bằng gì**:

Cả hai node giờ **trả bằng cùng một thứ** — quota gói. Nên câu hỏi còn
lại chỉ là khối lượng, và hai node này ở hai đầu đối nhau:

| node | khối lượng | model |
|---|---|---|
| `bao-cao` | **cố định**: 2 file JSON ~25 KB → 15 dòng, `--max-turns 8` | **Opus 5** |
| `dai-quan-trac` | **phình không chặn được**: WebSearch kéo cả trang web vào ngữ cảnh, nhân sáu chiến trường | **Haiku 4.5** |

Chỗ khối lượng cố định thì Opus rẻ hơn ta tưởng, mà phần giá trị nhất của
báo cáo — câu "nên xem chỗ nào trước" — đúng là chỗ model mạnh hơn thấy
rõ hơn. Chỗ khối lượng phình thì ngược lại: đổi sang Opus ở đó là đổi một
thứ không đo được thành một thứ không đo được và đắt gấp bội.

Quota không phải miễn phí — nó là gói của **bạn**. Bỏ được hoá đơn API
không có nghĩa là hết cần cân nhắc; nó chỉ đổi đơn vị đo từ đô la sang
lượt dùng của chính mình.

**Token gắn với một người.** `claude setup-token` cấp token theo gói của
người chạy lệnh, nên mỗi lượt bot ăn vào quota của chính người đó.

Muốn đổi số liệu thì sửa script sinh ra chúng trong `scripts/`, không sửa
file kết quả. (Và sửa `scripts/` là file dùng chung — hỏi trước.)

Chạy script ở máy để **kiểm** kết quả thì được, nhưng **đừng commit file
kết quả** — để bot ghi. Sửa xong script, push script, rồi chờ lượt bot kế
tiếp; kết quả tự đúng. Commit tay chỉ tạo hai nguồn ghi vào cùng một file.

    node scripts/build-tangthu.mjs        # xem số có hợp lý không
    git checkout tang-thu-cac/assets/     # rồi trả lại, đừng mang theo

**Khối `git add` trong workflow KHÔNG còn chép tay nữa** (từ 20/08). Nó
gọi `node scripts/nha-may.mjs duong-ra`, sinh thẳng từ `ra` của node.
Muốn đổi phạm vi thì sửa `ra` trong `scripts/node/<cung>.mjs` — một chỗ,
và workflow tự theo.

Danh sách trên đây vẫn phải khớp, và `npm run kiem` vẫn canh — nhưng giờ
nó đối chiếu với **sổ đăng ký** chứ không với một bản chép trong YAML.
Ba nơi phải khớp đã còn hai, và một trong hai là nguồn.

`duong-ra` chỉ in đường **có thật trên đĩa**. Nhờ vậy cả lớp lỗi
`pathspec did not match any files` biến mất — thứ đã giết năm lượt
liên tiếp ngày 15/08 vì `factory/bao-cao.md` chưa từng tồn tại.

### Hoàng Thành là ngoại lệ — sinh bằng tay, PHẢI commit

    hoang-thanh/assets/js/data.js
    hoang-thanh/assets/js/v/

Luật "đừng commit file kết quả" ở trên **không áp dụng cho cung này**, và
lý do nằm ở chỗ nguồn:

    D:\SUNSWaGz 2027\SUNSWaGz\sunswagz-hub\08_world_culture_forest

Thư mục đó nằm **ngoài repo**. Actions checkout repo này ra máy ảo thì
không có nó, nên không workflow nào quét được. Chạy tay ở máy có nguồn rồi
commit kết quả là cách duy nhất:

    npm run hoangthanh

**Đừng thêm bước này vào `refresh-data.yml`.** Nó sẽ luôn thấy thiếu nguồn
và không làm gì — một bước xanh vĩnh viễn không sinh ra gì, khó phát hiện
hơn là một bước đỏ.

Hệ quả cho độ tươi dữ liệu: dòng "rừng văn hoá Hoàng Thành: sinh cách đây N
ngày" **không bao giờ kèm ⚠**, vì nó sinh tay. **Năm** nguồn kia do bot ghi
và phải tươi trong **1 ngày**. Node số liệu có `nhip: 6` nên nhiều nhất
4 lượt ghi mỗi ngày dù workflow thức dậy 8 lần; quá 1 ngày nghĩa là bốn
lượt liên tiếp không ghi được gì.

### Ba runtime Python là ngoại lệ — và KHÔNG thư mục nào trong ba là cung

    tu-cam-thanh/assets/js/v/phien.js        ← sinh tay, PHẢI commit
    tu-cam-thanh-runtime/                    ← Python, KHÔNG lên site

    kham-thien-giam/assets/js/v/dai-chiem.js ← sinh tay, PHẢI commit
    kham-thien-giam-runtime/                 ← Python, KHÔNG lên site

    thi-bac-ty/assets/js/v/cang-phi.js       ← sinh tay, PHẢI commit
    thi-bac-ty-runtime/                      ← Python, KHÔNG lên site

**Cả ba theo cùng một luật.** Mục này viết theo Tử Cấm Thành vì nó có
trước; mọi câu dưới đây áp dụng y nguyên cho hai runtime kia, chỉ đổi tên
thư mục, cổng, và lệnh sinh lát cắt:

    cd kham-thien-giam-runtime
    python run.py                 buồng lái ở localhost:5186
    python -m kham.snapshot       ghi một lần rồi thoát
    python scripts/selftest.py    305 phép kiểm số học, KHÔNG cần mạng
    node scripts/kiem-giao-dien.mjs   10 phép kiểm giao diện (tương phản WCAG, z-index, ô trống)
    node scripts/kiem-buong-lai.mjs   13 ô của buồng lái có vẽ được không
    node scripts/kiem-lat-cat.mjs     lát cắt có khớp thứ cung tĩnh đọc không

    cd thi-bac-ty-runtime
    python run.py                 buồng lái ở localhost:5188
    python -m bac.snapshot        quét một lượt, ghi, rồi thoát
    python scripts/selftest.py    1081 phép kiểm số học, KHÔNG cần mạng
    pythonw dichvu/chay-nen.py    chạy nền 24/7 để tích băng đào tạo

Thị Bạc Ty **không cần khoá nào để chạy đủ**: nó chỉ đọc dữ liệu CÔNG KHAI
— bốn sàn perp, ba sàn giao ngay, Deribit, LI.FI, DefiLlama, và RPC công
khai bốn chuỗi. Không nguồn nào đòi khoá. `.env` chỉ để buồng lái nói đúng
cửa nào đang đóng —
`bac/config.py` không đọc giá trị khoá nào ở bản này, và lớp đặt lệnh thì
chưa được viết, nên không cấu hình nào biến nó thành trader.

Một khác biệt đáng ghi: runtime Khâm Thiên Giám **không cần khoá nào để
chạy đủ**. `ANTHROPIC_API_KEY` chỉ dùng cho vòng não CHẬM (hậu kiểm, đọc
lại băng); thiếu nó thì runtime vẫn chạy kín vòng vì mọi quyết định trong
đường nhanh là toán Python tất định. Còn khoá ví Polymarket thì nằm sau
**ba cửa** phải cùng mở mới đặt được một lệnh thật, và mặc định cả ba đều
đóng — xem `kham/config.py`. Thiếu bất kỳ cửa nào là rơi về sổ giấy, và
nó ghi rõ cửa nào đang đóng chứ không rơi trong im lặng.

Cung `tu-cam-thanh/` là trang tĩnh chỉ-đọc như mọi cung khác. Thứ sinh ra số
liệu cho nó là `tu-cam-thanh-runtime/` — một runtime Python (FastAPI + vòng
lặp nền + `ANTHROPIC_API_KEY` + ghi đĩa). Cùng lý do Hoàng Thành: Actions
không chạy được thứ đó, nên chạy tay ở máy rồi commit lát cắt.

    cd tu-cam-thanh-runtime
    python run.py                 buồng lái ở localhost:5182, ghi mỗi vòng lặp
    python -m trader.snapshot     ghi một lần rồi thoát
    python scripts/selftest.py    phép kiểm số học, KHÔNG cần mạng
                                  (không in tổng số như hai runtime kia)
    node scripts/kiem-giao-dien.mjs   giao diện có đọc được mọi trường nó cần không

**Đừng thêm bước này vào `refresh-data.yml`** — cùng lý do Hoàng Thành: một
bước xanh vĩnh viễn không sinh ra gì.

**KHÔNG runtime nào được thêm vào `HALLS` của `build-dist.mjs`.** Cả ba nằm
ngoài `dist/` vì `GATE` là danh sách tường minh. Thêm vào là đẩy mã nguồn và
cấu hình lên GitHub Pages lẫn IPFS — mà IPFS đã pin là không rút lại được.
Chúng cũng không bị `npm run kiem` nhầm là cung, vì bộ kiểm chỉ tính thư mục
có `index.html` **ngay tại gốc** thư mục đó; cả ba runtime chỉ có
`web/index.html` ở tầng hai. **Đừng tạo `<runtime>/index.html`.**

Buồng lái ở `:5182`, `:5186` và `:5188` có nút điều khiển nên **chỉ sống ở
máy**,
không bao giờ lên site — trang công khai mà gọi được model, hoặc bấm được
nút đặt lệnh, là khoá đã ra tới trình duyệt. Cung tĩnh và buồng lái cố ý là
hai giao diện: cung quan sát, runtime điều khiển.

**Runtime này đọc `ANTHROPIC_API_KEY`, và đó KHÔNG mâu thuẫn với mục "Repo
này không dùng `ANTHROPIC_API_KEY` nữa" bên trên.** Luật đó nói về *xưởng* —
các node chạy tự động trong Actions, nay trả bằng quota gói qua
`CLAUDE_CODE_OAUTH_TOKEN`. Runtime giao dịch nằm cùng nhóm với
`scripts/dich-skill.mjs`: **công cụ chạy tay, ngoài vòng tự động**. Khoá đọc
từ `tu-cam-thanh-runtime/.env` ở máy người chạy, file đó đã gitignore, và
**repo không có secret nào cho nó**.

Hệ quả phải giữ: **đừng đưa runtime nào vào bất kỳ workflow nào.** Làm vậy là
đòi một secret tính tiền theo token quay lại repo — đúng thứ vừa bị bỏ, và ở
đây còn tệ hơn vì vòng lặp giao dịch chạy liên tục chứ không phải 1 lượt/ngày.
Với Khâm Thiên Giám còn thêm một mức nữa: đưa nó vào Actions là đặt **khoá ví
có tiền thật** vào một môi trường tự động mà không ai ngồi nhìn.
Runtime tự có trần `dailyBudgetUsd` và `maxCallsPerDay` trong `config.json`,
nhưng trần ấy chỉ bảo vệ được máy đang chạy — nó không thay được việc **không
để đường tự động nào chạm tới khoá**.

### knowledge-os là ngoại lệ thứ tư — dữ liệu, không phải cung

    knowledge-os/                     ← nguồn, KHÔNG lên site
    <cung>/assets/js/v/tri-thuc.js    ← BOT ghi (node `tri-thuc`) · 11 cung

Lớp tri thức nền: nó trả lời "con số đang hiện đóng vai trò kinh tế gì",
không đổi công thức nào. **Đây không phải cung đọc sách và đừng dựng một
cái.** Gói lõi ở nguồn; mỗi cung nhận một lát cắt 9–30 KB.

    npm run tri-thuc-kiem       kiểm dữ liệu, và kiểm nó khớp repo thật
    npm run tri-thuc            sinh lát cắt cho mọi cung đã ánh xạ
    npm run tri-thuc -- --thu   xem sẽ ghi gì, chưa ghi
    npm run tra -- cung ho-bo   tra cứu ở dòng lệnh

**File sinh ra mang CẢ dữ liệu lẫn phần vẽ.** Mười một cung dùng chung
một khuôn HTML, nên khuôn ấy viết một lần trong `knowledge-os/sinh.mjs`
chứ không chép mười một bản — đúng lối `scripts/build-halls.mjs` đã đi
với `halls.js`. Cung chỉ gọi một dòng: `TT.them(host, maPhong)` (cung vẽ
lại theo tuyến) hoặc `TT.gan(maPhong, thẻ)` (cung dựng trang tĩnh). Sửa
cách vẽ thì sửa `sinh.mjs` rồi sinh lại, **đừng sửa `tri-thuc.js`**.

**Mã phòng phải trỏ vào mã CÓ THẬT, và cái không ánh xạ phải nói vì
sao.** 75 phòng đã ánh xạ, 29 phòng khai `rooms_skipped` kèm lý do —
phòng công cụ (xưởng huy hiệu, trang tra từ) không mang nội dung kinh tế
nào. Không có khai báo ấy thì bộ kiểm nhắc "còn N phòng chưa ánh xạ" mãi
cho những phòng sẽ không bao giờ được ánh xạ, và cảnh báo kêu mãi thì
người ta bỏ qua cảnh báo. `kinh-thanh` không ánh xạ phòng nào: thanh bên
của nó dựng theo từng quốc gia từ dữ liệu bot, nên không có mã cố định —
nó khai `rooms_note_vi` nói đúng câu đó.

Thêm cung mới **không bắt buộc** ánh xạ tri thức; bộ kiểm của gói chỉ
nhắc, không chặn.

Đường ghi nằm ở `assets/js/v/`, nhánh **mạng-trước**, nên sửa nó không cần
nâng `CACHE_VERSION`.

#### Hai node, và vì sao trước đây không có node nào

    tri-thuc            script · 24 giờ · dựng lại 11 lát cắt
    tri-thuc-tien-hoa   claude · 24 giờ · mở rộng chính lớp tri thức

Bản đầu **cố ý** không khai node nào, và lý do khi đó đúng: chưa có
**phiếu đo** cho lớp tri thức. `kiem.mjs` trả đúng/sai, mà đúng/sai thì
không so được giữa hai lượt — cắm một vòng tiến hoá vào lúc ấy là cho
model sửa dữ liệu mà cổng chặn không có gì để chấm ngoài "còn hợp lệ".

`knowledge-os/do.mjs` lấp đúng chỗ đó — bảy thước bằng số:

    npm run tri-thuc-do          phiếu đo
    node knowledge-os/do.mjs de-bai            ra đề cho model
    node knowledge-os/do.mjs cong --so <file>  cổng chặn

Có số rồi thì mới có vòng. Đây là vòng tiến hoá **thứ năm** của xưởng và
là vòng đầu tiên không sửa giao diện: bốn vòng kia vá `app.css`/`app.js`,
vòng này vá chính dữ liệu tri thức.

**Thước thứ tám tồn tại vì bảy thước kia không cho vòng việc gì làm.**
Bảy thước đầu đều hỏi "có gì hỏng không" — hỏng thì sửa xong là hết,
nên chúng cùng xanh và ở nguyên đó. Mà `de-bai` đọc chính phiếu này,
nên bảy-xanh nghĩa là `yeu=0`, nghĩa là **model không bao giờ được
gọi**: vòng đã dựng xong mà nằm im, thứ tệ hơn một vòng chưa dựng vì
nhìn vào sổ thì nó có vẻ đang chạy.

Thước tám hỏi chuyện khác — lớp 2026 đã phủ tới đâu:

    Khái niệm sách có phán quyết 2026    12/48 · mốc 24

Mốc là **một nửa, không phải tất cả**. Trong 48 khái niệm sách có
những cái thuần định nghĩa (`economic_value`, `unit_of_account`) mà
2018→2026 thật sự không có tin gì; đòi đủ 48 là dựng một thước không
bao giờ xanh nổi. Và **không có danh sách khai-bỏ-qua** ở thước này,
khác thước "phủ phòng" — danh sách ấy sẽ phải nằm trong lớp model
được phép sửa, tức là cho model tự khai miễn trừ cho chính nó.

Cổng chặn nay đọc cả **số**, không chỉ đếm ô xanh: thước nào có số thì
số cũng không được tụt. Không có phép ấy thì 12→7 và 12→20 đều là
"giữ nguyên 7/8" và đều qua cổng — model xoá năm quan hệ rồi thêm một
cái cũng được nhận.

#### Thứ tự ba lớp của cổng chặn là BẮT BUỘC

    1. validator qua        2. sinh lại chạy được        3. phiếu không tụt

Bản đầu xếp "rẻ trước, đắt sau" nên chấm phiếu trước rồi mới sinh lại.
Nhưng thước `lat-cat-tuoi` hỏi "lát cắt có khớp dữ liệu hiện tại
không", mà ngay sau khi model sửa dữ liệu thì câu trả lời **luôn** là
không — cho tới khi sinh lại. Nên phiếu tụt ở lớp 2 và **mọi bản vá
hợp lệ đều bị trả lại**: một lượt Opus mỗi ngày, vĩnh viễn, không lượt
nào được nhận, sổ ghi `loi` mà không ai đọc ra vì sao. Đúng cái bẫy đã
giết vòng Đài Quan Trắc chín lượt liền.

    npm run tri-thuc-thu      bắn 4 bản vá giả vào cổng, xem nhận/trả đúng không

Bốn kịch bản: bản vá thật phải **nhận**; xoá bớt quan hệ, chạm lớp
sách, và trùng id lớp 2026 phải **trả lại**. Nó bắt được lỗi thứ tự
trên ngay lượt chạy đầu tiên. Chạy nó mỗi khi sửa `do.mjs`.


**Phạm vi model hẹp hơn mọi vòng khác, và cố ý.** Nó chỉ được chạm lớp
phân tích (`data/bridges/repo.json`) và lớp 2026. Lớp **sách cấm tuyệt
đối** — nó cần người có PDF trong tay, còn một model đoán một số trang
nằm đúng khoảng chương thì qua được **mọi** phép kiểm mà vẫn là trích dẫn
bịa. Cổng chặn không bắt được chuyện đó, nên chặn ở **phạm vi** chứ không
chặn ở kết quả.

Thước thứ bảy canh đúng lớp model được sửa: `source_ref` của lớp 2026
phải trỏ vào một đường **có thật trên đĩa**. Một đường không tồn tại là
trích dẫn bịa mà qua được mọi phép kiểm khác.

`npm run kiem` nay gọi `knowledge-os/kiem.mjs` ở đầu mỗi phiên. Trước đó
không có gì gọi nó, nên drift nằm im tới khi ai đó nhớ ra — đã có thật:
Thị Bạc Ty thêm phòng `trung-uong` mà lớp giải nghĩa không hay biết.

**Ranh giới nguồn là luật, không phải khuyến nghị.** Bốn nhãn hiện trên
từng dòng của trang: `sách` (tác giả mô tả, có chương/trang) · `tác giả`
(lập trường riêng) · `phân tích` (SUNSWaGz suy ra) · `repo` (đo được từ
repo/runtime, năm 2026). Gộp "tác giả" vào "sách" là biến một lập trường
thành sự thật; gộp "phân tích" vào "sách" là mượn uy tín của sách cho suy
luận của mình. Cả hai đều nói dối mà không câu nào sai ngữ pháp, nên
`kiem.mjs` chặn từng cái — kể cả chiều ngược: gắn chương/trang sách cho
một mục `analysis` là lỗi.

Sách viết **2018**. Chuyện sau đó nằm riêng ở `data/2026/`; **đừng sửa dữ
liệu sách để "cập nhật" nó** — sửa là mất luôn khả năng nói "chỗ này tác
giả sai", vì không còn bản gốc để so.

Ánh xạ toa/phòng phải trỏ vào **mã có thật**. `kiem.mjs` đọc mã thẳng từ
mã nguồn cung (`toa.js`, mảng `PHONG`, `<section id>`) chứ không giữ bản
chép — trỏ vào mã không tồn tại thì trang vẫn mở bình thường và lặng lẽ
không hiện gì. Cung nào bộ kiểm chưa đọc được thì nó nói thẳng là không
kết luận được; thêm một nhánh vào `maPhong()` là xong.

Chi tiết ở `knowledge-os/README.md` và `knowledge-os/docs/SOURCE_POLICY.md`.

Danh sách nguồn và ngưỡng nằm ở `scripts/tuoi-du-lieu.mjs`, dùng chung cho
`npm run dist` (in ra) và `npm run kiem` (nhắc ở đầu phiên). Thêm cung mới
có dữ liệu tự sinh thì thêm một dòng vào `NGUON` ở đó, không chép sang chỗ
khác.

(`tri-thuc.js` **không** có trong `NGUON`: nó không phải số liệu có tuổi.
Một lát cắt tri thức "cũ ba ngày" không nói lên điều gì — dữ liệu nguồn
đổi khi có người sửa nó, không đổi theo giờ. `kiem.mjs` của gói canh đúng
thứ đáng canh: lát cắt có sinh sau lần sửa dữ liệu gần nhất không.)

`npm run kiem` **nhắc** chứ không báo lỗi khi dữ liệu cũ: bot chết không
phải lỗi của phiên đang mở, không được chặn họ làm cung của mình. Nhưng nó
in ở đầu mỗi phiên nên không chết âm thầm được nữa — đợt 13–14/08/2026
đường ống nằm hơn một ngày mà không ai hay, vì phép kiểm khi đó chỉ nằm
trong `npm run dist` và không ai chạy lệnh đó mỗi phiên.

Vì bot đẩy vào `main` liên tục, worktree phải nhánh từ `origin/main` chứ
không phải HEAD local. Đó là mặc định (`worktree.baseRef: fresh`); đừng
đổi sang `head`.

Hệ quả cho chính file này: worktree nhánh từ `origin/main`, nên sửa
`CLAUDE.md` phải commit và **push lên `main`** mới có tác dụng. Worktree
tạo trước đó vẫn giữ bản cũ.

### Sửa file trong SHELL thì phải nâng CACHE_VERSION

Mỗi `sw.js` khai một mảng `SHELL` và phục vụ những file đó theo lối
**cache trước** (`return hit || net`). Sửa một file trong SHELL mà không
nâng `CACHE_VERSION` ở đầu file thì máy đã cài app **cứ dùng bản cũ**.

Đây là kiểu hỏng khó lần ra nhất trong repo, vì nó không giống lỗi:

- không có 404, không có lỗi mạng, Actions xanh, `curl` thấy bản mới
- nhưng trình duyệt ghép **HTML mới với CSS cũ** — và cái lộ ra là
  **giao diện vỡ**, nên người ta đi tìm bug ở HTML/CSS mới thay vì ở cache

Đã dính thật: xếp lại thứ bậc Cổng Thành có đổi `assets/css/portal.css`,
quên nâng `v4 → v5`; luật `.vong-ic svg { width:15px }` không tới máy
người dùng, mà SVG chỉ có `viewBox` thì không có cỡ nội tại — icon phình
kín màn hình.

Đừng đếm tay xem cung nào cần nâng — có lệnh làm hộ:

    npm run nang -- --thu     xem sẽ nâng chỗ nào, chưa ghi gì
    npm run nang              nâng thật

Nó tính đúng thứ `npm run kiem` báo, nhưng còn nhìn cả file **đang sửa
dở** trong cây làm việc, nên chạy được TRƯỚC khi commit — đó là lúc cần
nó. (`kiem` chỉ soi trạng thái đã commit, đúng vai của nó là soát thứ
sắp đẩy đi.)

Còn một việc lệnh không làm thay được: **cho SVG cỡ nội tại**
(`width="15" height="15"`) chứ đừng chỉ dựa vào CSS. Lỡ CSS cũ còn kẹt
thì hỏng nhẹ, không phình kín trang.

**File phục vụ MẠNG-TRƯỚC thì không cần nâng.** Cả `kiem` lẫn `nang` đều
bỏ qua chúng: service worker lấy bản mới mỗi lần, cache chỉ là lưới đỡ
lúc mất mạng. Không có luật trừ này thì bot cập nhật số liệu 4 lượt/ngày
sẽ đòi nâng version 4 lượt/ngày, và cảnh báo hoá thành tiếng ồn.

Ngược lại, file bot sinh mà nằm nhánh **cache-trước** là bẫy: đã dính với
`cong-bo/assets/js/logos.js` — bot ghi 4 lượt/ngày nhưng máy đã cài app
giữ bảng tra logo cũ tới lần nâng version kế tiếp, nên logo dự án mới
không bao giờ hiện dù ảnh đã lên site. Đã chuyển nó sang mạng-trước.

#### Khai mạng-trước theo dạng nào cũng được, miễn bộ kiểm đọc được

Hai dạng đang dùng thật, cả hai đều hợp lệ:

    url.pathname.indexOf("/assets/js/v/") !== -1          chín cung

    var MANG_TRUOC = ["/assets/js/scan.js", …];           dai-quan-trac
    MANG_TRUOC.some(function (p) {
      return url.pathname.indexOf(p) !== -1; })

Nhận diện nằm **một chỗ**: `scripts/mang-truoc.mjs`, dùng chung cho cả
`kiem` lẫn `nang`. Trước 20/08/2026 cùng một regex bị chép ở hai script,
và nó chỉ bắt được dạng thứ nhất — nên Đài Quan Trắc bị báo "CACHE_VERSION
chưa nâng" sau **mỗi** lượt bot ghi `scan.js`, suốt nhiều ngày, trong khi
file đó vốn đã mạng-trước từ đầu.

Cái giá không phải một dòng báo thừa. Cảnh báo báo nhầm đều đặn thì người
ta bỏ qua cảnh báo — rồi bỏ qua luôn lần nó đúng. Đúng thứ cả bộ kiểm này
sinh ra để chặn.

Nên nay bộ kiểm phân biệt **"không có đường mạng-trước nào"** với **"tôi
không đọc được khai báo"**. Gặp dạng thứ ba nó chưa biết, nó nói thẳng là
không kết luận được và chỉ sang file trên, thay vì buộc tội oan; còn `nang`
thì bỏ qua cung đó chứ không nâng bừa. Viết sw.js theo dạng mới thì **thêm
một nhánh nhận dạng vào `scripts/mang-truoc.mjs`** — đừng bẻ sw.js cho vừa
bộ kiểm, công cụ phải theo được mã thật chứ không phải ngược lại.

### Hai thang: một lệnh cho mỗi cung, đừng sửa CSS cung người khác

    npm run thang -- <cung> --thu     xem sẽ đổi gì, chưa ghi (cả hai thang)
    npm run thang -- <cung>           ghi thật · --chu / --cach để chọn một
    npm run thang -- --tat-ca --thu   soi cả 12 cung một lượt

Hai thước `thang-chu` và `thang-cach` trong `scripts/tien-hoa.mjs` — dịch từ skill
`frontend-design` (kho anthropics/skills, đang nằm trên kệ
`.claude/skills/`): *"set a clear type scale"* — đếm số cỡ chữ px rời
rạc còn viết thẳng vào rule. Đo ngày 28/08 thì **11 trên 12 cung
trượt**, từ 16 tới 34 cỡ. Hộ Bộ có 32 cỡ, trong đó **mười một** cỡ chen
giữa 11px và 13px. Đó không phải thang, đó là số bốc từng lúc.

Máy gom cỡ của **chính cung đang sửa** thành cụm rồi lấy cỡ dùng nhiều
nhất mỗi cụm làm nấc — nên cỡ phổ biến đứng yên, chỉ cỡ lẻ bị kéo về,
và nó luôn in ra "cỡ dịch nhiều nhất bao nhiêu phần trăm" (đo được
3,8–6,6%, tức dưới một pixel ở cỡ chữ thân bài). **Không áp thang của
Hộ Bộ cho cung khác**: cung 54 phòng và cung 5 phòng không cần cùng
một thang.

Vì sao là máy chứ không sửa tay: lúc viết mục này có **16 worktree
đang mở**, bảy trong số đó giữ đúng những cung cần sửa. Một phiên đi
sửa CSS của 11 cung khác là đúng thứ luật "chỉ sửa thư mục cung mình"
sinh ra để chặn. `--tat-ca` **cố ý chỉ chạy cùng `--thu`**.

**Thang khoảng cách là chuyện khác thang chữ, đừng lẫn.** Cỡ chữ gom
được sâu (32 → 10 nấc) vì các cỡ nằm sát nhau; khoảng cách thì không —
`8px` và `10px` cách nhau 25%, gom lại là đổi bố cục thấy được. Nên máy
**chặn theo MỨC ĐỔI (6%) chứ không chặn theo số nấc**, và số nấc là thứ
rơi ra. Bản đầu làm ngược, ép xuống 16 nấc bằng mọi giá, và khoảng cách
phải dịch 10–15% — ở `padding: 40px` là 6px, mắt thấy rõ.

Hệ quả phải chấp nhận: với khoảng cách, máy thường chỉ bớt được vài
nấc. Nó **in ra một dòng ⚠ khi kết quả vẫn trên 12 nấc**, và **từ chối
chạy** khi không bớt được nấc nào — vì lúc đó nó chỉ đang đổi tên.

Và hai thước **đếm cả nấc `--t-*` / `--k-*`, không chỉ px viết thẳng**.
Không đếm thì chúng lách được bằng đúng phép đổi tên ấy: `12.3px` thành
`var(--t-7)` là px biến sạch, thước báo 0, mà cung vẫn có 32 giá trị
rời rạc — chỉ là đã dọn vào một chỗ. Dọn vào một chỗ là tốt, nhưng đó
không phải câu thước hỏi. Không có phép đếm này thì `scripts/thang.mjs`
là một cái máy dựng ra để lách chính thước mà nó phục vụ.

Sửa xong thì `node scripts/tien-hoa.mjs do <cung>` để soát, rồi
`npm run nang` — `app.css` nằm trong SHELL.

**Một bẫy đã cắn thật, ghi lại để đừng ai gỡ mất bản vá.** Bản đầu của
máy này chèn khối thang chữ **trước** khối `:root` đầu tiên. Phép đo
tương phản khi đó chỉ đọc khối `:root` **đầu tiên**, nên nó gặp một
khối toàn px không màu nào và chuyển sang "không đo được" — Đô Sát Viện
đi từ 10/11 xuống 10/10: mẫu số tụt một, **điểm vẫn đẹp**, và không
dòng nào kêu. Nay `doMau` đọc **mọi** khối `:root`, còn máy vẫn chèn
sau khối đầu. Giữ cả hai; bỏ một cái là mở lại cửa cho một phép kiểm
biến mất trong im lặng.

### Ba thước tiếp cận: một máy nữa, cùng lối `thang.mjs`

    npm run tiep-can -- <cung> --thu     xem sẽ đổi gì, chưa ghi
    npm run tiep-can -- <cung>           ghi thật
    npm run tiep-can -- --tat-ca --thu   soi cả 12 cung một lượt

Cùng giao diện và cùng luật `--tat-ca` chỉ đi với `--thu` như mục trên,
nên đây chỉ nói phần khác.

Ba thước, ba cách hỏng khác nhau, nhưng cùng một tính chất: **người dùng
chuột trên màn hình sáng không bao giờ gặp chúng**, nên chúng nằm im
nhiều tháng mà không ai báo.

    nhan       svg trang trí thiếu aria-hidden → trình đọc màn hình đọc
               ra một mớ toạ độ giữa câu
    tieu-diem  thiếu :focus-visible → đi bằng bàn phím thì không biết
               mình đang đứng ở đâu trên trang
    so-cot     thiếu tabular-nums → mỗi lượt cập nhật là cả bảng số nhảy
               ngang, và mắt đọc lướt theo cột bị gãy

Vòng tiêu điểm dùng **màu nhấn cung tự chọn** — biến đang làm `color`
của thẻ `a` — chứ không bịa thêm một màu thứ hai. `tabular-nums` khai ở
`body` vì `font-variant-numeric` **di truyền**: một dòng phủ cả trang,
và bộ đo có nhánh nhận đúng chuyện đó.

**Phép nhận diện của máy phải là bản CHÉP của thước, không phải bản rút
gọn.** Đã cắn thật ngay lúc viết file này: bản đầu chỉ hỏi "`tabular-nums`
có khai ở gốc không", nên nó đòi vá **sáu** cung đang khai theo từng khối
và đang ĐẠT thước. Máy vá thứ không hỏng thì sinh ra diff rỗng, mà người
duyệt gặp diff rỗng vài lần là thôi đọc diff. Nay nó chép nguyên cả nhánh
di truyền của `so-cot` trong `scripts/tien-hoa.mjs`, và in ra **đếm được
bao nhiêu mặt số còn thiếu** thay vì một câu chung. Nghĩ ra một phép nhận
diện khác là sớm muộn máy vá một tập, bộ đo soi một tập khác, và không
bên nào sai rõ ràng để mà sửa.

Đo ngày 29/08: tám cung đủ cả ba; còn `kham-thien-giam` (53 mặt số),
`tang-thu-cac` (1), `thi-bac-ty` và `tu-cam-thanh` (thiếu cả ba) — cả
bốn đều đang nằm trong worktree của phiên khác, nên phiên giữ cung nào
chạy lệnh cho cung ấy.

`index.html` nằm trong SHELL, nên vá `nhan` xong phải `npm run nang`.

### Chỗ đè im lặng trong CSS

    npm run de-im-lang            soi Cổng Thành + 12 cung · thoát 1 khi còn chỗ đè
    npm run de-im-lang -- <cung>  soi một cung

`npm run kiem` gọi nó ở đầu mỗi phiên và **nhắc** chứ không chặn: CSS
của cung khác không phải việc của phiên đang mở.

Báo khi **cùng ngữ cảnh, cùng selector, cùng thuộc tính, khác giá trị,
ở hai khối khác nhau** — tức là một trong hai đang chết mà người viết
nó không hay.

**Vì sao đáng có một phép canh riêng: lớp lỗi này mở rộng theo số
cung.** `knowledge-os` sinh widget mang tiền tố `tt-` cho mười một
cung, nên mỗi lớp mới là mười một chỗ có thể đụng tên với lớp sẵn có.
Đã đụng thật: Đài Quan Trắc dùng `tt-` cho *trạng thái*, widget dùng
`tt-` cho *tri thức*, cùng độ đặc hiệu thì cái nằm dưới thắng — số cấp
độ, chữ to nhất trên dải trạng thái, bị vẽ 10,5px thay vì 27px ở mọi
trang, mọi chủ thể, không lỗi nào báo. Tìm ra nó là do may.

Hai luật trừ, cả hai đều đã báo nhầm trong bản nháp và đều phải giữ:

- **Khai hai lần trong CÙNG một khối là dự phòng cố ý**, không phải
  chỗ đè — `height:100vh; height:100dvh`, `display:block;
  display:-webkit-box`. Đó là cách duy nhất viết dự phòng trong CSS.
  Nên trong mỗi khối chỉ lấy giá trị CUỐI, đúng thứ trình duyệt dùng.
- **Khoá theo CẢ danh sách selector, không tách ra.** `.a,.b{color:x}`
  rồi `.b{color:y}` là nền chung rồi biệt hoá — tác giả cố ý viết thế.
  Tách danh sách thì nó thành "cùng `.b`, khác giá trị" và bị gọi oan.

Máy **chỉ báo, không tự sửa**, và đó là chủ ý: `.drawer` rộng 470px
hay 400px là quyết định thiết kế, chỉ người dựng cung ấy biết. Thứ máy
nói chắc chắn là hôm nay một trong hai đang chết.

### Cổng dev

Mỗi cung có một cổng cố định. Phiên lo cung nào thì dùng đúng cổng của
cung đó — tự tra bảng này, không cần ai giao số:

    5173  Cổng Thành (gốc repo)   ← cũng là mặc định của server.js
    5174  cong-bo
    5175  dai-quan-trac
    5176  do-sat-vien
    5177  kinh-thanh
    5178  tang-thu-cac
    5179  hoang-thanh
    5180  tao-bien-xu
    5181  tu-cam-thanh
    5182  tu-cam-thanh-runtime  ← KHÔNG phải cung; là runtime Python (xem mục dưới)
    5183  ho-bo
    5184  thai-boc-tu
    5185  kham-thien-giam
    5186  kham-thien-giam-runtime  ← KHÔNG phải cung; runtime Python thứ hai
    5187  thi-bac-ty
    5188  thi-bac-ty-runtime  ← KHÔNG phải cung; runtime Python thứ ba

Luôn truyền cổng, đừng để mặc định:

    node server.js 5175

Nhờ bảng cố định này mà hai phiên song song không bao giờ tranh cổng, kể
cả khi người dùng không nói gì về cổng.

Lưu ý `server.js` phục vụ từ **gốc repo**, không phải từ thư mục cung —
nên server nào cũng mở được cả bảy cung (`/cong-bo/`, `/kinh-thanh/`, …).
Cổng gắn với cung là để chia chỗ giữa các phiên, không phải vì mỗi cung
cần một server riêng. Đang sửa `cong-bo` mà muốn xem nó nối sang Cổng
Thành thì mở `localhost:5174/` là thấy, không cần bật thêm server.

Dải 5173–5199 dành riêng cho repo này.

### Không chạy trong phiên song song

    npm run dist     npm run deploy     npm run pin

Không phải vì tranh file — `dist/` đã gitignore và mỗi worktree có bản
riêng. Lý do là cả ba đều làm việc cho **toàn site**: đứng ở nhánh worktree
mà chạy thì bạn dựng ra một bản site có cung của bạn đã sửa còn các cung
khác là bản `origin/main` cũ, rồi `pin` đẩy luôn bản dở dang đó lên IPFS —
mà IPFS thì đã pin là không rút lại được.

Chỉ chạy sau khi đã gộp xong về `main`.

## Gộp về `main`

Gộp **không phải hàng đợi**. Hai cung là hai thư mục, hai nhánh chỉ đụng
thư mục của mình thì gộp cái nào trước cũng được, không tranh gì. Hàng đợi
chỉ xuất hiện khi hai nhánh cùng sửa file ở gốc repo.

Gộp **đứng nguyên trong worktree của mình**, đừng vào cây chính. Cây chính
là thứ dùng chung: hai phiên cùng chạy `git merge` ở đó thì tranh
`index.lock` và HEAD của cùng một cây, và file trong đó đổi dưới chân
người đang nhìn nó.

Trước khi gộp, chứng minh bằng lệnh chứ đừng tin cảm giác:

    git fetch -q
    BASE=$(git merge-base origin/main HEAD)

    # 1. nhánh đó có chạm ra ngoài thư mục cung của nó không?
    git diff --name-only $BASE..HEAD | grep -v '^<cung>/'

    # 2. hai bên có file nào cùng sửa không?
    comm -12 <(git diff --name-only $BASE..origin/main | sort) \
             <(git diff --name-only $BASE..HEAD        | sort)

    # 3. có phải fast-forward sạch không?
    git merge-base --is-ancestor origin/main HEAD && echo "ff sạch"

Cả ba lệnh không in ra gì (trừ lệnh 3) thì đẩy thẳng:

    git push origin HEAD:main

Lệnh này làm đúng một fast-forward trên remote — không checkout, không
merge, không chạm cây chính, nên **không có thao tác dùng chung nào để
tranh**. Hai phiên gộp cùng lúc thì phiên sau bị từ chối chứ không hỏng
gì: `git fetch -q`, chạy lại ba lệnh kiểm, đẩy lại.

**Không bao giờ `--force` lên `main`.** Lệnh cấm này chỉ nói về `main` —
nhánh worktree của chính bạn thì khác: rebase xong, lịch sử nhánh đã viết
lại nên push thường sẽ bị từ chối, và đẩy lại bằng

    git push origin HEAD:<tên cung> --force-with-lease

là bình thường, không phạm gì. Dùng `--force-with-lease` chứ đừng
`--force` trần: nếu có ai đó đã đẩy lên nhánh đó sau lần fetch cuối của
bạn, lease sẽ chặn thay vì ghi đè im lặng.

(Vì không đụng cây chính nữa, cũng không còn phải soát
`git status --short | grep '^??'` sau khi gộp — trước đây bước đó để chắc
mình không cuốn theo file chưa theo dõi của phiên khác đang nằm trong cây
chính. Đẩy từ worktree thì không có đường nào cuốn được.)

Push vào `main` là kích hoạt deploy thật. Đừng push khi cây chính đang có
một cung dựng dở mà cung đó **đã** được thêm vào `HALLS` của
`build-dist.mjs` — lúc đó bản dựng sẽ gãy hoặc đẩy lên site một cung thiếu
file. (Cung dở mà chưa nối vào đâu thì vô hại, `build-dist` không ngó tới.)

## Thêm cung mới

Một việc bắt buộc phải nhớ, và hai lệnh làm hộ phần còn lại.

**Cấp cổng và ghi vào bảng "Cổng dev" bên trên.** Lấy số kế tiếp trong
dải 5173–5199. Không ghi thì phiên sau đọc file này sẽ không biết dùng
cổng nào, đoán bừa, và tranh cổng với phiên đang chạy.

Rồi thêm một khối vào `scripts/cung.mjs` và chạy:

    npm run halls      sinh lại halls.js cho MỌI cung
    npm run nang       nâng CACHE_VERSION ở mọi sw.js vừa bị đổi

**`paths` không còn là việc phải nhớ nữa.** `deploy-pages.yml` đã đổi từ
danh sách CHO PHÉP sang danh sách LOẠI TRỪ (`paths-ignore`), nên cung mới
tự kích hoạt deploy vì không ai phải nhớ thêm nó vào đâu.

Đó từng là cái bẫy tệ nhất của repo này — quên một dòng thì push thành
công, không workflow nào chạy, site vẫn bản cũ, im lặng hoàn toàn (đã cắn
thật ở commit 311e885). Bẫy đó tệ dần theo số cung, nên với nhiều bộ
nhiều ban thì nó là lỗi chắc chắn xảy ra, chỉ chưa biết lúc nào. Đảo danh
sách lại là gỡ hẳn, không phải nhớ giỏi hơn.

`deploy-ipfs.yml` thì không còn chạy theo push nữa — xem mục dưới.

Nhánh worktree không kích hoạt deploy — đúng như thiết kế, deploy xảy ra
lúc gộp vào `main`.

### IPFS pin theo tag, không theo push

Gói Pinata **free là 1 GB**, còn bản site đo ngày 14/08 đã **21,8 MB /
462 file** và còn tăng theo số cung. Pin mỗi push là chắc chắn hết hạn
mức: workflow đó đã hỏng **liên tục 20 lượt** từ 13/08, bắt đầu đúng
commit thêm Đô Sát Viện (+236 file một lúc).

Ghi chú cũ trong workflow viết "mỗi bản site ~440 KB". Đúng hồi repo còn
hai cung, sai gấp 50 lần sau khi tách thư mục — và phép tính hạn mức dựa
trên số đó nên sai theo.

IPFS ở đây là **bản lưu bất biến**, không phải đường chạy chính. Đường
chạy chính là GitHub Pages, và Pages chưa hỏng lượt nào (27/27). Nên giờ
chỉ pin khi thật sự muốn đóng dấu một bản:

    git tag v2026.08.14
    git push origin v2026.08.14

hoặc bấm tay trong tab Actions. Đóng dấu **số liệu** thì vẫn chạy 4
lượt/ngày trong `refresh-data.yml` — bản đó 1,8 KB nên rẻ, và đó mới là
thứ đáng lưu vĩnh viễn.

Hệ quả cho mở rộng: thêm bao nhiêu cung nữa cũng không làm workflow này
chạy thêm lượt nào.

**Gói GitHub trả phí không giải quyết gì ở đây.** Repo công khai thì
Actions đã miễn phí không giới hạn phút; gói trả phí chỉ thêm phút cho
repo riêng tư. Thứ chạm trần là Pinata và Anthropic, không phải GitHub.

### Một cung coi là XONG khi

Thiếu bất kỳ dòng nào dưới đây thì **chưa được nối vào `HALLS` và chưa
được gộp về `main`** — nối sớm là dựng ra một site gãy.

Bảy chỗ phải sửa, không chỗ nào tự báo nếu quên:

    <cung>/index.html · sw.js · manifest.webmanifest
    <cung>/assets/css/app.css · halls.css
    <cung>/assets/js/app.js · halls.js · pwa.js
    <cung>/assets/icons/  (192, 512, maskable, apple-touch, favicon)

    1. index.html ở gốc            thẻ trong lưới .halls
    2. assets/js/portal.js         đọc ngày cập nhật (chỉ khi cung có dữ liệu tự sinh)
    3. scripts/cung.mjs            thêm một khối → `npm run halls` lo mọi halls.js
    4. sw.js ở gốc                 thêm dòng bỏ qua phạm vi cung mới
    5. scripts/build-dist.mjs      thêm vào mảng HALLS
    6. bảng "Cổng dev" trong file này        cấp số cổng kế tiếp
    7. `npm run nang`              nâng CACHE_VERSION mọi sw.js vừa đổi

Mục 3 sinh ra file nằm trong thư mục cung KHÁC — ngoại lệ duy nhất của
luật "chỉ sửa thư mục cung mình". Nhưng giờ là máy sinh chứ không sửa
tay, nên không còn chuyện sót một cung. Làm gọn trong một commit, và nói
rõ trong lời commit là đang nối cung mới.

`paths` của hai workflow deploy **không còn trong danh sách này** —
`deploy-pages.yml` dùng `paths-ignore` nên cung mới tự khớp, còn
`deploy-ipfs.yml` chỉ pin theo tag.

Kiểm nhanh trước khi bảo là xong:

    for f in index.html sw.js manifest.webmanifest \
             assets/css/app.css assets/js/app.js assets/js/halls.js assets/js/pwa.js; do
      [ -f "<cung>/$f" ] || echo "THIẾU $f"
    done
    grep -L "<cung>" index.html sw.js scripts/build-dist.mjs \
         .github/workflows/deploy-pages.yml .github/workflows/deploy-ipfs.yml

## Khi phát hiện lỗi trong chính file này

Tài liệu này lệch thực tế là chuyện thường: repo đổi mỗi ngày, còn nó thì
chỉ đổi khi có người nhớ ra. Phiên nào phát hiện thì phiên đó vá — đừng để
lại cho người sau, vì người sau sẽ tin theo bản sai.

### Vá ngay, không cần hỏi

Khi tài liệu **nói sai sự thật đang có** — sửa liền, đó là chữa lỗi:

- `npm run kiem` báo lệch bất kỳ dòng nào
- bảng cổng thiếu cung, hoặc hai cung cùng một số
- danh sách file bot tự sinh không khớp `git add` trong workflow
- đường dẫn, tên lệnh, tên file trong tài liệu đã đổi hoặc không còn
- một luật mô tả tình huống đã hết đúng

### Phải hỏi trước

Khi đụng vào **cách làm việc** chứ không phải sự thật:

- bỏ hoặc đổi mô hình worktree, đổi quy ước đặt tên nhánh
- đổi ai được push lên `main`
- nới một luật đang chặn (ví dụ cho phép `git add -A` trong trường hợp nào đó)
- thêm luật buộc mọi phiên khác đổi thói quen

Ranh giới: **sửa cho tài liệu khớp thực tế thì cứ làm; đổi thực tế thì hỏi.**

### Cách vá

1. `git fetch -q` rồi đọc bản mới nhất — phiên khác có thể vừa vá:

       git show origin/main:CLAUDE.md

2. Sửa **đúng mục sai**, đừng viết lại cả file. Viết lại là conflict chắc
   chắn với phiên đang sửa mục khác.

3. Mỗi lần vá là **một commit riêng chỉ chứa `CLAUDE.md`** (kèm
   `scripts/kiem-quy-trinh.mjs` nếu có sửa bộ kiểm). Đừng gói chung với
   việc của cung — người sau cần đọc lịch sử của luật mà không phải lội
   qua diff của app.

4. Chạy `npm run kiem` trước và sau khi vá.

5. Push thẳng lên `main`, đứng nguyên trong worktree:

       git push origin HEAD:main

   Đây là **ngoại lệ có chủ ý** của luật "không push `main`": tài liệu chỉ
   có tác dụng khi ở `main`, vì worktree mới luôn nhánh từ `origin/main`.

6. Push bị từ chối là phiên khác vừa vá xong trước bạn. Rebase lên
   **`origin/main`**, không phải lên nhánh của mình:

       git fetch -q
       git rebase origin/main

   (`git pull --rebase` ở đây là sai: upstream của nhánh worktree là
   `origin/<tên cung>`, nên nó rebase lên nhánh của chính bạn rồi báo
   thành công trong khi bạn vẫn đi sau `main`.)

   Rebase xong đọc lại `git diff HEAD origin/main -- CLAUDE.md` để chắc
   bản vá của phiên kia và của bạn không nói ngược nhau, rồi đẩy lại.
   **Không bao giờ `--force` lên `main`** — nhánh worktree của mình sau
   rebase thì `--force-with-lease` là bình thường, xem mục "Gộp về
   `main`".

### Mỗi luật thêm vào phải trả giá

Chỉ thêm luật khi có **một chuyện đã thật sự xảy ra hoặc suýt xảy ra**, và
viết kèm:

- tình huống cụ thể đã gặp
- **hậu quả nếu làm sai** — nhất là khi hậu quả im lặng, không báo lỗi
- một lệnh kiểm được, nếu có

Không thêm luật phòng xa. Tài liệu dài vì luật giả tưởng là tài liệu không
ai đọc hết, và không ai đọc hết thì luật thật cũng chìm theo.

### File dùng chung: chỗ `git add <thư mục>` không cứu được

Luật "chỉ add đúng thư mục cung" bảo vệ được file của cung, **không bảo vệ
được `CLAUDE.md`, `index.html`, `sw.js`, `scripts/`, `package.json`** — vì
chúng không thuộc cung nào. Hai phiên sửa cùng một file dùng chung trong
cây chính thì git không thấy gì để ngăn.

Trước khi commit một file dùng chung, đọc diff của nó:

    git diff CLAUDE.md

Thấy phần **không phải mình viết** thì:

- **Đừng `git checkout` để "dọn cho sạch".** Đó là xoá thẳng việc chưa
  commit của phiên khác, không khôi phục được.
- Đọc xem phần đó đúng không. Đúng và đã xong thì commit chung, và **nói rõ
  trong lời commit** là có mang theo sửa của phiên khác.
- Còn dở hoặc không chắc thì dừng, hỏi người dùng.

Chuyện này đã xảy ra ngay lúc viết mục này: hai phiên cùng sửa `CLAUDE.md`,
một phiên thêm ngoại lệ Hoàng Thành, một phiên thêm mục này — cả hai đều
đúng, và commit đầu tiên buộc phải mang cả hai.
