# blockchainworld

Repo chứa Cổng Thành (`index.html` ở gốc) và sáu cung, mỗi cung là một
webapp tĩnh độc lập có `index.html` riêng:

    cong-bo/  dai-quan-trac/  do-sat-vien/  hoang-thanh/
    kinh-thanh/  tang-thu-cac/

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
    npm run kiem                      # tài liệu này có còn khớp repo không

`git status --short` mà thấy thư mục lạ (`?? hoang-thanh/`) thì **có phiên
khác đang dựng dở trong cây chính**. Đừng đụng, đừng add, đừng chạy
`npm run dist` — bản dựng sẽ dính nửa cung chưa xong.

`npm run kiem` báo lệch thì xem mục **"Khi phát hiện lỗi trong chính file
này"** ở cuối — sửa trước khi làm việc khác, vì mọi luật ở đây chỉ đúng
khi tài liệu còn khớp thực tế.

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
- Không merge, không rebase, không push lên `main`. Commit và push lên
  đúng nhánh worktree hiện tại; việc gộp để người dùng làm.

### File do workflow tự sinh — đừng sửa tay

Hai workflow chạy theo lịch và commit thẳng vào `main`, mỗi cái 4 lần một
ngày. Chúng ghi đè đúng những đường dẫn dưới đây; sửa tay là chắc chắn
conflict lúc merge.

`refresh-data.yml` (17 phút sau 0, 6, 12, 18 giờ UTC):

    kinh-thanh/assets/js/data/live.js
    kinh-thanh/assets/js/data/provenance.js
    kinh-thanh/assets/data/history.json
    do-sat-vien/assets/js/data.js
    cong-bo/assets/js/
    tang-thu-cac/assets/js/data.js
    tang-thu-cac/assets/data/

`scan-observatory.yml` (41 phút sau 1, 7, 13, 19 giờ UTC):

    dai-quan-trac/assets/js/scan.js

Muốn đổi số liệu thì sửa script sinh ra chúng trong `scripts/`, không sửa
file kết quả. (Và sửa `scripts/` là file dùng chung — hỏi trước.)

Chạy script ở máy để **kiểm** kết quả thì được, nhưng **đừng commit file
kết quả** — để bot ghi. Sửa xong script, push script, rồi chờ lượt bot kế
tiếp; kết quả tự đúng. Commit tay chỉ tạo hai nguồn ghi vào cùng một file.

    node scripts/build-tangthu.mjs        # xem số có hợp lý không
    git checkout tang-thu-cac/assets/     # rồi trả lại, đừng mang theo

Danh sách này phải khớp với các dòng `git add` trong hai workflow. Đổi
phạm vi bên đó thì cập nhật lại đây.

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

Hệ quả cho `npm run dist`: dòng "rừng văn hoá Hoàng Thành: sinh cách đây N
ngày ⚠" là **bình thường**, không phải dấu hiệu bot chết. Bốn cung kia mới
phải tươi trong 2 ngày.

Vì bot đẩy vào `main` liên tục, worktree phải nhánh từ `origin/main` chứ
không phải HEAD local. Đó là mặc định (`worktree.baseRef: fresh`); đừng
đổi sang `head`.

Hệ quả cho chính file này: worktree nhánh từ `origin/main`, nên sửa
`CLAUDE.md` phải commit và **push lên `main`** mới có tác dụng. Worktree
tạo trước đó vẫn giữ bản cũ.

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

Luôn truyền cổng, đừng để mặc định:

    node server.js 5175

Nhờ bảng cố định này mà hai phiên song song không bao giờ tranh cổng, kể
cả khi người dùng không nói gì về cổng.

Lưu ý `server.js` phục vụ từ **gốc repo**, không phải từ thư mục cung —
nên server nào cũng mở được cả sáu cung (`/cong-bo/`, `/kinh-thanh/`, …).
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

Trước khi gộp, chứng minh bằng lệnh chứ đừng tin cảm giác:

    BASE=$(git merge-base main <nhánh>)

    # 1. nhánh đó có chạm ra ngoài thư mục cung của nó không?
    git diff --name-only $BASE..<nhánh> | grep -v '^<cung>/'

    # 2. hai bên có file nào cùng sửa không?
    comm -12 <(git diff --name-only $BASE..main    | sort) \
             <(git diff --name-only $BASE..<nhánh> | sort)

    # 3. có phải fast-forward sạch không?
    git merge-base --is-ancestor main <nhánh> && echo "ff sạch"

Cả ba lệnh không in ra gì (trừ lệnh 3) thì gộp an toàn:

    git merge --ff-only <nhánh>

Sau khi gộp, đếm lại file chưa theo dõi của phiên khác để chắc mình không
cuốn theo gì:

    git status --short | grep '^??'

Push vào `main` là kích hoạt deploy thật. Đừng push khi cây chính đang có
một cung dựng dở mà cung đó **đã** được thêm vào `HALLS` của
`build-dist.mjs` — lúc đó bản dựng sẽ gãy hoặc đẩy lên site một cung thiếu
file. (Cung dở mà chưa nối vào đâu thì vô hại, `build-dist` không ngó tới.)

## Thêm cung mới

Hai việc bắt buộc, làm ngay trong cùng lần thêm — để sót cái nào cũng
không có lỗi nào báo:

**1. Cấp cổng và ghi vào bảng "Cổng dev" bên trên.** Lấy số kế tiếp trong
dải 5173–5199. Không ghi thì phiên sau đọc file này sẽ không biết dùng
cổng nào, đoán bừa, và tranh cổng với phiên đang chạy.

**2. Thêm đường dẫn của cung vào `paths` của CẢ HAI file**
`deploy-pages.yml` và `deploy-ipfs.yml`. Hai workflow này chỉ chạy khi
push vào `main` **và** file thay đổi khớp `paths`. Danh sách đó phải liệt
kê thủ công từng cung, vì sau khi tách thư mục thì `assets/**` chỉ còn
khớp assets của Cổng Thành.

Quên bước 2 thì: push thành công, không lỗi, không workflow nào chạy, và
bản trên site vẫn là bản cũ. Không có gì báo cho bạn biết.

Nhánh worktree không kích hoạt deploy — đúng như thiết kế, deploy xảy ra
lúc gộp vào `main`.

### Một cung coi là XONG khi

Thiếu bất kỳ dòng nào dưới đây thì **chưa được nối vào `HALLS` và chưa
được gộp về `main`** — nối sớm là dựng ra một site gãy.

Bảy chỗ phải sửa, không chỗ nào tự báo nếu quên:

    <cung>/index.html · sw.js · manifest.webmanifest
    <cung>/assets/css/app.css · halls.css
    <cung>/assets/js/app.js · halls.js · pwa.js
    <cung>/assets/icons/  (192, 512, maskable, apple-touch, favicon)

    1. index.html ở gốc            thẻ trong lưới .halls
    2. assets/js/portal.js         đọc ngày cập nhật cho thẻ đó
    3. halls.js của MỌI cung cũ    thêm vào mảng HALLS
    4. sw.js ở gốc                 thêm dòng bỏ qua phạm vi cung mới
    5. scripts/build-dist.mjs      thêm vào mảng HALLS
    6. deploy-pages.yml + deploy-ipfs.yml   thêm "<cung>/**" vào paths
    7. bảng "Cổng dev" trong file này        cấp số cổng kế tiếp

Mục 3 phải sửa file của cung khác — đó là ngoại lệ duy nhất của luật
"chỉ sửa thư mục cung mình". Làm gọn trong một commit, và nói rõ trong
lời commit là đang nối cung mới.

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

5. Push thẳng lên `main`. Đây là **ngoại lệ có chủ ý** của luật "không push
   `main`": tài liệu chỉ có tác dụng khi ở `main`, vì worktree mới luôn
   nhánh từ `origin/main`.

6. Push bị từ chối thì `git pull --rebase` rồi soát lại, **không bao giờ
   `--force`**.

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
