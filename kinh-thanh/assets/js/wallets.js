/* ═══════════════════════════════════════════════════════
   Phát hiện ví theo EIP-6963.

   Trước đây hộ chiếu chỉ dùng window.ethereum — tức là chỉ nói
   chuyện được với MỘT ví, và khi cài nhiều extension thì chúng
   giành nhau biến đó: bấm "kết nối MetaMask" có thể mở ra Rabby.

   EIP-6963 sửa đúng chỗ này: mỗi ví tự thông báo sự tồn tại của
   mình kèm tên, icon và rdns, app liệt kê hết rồi để người dùng
   chọn. Chuẩn thuần trình duyệt, không thư viện, không khoá.

   MetaMask, Coinbase Wallet, Rabby, Phantom, Uniswap Extension,
   Brave, Trust… đều đã hỗ trợ.

   KHÔNG bao gồm WalletConnect (ví di động: Trust, Rainbow,
   MetaMask mobile). Cái đó cần thư viện @walletconnect và một
   projectId đăng ký — xem ghi chú cuối file.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var found = [];   // {info:{uuid,name,icon,rdns}, provider}
  var seen = {};
  var listeners = [];

  function announce(e) {
    var d = e.detail;
    if (!d || !d.info || !d.provider) return;
    var key = d.info.rdns || d.info.uuid;
    if (seen[key]) return;
    seen[key] = true;
    found.push(d);
    listeners.forEach(function (fn) { try { fn(found.slice()); } catch (err) {} });
  }

  window.addEventListener("eip6963:announceProvider", announce);
  // Ví nào đã nạp trước sẽ trả lời ngay; ví nạp sau tự thông báo.
  window.dispatchEvent(new Event("eip6963:requestProvider"));

  /* Ví cũ chưa theo EIP-6963 vẫn còn dùng window.ethereum.
     Chỉ thêm vào danh sách khi KHÔNG ví nào tự thông báo, để
     tránh hiện trùng một ví hai lần. */
  function withLegacy() {
    if (found.length) return found.slice();
    if (!window.ethereum) return [];
    return [{
      info: {
        uuid: "legacy",
        rdns: "legacy.injected",
        name: window.ethereum.isMetaMask ? "MetaMask" : "Ví trong trình duyệt",
        icon: null
      },
      provider: window.ethereum
    }];
  }

  window.KT_WALLETS = {
    list: withLegacy,
    /* Gọi lại khi có ví mới thông báo — một số extension nạp chậm
       hơn trang, nên danh sách có thể dài thêm sau khi đã vẽ. */
    onChange: function (fn) {
      listeners.push(fn);
      return function () {
        var i = listeners.indexOf(fn);
        if (i >= 0) listeners.splice(i, 1);
      };
    },
    /* Xin địa chỉ từ một ví cụ thể. Chỉ eth_requestAccounts —
       không có đường nào ký hay gửi giao dịch ở đây. */
    connect: function (entry) {
      return entry.provider.request({ method: "eth_requestAccounts" })
        .then(function (accs) { return accs && accs[0] ? accs[0] : null; });
    }
  };
})();
