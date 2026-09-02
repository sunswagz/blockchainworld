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
    factory/chieu-mu.json
    factory/huong.json
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

Bảy cung dưới đây do **một** node đồng sửa — `tien-hoa-xoay`, mỗi ngày
một cung, bảy ngày giáp vòng (xem `scripts/vong-xoay.mjs`). Danh sách
đường sinh thẳng từ `VONG_XOAY` nên thêm cung vào vòng là bốn đường
này tự có; không phải chép tay ở hai chỗ:

    cong-bo/index.html
    cong-bo/assets/css/app.css
    cong-bo/assets/js/app.js
    cong-bo/sw.js
    do-sat-vien/index.html
    do-sat-vien/assets/css/app.css
    do-sat-vien/assets/js/app.js
    do-sat-vien/sw.js
    hoang-thanh/index.html
    hoang-thanh/assets/css/app.css
    hoang-thanh/assets/js/app.js
    hoang-thanh/sw.js
    kinh-thanh/index.html
    kinh-thanh/assets/css/app.css
    kinh-thanh/assets/js/app.js
    kinh-thanh/sw.js
    tang-thu-cac/index.html
    tang-thu-cac/assets/css/app.css
    tang-thu-cac/assets/js/app.js
    tang-thu-cac/sw.js
    thi-bac-ty/index.html
    thi-bac-ty/assets/css/app.css
    thi-bac-ty/assets/js/app.js
    thi-bac-ty/sw.js
    tu-cam-thanh/index.html
    tu-cam-thanh/assets/css/app.css
    tu-cam-thanh/assets/js/app.js
    tu-cam-thanh/sw.js

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

### Khâm Thiên Giám — đường tới chợ CHẬP CHỜN, và khung ăn thua CÓ giá

Không phải "bị chặn TLS vĩnh viễn". Trong 24 phút thông (14:54–15:18 UTC
29/08) runtime ghi được 578 dòng sổ lệnh KHUNG ĂN THUA. Cách nhận ra:
đếm `giai_doan_cua(tt) == "quan-sat"` trong băng — đừng tin cờ nguồn lỗi
hiện tại, nó chỉ nói lúc này.

Số MỚI NHẤT (1.018 dòng, **14 CỬA SỔ**, khoảng tin lấy lại theo CỬA SỔ):

    sổ dùng được   1.018/1.018 (100%) · thang chờ 0 · spread 1,00¢
    kỹ năng CHỢ      +3,8%  [−47,8%, +44,7%]   ← CHỨA 0
    kỹ năng MÔ HÌNH +49,6%  [+26,3%, +68,9%]   ← HẲN BÊN DƯƠNG
    w ước lượng      0,491  [−0,248, +0,907]

**Đây là kết quả dương duy nhất trong cả hệ đứng được về mặt thống kê:**
mô hình có kỹ năng thật trên dữ liệu khung ăn thua có thật, và khoảng tin
nằm hẳn bên dương. Kỹ năng của CHỢ thì chưa đo được — khoảng tin chứa 0.

Nhưng đọc cho đúng cỡ: `w` trải từ −0,25 tới +0,91. Bảng quét cho thấy
bot có lãi tới quãng w ≈ 0,9 và đứng ngoài từ 0,95 — nên cả điểm ước
lượng lẫn cận trên của `w` vẫn nằm trong vùng có lãi, chỉ là cận trên
nằm sát mép. Mười bốn cửa sổ không kết luận được nhiều hơn thế.

(Lần đo trước, trên 578 dòng, ghi *"kỹ năng chợ +16,8% · w 0,710"* mà
KHÔNG có khoảng tin — và đếm theo DÒNG chứ không theo cửa sổ. Đếm theo
dòng làm 14 quan sát trông như một nghìn.)

> Dòng này từng ghi thêm *"(phiên giấy hoà vốn quanh w ≈ 1)"*, và câu ấy
> SAI. Ở w = 0,95 và 1,00 phiên giấy có **0 lệnh khớp, 0 kết toán** — lãi
> lỗ $0,00 vì bot ĐỨNG NGOÀI, không phải vì nó hoà. Phép dò đổi dấu đọc
> số 0 ấy thành một điểm hoà vốn. Sự thật đo được: w = 0,7 cho quãng
> +30%, w = 0,9 cho quãng +1%, và từ w ≈ 0,95 trở lên cổng rủi ro chặn
> hết — **không có điểm hoà vốn nào trong dãy quét**. (Hai con số ấy đo
> trên nến Binance lấy mới mỗi lần chạy nên xê dịch vài phần trăm; đọc
> bậc, đừng đọc chữ số.) Nên câu "chợ thật nằm DƯỚI điểm hoà vốn" cũng
> không đứng được: chưa đo được điểm ấy ở đâu. Cái đo được là cổng
> rủi ro chặn TRƯỚC khi lợi thế thành âm — tin tốt, nhưng là một câu
> khác. Đã sửa `doc_quet()` và canh bằng bốn phép kiểm.

Lãi lỗ THẬT, chạy hết băng (133.829 khung, 8 ngày, 30/08/2026):

    17 cửa sổ thấy được · 6 kết toán · 18 lệnh khớp
    +$16,17 trên $1.000 (+1,62%)
    khoảng tin 95%  [-$140,52, +$163,17]   ← CHỨA 0
    phép nắn: 17 mẫu, KHÔNG bật ⇒ đây là mô hình THÔ, chưa nắn

(Con số này đã đổi ba lần trong một ngày: +$32,99 → +$23,59 → +$16,17.
Lần đầu vì phiên giấy đóng cứng `giaiDoan`; lần sau vì thêm cổng nhất
quán hai sổ. **Đừng đọc dãy ấy như một xu hướng** — với 6 cửa sổ và
khoảng tin ±150 đô, cả ba con số là cùng một con số. Cái đổi thật là
phiên giấy nay mô phỏng đúng cỗ máy đang chạy hơn trước.

Chi tiết lần đầu: +$32,99 / 7 cửa sổ. Nó được đo khi phiên giấy đóng
cứng `giaiDoan="dat-cuoc"`, một chuỗi không nằm trong bốn giai đoạn hợp
lệ — nên `tao-lap` và `can-ket-qua` im suốt phiên và phiên ấy mô phỏng
một cỗ máy KHÁC cỗ máy đang chạy. Xem mục PHÍ ở trên: cùng một bài học,
hai đường phải nói giống nhau về cùng một lệnh.)

**Khoảng tin chứa 0, nên con số +3,30% CHƯA nói được rằng cỗ máy này có
lãi.** Giá trị của phiên là chứng minh cả đường ống chạy trọn. KHÔNG đổi
cấu hình theo nó. `scripts/chay-phat-lai.py` nay tự in khoảng tin ấy —
lấy lại THEO CỬA SỔ — và tự nói thẳng khi nó chứa 0, để lần sau không ai
đọc con số giữa mà bỏ qua bề rộng.

(Lần đo trước ghi *"5 cửa sổ, +$33,94 trên $10.000"* kèm câu "năm cửa sổ
là vô nghĩa về thống kê". Câu ấy đúng nhưng là văn xuôi; nay nó thành
một khoảng tin do chính script in ra — [[luat-phai-chay-duoc]].)

`scripts/do-cho-that.py` và `scripts/chay-phat-lai.py` chạy lại được mỗi
khi băng dày thêm.

### Khâm Thiên Giám — PHẢI ĐÚNG TRƯỚC KHI MỞ BA CỔNG

Danh sách này chỉ gồm những điều **đã kiểm được bằng chứng**, không gồm
phỏng đoán. Ba cổng là `che:"that"` + `toiXacNhanDaDocRuiRo` +
`POLYMARKET_PRIVATE_KEY`; cả ba đang đóng.

Nhưng đo thật thì có **BỐN lớp**, không phải ba — và biết đủ bốn thì mới
biết mở cổng nghĩa là gì:

    1. `CongLenh.dat` đọc `che_hieu_luc()`; thiếu cổng ⇒ đi đường GIẤY
    2. `AdapterPolymarket` TỰ kiểm cổng lần nữa, ném `RuntimeError` kể
       tên từng cửa đang đóng — gọi thẳng adapter vẫn không lọt
    3. gói `polymarket-client` chưa cài ⇒ `RuntimeError` khác
    4. `NotImplementedError` trong chính `dat_lenh`

Mở hết ba cổng trong bộ nhớ (kể cả cắm khoá ví giả vào môi trường):
`che_hieu_luc()` thành `that`, không cửa nào còn đóng — và lệnh VẪN không
đặt được, chặn ở lớp 3. `kiem_lenh_that_khong_thoat_duoc` canh cả bốn.

**1. Vị thế KHÔNG sống qua khởi động lại — và đây là món nặng nhất.**
`Kho` và `KetToan.cho` chỉ nằm trong bộ nhớ. `VoDich`, `HieuChinh`,
`nan_lai`, `so_ket_qua` đều đọc đĩa; hai cái này thì không. Khởi động
lại giữa một khung là bot QUÊN mình đang cầm cổ phiếu — trong khi sàn
thì không quên. Hệ quả: hạn mức phơi nhiễm tính sai, và lần kết toán ấy
không bao giờ vào sổ, nên cả `nap_tu_so` cũng không thấy.

Lối chữa ĐÚNG là **đối soát với SÀN lúc khởi động**, không phải ghi thêm
một file vị thế cục bộ. Sàn là nguồn sự thật về việc mình đang cầm gì;
một file cục bộ chỉ tạo ra nguồn sự thật thứ hai để lệch nhau.

**Từ 30/08 mối nguy này không còn IM LẶNG.** Chưa nối được sàn thì không
cách nào BIẾT đang cầm gì — nhưng từ chối thì làm được ngay, và từ chối
là việc đúng: giả định ngầm rằng tài khoản đang trống sẽ sai đúng vào
lúc nó đắt nhất. `Kho.daDoiSoatVoiSan` mặc định `False` và cổng 0 của
`RiskEngine.duyet` chặn MỌI lệnh ở chế độ THẬT khi nó còn `False`, có
nêu tên lý do. Chế độ giấy không bị chặn — vị thế giấy là của riêng ta,
quên là hết.

`Kho.danh_dau_da_doi_soat(viThe)` là chỗ duy nhất bật cờ, và nó nạp
luôn thứ sàn nói là đang cầm. Truyền `None` nghĩa là sàn xác nhận tài
khoản TRỐNG — khác hẳn "chưa hỏi", và đó là cả lý do hàm này tồn tại.
Chưa ai gọi nó; adapter sàn sẽ gọi khi có. Nên việc còn lại KHÔNG phải
"nhớ đối soát" mà là "nối được sàn" — một việc rõ ràng thay cho một
điều phải nhớ.

**2. ĐÃ ĐỐI CHIẾU (30/08/2026) — và nó SAI, sai cả hai vế.**
`docs.polymarket.com` vào được (HTTP 200) trong khi `gamma-api` và
`clob` vẫn bị chặn ở tầng TLS. Công thức chính thức:

    fee = C × feeRate × p × (1 − p),   Crypto: feeRate = 0,07

Mã dùng `heSo × min(p, 1−p)` với `heSo = 0,02`. Hình dạng cũng đạt đỉnh
ở 50c và về 0 ở hai đầu nên nó TRÔNG đúng, nhưng thiếu 43–71% ở mọi mức
giá — luôn thiếu, không bao giờ thừa. Nghĩa là mọi `netEdge` từ trước
tới nay đều lạc quan đúng chừng ấy.

Đo cái giá trên phiên phát lại: phí tổng $3,68 → $7,26, lãi +5,33% →
**+4,94%**. Số cũ đẹp hơn sự thật đúng bằng khoản phí bị bỏ quên.

Bảng phí chính thức (Crypto, 100 cổ, 21 dòng) nay nằm trong bộ kiểm,
khớp tới từng xu — chỉ kiểm hình dạng thì công thức sai cũ cũng qua.
Maker = 0 (tài liệu nói thẳng), phí làm tròn 5 chữ số, dưới 0,00001
USDC thì về 0.

CÒN LẠI: hạng mục của TỪNG market nằm trong `Market Details` của API —
thứ đang bị chặn. Năm market đang theo đều là crypto nên 0,07 đúng cho
chúng; thêm market ngoài crypto thì phải đọc lại hệ số (Sports 0,05 ·
Finance 0,04 · Politics 0,04 · Geopolitics 0).

**3. Chân lệch không có LỐI THOÁT tự động — nhưng CỠ thì có trần, và
đã chứng minh.** `quyet_chan` chỉ là LỜI KHUYÊN; không ai huỷ lệnh, vượt
spread hay đóng chân theo nó. Ca "không ai bán bên thiếu" vẫn bỏ ngỏ.

Hai chuyện ấy hay bị nói lẫn vào nhau, và phân biệt được thì mới quyết
được: bỏ ngỏ LỐI THOÁT thì đúng, bỏ ngỏ CỠ thì không. Cỡ bị chặn ở
`khoDoi.phanTramChuaPhongHo` = 5% vốn đầu ngày, và từ 30/08 còn bị chặn
lần nữa bởi cổng 6b (ngân sách lỗ ngày còn lại). `kiem_tran_chan_tran_
khong_vuot` lùa 400 lệnh ngẫu nhiên qua đúng cửa duyệt thật, khớp TRỌN
mọi thứ được duyệt, và đòi trần không bao giờ bị vượt — đo bất biến ở
đầu ra chứ không tin một cổng đơn lẻ.

Nên rủi ro còn lại là: mất tối đa 5% vốn trong tối đa một khung, khi
không ai bán bên thiếu. Một rủi ro CÓ CHẶN và một rủi ro không chặn là
hai thứ khác hẳn nhau khi quyết có mở cổng hay không.

**4. ĐÃ SỬA (30/08/2026) — hai động cơ nay đứng trên CÙNG một độ đo.**
`cham_moc` từng bỏ số hạng `−σ²τ/2` với lý lẽ "không giả định xu hướng".
Lý lẽ ấy đúng cho một xu hướng thật, sai cho số hạng này: nó là hiệu
chỉnh bắt buộc để chính GIÁ là martingale, nên bỏ nó đi chính là khai
rằng giá tăng với tốc độ σ²/2. Đo được: bỏ trôi làm P(chạm) cao hơn
~40% tương đối ở chân trời 124 ngày — tức định giá vế YES hào phóng hơn
thực. Nay dùng dạng đóng đầy đủ của xác suất chạm lần đầu. Mất đẳng
thức phản xạ (`P = 2Φ(−z)` chỉ đúng khi không trôi), đổi lại thoả hai
giới hạn mà bản cũ không thoả: τ → ∞ cho `S/K` ở rào trên và `1` ở rào
dưới. Cả hai đều có phép kiểm.

**5. ĐÃ SỬA (30/08/2026) — phạt tồn kho của `tao-lap` nay khác 0.** Công
thức cũ `q·λ·σ²·(T−t)` sai thứ nguyên: `sigmaGiay` là σ của log-return
mỗi giây (~3,7e-5) nên σ²τ ra cỡ 4e-7 — một phương sai log, không phải
khoảng giá — trong khi giá yết nằm trong [0,1]. Phạt lớn nhất nhỏ hơn
trần kẹp mười nghìn lần, nên `tao-lap` yết ĐỐI XỨNG. Thứ A–S cần là
phương sai của GIÁ tới lúc kết toán, và ở chợ nhị phân nó tính chính
xác được: `p(1−p)`. τ biến mất vì p(1−p) đã mang thời gian trong nó, và
phạt tự về 0 khi p về hai đầu. γ = 0,0004 chốt để 100 cổ ở p = 0,50
chịu phạt đúng 1 cent. LƯU Ý: cái giá của thay đổi này KHÔNG đo được
bằng tiền — phiên phát lại bỏ mọi lệnh maker vì chưa mô phỏng hàng chờ,
nên A/B ra giống hệt tới từng xu. Nó đứng trên suy dẫn và phép kiểm.

**6. Sự thật nền chưa bao giờ được sàn xác nhận.** Sổ kết quả có 11.436
khung, **100% nguồn `tu-tinh`** — tự tính bằng cách so giá Binance ở hai
mốc. Không một dòng nào do sàn xác nhận. Toàn bộ điểm Brier, điểm kỹ
năng, và cả vòng tiến hoá đứng trên sự thật do chính mình tính ra.

Với market lên/xuống thì phép tính ấy đơn giản và gần như chắc đúng.
Nhưng `can_ket_qua` liệt kê "sai nguồn giá resolution" là một rủi ro vận
hành mà không mô hình nào bắt được, và cách duy nhất biết là ĐỐI CHIẾU.
Đường tới chợ thông trở lại thì việc đầu tiên là lấy kết quả `san` cho
vài chục khung và so với `tu-tinh`.

**7. Chưa có bằng chứng cỗ máy này có lãi.** Phiên giấy trên băng thật:
6 cửa sổ, +$23,59, **khoảng tin 95% [−$132,46, +$169,04] — chứa 0**. Con
số dương ấy chưa nói được gì. Cần nhiều cửa sổ hơn, và cửa sổ chỉ dày
thêm khi đường tới Polymarket thông.

Hai món đã sửa trong ngày 30/08/2026 và nay có phép canh giữ — ghi lại
để đừng kiểm lại: **phí đã được trừ** khỏi lãi lỗ ở cả hai đường, và
**trạng thái rủi ro dựng lại từ sổ** lúc khởi động.

### Khâm Thiên Giám — RỦI RO từng quên sạch mỗi lần khởi động lại

Buồng lái khai `von 1.000` và `sutVonPct 0,0%` trong khi sổ kết toán ghi
một lệnh LỖ $49,95. `RiskEngine.__init__` đặt `von = vonBanDau` từ config
và không đọc gì cả.

Ba cầu dao dựa trên đúng những con số ấy — trần lỗ NGÀY, trần sụt vốn từ
ĐỈNH, và cỡ lệnh Kelly theo vốn. Nên một bot vừa chạm trần lỗ ngày, bị
khởi động lại (sập, cập nhật, hay người bấm), có NGAY một ngân sách lỗ
mới nguyên. Riêng ngày sửa lỗi này runtime được khởi động lại sáu lần.

Sau khi sửa, đọc thật từ máy đang chạy:

    von 950,05 · đỉnh 1.000 · sụt 4,99% · lỗ ngày 49,95 / trần 50,00

Tức bot đã dùng gần hết ngân sách lỗ của ngày — và chính con số ấy trước
đây bị xoá mỗi lần khởi động.

`RiskEngine.nap_tu_so()` dựng lại từ SỔ, không thêm file trạng thái mới:
sổ kết toán đã là nguồn sự thật, và **hai nguồn sự thật thì sớm muộn lệch
nhau**. Bốn chỗ cố ý, mỗi chỗ một cái bẫy đã tránh:

    · ĐỈNH vốn dựng theo cả đường vốn, không lấy giá trị cuối
    · ngày lấy từ mốc GHI TRONG SỔ, không lấy đồng hồ máy — lấy đồng hồ
      thì đọc lại sổ cũ là mọi dòng thành "hôm nay", cầu dao ngắt oan
    · nạp xong SOÁT NGAY, không đợi lệnh kế tiếp (có thể không có)
    · nạp hỏng thì KÊU — chạy tiếp im lặng chính là cái lỗi đang sửa

Bài học chung với mục PHÍ ngay dưới: **trạng thái sống trong bộ nhớ mà
sự thật nằm trên đĩa thì phải hỏi đĩa lúc khởi động.** Không hỏi thì cỗ
máy không sai một phép tính nào — nó chỉ bắt đầu lại từ một quá khứ khác.

### Khâm Thiên Giám — PHÍ từng biến mất khỏi lãi lỗ (30/08/2026)

`dat_lenh` tính phí đúng và in ra nhật ký — `phí $0.0900` — rồi thả nó
xuống đất. `ghi_khop()` không nhận phí, `tienUp/tienDown` chỉ là tiền
HÀNG, `ket_toan._ghi_so` ghi thẳng `phiUsd=0.0`. Không ai trừ nó.

Ba hệ quả, tất cả cùng một chiều — ĐẸP HƠN SỰ THẬT:

    · sổ kết toán khai tổng phí = $0 vĩnh viễn
    · lãi lỗ mỗi cửa sổ cao hơn thật đúng bằng khoản phí ($2,93 trên
      $32,99 lãi trong phiên giấy chạy hết băng — 9%)
    · `risk.ghi_lai_lo` nhận con số đẹp ấy ⇒ cầu dao lỗ ngày ngắt MUỘN
      hơn mức đã thiết kế

Chỗ làm lộ ra: `phat_lai.py` (mô phỏng) TRỪ phí đúng, đường chạy thật
thì không — nên **máy thật báo đẹp hơn chính bản mô phỏng của nó** trên
cùng những lệnh ấy. Khi hai đường nói khác nhau về cùng một lệnh, đừng
cho là chuyện lặt vặt: một trong hai đang sai.

Nay `ViThe.phiUsd` cộng dồn theo từng lần khớp và `lai_lo_khi_ket_qua()`
trừ nó. **Bất biến buộc hai đường về một định nghĩa**, canh trong
selftest trên mọi dòng sổ đã ghi:

    laiLo = tienRa − tienVao − phiUsd

Bài học rộng hơn: một khoản chi được TÍNH và được IN RA thì rất dễ bị
tưởng là đã được TRỪ. Nhật ký có chữ "phí $0.09" nằm ngay đó suốt, và
chính nó làm người đọc yên tâm. Muốn biết một khoản có vào sổ không thì
phải lần theo nó tới tận phép trừ, đừng dừng ở chỗ nó được in.

### Khâm Thiên Giám — MÔ HÌNH ĐÃ Ở SÁT TRẦN, thôi vặn

Đo được (`scripts/do-tran-mo-hinh.py`, 20 ngày BTC, 9.220 cặp ngoài mẫu):

    SÀN   đoán bừa tỉ lệ nền (49,2%)      0.24994
    NAY   mô hình + nắn, ngoài mẫu        0.15743
    TRẦN  đơn điệu, khớp TRONG mẫu        0.15642   ← thiên vị THẤP
    TRẦN  đơn điệu, khớp CHÉO 4 phần      0.15760   ← đọc cái này

    NAY đã NGANG/VƯỢT trần khớp chéo — không còn chỗ cho phép nắn nào

Mọi phép nắn đều là biến đổi đơn điệu của `p`, nên không phép nắn nào
vượt được cái trần ấy. **Vặn thêm tham số mô hình là phí công.** Muốn
khá hơn phải thêm THÔNG TIN MỚI vào `p`: sổ lệnh, dòng lệnh, độ trễ
liên sàn.

> Dòng này từng ghi *"đã vắt 98,9%, còn lại 1,1%"*, đọc từ cái trần khớp
> NGAY TRÊN tập chấm. Trần khớp trong mẫu bị kéo xuống thấp hơn sự thật,
> nên nó làm khoảng cách NAY→TRẦN trông HẸP hơn — tức là thiên vị về
> phía kết luận *"thôi vặn"*, đúng cái kết luận đang rút ra từ nó. Khớp
> chéo bốn phần thì đường nắn không bao giờ thấy điểm nó đang chấm; và
> lần này nó làm kết luận MẠNH thêm chứ không mềm đi: 1,1% kia không có
> thật. Chênh 0.00118 giữa hai trần là phần khớp quá của chính phép đo
> trần. Nhắc lại luật chung: **cái thước tự khớp trên tập nó chấm thì
> phải khai ra nó thiên vị chiều nào.**

**Cái TRẦN đã đóng sẵn nửa danh sách ý tưởng — đọc kỹ chỗ này trước khi
nghĩ hướng mới.** Trần đo bằng phép biến đổi ĐƠN ĐIỆU tốt nhất của `p`.
Nên bất cứ ý tưởng nào chỉ đổi cách biến `z` thành xác suất đều nằm DƯỚI
trần ấy theo định nghĩa, và không cần đo:

    thay Φ bằng Student-t (đuôi dày)     ĐƠN ĐIỆU trong p ⇒ vô ích
    hiệu chỉnh lại, nắn kiểu khác        ĐƠN ĐIỆU ⇒ vô ích
    kẹp, làm trơn, đổi thang xác suất    ĐƠN ĐIỆU ⇒ vô ích

Crypto có đuôi dày thật, và Student-t nghe rất hợp lý — nhưng nếu `z`
không đổi thì `t_ν(Φ⁻¹(p))` chỉ là một hàm tăng của `p`, và trần đã nói
không hàm tăng nào giúp được. Muốn dùng đuôi dày thì phải đổi **chính
`z`**, tức đổi một trong `S, K, τ, σ`.

Vậy hướng còn cửa chỉ có một loại: **thứ gì làm `z` khác đi.** Danh sách
dưới đây toàn là loại ấy, và tới nay đều đóng.

Ba phép thử đã đóng lại ba hướng, mỗi hướng một con số:

    cửa sổ σ 300s → 900s                   −1,9%   ĐÃ NHẬN, đưa gần hết đường
    bộ ước σ: parkinson thay close-close    trả lại — khoảng tin chứa 0
    nắn RIÊNG theo τ thay vì gộp            −0,08%  trả lại
    dòng lệnh nhịp 1 phút (taker buy)       KHÔNG đủ bằng chứng
    BTC dẫn ETH · XRP                       KHÔNG đủ bằng chứng
    BTC dẫn SOL                             TỆ HƠN, khoảng tin hẳn bên âm
    cửa sổ σ riêng từng market              cả ba đều chọn 900s
    nới MÉP cửa sổ σ 900 → 3600             đường cong PHẲNG sau ~960s
    mùa vụ theo GIỜ trong ngày              trả lại — khoảng tin chứa 0
    KHỐI LƯỢNG báo σ                        trả lại — suy giảm ĐƠN ĐIỆU
    σ CHỐNG NHẢY GIÁ (bipower, medRV)       TỆ HƠN, khoảng tin hẳn bên dương
    TRỌNG SỐ phần nhảy — quét cả trục λ     đương nhiệm Ở ĐÁY, trục đã hết
    (`ewma` thì TỆ HƠN close-close rõ rệt)

Hướng thứ bảy (`scripts/thu-mua-vu-gio.py`, 30/08/2026) đáng ghi riêng vì
nó là hướng duy nhất thêm THÔNG TIN NGOÀI 900 giây nến vừa qua — giờ
trong ngày không nằm trong cửa sổ ấy. Nhân σ với một hệ số học riêng cho
từng khối 6 giờ (và 3 giờ) UTC:

    trơn        Brier CHỌN 0.15591   CHỐT 0.15809
    mùa vụ ×4              0.15603        0.15822
    mùa vụ ×8              0.15599        0.15802
    khoảng tin 95% chênh CHỐT (1.440 KHUNG): [−0,000293, +0,000144]

Cả hai biến thể TỆ HƠN ở tập CHỌN, và chia mịn hơn không cứu được. Phần
đáng đọc nhất là chính các hệ số học ra: **0,87–1,06**. Bộ ước 900 giây
đã gần như không thiên vị theo giờ — nên không có mùa vụ nào để ăn, chứ
không phải có mà đo không ra.

Hướng thứ tám (`scripts/thu-khoi-luong.py`) hỏi thứ nằm sẵn trong mọi
lời gọi kline mà chưa ai đọc: **cột khối lượng**. σ nhân
`(V/V_thường)^β`, β dò trên lưới năm điểm có cả β = 0 làm đối chứng:

    β     Brier CHỌN   Brier CHỐT
    0,00     0.15591      0.15809   ← đương nhiệm
    0,10     0.15624      0.15822
    0,20     0.15697      0.15855
    0,30     0.15762      0.15894
    0,50     0.15831      0.15954

**Suy giảm ĐƠN ĐIỆU trên cả hai tập chấm.** Đây là kết luận mạnh hơn
"chưa đủ bằng chứng": nếu khối lượng có tin, phải có một β > 0 thắng
được β = 0. Không có. Lý do gần như chắc chắn là σ đo trên ĐÚNG cửa sổ
ấy đã nuốt hết phần khối lượng nói được — biến động thực hiện và khối
lượng đo cùng lúc thì tương quan rất cao, nên nhân thêm chỉ là cộng
nhiễu vào một con số đã đủ.

(Đừng nhầm với hướng "dòng lệnh taker buy" đã đóng: cái đó đo HƯỚNG,
cái này đo ĐỘ LỚN. Hai câu hỏi khác nhau, và cả hai đều trả lời không.)

Hướng thứ chín (`scripts/thu-nhay-gia.py`) là hướng đầu tiên trả về một
kết luận CÓ CHIỀU chứ không phải một con số không. Biến động thực hiện =
phần khuếch tán + phần NHẢY. Mô hình `Φ(z)` giả định khuếch tán liên
tục, nên nghe rất hợp lý rằng phần nhảy là tạp chất thổi σ lên:

    dong-dong  ← đương nhiệm   CHỌN 0.15607   CHỐT 0.15787
    pha-nua  (½RV + ½BV)            0.15618        0.15822
    bipower  (bỏ nhảy)              0.15646        0.15902
    med-rv   (bỏ nhảy mạnh nhất)    0.15679        0.15856
    khoảng tin 95% chênh CHỐT (1.440 KHUNG): [+0,000006, +0,000704]

**Càng bỏ nhảy giá càng TỆ, và khoảng tin nằm hẳn bên dương** — tức ứng
viên tốt nhất kém hơn một cách có ý nghĩa. Thứ tự `pha-nua` < `bipower`
< `med-rv` là thứ tự mức độ bỏ nhảy.

Đọc ra một điều về THẾ GIỚI, không phải về phép đo: với khung 5 phút,
phần nhảy trong σ **không phải tạp chất — nó là dự báo thật cho 5 phút
tới**. Biến động cụm lại; một cú nhảy vừa xảy ra là dấu hiệu mạnh rằng
năm phút tới còn động. Bỏ nó ra là vứt tin đi.

Hướng thứ mười (`scripts/thu-trong-so-nhay.py`) là hướng thứ chín viết
lại cho ĐÚNG CÁCH, và nó nói được nhiều hơn hẳn. Thay vì so vài bộ ước
rời rạc, đặt cả câu hỏi lên MỘT trục liên tục:

    σ² = RV + λ·(RV − BV)

λ = −1 là bipower (bỏ sạch nhảy), λ = 0 là đương nhiệm, λ > 0 khuếch đại
phần nhảy. Quét bảy điểm:

    λ        Brier CHỌN   Brier CHỐT
    −1,00       0.15649      0.15889
    −0,50       0.15614      0.15815
    −0,25       0.15606      0.15791
    +0,00       0.15605      0.15775   ← đương nhiệm
    +0,25       0.15605      0.15766
    +0,50       0.15607      0.15755
    +1,00       0.15622      0.15756
    khoảng tin 95% chênh CHỐT (1.440 KHUNG): [−0,000233, +0,000040]

**Đường cong hình chữ U với đáy ngay tại đương nhiệm.** Đây là kết luận
mạnh hơn "không tìm thấy cải thiện": trục đã được VẼ BẢN ĐỒ, và λ = 0
nằm đúng đáy. Không còn chỗ nào trên trục ấy để đi.

Hai chuyện phụ đáng giữ. Thứ nhất, λ = −1 tái lập gần khít kết quả
hướng thứ chín — một phép tự kiểm chéo giữa hai phép đo viết độc lập.
Thứ hai, phía CHỐT có đáy hơi lệch dương (λ +0,5), khớp chiều với kết
luận "nhảy là tin thật" của hướng chín, nhưng khoảng tin chứa 0 nên
không đủ để vặn.

**Bài học về cách THỬ, không phải về mô hình:** hướng thứ chín lẽ ra
nên viết theo trục ngay từ đầu. So vài ứng viên rời rạc chỉ cho biết ai
thắng ai; quét một trục cho biết CHIỀU, chỗ tối ưu, và cả độ dốc quanh
nó — tức là biết luôn còn đáng đi tiếp hay không. Cùng số lần chạy.

Chú ý khi đọc lại: các phép thử này lấy nến MỚI mỗi lần chạy nên cửa sổ
20 ngày trượt, và Brier của cùng một đương nhiệm xê dịch chừng 0,0002
giữa hai lần. So sánh trong CÙNG một bảng thì có nghĩa; so chéo giữa hai
bảng chạy khác ngày thì không.

Một hướng nữa đáng ghi vì nó là chuyện về CÁCH ĐI TÌM, không phải về mô
hình. `tien-hoa-mo-hinh` tự dò ngoài dải rồi khai: *"quán quân nằm ở MÉP
dải cho phép ([60, 900]) — trần đang quyết định, không phải dữ liệu"*, và
ước tính tối ưu thật quanh 2.700–3.600s, khá hơn chừng 0,05%.

Mép trên của nút BẰNG ĐÚNG giá trị đang dùng. Một cái nút như thế thì
không bao giờ tăng được — nên nới mép ra là việc phải làm, bất kể kết
quả. **Nới MÉP chứ không đặt GIÁ TRỊ**: quyền quyết vẫn ở cổng tiến hoá.

Nới rồi thì câu trả lời ngược với dự đoán:

     960s  Brier đuôi 0.16164     2160s  0.16164
    1260s        0.16163          2760s  0.16169
    1560s        0.16161  ← đáy   3360s  0.16166

**Đường cong PHẲNG sau ~960 giây.** Đáy ở 1560s chỉ hơn 960s đúng
0,00003 — cổng từ chối, đúng như phải thế. Con số "0,05%" trước đó là
một phép ngoại suy TRONG dải, và nó không sống nổi khi đo thật ngoài dải.

Đo độc lập bằng `thu-uoc-sigma` trên 20 ngày thì mọi khoảng tin 95% của
chênh Brier CHỐT đều CHỨA 0 (±0,001 quanh một hiệu 0,0008). Hai phép đo
không khớp nhau về độ dốc, và cả hai đều không đủ để vặn.

Bài học: **một quán quân nằm ở mép dải là một câu hỏi, không phải một
kết quả.** Phải nới mép rồi đo lại — có thể ra vàng, cũng có thể ra một
mặt phẳng như lần này. Cái không được làm là đọc con số ở mép rồi tin nó.

**Vì sao `nanLai.heSoGiamChan` cứ suýt thắng mãi — và vì sao đừng tin
chuỗi suýt thắng ấy.** Nút này là quán quân ở nhiều lượt `tu-nang-cap`
độc lập (0,7 → 0,35, rồi 0,7 → 0,3), lần nào cũng thiếu một chút so với
biên. Thấy vậy rất dễ nghĩ "nó gần đúng rồi, nới biên đi".

Quét cả trục thì hết nghĩ:

    hệ số   Brier CHỌN   Brier CHỐT
     0,30     0.15578      0.15861
     0,50     0.15586      0.15857
     0,70     0.15601      0.15861   ← đương nhiệm
     0,85     0.15618      0.15868
     1,00     0.15638      0.15879
    mọi khoảng tin 95% của chênh CHỐT đều CHỨA 0

**CHỌN cải thiện ĐƠN ĐIỆU, CHỐT PHẲNG LÌ.** Đó là dấu vân tay của khớp
quá trên tập xếp hạng, và là lý do tập CHỐT tồn tại. Chuỗi "suýt thắng"
không phải bằng chứng tích luỹ — nó là cùng một tiếng ồn nhìn từ nhiều
lượt, vì nút này nhạy với nhiễu tập CHỌN hơn mọi nút khác.

Đồng thời chuyện này giải luôn mâu thuẫn giữa hai công cụ:
`kiem-nan-ngoai-mau` khuyên TĂNG hệ số (bỏ bớt giảm chấn) còn
`tu-nang-cap` cứ nhắm GIẢM. Cả hai đều cư xử đúng — cái đầu chấm sai số
hiệu chỉnh, cái sau chấm Brier, và trên Brier thì cả trục là mặt phẳng.

`tu-nang-cap` nay in tập CHỐT ra ngay cả khi ứng viên đã bị loại ở CHỌN,
để lần sau không ai phải đi quét trục mới biết chuyện này.

**Dữ liệu giá Binance đã cạn.** Sáu hướng, sáu kết quả, cùng một kết
luận. Alpha còn lại — nếu có — nằm ở vi cấu trúc của chính cái chợ: sổ
lệnh, hàng chờ, độ trễ tới sàn. Tất cả sau đúng một cánh cửa đang đóng.

Những kết quả ÂM ở trên đáng giữ đúng bằng kết quả dương: chúng ngăn một
phiên sau làm lại toàn bộ chuỗi thí nghiệm này.

⚠ Hai dòng đầu TỪNG được ghi là "TỆ HƠN, khoảng tin hẳn bên âm". Sai:
khoảng tin ấy dựng bằng bootstrap theo CẶP, trong khi bốn lát cắt của
một khung chia chung một kết quả. Lấy lại theo KHUNG thì khoảng tin rộng
ra và chứa 0 — "không đủ bằng chứng", không phải "tệ hơn". Kết luận của
SOL sống sót qua phép sửa; hai cái kia thì không.

Công cụ, tất cả chỉ cần Binance — không cần chợ, không cần giả định:

    scripts/hoc-tu-binance.py     dựng sổ hiệu chỉnh (7 ngày, BỐN chợ ≈ 160.000 mẫu)
    scripts/thu-sigma-bien-do.py  σ pha biên độ so với σ giá đóng, hai quãng
    scripts/thu-nan-them-coin.py  thêm coin vào phần khớp có giúp không
    scripts/thu-dong-lenh-giay.py dòng lệnh nhịp GIÂY có thêm tin không
    scripts/tien-hoa-mo-hinh.py   vặn MỘT nút, chấm bằng Brier ngoài mẫu
    scripts/tu-nang-cap.py        lặp tới khi hết cải thiện, tự dừng
    scripts/do-tran-mo-hinh.py    còn bao nhiêu chỗ để cải thiện
    scripts/thu-uoc-sigma.py      so bốn bộ ước σ
    scripts/thu-nan-theo-tau.py   nắn gộp hay nắn riêng theo τ
    scripts/thu-dong-lenh.py      dòng lệnh có thêm thông tin không
    scripts/thu-btc-dan.py        BTC có dẫn các đồng khác không
    scripts/chay-demo.py          demo trọn vẹn, tiền ảo, có `--quet`

**Và luật thứ hai: BOOTSTRAP THEO KHUNG, không theo cặp.** Bốn lát cắt
(τ = 240/180/120/60) của một khung chia chung MỘT kết quả. Lấy lại theo
cặp cho khoảng tin hẹp hơn 2,18 lần, và nó ĐÃ làm sai một kết luận đã
ghi vào tài liệu. Mọi phép thử ở đây gọi
`kham/hoc_offline.khoang_tin_theo_khoi()`.

**Luật thứ ba: BIÊN TÍNH TRÊN ĐỘ LỚN, đừng nhân thẳng vào một số CÓ
DẤU.** `B < A * 1,1` đọc như "ứng viên phải hơn đương nhiệm 10%", và nó
đúng — chừng nào A dương. Khi A âm nó LẬT: A = −10 ⇒ ngưỡng −11 ⇒ ứng
viên −10,5 (TỆ HƠN) lọt qua. Biên "phải hơn 10%" thành "được phép kém
tới 10%", và nó lật đúng vào lúc cần cổng nhất — khi cỗ máy đang lỗ.

Viết `A + |A|·(bien − 1)`, và dùng `<=` để mép cũng đóng. Đã cắn ở HAI
chỗ cùng khuôn (`tien_hoa.thu_mot_de_xuat`, `vo_dich` cửa 3), cả hai đều
nằm im vì kỳ vọng hiện tại đang dương — chúng chờ đúng ngày xấu.

Nhân thẳng CHỈ đúng khi đại lượng có dấu cố định và ta muốn nới theo
chiều ấy: `duoi5pct` (phân vị 5%, gần như luôn âm) nhân 1,15 chính là
"cho phép đuôi xấu thêm 15%". Kiểm dấu trước, đừng chép công thức.

**Luật của mọi phép thử ở đây: BA TẬP tách theo THỜI GIAN.** HỌC khớp
nắn · CHỌN xếp hạng ứng viên · CHỐT chỉ GẬT hay LẮC, không bao giờ dùng
để xếp hạng. Lặp N vòng trên một tập kiểm thì tập ấy thôi còn là ngoài
mẫu, và chuyện đó không lộ ra ở đâu — mọi con số vẫn đẹp dần. Đã cứu một
bàn thua thật: một ứng viên qua cả CHỌN lẫn CHỐT ở lượt đầu, chạy lại
vài phút sau với dữ liệu mới hơn thì CHỐT lắc.

### Khâm Thiên Giám — CỬA NÀO là cửa làm việc (đọc trước khi sửa)

Slug `<coin>-updown-5m-T` có HAI cửa và chúng không thay nhau được:

    [T−300, T]   cửa ĐẶT CƯỢC   strike CHƯA TỒN TẠI
    [T,   T+300] khung ĂN THUA  strike = giá lúc T, đã biết

Kết quả là `giá(T+300) > giá(T)` — đo bằng cách chấm điểm chính chợ trên
ba giả thuyết, mẫu ngẫu nhiên trải cả băng, đối chứng bằng TỈ LỆ NỀN
(`scripts/do-strike.py`, 489 slug): điểm kỹ năng +6,6% cho định nghĩa
này, −38,7% cho "giá(T+300) > giá(T−300)" mà runtime từng dùng.

Hệ quả không phải một tham số sai. Trong cửa đặt cược, số gia từ T tới
T+300 độc lập với mọi thứ quan sát được ⇒ **giá trị thật đúng 0,5**, bất
kể giá đang ở đâu. Công thức `z = [ln(S/K) − σ²τ/2]/(σ√τ)` chỉ có nghĩa
khi K đã biết. Đo thẳng, cùng mô hình, cùng τ=60s, cùng tỉ lệ nền
(`scripts/do-cua-nao.py`):

    đứng ở cửa đặt cược,      K = giá(T−300)   kỹ năng  −74,3%
    đứng trong khung ăn thua, K = giá(T)       kỹ năng  +43,5%

Suốt tám ngày đầu bot làm việc ở cửa đầu và tắt máy đúng lúc cửa sau bắt
đầu. **Mọi con số hậu kiểm trước 29/08/2026 là ảo** — sổ kết quả, bảng
hiệu chỉnh, đường nắn và phép kiểm ngoài mẫu của nó, kỳ vọng cổng tiến
hoá. Sổ cũ cất ở `data/*-dinh-nghia-A.*`, không xoá. Dựng lại sổ kết quả
thì 25,7% kết quả lật ngược.

**Băng nay có HAI loại dòng và KHÔNG cùng nghĩa.** Mọi chỗ tiêu thụ băng
phải lọc qua `bang.giai_doan_cua(tt)`; thiếu trường thì đọc là
`"dat-cuoc"`. Trộn hai loại là dựng một con số không nói về thứ gì.

**Hai bẫy đo lường đã cắn trong chính việc chốt chuyện này:**

1. **Điểm Brier THÔ đo lẫn tỉ lệ nền với kỹ năng.** Bản đầu lấy 300 slug
   đầu bảng chữ cái — một khối thời gian liền — và ra "đúng hướng 69,3%"
   trong khi đó chỉ là tỉ lệ nền của một quãng chợ đi xuống. Luôn lấy
   mẫu ngẫu nhiên trải cả băng và chấm bằng ĐIỂM KỸ NĂNG.
2. **Mô hình sai + đáp án đúng trông thuyết phục hơn cả hai đều sai.**
   Sau khi dựng lại sổ kết quả mà vẫn định giá bằng strike cũ, phiên
   phát lại ra +191% với tỉ lệ thắng 26%. `kham/phat_lai.py` nay TỪ CHỐI
   dòng cửa đặt cược và trả về 0 kèm lý do — thà không có số.

### MỌI BUỒNG LÁI LOCALHOST — kiểm chỗ này, nó là lỗ hổng thật

Tìm ra ở Khâm Thiên Giám 30/08/2026, và **các cung khác nhiều khả năng
cũng có** — Thị Bạc Ty (5188), Thái Bộc Tự (5184), Hộ Bộ (5183), Tử Cấm
Thành (5182) đều có buồng lái localhost kèm nút điều khiển.

Buồng lái nghe ở `127.0.0.1` và không lên site. Nghe thì kín. Nhưng nếu
các lối POST không thân, không xác thực thì **bất kỳ trang web nào người
vận hành mở trong cùng trình duyệt đều gọi được**:

    fetch("http://localhost:5186/api/tam-dung",
          {method: "POST", mode: "no-cors"})

Đây là "simple request" nên trình duyệt KHÔNG hỏi preflight. Trang kia
không đọc được phản hồi, nhưng **tác dụng phụ đã xảy ra**: bot dừng, cầu
dao lật, chiến thuật tắt, lệnh bị huỷ, một lượt chạy lại tốn kém chạy.

Nghe ở 127.0.0.1 KHÔNG cứu được — chính trình duyệt trên máy ấy là kẻ
gửi. Thử thật trước khi vá: `Origin: http://evil.example` → HTTP 200.

Vá bằng một middleware, chừng mười dòng:

    có Origin, không nằm trong danh sách  → 403
    có Origin đúng (buồng lái tự gọi)     → cho qua
    KHÔNG có Origin (curl, script)        → cho qua

Ca thứ ba nghe như một lỗ nhưng không phải: thứ đang chặn là TRÌNH DUYỆT
BỊ LỪA. Một chương trình chạy trên máy này vốn đã làm được mọi thứ nó
muốn mà chẳng cần hỏi buồng lái. Xem `kham/server.py`.

Dựng danh sách Origin TỪ cổng trong config, đừng chép số — ca "đúng host
mà sai cổng" rất dễ sót.

    cd kham-thien-giam-runtime
    python run.py                 buồng lái ở localhost:5186
    python -m kham.snapshot       ghi một lần rồi thoát
    python scripts/kham-suc-khoe.py   MỘT lệnh, một trang kết luận (5 giây)
    python scripts/selftest.py    1641 phép kiểm số học, KHÔNG cần mạng
    python scripts/quet-dot-bien.py --file=kham/phat_lai.py  33 con: 17 chết, 16 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/chan_rui_ro.py 12 con: 4 chết, 8 tương đương
    python scripts/quet-dot-bien.py --file=kham/chan_doan.py 23 con: 7 chết, 16 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/tien_hoa.py  36 con: 17 chết, 19 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/vo_dich.py  10 con: 7 chết, 3 tương đương
    python scripts/quet-dot-bien.py --file=kham/ket_qua.py   7 con: 6 chết, 1 tương đương
    python scripts/quet-dot-bien.py --file=kham/so.py        8 con: 5 chết, 3 tương đương
    python scripts/quet-dot-bien.py --file=kham/ban_thu.py   11 con: 4 chết, 7 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/hoc_offline.py 22 con: 15 chết, 7 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/chay_lai.py  21 con: 9 chết, 12 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/do_thi.py   9 con: 9 chết, 0 sống
    python scripts/quet-dot-bien.py --file=kham/vong.py    50 con: 9 chết, 41 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/chien_thuat.py 22 con: 12 chết, 10 tương đương
    python scripts/quet-dot-bien.py --file=kham/do_tre.py   26 con: 13 chết, 13 CÒN NỢ
    python scripts/quet-dot-bien.py --file=kham/dongho.py    7 con: 7 chết, 0 sống
    python scripts/quet-dot-bien.py --file=kham/cap_token.py 9 con: 9 chết, 0 sống
    python scripts/quet-dot-bien.py --file=kham/dat_lenh.py  21 con: 14 chết, 7 tương đương
    python scripts/quet-dot-bien.py --file=kham/nan_lai.py   13 con: 7 chết, 6 tương đương
    python scripts/quet-dot-bien.py --file=kham/so_lenh.py   24 con: 17 chết, 7 tương đương
    python scripts/quet-dot-bien.py --file=kham/can_loi.py   18 con: 12 chết, 6 tương đương
    python scripts/quet-dot-bien.py --file=kham/dinh_gia.py  22 con: 15 chết, 7 tương đương
    python scripts/quet-dot-bien.py --file=kham/ket_toan.py  15 con: 9 chết, 6 tương đương
    python scripts/quet-dot-bien.py --file=kham/cham_moc.py  12 con: 7 chết, 5 tương đương
    python scripts/quet-dot-bien.py --file=kham/kho_doi.py   26 con: 18 chết, 8 tương đương
    # ── QUÉT ĐỘT BIẾN ────────────────────────────────────────────────
    #
    # 25 module · 493 con · 284 chết (58%) · 209 còn sống.
    #
    # ⚠ Con số của `vong.py` TỪNG được ghi là 16 sống. SAI: lượt quét ấy
    # chạy trong khi một lệnh `git rebase --autostash` cất rồi trả lại
    # file giữa chừng, nên nhiều lượt chấm chạy trên một file KHÔNG phải
    # file bộ quét tưởng. Chiều lệch là chiều NGUY: file mang đột biến
    # của lượt trước thì bài kiểm đỏ, và con đang xét bị đếm là CHẾT —
    # tức tai nạn ấy làm phiếu điểm ĐẸP LÊN. Quét lại khi cây yên tĩnh:
    # 41 sống, và danh sách 41 con chứa TRỌN danh sách 16 con cũ.
    #
    # Bộ quét nay tự chứng: ghi con đột biến xong thì ĐỌC LẠI đĩa và đối
    # chiếu từng byte; khác thì dừng với mã 8. Lời dặn trong văn xuôi
    # (`ĐỪNG chạy git trong lúc quét`) đã có sẵn ở đầu file ấy và không
    # giữ được gì.
    #
    # Lượt 30/08 trên  (1 chết/22 sống → 15/7) tìm ra
    # HAI lỗi thật, không chỉ hạ con số: mép trên của dải tìm không bao
    # giờ chạm tới được (bước 300 từ 60 dừng ở 3360, dải khai 3600), và
    # trị đang dùng 900 nằm NGOÀI lưới của chính nó.
    #
    # Con SỐNG SÓT = một dòng mã sửa sai mà không phép kiểm nào kêu.
    # Phần lớn số còn sống đã kiểm TAY là tương đương (epsilon nuốt
    # điểm bằng nhau, hoặc nhánh bị chặn từ dòng trên); phần ghi
    # "CÒN NỢ" là nợ thật, có tên, chưa trả.
    #
    # BA module chưa quét mà CÓ nhánh quyết định: `vong.py` (vòng điều
    # phối — cần một khung giả lớn), `do_thi.py`, `vi.py`. Danh sách
    # phân loại nằm trong `selftest.py` (`DA_QUET_DOT_BIEN` /
    # `CHUA_QUET_DOT_BIEN`), và một phép kiểm bắt module mới phải được
    # phân loại chứ không nằm ngoài lặng lẽ.
    #
    # Số con còn sống là MỘT thước, không phải THƯỚC: bộ quét chỉ đổi
    # toán tử so sánh, nên nó mù với chia khối sai, hạt giống không cố
    # định, sai thứ nguyên, và lật dấu. Bốn thứ ấy đều đã cắn thật.
    python scripts/quet-dot-bien.py --file=kham/rui_ro.py   44 con: 30 chết, 14 tương đương
    node scripts/kiem-giao-dien.mjs   10 phép kiểm giao diện (tương phản WCAG, z-index, ô trống)
    node scripts/kiem-buong-lai.mjs   13 ô của buồng lái có vẽ được không
    node scripts/kiem-lat-cat.mjs     lát cắt có khớp thứ cung tĩnh đọc không

    cd thi-bac-ty-runtime
    python run.py                 buồng lái ở localhost:5188
    python -m bac.snapshot        quét một lượt, ghi, rồi thoát
    python scripts/selftest.py    1988 phép kiểm số học, KHÔNG cần mạng
    node scripts/kiem-buong-lai.mjs   58 phép: 10 trang + 7 khối tầng ba, × 3 mẫu; khoá đọc/sinh có khớp
    pythonw dichvu/chay-nen.py    chạy nền 24/7 để tích băng đào tạo
    powershell -File dichvu\giam-sat.ps1 -Vong   bộ giám sát THƯỜNG TRÚ

**Cung này có bộ giám sát vì nó đã chết 70,8 giờ mà không ai hay**
(30/08 16:53 UTC → 02/09, đo ngày 02/09). Thiết kế của nó bị ép bởi một
ràng buộc của MÁY chứ không phải của mã: **Task Scheduler đang TẮT.**

    Get-Service Schedule    -> Stopped  (StartType: Automatic)
    Start-Service Schedule  -> "Cannot open Schedule service"  (thiếu admin)
    schtasks /create        -> không dùng được
    COM Schedule.Service    -> "The Task Scheduler Service is not running"

**Đừng đi lại đường tác vụ định kỳ** — mất thì giờ rồi cụt. Móc khởi
động DUY NHẤT còn dùng được là **thư mục Startup**
(`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`), đúng thứ
Tử Cấm Thành đang dùng. Mà lối tắt Startup chỉ bắn MỘT phát lúc đăng
nhập, nên bộ giám sát phải THƯỜNG TRÚ mới lấp được cả lỗ «sập giữa
chừng». Gỡ bằng cách xoá file `.lnk` — không để lại gì.

Hai chi tiết đã cắn lúc dựng nó, ghi để khỏi cắn lại: `.ps1` **phải có
BOM** (PowerShell 5.1 đọc file không BOM theo ANSI, dấu tiếng Việt hoá
rác, và một byte lạc cho `Missing closing '}'` ở một dòng hoàn toàn
lành); và **đừng thăm dò bằng `/api/trang-thai`** — nó mất 11,24 giây vì
dựng cả ảnh chụp, nên bộ giám sát báo nhầm là chết. Hỏi `/api/cau-hinh`
(0,061 giây).

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
    python scripts/selftest.py    513 phép kiểm số học, KHÔNG cần mạng
    python scripts/so-hai-lan.py  hai làn cạnh nhau (vốn, nhịp lệnh, R từng hướng)
    node scripts/kiem-giao-dien.mjs   giao diện có đọc được mọi trường nó cần không

**Làn demo HAI CHIỀU ở `:5282`** (= 5182 + 100, theo tiền lệ Thị Bạc Ty). Làn
chính chạy sàn spot testnet nên `risk.py` chặn SHORT — mà mọi lợi thế đo được
của hệ này nằm ở nửa SHORT: MOCK_KEO_LUI_V1 trên 33 chợ 1d chưa từng dùng cho
SHORT +0,303R/226 lệnh và LONG −0,306R/44 lệnh. Làn demo chạy chế độ `paper`,
ở đó `spot_only` tắt, nên nó đánh được cả hai chiều trên giá THẬT:

    powershell -File dichvuat.ps1 -Demo          ← cách BẬT, chạy nền, sống qua đăng xuất
    powershell -File dichvu\dung.ps1 -Demo         ← cách DỪNG

Chạy tay (chỉ để gỡ lỗi — chết theo cửa sổ terminal):

    $env:BRAIN="mock"; $env:TCT_LAN_DEMO="1"
    $env:TCT_CONFIG="config-hai-chieu.json"
    $env:TCT_DATA_DIR="$PWD\data-hai-chieu"
    python run.py

Ba biến đó phải có ĐỦ: thiếu `TCT_DATA_DIR` là hai bot ghi chung một sổ lệnh,
thiếu `TCT_LAN_DEMO` là làn demo ghi đè cung tĩnh của làn chính, thiếu
`TCT_CONFIG` là nó chạy cấu hình của làn chính (15 chợ, cổng 5182 — cổng bận,
uvicorn chết). `BRAIN=mock` để nó không ăn vào trần 8 lượt/ngày của làn chính.

`config-hai-chieu.json` khác `config.json` bốn chỗ, và tự khai vì sao ngay
trong file: 46 chợ thay vì 15 (rút phép đo tiến tướng từ ~4 tháng xuống ~6 tuần
bằng cách thêm QUAN SÁT chứ không nới ngưỡng), trần vị thế 12 thay vì 4 (48 chợ
mà 4 chỗ thì tín hiệu bị vứt khi hết chỗ, và mẫu nghiêng theo bộ chấm), vòng 60
giây thay vì 20 (46 chợ × 2 khung, ở 20 giây là sát trần trọng số của Binance
khi cộng cả làn chính), và `mode: paper`. Rủi ro mỗi lệnh GIỮ NGUYÊN — nới nó
là đo một hệ khác.

Đọc hai làn bằng `python scripts/so-hai-lan.py`.

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

### Lớp CSS không ai dùng

    npm run lop-chet            soi Cổng Thành + 12 cung
    npm run lop-chet -- <cung>  soi một cung

`npm run kiem` gọi nó ở đầu mỗi phiên và **nhắc** chứ không chặn, cùng
lý do với mục dưới: CSS của cung khác không phải việc của phiên đang mở.

CSS thừa không báo lỗi. Nó nằm trong SHELL, tải về mỗi lượt, và lớn dần
theo mỗi tính năng bị gỡ mà quên dọn kiểu. Đo ngày 02/09: **44 lớp trên
13 cung**, trong đó nhóm `hs-*` — tám lớp giống hệt — chết ở CẢ HAI cung
`kham-thien-giam` và `thai-boc-tu`.

**Đây là PHỎNG ĐOÁN, không phải phép đo — và nó đã kêu oan bốn lần.**
Lớp CSS không được ai *gọi*, nó chỉ khớp hoặc không, nên không có phép
nào chắc chắn. Bốn bản nháp lần lượt: ghi cứng danh sách tệp JS · khớp
chuỗi con (`.tang` sống vì chữ "tang" trong một bản tin) · đòi tiền tố
dài hơn 2 ký tự (bỏ sót `'lv l'+n`) · không gỡ dấu thoát (`class=\"ts-i\"`
trong chuỗi JS của Cộng Bố). Bản đang dùng kiểm chéo được 40/45 ứng viên
bằng một phép độc lập, và 5 cái còn lại chỉ "ngờ" vì tên lớp trùng khoá
dữ liệu (`.ng` gặp `ng:"2026-08-28"`) hay trùng chữ tiếng Việt.

**Kiểm bằng tay trước khi xoá.** Một bộ kiểm xui người ta xoá nhầm một
lần là mất niềm tin vĩnh viễn — thà bỏ sót một lớp chết.

### Chỗ đè im lặng trong CSS

    npm run de-im-lang            soi Cổng Thành + 12 cung · thoát 1 khi còn chỗ đè
    npm run de-im-lang -- <cung>  soi một cung

`npm run kiem` gọi nó ở đầu mỗi phiên và **nhắc** chứ không chặn: CSS
của cung khác không phải việc của phiên đang mở.

Báo khi **cùng ngữ cảnh, cùng selector, cùng thuộc tính, khác giá trị,
ở hai khối khác nhau** — tức là một trong hai đang chết mà người viết
nó không hay.

**Hai lượt soi: trong một tệp, và BẮC QUA hai tệp.** Lượt thứ hai có vì
lượt thứ nhất để lọt một ca thật. Đài Quan Trắc nạp ba tệp CSS;
`app-shell.css` style `.sw-toast` và `.install-dqt` từ 12/08. Một phiên
soi `app.css` với `halls.css`, không thấy hai lớp ấy đâu, kết luận
"không ai style", rồi viết khối mới vào `halls.css` — tệp nạp SAU CÙNG.
22 thuộc tính bị đè, thanh thông báo bản mới đổi hình, và lượt soi
từng-tệp in ✓ suốt. Thứ tự tệp đọc từ `<link>` của `index.html`, không
xếp theo tên: cái nạp sau mới là cái thắng.

Bài học đi kèm, cho mọi phiên: **trước khi kết luận một lớp "không ai
style", đếm xem cung có mấy tệp CSS.** Không cung nào chỉ có một.

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

### Ảnh khai mà không có trên đĩa

    npm run kiem-anh      thoát 1 nếu có đường khai mà thiếu

`npm run kiem` gọi nó ở đầu mỗi phiên và **nhắc** chứ không chặn — ảnh
do bot ghi, phiên đang mở không phải người gây ra.

Nó canh đúng lớp lỗi mục "File do workflow tự sinh" đã mô tả bằng văn
xuôi, kèm cả câu *"sẽ nổ đúng lần L2BEAT thêm dự án mới"*:
`build-l2beat.mjs` và `build-congbo.mjs` **tải** ảnh về
`assets/logos/` rồi ghi `logos.js` trỏ tới chúng; `git add` không phủ
thư mục ảnh thì bảng tra được commit còn ảnh thì không. Trang hiện ô
vỡ, và **không lỗi nào báo** — không 404 trong log build, không phép
kiểm nào đỏ, Actions xanh.

Lời cảnh báo nằm trong văn xuôi chỉ cứu được người vừa đọc đúng đoạn
ấy. Đây là bản chạy được của nó. Soi 596 đường, ba nhóm: mọi
`src`/`href` cục bộ trong `index.html` của Cổng Thành + 12 cung; mảng
`SHELL` của mọi `sw.js`; và cả hai bảng tra logo.

**Nhóm SHELL hậu quả nặng hơn ảnh vỡ.** `cache.addAll(SHELL)` là MỘT
giao dịch — một đường 404 làm cả lời hứa thất bại, service worker
**không cài được**, và PWA mất sạch phần chạy offline. Trang đang mở
thì không thấy gì khác thường, vì mạng vẫn phục vụ bình thường.

**Cắt chú thích trước khi bóc chuỗi.** Bản nháp không cắt và báo
`tang-thu-cac` thiếu đường `"còn nguyên bản gốc 2859"` — một câu tiếng
Việt trong khối chú thích GIỮA mảng SHELL. Cùng đúng cái bẫy thước
`bo-qua` đã vấp: dò bằng chuỗi thô thì chú thích giải thích một thứ bị
tính là chính thứ đó.

**Đọc bảng bằng cách NẠP, không bằng regex.** Bản nháp bóc bảng bằng
regex rồi báo 93/93 ảnh thiếu — báo oan sạch, vì có **hai** bảng trỏ
vào **hai** thư mục khác nhau và regex ghép nhầm:

    DSV_LOGO_MAP → do-sat-vien/assets/logos/   (dùng chung)
    CB_LOGO_BU   → cong-bo/assets/logos/       (ảnh bù, dự án đã ngừng)

`logos.js` là JS hợp lệ gán vào `window`, nên `new Function` đọc đúng
thứ trình duyệt đọc chứ không phải một bản phỏng đoán về nó.

### Node `huong` — thứ duy nhất KHÔNG sinh bản vá

    node scripts/huong.mjs --in    xem đề xuất, không ghi
    node scripts/huong.mjs         ghi factory/huong.json   (nhịp 168 giờ)

Bảy vòng tiến hoá đang chạy **đều là vòng SỬA**. Thước hỏi "có gì
hỏng không"; hỏng thì vá xong là hết, và khi phiếu đã đầy thì model
chỉ còn được bảo *"tìm một chỗ không thước nào đo"*. Nó làm được —
sổ tiến hoá chứng minh — nhưng đó là phán đoán trong **phạm vi một
trang**. Không cơ chế nào hỏi "cả cái này nên thành cái gì tiếp".

Hướng có hai nửa, và chỉ một nửa suy ra được:

    "thiếu gì · lệch gì · phí gì"             SUY RA ĐƯỢC từ repo
    "cái này ĐỂ LÀM GÌ, gì quan trọng nhất"   KHÔNG suy ra được

Node này làm nửa đầu cho tử tế rồi **giao nửa sau**. Bốn tín hiệu,
tất cả lấy từ repo, không cái nào là ý kiến:

    model tự chọn gì      sổ tien-hoa.jsonl, trường daLam — lớp nào
                          hiện lại ở ≥2 cung do các lượt độc lập
    lệch giữa các cung    năng lực cung này có mà cung kia không —
                          bằng chứng đường ấy ĐI ĐƯỢC, khác ý tưởng
    sinh ra không ai đọc  file xưởng ghi mỗi ngày mà không trang nào nạp
    chạy mà chưa đổi gì   node có `lucDoi` null

**Mỗi mục kèm một con số và một lệnh để BÁC nó.** Không có luật ấy
thì đây là máy sinh ý tưởng — mà ý tưởng thì không thiếu; thứ thiếu
là ý tưởng có bằng chứng.

**Và nó sai được, đã sai hai lần ngay lúc dựng.** Lần đầu: tín hiệu
"không ai đọc" im lặng, vì ba file `bao-cao.md` · `phieu.json` ·
`kho-de-xuat.json` có tên trong `van-hanh.js` — mà `van-hanh.js` là
bản chiếu sổ đăng ký, nên **mọi** đường khai trong `ra` đều hiện ở
đó theo cấu tạo. Nay trừ file máy sinh ra khỏi corpus. Lần hai là ở
báo cáo Opus chứ không ở đây, nhưng cùng một bài: nó khai `tri-thuc`
"CẦN KIỂM" vì `lucDoi` null; kiểm thật thì sinh lại 11 lát cắt ra
**0 file đổi** — cổng chặn của `tri-thuc-tien-hoa` đã sinh lại ở lớp
2 nên node kia không còn việc. Báo động nhầm, và nhầm rất thuyết
phục.

Nên đọc `factory/huong.json` như một **bàn đã dọn**, không phải một
quyết định. Chọn xong thì việc mới thành việc: thêm thước, thêm node,
hay sửa tay — đó là lúc bảy vòng kia vào cuộc.

### Quét đột biến giao diện — thước ĐO CHÍNH BỘ THƯỚC

    node scripts/dot-bien-giao-dien.mjs <cung>          thả 18 con, in kết quả
    node scripts/dot-bien-giao-dien.mjs <cung> --song   chỉ in con SỐNG
    node scripts/dot-bien-giao-dien.mjs <cung> --ghi    ghi factory/chieu-mu.json

Một cung 17/17 **không** có nghĩa là nó đẹp — có nghĩa là mười bảy câu
hỏi đã trả lời hết. Câu đắt hơn là *mười bảy câu ấy phủ được bao nhiêu
phần của cái đáng hỏi*, và cách duy nhất trả lời được là **cố ý làm
hỏng một thứ rồi xem có thước nào kêu**.

    con CHẾT = có thước bắt được → chiều ấy đang được canh
    con SỐNG = không ai kêu      → CHIỀU MÙ, và nó có TÊN

**Đo ngày 02/09 trên bốn cung: 31/64 — bộ thước bắt được 48%.** Mười
hai cung đều 16/16 hoặc 17/17 trong khi bộ thước mù hơn một nửa những
hỏng hóc thật. Hai con số ấy không mâu thuẫn; chúng đo hai thứ khác
nhau, và chỉ có con số thứ hai nói được còn bao xa để đi.

**Đây là thước duy nhất của vòng giao diện KHÔNG bão hoà.** Mười chín
thước kia đều hỏi "cung có gì hỏng không" — hỏng thì sửa, sửa xong là
xanh vĩnh viễn, và đó là lý do 12 cung đứng ở 16/16 từ 01/09. Độ phủ
hỏi "bộ thước có mù chỗ nào không": thêm một con đột biến mới là tỉ lệ
tụt ngay. Cùng loại với thước `phan-quyet-2026` của knowledge-os, đo
ĐỘ PHỦ chứ không đo lỗi.

**Con SỐNG mà có khai `canh` là THƯỚC HỎNG, không phải chiều mù** — và
nó tìm ra một cái ngay lượt chạy đầu: `svg-co` dùng `/width=/` không
ranh giới nên `stroke-width="1.7"` khớp, thước báo 0 vĩnh viễn. Sửa
xong thì **11/12 cung tụt điểm**, lộ ra 41 svg thiếu cỡ nội tại.

**Luật tự chứng, chép từ Khâm Thiên Giám:** ghi con đột biến xong thì
đọc lại đĩa đối chiếu **từng byte**, khác thì dừng với mã 8. Bên ấy
từng có `git rebase --autostash` chen giữa lượt quét, và chiều lệch là
chiều NGUY — file mang đột biến của lượt trước thì bài kiểm đỏ, con
đang xét bị đếm là CHẾT, tức tai nạn làm phiếu **đẹp lên**. Lời dặn
trong văn xuôi ở đó đã có sẵn và không giữ được gì.

`DA_DONG` trong chính file ấy giữ **hướng đã đóng** — kết quả âm đáng
giữ đúng bằng kết quả dương, vì chúng ngăn một phiên sau làm lại trọn
một chuỗi thí nghiệm đã thất bại. Đang ghi hai hướng, mỗi hướng kèm số
đo chứ không chỉ kèm chữ "không được".

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
    5282  tu-cam-thanh-runtime LÀN DEMO  ← làn hai chiều (paper, short được)
    5288  thi-bac-ty-runtime BẢN DEMO  ← làn thứ hai của cùng runtime ấy

`5288 = 5188 + 100` chứ KHÔNG phải 5189: dãy `518x` là dãy cấp cho
CUNG, và lấy 5189 cho một bản demo là ăn mất số của cung tiếp theo.
Bản demo không phải một cung — nó là cùng một runtime chạy làn thứ
hai, vốn ảo khác, sổ khác (`data-demo/`), và KHÔNG ghi cung tĩnh.
Bật bằng `dichvu\bat.ps1 -Demo`.

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

Tám chỗ phải sửa, và chỉ MỘT chỗ tự báo nếu quên (mục 8):

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
    8. scripts/vong-xoay.mjs       thêm cung vào VONG_XOAY (xem dưới)

Mục 8 là chỗ DUY NHẤT trong danh sách này tự báo khi quên: `npm run
kiem` nhắc tên cung nào không thuộc vòng tiến hoá nào. Cung quên khai
ở đó vẫn chạy bình thường — nó chỉ **không bao giờ tự tiến hoá**, và
đó là loại đứng yên mà mọi bảng vẫn xanh. Cấp cho cung một vòng riêng
thì ngược lại: phải GỠ nó khỏi VONG_XOAY, không thì mỗi tuần có một
ngày hai model sửa nó trong cùng một lượt. `npm run kiem` canh cả hai
chiều.

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
