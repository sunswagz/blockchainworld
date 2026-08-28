"""GỌI MODEL QUA CLAUDE CODE CLI — trả bằng QUOTA GÓI, không cần khoá API.

Chỗ đứt lớn nhất của hệ này suốt nhiều lượt: 13 kỹ năng, 28 phát hiện, sổ giả
thuyết — tất cả đổ vào một prompt mà không ai đọc, vì bộ não ở chế độ `mock`.
Nối được nó cần `ANTHROPIC_API_KEY`, mà khoá ấy tính tiền theo từng lượt gọi.

Nhưng máy này có `claude.exe` đã đăng nhập sẵn bằng gói tháng. Chạy nó ở chế độ
không tương tác thì có đúng thứ cần: một lượt suy luận thật, tính vào quota gói,
không đồng nào phát sinh.

    claude -p "<prompt>" --output-format json

BỐN CHỐT, VÌ ĐÂY LÀ THỨ TIÊU QUOTA CỦA NGƯỜI DÙNG

**1. Tắt hết công cụ.** `--disallowed-tools` liệt kê đủ Bash/Read/Write/… Bộ não
giao dịch chỉ cần suy luận trên dữ liệu được đưa vào; cho nó quyền chạy lệnh
trên máy là mở một cửa không ai xin.

**2. Cắt phần mở đầu động.** `--exclude-dynamic-system-prompt-sections` cùng với
`--system-prompt` riêng: đo được 33.838 → 17.495 token nạp mỗi lượt. Phần bị cắt
là hướng dẫn dành cho Claude Code làm việc trên mã nguồn — vô dụng ở đây.

**3. Vẫn đi qua đồng hồ chi phí cũ.** Trên gói tháng thì `total_cost_usd` không
phải tiền thật, nhưng nó là thước đo quota tốt nhất đang có, và trần
`maxCallsPerDay` thì đúng nghĩa đen. Không nối vào đồng hồ là để một vòng lặp
chạy 24/7 tự do tiêu quota — đúng thứ luật của repo cấm.

**4. Hết giờ thì bỏ, không treo.** Một lượt mất ~10 giây; đặt trần 180 giây. Vòng
giao dịch không được đứng chờ một tiến trình con.

VÌ SAO KHÔNG DÙNG SDK CLAUDE AGENT

Nó cũng chạy bằng gói, nhưng kéo theo cả một khung agent với vòng lặp công cụ.
Ở đây cần đúng một lượt hỏi–đáp có schema. Gọi thẳng CLI là thứ đơn giản nhất
làm được việc, và đơn giản thì soát được.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

# Thứ tự tìm: PATH trước (người dùng tự cài ở đâu cũng thấy), rồi chỗ mặc định.
CHO_TIM = (
    Path.home() / ".local" / "bin" / "claude.exe",
    Path.home() / ".local" / "bin" / "claude",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "claude" / "claude.exe",
)

TAT_CONG_CU = ("Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,Task,TodoWrite,"
               "NotebookEdit,Agent,Artifact,SlashCommand")
# Trần thời gian một lượt gọi. 180 giây là con số tôi ĐOÁN lúc đầu và nó hết giờ
# ngay lượt chạy thật đầu tiên: model nghĩ trên lời nhắc hệ thống 48k ký tự, và
# gói dữ liệu thị trường chỉ 7k nên chậm là do NGHĨ chứ không do đọc.
#
# 7 phút không tốn gì ở đây: `asyncio.to_thread` giữ vòng lặp sống trong lúc chờ,
# `tick()` được await tuần tự nên không có lượt gọi thứ hai chồng lên, và trên
# khung 4h thì một luận điểm chậm vài phút vẫn còn nguyên giá trị.
HET_GIAY = 420


def duong_dan() -> str | None:
    """Đường tới `claude` CLI, hoặc None nếu máy này không có."""
    tay = os.environ.get("CLAUDE_CLI")
    if tay and Path(tay).exists():
        return tay
    tren_path = shutil.which("claude")
    if tren_path:
        return tren_path
    for p in CHO_TIM:
        if p and p.exists():
            return str(p)
    return None


def co_the() -> bool:
    return duong_dan() is not None


class _Usage:
    """Giả dạng `usage` của SDK để dùng lại nguyên đồng hồ chi phí cũ.

    Đồng hồ đọc bằng `getattr`, nên một đối tượng có đủ bốn thuộc tính là vừa.
    Viết một lớp nhỏ ở đây rẻ hơn nhiều so với sửa đồng hồ để nhận hai hình dạng.
    """

    def __init__(self, u: dict) -> None:
        self.input_tokens = u.get("input_tokens", 0) or 0
        self.output_tokens = u.get("output_tokens", 0) or 0
        self.cache_creation_input_tokens = u.get("cache_creation_input_tokens", 0) or 0
        self.cache_read_input_tokens = u.get("cache_read_input_tokens", 0) or 0


_RAO = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.MULTILINE)


def _boc_json(t: str) -> Any:
    """Lấy JSON ra khỏi câu trả lời.

    CLI hay trả JSON bọc trong rào ```json. Gỡ rào trước; nếu vẫn không phân tích
    được thì tìm khối `{...}` dài nhất. Thất bại thì ném — gọi bên ngoài sẽ rơi
    về `mock`, và im lặng nuốt ở đây là để bộ não chạy trên một dict rỗng.
    """
    t = _RAO.sub("", (t or "").strip())
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    i, j = t.find("{"), t.rfind("}")
    if i >= 0 and j > i:
        return json.loads(t[i:j + 1])
    raise ValueError(f"không tìm thấy JSON trong phản hồi ({len(t)} ký tự)")


def goi(*, he_thong: str, nguoi_dung: str, schema: dict | None = None,
        model: str = "claude-sonnet-4-6") -> tuple[Any, _Usage]:
    """Một lượt gọi. Trả (dữ liệu đã phân tích, usage). Ném nếu hỏng.

    `schema` được nhét vào lời nhắc chứ không phải tham số API — CLI không có
    `output_config`. Vẫn ràng buộc được vì bên gọi tự kiểm lại hình dạng, y như
    đường SDK vẫn làm sau khi nhận JSON.
    """
    exe = duong_dan()
    if not exe:
        raise FileNotFoundError("không tìm thấy claude CLI trên máy này")

    nhac = nguoi_dung
    if schema:
        nhac += ("\n\nTRẢ LỜI CHỈ BẰNG MỘT KHỐI JSON hợp lệ, không lời dẫn, không rào "
                 "```. Nó phải khớp lược đồ sau:\n" + json.dumps(schema, ensure_ascii=False))

    # KHÔNG nhét lời nhắc vào argv. Windows chặn dòng lệnh ở ~32.767 ký tự, mà
    # riêng lời nhắc hệ thống ở đây đã 48.476 ký tự (kho kỹ năng chiếm gần hết).
    # Bản đầu truyền thẳng và nhận:
    #
    #     FileNotFoundError: [WinError 206] The filename or extension is too long
    #
    # Lỗi ấy không nói gì về độ dài prompt, và nó chỉ hiện ra trong nhật ký —
    # bảng vẫn xanh vì đường rơi-về-mock che mất. Lời nhắc hệ thống đi qua FILE,
    # lời nhắc người dùng đi qua STDIN; cả hai đều không có trần.
    tmp = tempfile.mkdtemp(prefix="tct-cli-")
    f_he = Path(tmp) / "he-thong.txt"
    f_he.write_text(he_thong, encoding="utf-8")

    lenh = [exe, "-p",
            "--system-prompt-file", str(f_he),
            "--exclude-dynamic-system-prompt-sections",
            "--disallowed-tools", TAT_CONG_CU,
            "--model", model,
            "--output-format", "json"]

    try:
        r = subprocess.run(lenh, input=nhac, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=HET_GIAY,
                           # Chạy ở thư mục tạm: CLI quét thư mục làm việc để dựng
                           # ngữ cảnh dự án, và ta không muốn nó đọc repo.
                           cwd=tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode != 0:
        raise RuntimeError(f"claude CLI thoát mã {r.returncode}: {(r.stderr or '')[-300:]}")

    vo = json.loads(r.stdout)
    if vo.get("is_error"):
        raise RuntimeError(f"claude CLI báo lỗi: {str(vo.get('result'))[:200]}")

    u = _Usage(vo.get("usage") or {})
    return (_boc_json(vo.get("result") or "") if schema else vo.get("result"), u)
