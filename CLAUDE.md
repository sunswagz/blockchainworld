# blockchainworld

Repo chứa Cổng Thành (`index.html` ở gốc) và năm cung, mỗi cung là một
webapp tĩnh độc lập có `index.html` riêng:

    cong-bo/  dai-quan-trac/  do-sat-vien/  kinh-thanh/  tang-thu-cac/

## Chạy song song nhiều phiên

Repo này thường có 2–4 phiên Claude Code chạy cùng lúc, mỗi phiên một
git worktree riêng, mỗi phiên lo một cung:

    claude --worktree cong-bo

Các cung tách thư mục hẳn nên file nguồn không đụng nhau. Ba thứ còn dùng
chung, và toàn bộ luật dưới đây chỉ để chia ba thứ đó:

- `.git` — chung index, chung branch `main`
- các file ở gốc repo, và `.github/workflows/`
- cổng localhost — worktree cô lập file, không cô lập runtime

### Phạm vi sửa

- Chỉ sửa file bên trong thư mục cung được giao cho phiên này.
- **Không bao giờ `git add -A` hay `git add .`** — chỉ add đúng thư mục
  cung. Phiên khác có thể đang viết dở file của nó; `git add -A` sẽ nuốt
  luôn nửa việc chưa xong của họ vào commit của bạn.
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

Danh sách này phải khớp với các dòng `git add` trong hai workflow. Đổi
phạm vi bên đó thì cập nhật lại đây.

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

Luôn truyền cổng, đừng để mặc định:

    node server.js 5175

Nhờ bảng cố định này mà hai phiên song song không bao giờ tranh cổng, kể
cả khi người dùng không nói gì về cổng.

Lưu ý `server.js` phục vụ từ **gốc repo**, không phải từ thư mục cung —
nên server nào cũng mở được cả năm cung (`/cong-bo/`, `/kinh-thanh/`, …).
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
