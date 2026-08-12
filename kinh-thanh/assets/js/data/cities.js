(function () {
"use strict";

/* ══ thành phố: dữ liệu dòng chảy ═════════════════════ */
var C_=function(ic,n,sub,to,edge,p){return {ic:ic,n:n,s:sub,to:to||null,edge:edge||null,p:p||null};};
var O_=function(ic,n,sub){return {ic:ic,n:n,s:sub};};

var LINKWORD={eth:"rollup",bnb:"rollup",avax:"subnet",dot:"thuê chỗ trên relay chain",atom:"nối bằng IBC"};
var CITY_OK={eth:1,bnb:1,avax:1,dot:1,atom:1};
var LOOPS={
 eth:["Người dân trả phí bằng ETH mỗi lần bấm trong thành phố",
      "Sequencer gom các giao dịch lại thành khối",
      "Thành phố đăng dữ liệu nén (blob) lên Ethereum",
      "Ethereum quyết toán và trả bảo mật ngược về thành phố"],
 bnb:["Người dân trả phí bằng BNB",
      "Validator của chuỗi phụ xác thực và đóng khối",
      "Trạng thái được ghi về BNB Smart Chain",
      "Thanh khoản và người dùng từ sàn Binance chảy ngược vào"],
 avax:["Người dân trả phí bằng token của chính subnet",
       "Bộ validator riêng của subnet xác thực giao dịch",
       "P-Chain ghi nhận và quản lý danh sách validator đó",
       "Subnet tiếp tục tự vận hành — bảo mật không đến từ mạng chính"],
 dot:["Người dân trả phí bằng token của bang",
      "Collator của bang gom giao dịch thành khối ứng viên",
      "Validator relay chain kiểm chứng khối đó",
      "Bảo mật chung của cả đế chế phủ ngược xuống bang"],
 atom:["Người dân trả phí bằng token của chính nước đó",
       "Validator của nước xác thực, quyết toán tức thời",
       "IBC chuyển tài sản và tin nhắn sang nước thành viên khác",
       "Thanh khoản quay về qua chính con đường IBC ấy"]
};
var RETURN_NOTE={
 eth:"Vòng khép kín: càng nhiều người dùng thành phố, càng nhiều phí chảy về Ethereum, càng nhiều ETH bị đốt — và thành phố càng được bảo vệ chắc hơn.",
 bnb:"Vòng khép kín: người dùng từ sàn đổ vào chuỗi phụ, phí rẻ giữ họ ở lại, hoạt động lại kéo thêm dự án mới.",
 avax:"Vòng khép kín: subnet càng đông thì càng đủ tiền nuôi validator riêng — nhưng nếu vắng, không có ai đỡ hộ.",
 dot:"Vòng khép kín: bang trả tiền coretime cho relay chain, relay chain trả lại an ninh — không bang nào phải tự dựng quân đội.",
 atom:"Vòng khép kín: mỗi nước tự nuôi validator của mình, và IBC biến thanh khoản rời rạc thành một thị trường chung."
};

var CITIES={
 "base":{parent:"eth",n:"Base",
  theme:{acc:"#0052FF", accT:"#E6EDFF", brand:"base", mark:"base",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Base. Đây là bản tôi vẽ lại, không phải tệp logo chính thức của Coinbase."},
  standard:{n:"OP Stack", badge:"Bộ quy chuẩn xây thành phố L2",
    s:"Bộ luật xây dựng và tiêu chuẩn hạ tầng đô thị. Base không tự phát minh kiến trúc rollup — nó là một thành phố xây theo bộ tiêu chuẩn này, cùng bản vẽ với Optimism, Mode, Ink và cả Superchain.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  machine:{
   note:"Đây mới là chính quyền vận hành vật lý của thành phố. Hạ tầng đô thị bên dưới (RPC, oracle, indexer) là cổng giao tiếp với hệ thống — không phải bộ máy chạy nó.",
   foot:"Hai chân cuối — L1 settlement và data availability — cắm ngược về Ethereum. Đó là chỗ thành phố trả lại chủ quyền cho triều đình.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Nhận giao dịch, quyết định thứ tự, trả kết quả trong chưa tới một giây",plead:"Phần mềm chạy khâu này",p:["op-node","op-geth"]},
    {ic:"layers",n:"Batch / block production",s:"Gom giao dịch thành lô, nén lại rồi gửi về Ethereum",plead:"Phần mềm chạy khâu này",p:["op-batcher"]},
    {ic:"cpu",n:"Execution",s:"Chạy từng giao dịch qua máy ảo EVM để ra kết quả",plead:"Phần mềm chạy khâu này",p:["op-geth"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối: ai giữ gì, hợp đồng đang ở tình trạng nào"},
    {ic:"scale",n:"Fault proofs",s:"Cơ chế cho phép bất kỳ ai tố cáo một kết quả sai và chứng minh trên Ethereum",plead:"Phần mềm chạy khâu này",p:["Cannon","op-challenger"]},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum là nơi chốt cuối cùng — rút tài sản về L1 phải qua cửa này",plead:"Phần mềm chạy khâu này",p:["op-proposer"]},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob để ai cũng dựng lại được trạng thái",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  intro:"Thành phố do Coinbase quy hoạch. Đặc điểm riêng: cổng thành và quảng trường được xây sẵn thành một ứng dụng, nên người dân bước vào mà gần như không biết mình đang dùng blockchain.",
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi: ứng dụng đọc trạng thái và gửi giao dịch qua đây",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô thành dạng truy vấn được",
         C_("satellite","Explorer","cổng tra cứu công khai cho con người",null,null,
            ["Basescan","Blockscout"]),
         "API / cơ sở dữ liệu", ["The Graph","Goldsky","Envio"]),
      "đọc trạng thái", ["Alchemy","QuickNode","Base RPC công cộng","Ankr"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời thật vào hợp đồng",null,null,
      ["Chainlink","Pyth Network","RedStone"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ Base, do chính kiến trúc rollup định nghĩa",null,null,
      ["Base Bridge","Superbridge"]),
   C_("network","Interoperability","Base ↔ chuỗi và ứng dụng khác, nhắn tin xuyên chuỗi",null,null,
      ["LayerZero","Wormhole","Chainlink CCIP","Across"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề để dựng ứng dụng trên Base",null,null,
      ["OnchainKit","viem / wagmi","Foundry"])],
  econ:{note:"Tiền và cư dân là hai thứ khác loại với RPC hay oracle — chúng không phải dịch vụ kỹ thuật mà là nền kinh tế và hộ tịch của thành phố.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · tài sản thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán · tài sản quyết toán · thanh khoản DeFi",plead:"Ai phát hành và phân phối",p:["Circle","Coinbase"]},
     {ic:"layers",n:"Tokens",s:"tài sản của nền kinh tế — token dự án, token quản trị, vật phẩm"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân: anh là ai trong thành phố này",plead:"Sản phẩm và chuẩn",p:["Base Account","Basenames","ERC-4337","Privy"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch, giữ tài sản, mở cửa vào ứng dụng",plead:"Ví đang được dùng",p:["Coinbase Wallet","MetaMask","Rainbow","Rabby"]}]}]},
  districts:{note:"Base không phải một đống dApp rời rạc — nó đang hình thành các ngành kinh tế và xã hội riêng biệt.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Morpho",s:"tín dụng"},{ic:"coin",n:"Aerodrome",s:"chợ thanh khoản"},
     {ic:"bank",n:"Uniswap",s:"trao đổi"},{ic:"box",n:"Vaults",s:"quỹ tự động sinh lợi suất",plead:"Ai đang làm",p:["Morpho Vaults","Beefy"]}]},
    {name:"Xã hội & truyền thông", ic:"chat", items:[
     {ic:"chat",n:"Farcaster",s:"mạng xã hội giao thức mở"},{ic:"chat",n:"XMTP",s:"nhắn tin giữa các ví"}]},
    {name:"Văn hoá & sáng tạo", ic:"person", items:[
     {ic:"person",n:"Zora",s:"đúc và bán tác phẩm"},{ic:"game",n:"NFT & Collectibles",s:"vật phẩm sưu tầm và chợ giao dịch",plead:"Ai đang làm",p:["OpenSea","Zora"]}]},
    {name:"Giải trí", ic:"game", items:[
     {ic:"game",n:"Games",s:"game onchain và vật phẩm sở hữu được"}]},
    {name:"Thương mại", ic:"card", items:[
     {ic:"card",n:"Commerce",s:"cửa hàng nhận thanh toán stablecoin",plead:"Ai đang làm",p:["Coinbase Commerce","Shopify"]},
     {ic:"card",n:"Payments",s:"chuyển tiền và thanh toán vi mô"}]},
    {name:"Công nghệ", ic:"robot", items:[
     {ic:"robot",n:"AI Apps",s:"tác tử có ví riêng"},{ic:"gear",n:"Developer apps",s:"công cụ cho người xây"}]}]},
  gate:{n:"Base App",q:"Cổng thành + quảng trường",tabs:["Wallet","Trade","Pay","Social","Discover","Apps"],
        note:"Một ứng dụng gom cả ví, sàn, thanh toán, mạng xã hội và kho ứng dụng — người dân đi qua đây để vào thành phố.",
        foot:"Đây là lớp phân phối, không phải nền tảng tạo ra Base. Nó đứng cuối vì mọi thứ bên trên đều gặp người dùng ở đây."},
  loop:["Người dùng mở ứng dụng trong thành phố",
        "Ứng dụng sinh ra giao dịch",
        "Base thực thi giao dịch qua máy ảo EVM",
        "Sequencer xếp thứ tự và đóng khối",
        "Gom thành lô, nén lại, đăng lên Ethereum dạng blob",
        "Ethereum vừa giữ dữ liệu công khai (data availability) vừa quyết toán (settlement)",
        "Bảo mật và tính cuối cùng của Ethereum chảy ngược về Base",
        "Base đáng tin hơn nên vốn và ứng dụng dám ở lại",
        "Có nhiều ứng dụng và vốn hơn thì kéo thêm người dùng — khép vòng"],
  loopNote:"Đừng đọc vòng này như quan hệ một đổi một. Phí mà Base trả cho Ethereum là tiền mua chỗ đăng dữ liệu, và giá chỗ đó lên xuống theo mức chen chúc của cả thị trường chứ không theo số dân của Base. Thứ chảy ngược lại chắc chắn hơn không phải là tiền, mà là niềm tin: càng dựa được vào Ethereum để quyết toán và công khai dữ liệu, thành phố càng giữ được vốn và ứng dụng ở lại."},

 "arbitrum one":{parent:"eth",n:"Arbitrum One",
  theme:{acc:"#12AAFF", accT:"#E2F5FF", brand:"arb", mark:"arb",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Arbitrum. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Arbitrum Nitro + Orbit", badge:"Bộ quy chuẩn xây thành phố L2",
    s:"Bản vẽ riêng của Offchain Labs. Nitro là bộ máy rollup, Orbit là quyền dùng lại bản vẽ đó để dựng đặc khu L3. Khác OP Stack ở chỗ máy phân xử chạy WASM và tranh chấp được thu hẹp qua nhiều vòng hỏi đáp thay vì một bước.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố lớn nhất về tài sản khoá trong nhóm rollup. Không có cổng thành hợp nhất — người dân vào bằng ví riêng, và khu tài chính là nơi đông đúc nhất.",
  machine:{
   note:"Bộ máy vận hành của Arbitrum khác Base ở khâu phân xử: thay vì chạy lại một bước trên Ethereum ngay, hai bên hỏi đáp thu hẹp tranh chấp qua nhiều vòng rồi mới chạy bước cuối.",
   foot:"Hai chân cuối — L1 settlement và data availability — cắm ngược về Ethereum, giống mọi rollup thật.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch, hiện do Offchain Labs vận hành",plead:"Phần mềm chạy khâu này",p:["Nitro sequencer"]},
    {ic:"layers",n:"Batch posting",s:"Nén và gửi lô giao dịch về Ethereum",plead:"Phần mềm chạy khâu này",p:["Batch poster"]},
    {ic:"cpu",n:"Execution",s:"Chạy EVM qua Nitro, phần lõi biên dịch sang WASM để phân xử được",plead:"Phần mềm chạy khâu này",p:["Nitro","ArbOS","Stylus"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối"},
    {ic:"scale",n:"Fraud proofs",s:"Tranh chấp thu hẹp qua nhiều vòng rồi chạy đúng một bước trên Ethereum",plead:"Cơ chế đang dùng",p:["BoLD","WAVM"]},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum chốt cuối cùng, rút tài sản phải qua cửa này"},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Arbiscan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Alchemy","Infura","QuickNode","Arbitrum RPC công cộng"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ Arbitrum, do kiến trúc rollup định nghĩa",null,null,["Arbitrum Bridge"]),
   C_("network","Interoperability","Arbitrum ↔ chuỗi khác",null,null,["LayerZero","Stargate","Across","Wormhole"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Stylus","Foundry","viem / wagmi"])],
  econ:{note:"Arbitrum là nơi duy nhất trong nhóm này có kho bạc DAO lớn tự quyết chi tiêu — đó là một phần nền kinh tế chứ không chỉ là quản trị.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"ARB",s:"token quản trị và kho bạc của DAO"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby","Coinbase Wallet"]}]}]},
  districts:{note:"Arbitrum lệch hẳn về tài chính. Mảng xã hội và sáng tạo mỏng hơn Base rõ rệt — đó là đặc điểm nhận dạng, không phải thiếu sót của bản đồ.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"GMX",s:"hợp đồng vĩnh cửu"},{ic:"bank",n:"Aave",s:"tín dụng"},
     {ic:"coin",n:"Camelot",s:"chợ thanh khoản bản địa"},{ic:"coin",n:"Pendle",s:"tách và giao dịch lợi suất"},
     {ic:"bank",n:"Uniswap",s:"trao đổi"}]},
    {name:"Giải trí", ic:"game", items:[
     {ic:"game",n:"Treasure",s:"hệ game và vật phẩm"},{ic:"game",n:"Games",s:"game onchain"}]},
    {name:"Đặc khu", ic:"gate", items:[
     {ic:"gate",n:"Orbit Chains",s:"L3 riêng mọc trên Arbitrum"}]},
    {name:"Quản trị", ic:"columns", items:[
     {ic:"columns",n:"Arbitrum DAO",s:"kho bạc và quyết định của thành phố"},
     {ic:"coin",n:"Kho bạc DAO",s:"một trong những ngân quỹ onchain lớn nhất"}]}]},
  gate:{n:"Arbitrum Bridge + Portal",q:"Cổng thành",tabs:["Bridge","Portal dApp","Stake","Governance"],
        note:"Trang cầu nối và danh mục ứng dụng — cổng vào thực tế của thành phố.",
        foot:"Không có ứng dụng cổng hợp nhất như Base. Người dùng tự lắp ví với ứng dụng, nên vào khó hơn nhưng ít phụ thuộc một công ty hơn."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Arbitrum thực thi qua Nitro","Sequencer xếp thứ tự và đóng khối",
        "Batch poster nén và gửi lô lên Ethereum","Ethereum giữ dữ liệu và quyết toán",
        "Bảo mật và tính cuối cùng chảy ngược về Arbitrum",
        "Phí thu được chảy một phần vào kho bạc DAO","DAO chi ngân quỹ để kéo thêm ứng dụng và người dùng"],
  loopNote:"Vòng của Arbitrum có thêm một nhánh mà Base không có: phần phí chảy vào kho bạc DAO, và chính DAO quyết chi lại. Nhánh đó mạnh về lý thuyết nhưng chậm trong thực tế — bỏ phiếu mất hàng tuần, và phần lớn quyền biểu quyết nằm ở một nhóm nhỏ."},

 "optimism":{parent:"eth",n:"Optimism",
  theme:{acc:"#FF0420", accT:"#FFE6E9", brand:"op", mark:"op",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Optimism. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"OP Stack", badge:"Bộ quy chuẩn xây thành phố L2",
    s:"Đây là nơi bản vẽ ra đời. Optimism không chỉ là một thành phố dùng OP Stack — nó là nơi viết ra bộ tiêu chuẩn ấy rồi cho các thành phố khác dùng lại, trong đó có Base.",
    linkUp:"settlement + bảo mật", linkDown:"thành phố gốc của bản vẽ"},
  intro:"Thành phố đặc biệt ở chỗ đem chính bản quy hoạch của mình cho nơi khác dùng lại. Nhiều thành phố khác — kể cả Base — được xây từ đúng bản vẽ này.",
  machine:{
   note:"Bộ máy giống hệt Base vì cùng bản vẽ. Khác biệt nằm ở chỗ Optimism là nơi phát triển bản vẽ đó, nên nâng cấp thường xuất hiện ở đây trước.",
   foot:"Hai chân cuối — L1 settlement và data availability — cắm ngược về Ethereum.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch, hiện do OP Labs vận hành",plead:"Phần mềm chạy khâu này",p:["op-node","op-geth"]},
    {ic:"layers",n:"Batch / block production",s:"Gom giao dịch thành lô và gửi về Ethereum",plead:"Phần mềm chạy khâu này",p:["op-batcher"]},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM",plead:"Phần mềm chạy khâu này",p:["op-geth"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối"},
    {ic:"scale",n:"Fault proofs",s:"Cho phép tố cáo một kết quả sai và chứng minh trên Ethereum",plead:"Phần mềm chạy khâu này",p:["Cannon","op-challenger"]},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum chốt cuối cùng",plead:"Phần mềm chạy khâu này",p:["op-proposer"]},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Optimistic Etherscan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Alchemy","Infura","OP Labs RPC"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ Optimism",null,null,["Optimism Bridge","Superbridge"]),
   C_("network","Interoperability","đi lại giữa các thành phố cùng bản vẽ và ra ngoài",null,null,["Superchain interop","LayerZero","Across"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng và dựng cả thành phố mới",null,null,["OP Stack SDK","Foundry","viem / wagmi"])],
  econ:{note:"Optimism là nơi duy nhất biến việc tài trợ hàng công cộng thành một cơ chế kinh tế thường trực, không phải hoạt động từ thiện bên lề.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"OP",s:"token quản trị, và là nguồn chi cho Retro Funding"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch và danh tiếng onchain",plead:"Sản phẩm và chuẩn",p:["EAS Attestations","ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Coinbase Wallet","Rainbow"]}]}]},
  districts:{note:"Điểm nhận dạng của Optimism không nằm ở số ứng dụng mà ở khu quản trị: đây là thành phố đầu tư nhiều nhất vào việc trả tiền cho hàng công cộng.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"coin",n:"Velodrome",s:"chợ thanh khoản bản địa"},{ic:"bank",n:"Synthetix",s:"tài sản tổng hợp"},
     {ic:"bank",n:"Aave",s:"tín dụng"},{ic:"bank",n:"Uniswap",s:"trao đổi"}]},
    {name:"Xã hội & truyền thông", ic:"chat", items:[
     {ic:"chat",n:"Farcaster registry",s:"sổ đăng ký danh tính của Farcaster đặt trên Optimism"}]},
    {name:"Quản trị", ic:"columns", items:[
     {ic:"columns",n:"Optimism Collective",s:"hai viện: người giữ token và công dân"},
     {ic:"coin",n:"Retro Funding",s:"trả tiền cho thứ đã tạo ra giá trị, không phải cho lời hứa"}]},
    {name:"Đặc khu", ic:"gate", items:[
     {ic:"gate",n:"Superchain",s:"mạng lưới các thành phố cùng bản vẽ"}]},
    {name:"Giải trí", ic:"game", items:[
     {ic:"game",n:"Games & NFT",s:"giải trí và vật phẩm"}]}]},
  gate:{n:"Superbridge + ví",q:"Cổng thành",tabs:["Bridge","dApp","Delegate","Governance"],
        note:"Cổng vào là trang cầu nối chung của cả Superchain, dùng được cho mọi thành phố cùng hệ.",
        foot:"Giống Arbitrum, không có ứng dụng cổng hợp nhất. Bù lại cổng này mở cho cả nhóm thành phố chứ không riêng Optimism."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Optimism thực thi qua op-geth","Sequencer xếp thứ tự và đóng khối",
        "op-batcher nén và đăng blob lên Ethereum","Ethereum giữ dữ liệu và quyết toán",
        "Bảo mật chảy ngược về Optimism","Một phần doanh thu chảy vào quỹ Retro Funding",
        "Quỹ trả cho những thứ đã tạo giá trị, kéo thêm người xây"],
  loopNote:"Đây là vòng có ý đồ khác hẳn: Optimism cố biến doanh thu thành khoản trả cho hàng công cộng thay vì chỉ chia cho người giữ token. Ý tưởng đẹp, nhưng đánh giá thứ gì đã tạo ra giá trị là việc chủ quan, và cơ chế này vẫn đang thử nghiệm chứ chưa chứng minh được là bền."},

 "opbnb":{parent:"bnb",n:"opBNB",
  theme:{acc:"#C99A0B", accT:"#FBF2D9", brand:"bnb", mark:"bnb",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của BNB Chain. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"OP Stack (bản BNB)", badge:"Bộ quy chuẩn xây thành phố L2",
    s:"opBNB dùng lại chính bản vẽ OP Stack của Optimism, nhưng đổi nơi cắm chân: dữ liệu và quyết toán đi về BNB Smart Chain chứ không về Ethereum.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Tỉnh trực thuộc của BNB Chain. Lý do tồn tại rất đơn giản: đẩy phí xuống mức game và ứng dụng nhiều thao tác chạy được.",
  machine:{
   note:"Bộ máy giống OP Stack, nhưng đây là điểm phải đọc kỹ: chân cắm không về Ethereum mà về BNB Smart Chain. Bảo mật kế thừa từ BSC — chuỗi chỉ có vài chục validator.",
   foot:"Khác biệt lớn nhất so với Base và Optimism nằm ở hai chân cuối: nơi cắm là BSC, không phải Ethereum.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch, do BNB Chain vận hành",plead:"Phần mềm chạy khâu này",p:["op-node"]},
    {ic:"layers",n:"Batch posting",s:"Gom và gửi lô giao dịch về BNB Smart Chain",plead:"Phần mềm chạy khâu này",p:["op-batcher"]},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM",plead:"Phần mềm chạy khâu này",p:["op-geth"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối"},
    {ic:"scale",n:"Fault proofs",s:"Cơ chế phân xử theo lộ trình OP Stack"},
    {ic:"anchor",n:"BSC settlement",s:"BNB Smart Chain là nơi chốt cuối, không phải Ethereum"},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng về BSC — rẻ hơn nhiều nhưng bảo mật kế thừa từ BSC",plead:"Hạ tầng liên quan",p:["BNB Greenfield"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["opBNBScan"]),
         "API / cơ sở dữ liệu",["NodeReal","The Graph"]),
      "đọc trạng thái",["NodeReal","opBNB RPC công cộng","Ankr"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Binance Oracle","Chainlink"]),
   C_("bridge","Cầu chính thức","BNB Smart Chain ↔ opBNB",null,null,["opBNB Bridge"]),
   C_("network","Interoperability","opBNB ↔ chuỗi khác",null,null,["LayerZero","Stargate","Celer cBridge"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","BNB Chain SDK"])],
  econ:{note:"Nền kinh tế ở đây gắn chặt với sàn Binance: phần lớn tiền vào ra đều đi qua tài khoản sàn chứ không qua cầu onchain.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"BNB",s:"gas · thế chấp · token gốc của cả hệ"},
     {ic:"card",n:"USDT / FDUSD",s:"stablecoin phổ biến nhất trong hệ",plead:"Ai phát hành",p:["Tether","First Digital"]},
     {ic:"layers",n:"Tokens",s:"token dự án và vật phẩm game"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm",p:["Space ID"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["Binance Web3 Wallet","Trust Wallet","MetaMask"]}]}]},
  districts:{note:"Thành phố này mỏng về tài chính phức tạp và dày về ứng dụng nhiều thao tác nhỏ — đúng với lý do nó được dựng.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"PancakeSwap",s:"trao đổi"},{ic:"coin",n:"Yield apps",s:"sản phẩm lợi suất"}]},
    {name:"Giải trí", ic:"game", items:[
     {ic:"game",n:"Game apps",s:"nhóm chính của tỉnh này"}]},
    {name:"Thương mại", ic:"card", items:[
     {ic:"card",n:"Thanh toán vi mô",s:"phí thấp nên trả từng khoản nhỏ được"}]},
    {name:"Công nghệ", ic:"robot", items:[
     {ic:"box",n:"BNB Greenfield",s:"lưu dữ liệu lớn ở chuỗi bên cạnh"},
     {ic:"robot",n:"AI & DePIN",s:"ứng dụng nhiều thao tác nhỏ"}]}]},
  gate:{n:"Binance Web3 Wallet",q:"Cổng thành",tabs:["Ví","Cầu nối","Khám phá dApp"],
        note:"Cổng vào nằm ngay trong ứng dụng sàn — không cần cài thêm gì.",
        foot:"Giống Base ở chỗ có cổng hợp nhất, nhưng cổng này nằm trong một sàn tập trung chứ không phải một ứng dụng độc lập."},
  loop:["Người dùng mở mini app hoặc game","Ứng dụng sinh ra rất nhiều giao dịch nhỏ",
        "opBNB thực thi với phí gần bằng không","Sequencer xếp thứ tự và đóng khối",
        "Gửi lô dữ liệu về BNB Smart Chain","BSC quyết toán và giữ dữ liệu",
        "Bảo mật của BSC chảy ngược về opBNB","Người dùng mới từ sàn Binance đổ vào","Phí rẻ giữ họ ở lại — khép vòng"],
  loopNote:"Vòng này ngắn hơn và mong manh hơn vòng của Base. Base cắm chân vào Ethereum với hơn một triệu validator; opBNB cắm vào BSC với vài chục. Đổi lại phí rẻ hơn nhiều. Đây là đánh đổi có thật, không phải chuyện tốt xấu."},

 "moonbeam":{parent:"dot",n:"Moonbeam",
  theme:{acc:"#C4147A", accT:"#FBE3F0", brand:"moon", mark:"moon",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Moonbeam. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Polkadot SDK (Substrate)", badge:"Bộ quy chuẩn dựng một bang",
    s:"Không phải bản vẽ rollup. Substrate là bộ khung dựng một chuỗi có runtime WASM nâng cấp được mà không cần chia tách mạng. Moonbeam thêm lớp EVM lên trên để lập trình viên Ethereum vào được.",
    linkUp:"thuê chỗ + bảo mật chung", linkDown:"dựng theo bộ khung"},
  intro:"Bang này tồn tại để làm phiên dịch: nó mang môi trường EVM vào đế chế Polkadot, để lập trình viên Ethereum không phải học lại từ đầu.",
  machine:{
   note:"Đây là chỗ khác rollup nhiều nhất. Không có sequencer đăng dữ liệu về chuỗi mẹ. Bang tự sản xuất khối bằng collator, rồi validator của relay chain kiểm chứng khối đó — bảo mật đến từ trên xuống chứ không phải từ việc công khai dữ liệu.",
   foot:"Không có chân nào cắm vào Ethereum. Bảo mật đến từ relay chain Polkadot, và bang trả tiền cho nó bằng coretime.",
   items:[
    {ic:"sequence",n:"Collator",s:"Gom giao dịch của bang thành khối ứng viên",plead:"Ai chạy khâu này",p:["Moonbeam collators"]},
    {ic:"cpu",n:"Execution",s:"Chạy EVM bên trong runtime WASM của Substrate",plead:"Phần mềm chạy khâu này",p:["Frontier","Substrate runtime"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái của bang"},
    {ic:"scale",n:"Relay validation",s:"Validator relay chain kiểm chứng khối do collator đưa lên",plead:"Ai chạy khâu này",p:["Polkadot validators"]},
    {ic:"shield",n:"Shared security",s:"Bang không tự tuyển quân — an ninh do cả đế chế lo chung"},
    {ic:"network",n:"XCM messaging",s:"Gửi tài sản và lệnh sang bang khác mà không cần cầu",plead:"Chuẩn dùng ở đây",p:["XCM"]},
    {ic:"coin",n:"Coretime",s:"Bang trả tiền thuê năng lực xử lý theo thời gian thực dùng",plead:"Cơ chế đang dùng",p:["Agile Coretime"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Moonscan","Subscan"]),
         "API / cơ sở dữ liệu",["Subsquid","SubQuery"]),
      "đọc trạng thái",["Endpoint công cộng","OnFinality","Dwellir"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Acurast"]),
   C_("bridge","Kênh nội bộ XCM","đi lại với các bang khác trong đế chế, không cần cầu",null,null,["XCM"]),
   C_("network","Interoperability","ra ngoài đế chế",null,null,["Wormhole","Snowbridge","Hyperbridge"]),
   C_("gear","Hạ tầng lập trình","dùng được cả bộ đồ nghề Ethereum lẫn Polkadot",null,null,["Foundry","Polkadot.js","viem / wagmi"])],
  econ:{note:"Điểm lạ so với các thành phố khác: phần lớn tài sản ở đây đến qua XCM chứ không qua cầu, nên chúng mang tiền tố xc.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"GLMR",s:"gas · đặt cọc collator · trả coretime"},
     {ic:"card",n:"xcUSDT / xcUSDC",s:"stablecoin nhận qua đường XCM từ bang khác"},
     {ic:"layers",n:"Tokens",s:"token dự án trong bang"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch — dùng chuỗi hệ thống riêng của Polkadot",plead:"Sản phẩm",p:["People Chain"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá — hai thế giới ví cùng dùng được",plead:"Ví đang được dùng",p:["Talisman","SubWallet","MetaMask","Nova Wallet"]}]}]},
  districts:{note:"Hệ ứng dụng mỏng hơn hẳn Base hay Arbitrum. Giá trị của Moonbeam nằm ở vai trò phiên dịch giữa hai thế giới, không nằm ở số lượng công trình.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"StellaSwap",s:"trao đổi"},{ic:"bank",n:"Moonwell",s:"tín dụng"},
     {ic:"coin",n:"Beamswap",s:"chợ thanh khoản"}]},
    {name:"Liên thông", ic:"network", items:[
     {ic:"network",n:"Remote EVM",s:"gọi hợp đồng EVM từ một bang khác qua XCM"},
     {ic:"network",n:"XCM apps",s:"ứng dụng chạy xuyên nhiều bang"}]},
    {name:"Quản trị", ic:"columns", items:[
     {ic:"columns",n:"Moonbeam Governance",s:"quản trị riêng của bang"},
     {ic:"columns",n:"OpenGov",s:"quản trị chung của cả đế chế"}]}]},
  gate:{n:"Ví + Polkadot.js",q:"Cổng thành",tabs:["Ví EVM","XCM Transfer","dApp","Staking"],
        note:"Người dùng Ethereum vào bằng MetaMask; người dùng Polkadot vào bằng ví gốc của hệ.",
        foot:"Hai cổng cho hai thế giới — tiện cho cả hai phía, nhưng cũng là dấu hiệu bang này chưa có bản sắc cửa vào của riêng mình."},
  loop:["Người dùng mở ứng dụng trong bang","Ứng dụng sinh ra giao dịch",
        "Moonbeam thực thi trong runtime WASM","Collator gom thành khối ứng viên",
        "Validator relay chain kiểm chứng khối","Bảo mật chung của đế chế phủ xuống bang",
        "Bang trả coretime bằng GLMR cho relay chain","Tài sản và lệnh đi lại với bang khác qua XCM",
        "Bang nào cũng dùng được dịch vụ của nhau — khép vòng"],
  loopNote:"Vòng này không đi qua Ethereum lần nào. Đó là điểm mạnh về chủ quyền kỹ thuật và điểm yếu về thanh khoản: bang được bảo vệ tốt nhưng nằm ngoài dòng vốn lớn nhất của ngành."},

 "osmosis":{parent:"atom",n:"Osmosis",
  theme:{acc:"#6B14D6", accT:"#EDE2FC", brand:"osmo", mark:"osmo",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Osmosis. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Cosmos SDK + CometBFT", badge:"Bộ quy chuẩn lập một quốc gia",
    s:"Khác hai bản vẽ kia ở chỗ căn bản: nó không dựng một thành phố phụ thuộc ai. Cosmos SDK lắp sẵn module tiền tệ, staking và quản trị để dựng thẳng một quốc gia đầy đủ chủ quyền.",
    linkUp:"chỉ là thành viên liên minh", linkDown:"dựng theo bộ khung"},
  intro:"Osmosis không phải tỉnh của ai. Nó là một L1 độc lập tự chọn nối vào liên minh, và tự nhận vai trò cảng thanh khoản chung cho cả Cosmos.",
  machine:{
   note:"Đọc kỹ chỗ này: Osmosis không phải L2. Nó không đăng dữ liệu về đâu, không thuê bảo mật của ai. Bộ máy của nó là bộ máy của một quốc gia, không phải của một thành phố.",
   foot:"Không có chân nào cắm xuống dưới. Vừa là chủ quyền tuyệt đối, vừa là chỗ mong manh nhất — sập là tự sập, không ai đỡ.",
   items:[
    {ic:"scale",n:"Validator set",s:"Khoảng một trăm năm mươi validator do người giữ OSMO uỷ quyền",plead:"Phần mềm chạy khâu này",p:["CometBFT"]},
    {ic:"sequence",n:"Block production",s:"Đề xuất và bỏ phiếu khối theo từng vòng"},
    {ic:"cpu",n:"Execution",s:"Chạy module gốc và hợp đồng CosmWasm",plead:"Phần mềm chạy khâu này",p:["CosmWasm"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái của chính nước này"},
    {ic:"anchor",n:"Instant finality",s:"Khối chốt ngay khi đủ hai phần ba phiếu — không có chuyện đảo khối"},
    {ic:"network",n:"IBC",s:"Hiệp ước nối sang nước thành viên khác, không cần cầu bên ngoài",plead:"Chuẩn dùng ở đây",p:["IBC","Skip"]},
    {ic:"shield",n:"Chủ quyền",s:"Không quyết toán ở đâu cả — bảo mật do chính validator của nước lo"}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Mintscan","Celatone"]),
         "API / cơ sở dữ liệu",["Numia","SQD"]),
      "đọc trạng thái",["Node cộng đồng","Polkachu"]),
   C_("satellite","Oracle","giá dùng trong giao thức và nguồn ngoài",null,null,["Oracle trong giao thức","Pyth Network"]),
   C_("bridge","Cửa vào tài sản","đưa tài sản từ ngoài liên minh vào",null,null,["Noble (USDC)","Axelar","Skip Go"]),
   C_("network","Interoperability","đi lại trong liên minh và ra ngoài",null,null,["IBC","Axelar","Wormhole"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng và dựng cả chuỗi mới",null,null,["CosmWasm","Cosmos SDK","Keplr SDK"])],
  econ:{note:"Đây là nước duy nhất trong nhóm tự phát hành đồng tiền để trả phí. Base, Arbitrum, Optimism đều dùng ETH của Ethereum — Osmosis dùng OSMO của chính mình.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"OSMO",s:"gas · đặt cọc validator · quyền bỏ phiếu"},
     {ic:"card",n:"USDC qua Noble",s:"stablecoin gốc đưa vào liên minh",plead:"Ai phát hành",p:["Circle","Noble (USDC)"]},
     {ic:"layers",n:"Tài sản qua IBC",s:"token từ hàng chục nước thành viên khác"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch và tài khoản liên chuỗi",plead:"Sản phẩm và chuẩn",p:["Interchain Accounts",".osmo names"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["Keplr","Leap","Ledger"]}]}]},
  districts:{note:"Osmosis gần như chỉ có một ngành: tài chính. Nhưng nó không phải một sàn trong thành phố — nó là cảng thanh khoản mà cả liên minh dùng chung.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Osmosis DEX",s:"cảng trao đổi chính của liên minh"},
     {ic:"coin",n:"Superfluid Staking",s:"vừa cung cấp thanh khoản vừa đặt cọc"},
     {ic:"bank",n:"Margined / Levana",s:"đòn bẩy và phái sinh"},
     {ic:"coin",n:"Milkyway / Stride",s:"staking thanh khoản nhận qua IBC"}]},
    {name:"Liên thông", ic:"network", items:[
     {ic:"network",n:"Skip",s:"định tuyến giao dịch qua nhiều nước trong một lần bấm"},
     {ic:"card",n:"Noble",s:"nước chuyên phát hành stablecoin cho cả hệ"}]},
    {name:"Quản trị", ic:"columns", items:[
     {ic:"columns",n:"Osmosis Governance",s:"cộng đồng tự quyết mọi tham số, kể cả phí giao dịch"}]}]},
  gate:{n:"Osmosis Zone",q:"Cổng thành",tabs:["Swap","Pools","Stake","Assets","Portfolio"],
        note:"Một trang gom cả trao đổi, hồ thanh khoản và cầu IBC — cổng vào thực tế của cả liên minh.",
        foot:"Đây là cổng thành gần với mô hình Base App nhất trong nhóm: một ứng dụng gom mọi việc. Khác ở chỗ nó do cộng đồng vận hành chứ không phải một công ty."},
  loop:["Người dùng mở Osmosis Zone","Đổi tài sản hoặc gửi vào hồ thanh khoản",
        "Osmosis thực thi giao dịch","Validator đề xuất và bỏ phiếu khối",
        "Khối chốt ngay khi đủ hai phần ba phiếu","Phí trả bằng OSMO chảy về validator và kho bạc",
        "IBC đưa tài sản sang các nước thành viên khác","Thanh khoản từ các nước quay về qua chính đường IBC ấy",
        "Cảng càng sâu thì càng nhiều nước neo vào — khép vòng"],
  loopNote:"Vòng này khép hoàn toàn trong nội bộ liên minh, không có chân nào cắm ra ngoài. Đó vừa là chủ quyền thật vừa là giới hạn thật: Osmosis tự quyết mọi thứ, nhưng cũng tự gánh mọi rủi ro, và nằm ngoài dòng vốn của Ethereum."}
,

 "zksync era":{parent:"eth",n:"zkSync Era",
  theme:{acc:"#1755F4", accT:"#E4ECFE", brand:"zk", mark:"zkfold",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của zkSync. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"ZK Stack", badge:"Bộ quy chuẩn xây thành phố ZK",
    s:"Bản vẽ riêng của Matter Labs để dựng chuỗi ZK. Khác OP Stack ở gốc: thay vì tin trước rồi cho tố cáo sau, mỗi lô giao dịch phải kèm một bằng chứng toán học ngay từ đầu.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố chứng minh mình đúng bằng toán học thay vì bằng thời hạn khiếu kiện. Máy ảo không phải EVM nguyên bản mà là bản dựng lại tương thích ở mức ngôn ngữ.",
  machine:{
   note:"Bộ máy của rollup ZK khác optimistic ở khâu chứng minh. Không có thời hạn khiếu kiện — mỗi lô giao dịch đi kèm một bằng chứng toán học, Ethereum kiểm bằng chứng đó rồi chốt luôn.",
   foot:"Hai chân cuối — verifier trên Ethereum và data availability — cắm ngược về Ethereum, giống mọi rollup thật.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch và trả kết quả tức thì"},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch để ra trạng thái mới"},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi lô"},
    {ic:"scale",n:"Prover",s:"Sinh bằng chứng toán học cho toàn bộ lô — khâu tốn sức tính toán nhất",plead:"Hệ chứng minh dùng ở đây",p:["Boojum"]},
    {ic:"shield",n:"Verifier trên Ethereum",s:"Hợp đồng trên Ethereum kiểm bằng chứng, đúng thì chốt"},
    {ic:"anchor",n:"L1 settlement",s:"Chốt ngay khi bằng chứng được duyệt, không phải chờ bảy ngày"},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["zkSync Era Explorer","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Envio"]),
      "đọc trạng thái",["Alchemy","QuickNode","zkSync RPC công cộng"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network","RedStone"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["zkSync Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Across"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["zksync-ethers","Foundry","viem / wagmi"])],
  econ:{note:"Điểm riêng: tài khoản trừu tượng nằm sẵn trong giao thức chứ không phải chuẩn thêm vào, nên trả phí bằng token khác ETH là chuyện mặc định.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"ZK",s:"token quản trị của hệ zkSync"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["Tài khoản trừu tượng gốc","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby","Zerion"]}]}]},
  districts:{note:"Hệ ứng dụng mỏng hơn Base và Arbitrum rõ rệt. Điểm mạnh của thành phố này nằm ở công nghệ chứng minh, chưa nằm ở số công trình.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"SyncSwap",s:"trao đổi"},{ic:"coin",n:"Koi Finance",s:"chợ thanh khoản"},
     {ic:"bank",n:"Aave",s:"tín dụng"}]},
    {name:"Đặc khu", ic:"gate", items:[
     {ic:"gate",n:"ZK Chains",s:"các chuỗi riêng dựng từ ZK Stack, nối nhau qua Elastic Chain"}]},
    {name:"Công nghệ", ic:"robot", items:[
     {ic:"gear",n:"Native AA apps",s:"ứng dụng khai thác tài khoản trừu tượng gốc"}]}]},
  gate:{n:"zkSync Bridge + Portal",q:"Cổng thành",tabs:["Bridge","Portal","dApp","Docs"],
        note:"Trang cầu nối và danh mục ứng dụng chính thức.",
        foot:"Không có ứng dụng cổng hợp nhất. Cửa vào là ví cộng trang cầu nối."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi và cập nhật trạng thái","Sequencer gom thành lô",
        "Prover sinh bằng chứng toán học cho cả lô","Đăng bằng chứng và dữ liệu lên Ethereum",
        "Hợp đồng verifier kiểm bằng chứng và chốt","Bảo mật của Ethereum chảy ngược về thành phố",
        "Rút tài sản không phải chờ khiếu kiện — khép vòng"],
  loopNote:"Vòng này bỏ được thời hạn bảy ngày, nhưng thêm một khâu tốn kém: sinh bằng chứng cần máy rất mạnh. Hiện việc đó do một bên vận hành. Bằng chứng đúng thì không ai lừa được ai, nhưng ai được sinh bằng chứng vẫn là câu hỏi mở."},
 "starknet":{parent:"eth",n:"Starknet",
  theme:{acc:"#29296E", accT:"#E6E6F2", brand:"stark", mark:"star4",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Starknet. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Cairo + Starknet Stack", badge:"Bộ quy chuẩn xây thành phố ZK",
    s:"Không dùng EVM. Cairo là ngôn ngữ và máy ảo thiết kế riêng cho việc chứng minh — mọi phép tính sinh ra bằng chứng rẻ hơn nhiều về mặt kiến trúc, đổi lại lập trình viên phải học lại từ đầu.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố chọn xây bằng vật liệu hoàn toàn khác. Bỏ EVM để đổi lấy hiệu năng chứng minh — đó là canh bạc lớn nhất trong nhóm L2 của Ethereum.",
  machine:{
   note:"Bộ máy của rollup ZK khác optimistic ở khâu chứng minh. Không có thời hạn khiếu kiện — mỗi lô giao dịch đi kèm một bằng chứng toán học, Ethereum kiểm bằng chứng đó rồi chốt luôn.",
   foot:"Hai chân cuối — verifier trên Ethereum và data availability — cắm ngược về Ethereum, giống mọi rollup thật.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch và trả kết quả tức thì"},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch để ra trạng thái mới"},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi lô"},
    {ic:"scale",n:"Prover",s:"Sinh bằng chứng toán học cho toàn bộ lô — khâu tốn sức tính toán nhất",plead:"Hệ chứng minh dùng ở đây",p:["STARK proofs","SHARP"]},
    {ic:"shield",n:"Verifier trên Ethereum",s:"Hợp đồng trên Ethereum kiểm bằng chứng, đúng thì chốt"},
    {ic:"anchor",n:"L1 settlement",s:"Chốt ngay khi bằng chứng được duyệt, không phải chờ bảy ngày"},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Starkscan","Voyager"]),
         "API / cơ sở dữ liệu",["Apibara","Checkpoint"]),
      "đọc trạng thái",["Alchemy","Blast API","Starknet RPC công cộng"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Pragma","Chainlink"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["StarkGate"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Rhino.fi"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Cairo","Scarb","starknet.js"])],
  econ:{note:"Starknet thu phí bằng ETH và cả STRK — một trong số ít L2 để người dùng chọn trả bằng token của chính thành phố.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"STRK",s:"token quản trị và trả phí của thành phố"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["Tài khoản trừu tượng gốc","Starknet ID"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["Argent","Braavos"]}]}]},
  districts:{note:"Hệ ứng dụng nhỏ nhưng có màu riêng: ví thông minh là mặc định, và mảng game hưởng lợi từ chi phí tính toán rẻ.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Ekubo",s:"trao đổi với thiết kế thanh khoản riêng"},
     {ic:"bank",n:"Vesu",s:"tín dụng"},{ic:"coin",n:"Nostra",s:"chợ tiền tệ"}]},
    {name:"Giải trí", ic:"game", items:[
     {ic:"game",n:"Dojo",s:"bộ khung dựng game chạy hoàn toàn onchain"},
     {ic:"game",n:"Realms",s:"thế giới game chạy thẳng trên chuỗi"}]},
    {name:"Công nghệ", ic:"robot", items:[
     {ic:"gear",n:"Cairo apps",s:"ứng dụng khai thác chi phí chứng minh rẻ"}]}]},
  gate:{n:"StarkGate + ví",q:"Cổng thành",tabs:["Bridge","dApp","Staking","Docs"],
        note:"Cầu chính thức cộng ví thông minh — người dùng ở đây không dùng MetaMask.",
        foot:"Vì không phải EVM, cửa vào tách hẳn khỏi thế giới Ethereum: ví khác, ngôn ngữ khác, công cụ khác."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi và cập nhật trạng thái","Sequencer gom thành lô",
        "Prover sinh bằng chứng toán học cho cả lô","Đăng bằng chứng và dữ liệu lên Ethereum",
        "Hợp đồng verifier kiểm bằng chứng và chốt","Bảo mật của Ethereum chảy ngược về thành phố",
        "Rút tài sản không phải chờ khiếu kiện — khép vòng"],
  loopNote:"Canh bạc của Starknet: bỏ EVM đổi lấy hiệu năng chứng minh. Nếu đúng, thành phố này chạy được thứ mà rollup EVM không kham nổi. Nếu sai, nó tự cắt mình khỏi toàn bộ kho lập trình viên và mã nguồn sẵn có của Ethereum. Đến nay cả hai vế đều đang đúng một phần."},
 "scroll":{parent:"eth",n:"Scroll",
  theme:{acc:"#A8551F", accT:"#F8ECE2", brand:"scroll", mark:"scrollm",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Scroll. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Scroll zkEVM", badge:"Bộ quy chuẩn xây thành phố ZK",
    s:"Tương thích EVM ở mức bytecode: hợp đồng Ethereum nạp lên chạy gần như nguyên trạng, không phải biên dịch lại. Đây là mức tương thích khó làm nhất trong nhóm ZK.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố chọn con đường khó nhất: giữ nguyên máy ảo của Ethereum rồi mới đi chứng minh. Đổi lại lập trình viên không phải sửa gì.",
  machine:{
   note:"Bộ máy của rollup ZK khác optimistic ở khâu chứng minh. Không có thời hạn khiếu kiện — mỗi lô giao dịch đi kèm một bằng chứng toán học, Ethereum kiểm bằng chứng đó rồi chốt luôn.",
   foot:"Hai chân cuối — verifier trên Ethereum và data availability — cắm ngược về Ethereum, giống mọi rollup thật.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch và trả kết quả tức thì"},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch để ra trạng thái mới"},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi lô"},
    {ic:"scale",n:"Prover",s:"Sinh bằng chứng toán học cho toàn bộ lô — khâu tốn sức tính toán nhất",plead:"Hệ chứng minh dùng ở đây",p:["zkEVM circuits","Halo2"]},
    {ic:"shield",n:"Verifier trên Ethereum",s:"Hợp đồng trên Ethereum kiểm bằng chứng, đúng thì chốt"},
    {ic:"anchor",n:"L1 settlement",s:"Chốt ngay khi bằng chứng được duyệt, không phải chờ bảy ngày"},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Scrollscan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Envio"]),
      "đọc trạng thái",["Alchemy","QuickNode","Scroll RPC công cộng"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Scroll Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Across","Orbiter"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","Hardhat","viem / wagmi"])],
  econ:{note:"Không có token riêng làm phí — mọi thứ trả bằng ETH, giống Base.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"Tokens",s:"token dự án trong thành phố"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby","OKX Wallet"]}]}]},
  districts:{note:"Hệ ứng dụng còn thưa. Giá trị của Scroll hiện nằm ở mức tương thích và ở cách nó làm mọi thứ công khai từ đầu.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Ambient",s:"trao đổi"},{ic:"bank",n:"Aave",s:"tín dụng"},
     {ic:"coin",n:"Nuri",s:"chợ thanh khoản"}]},
    {name:"Công nghệ", ic:"robot", items:[
     {ic:"gear",n:"Mã nguồn mở",s:"toàn bộ mạch chứng minh công khai từ ngày đầu"}]}]},
  gate:{n:"Scroll Bridge + ví",q:"Cổng thành",tabs:["Bridge","Ecosystem","Docs"],
        note:"Cầu chính thức và danh mục ứng dụng.",
        foot:"Cửa vào là ví Ethereum quen thuộc — đó chính là điều Scroll muốn: không bắt ai học lại gì."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi và cập nhật trạng thái","Sequencer gom thành lô",
        "Prover sinh bằng chứng toán học cho cả lô","Đăng bằng chứng và dữ liệu lên Ethereum",
        "Hợp đồng verifier kiểm bằng chứng và chốt","Bảo mật của Ethereum chảy ngược về thành phố",
        "Rút tài sản không phải chờ khiếu kiện — khép vòng"],
  loopNote:"Scroll đánh đổi ngược với Starknet: giữ tương thích tối đa nên chi phí chứng minh nặng hơn nhiều. Vòng vẫn khép đúng, chỉ là khâu prover đắt hơn — và đó là một lý do phí ở đây chưa rẻ bằng các rollup optimistic."},
 "linea":{parent:"eth",n:"Linea",
  theme:{acc:"#0B6E7A", accT:"#E0F0F2", brand:"linea", mark:"lines3",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Linea. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Linea zkEVM", badge:"Bộ quy chuẩn xây thành phố ZK",
    s:"Bản vẽ của ConsenSys — cùng nhà với MetaMask và Infura. Điểm mạnh không nằm ở kỹ thuật chứng minh mà ở chỗ nó nằm sẵn trong tay hai cửa vào lớn nhất của Ethereum.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố có lợi thế phân phối thay vì lợi thế công nghệ. Ai dùng MetaMask đều đã ở sẵn ngay cửa.",
  machine:{
   note:"Bộ máy của rollup ZK khác optimistic ở khâu chứng minh. Không có thời hạn khiếu kiện — mỗi lô giao dịch đi kèm một bằng chứng toán học, Ethereum kiểm bằng chứng đó rồi chốt luôn.",
   foot:"Hai chân cuối — verifier trên Ethereum và data availability — cắm ngược về Ethereum, giống mọi rollup thật.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch và trả kết quả tức thì"},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch để ra trạng thái mới"},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi lô"},
    {ic:"scale",n:"Prover",s:"Sinh bằng chứng toán học cho toàn bộ lô — khâu tốn sức tính toán nhất",plead:"Hệ chứng minh dùng ở đây",p:["Linea prover","gnark"]},
    {ic:"shield",n:"Verifier trên Ethereum",s:"Hợp đồng trên Ethereum kiểm bằng chứng, đúng thì chốt"},
    {ic:"anchor",n:"L1 settlement",s:"Chốt ngay khi bằng chứng được duyệt, không phải chờ bảy ngày"},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["LineaScan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Infura","Alchemy","Linea RPC công cộng"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Linea Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Across"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["MetaMask SDK","Foundry","viem / wagmi"])],
  econ:{note:"Linea đốt một phần phí bằng ETH — hiếm gặp ở L2, và là cách nó tự buộc mình vào lợi ích của Ethereum.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"Tokens",s:"token dự án trong thành phố"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby","Rainbow"]}]}]},
  districts:{note:"Hệ ứng dụng trung bình. Điểm nhận dạng là mức độ dính liền với bộ công cụ ConsenSys.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Lynex",s:"trao đổi"},{ic:"bank",n:"Aave",s:"tín dụng"},
     {ic:"coin",n:"Mendi",s:"chợ tiền tệ"}]},
    {name:"Cửa vào", ic:"gate", items:[
     {ic:"wallet",n:"MetaMask tích hợp",s:"cửa vào có sẵn trong ví phổ biến nhất ngành"}]}]},
  gate:{n:"Linea Bridge + MetaMask",q:"Cổng thành",tabs:["Bridge","Hub","dApp"],
        note:"Cầu chính thức, và trên thực tế là chính MetaMask.",
        foot:"Đây là thành phố có cửa vào rộng nhất nhóm ZK — không phải vì nó dựng cổng đẹp, mà vì chủ thành phố cũng là chủ cái ví."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi và cập nhật trạng thái","Sequencer gom thành lô",
        "Prover sinh bằng chứng toán học cho cả lô","Đăng bằng chứng và dữ liệu lên Ethereum",
        "Hợp đồng verifier kiểm bằng chứng và chốt","Bảo mật của Ethereum chảy ngược về thành phố",
        "Rút tài sản không phải chờ khiếu kiện — khép vòng"],
  loopNote:"Vòng của Linea có một nhánh khác thường: phí thu được dùng để đốt cả ETH lẫn token của mình. Về lý thuyết là gắn lợi ích với Ethereum. Về thực tế, phần lớn giá trị vẫn đến từ việc ConsenSys nắm cửa vào, không đến từ cơ chế kinh tế."},
 "polygon zkevm":{parent:"eth",n:"Polygon zkEVM",
  theme:{acc:"#6E29D6", accT:"#EEE4FC", brand:"poly", mark:"hexm",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Polygon. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Polygon CDK + AggLayer", badge:"Bộ quy chuẩn xây thành phố ZK",
    s:"CDK là bộ khung dựng chuỗi ZK riêng; AggLayer là lớp gộp bằng chứng và thanh khoản của nhiều chuỗi lại thành một. Ý đồ: nhiều thành phố nhưng người dùng thấy như một.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố trong hệ Polygon, và là bản mẫu cho ý đồ lớn hơn: gộp thanh khoản của cả một mạng lưới chuỗi qua AggLayer.",
  machine:{
   note:"Bộ máy của rollup ZK khác optimistic ở khâu chứng minh. Không có thời hạn khiếu kiện — mỗi lô giao dịch đi kèm một bằng chứng toán học, Ethereum kiểm bằng chứng đó rồi chốt luôn.",
   foot:"Hai chân cuối — verifier trên Ethereum và data availability — cắm ngược về Ethereum, giống mọi rollup thật.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch và trả kết quả tức thì"},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch để ra trạng thái mới"},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi lô"},
    {ic:"scale",n:"Prover",s:"Sinh bằng chứng toán học cho toàn bộ lô — khâu tốn sức tính toán nhất",plead:"Hệ chứng minh dùng ở đây",p:["Plonky2","CDK prover"]},
    {ic:"shield",n:"Verifier trên Ethereum",s:"Hợp đồng trên Ethereum kiểm bằng chứng, đúng thì chốt"},
    {ic:"anchor",n:"L1 settlement",s:"Chốt ngay khi bằng chứng được duyệt, không phải chờ bảy ngày"},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["PolygonScan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Alchemy","QuickNode","Polygon RPC công cộng"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Polygon zkEVM Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["AggLayer","LayerZero"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","Hardhat","viem / wagmi"])],
  econ:{note:"Phí trả bằng ETH, còn POL là token của cả hệ Polygon dùng cho đặt cọc và quản trị.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"POL",s:"token đặt cọc và quản trị của cả hệ Polygon"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby","Coinbase Wallet"]}]}]},
  districts:{note:"Hệ ứng dụng của riêng zkEVM khá thưa — phần lớn hoạt động của Polygon vẫn nằm ở chuỗi PoS cũ chứ không ở đây.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Quickswap",s:"trao đổi"},{ic:"coin",n:"Balancer",s:"chợ thanh khoản"}]},
    {name:"Đặc khu", ic:"gate", items:[
     {ic:"gate",n:"CDK Chains",s:"các chuỗi riêng dựng từ CDK"},
     {ic:"network",n:"AggLayer",s:"lớp gộp bằng chứng và thanh khoản giữa các chuỗi"}]}]},
  gate:{n:"Polygon Portal",q:"Cổng thành",tabs:["Bridge","Swap","Ecosystem"],
        note:"Cổng chung cho cả hệ Polygon, không riêng zkEVM.",
        foot:"Cửa vào chung cho nhiều chuỗi — tiện, nhưng cũng khiến người dùng khó biết mình đang đứng ở chuỗi nào."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi và cập nhật trạng thái","Sequencer gom thành lô",
        "Prover sinh bằng chứng toán học cho cả lô","Đăng bằng chứng và dữ liệu lên Ethereum",
        "Hợp đồng verifier kiểm bằng chứng và chốt","Bảo mật của Ethereum chảy ngược về thành phố",
        "Rút tài sản không phải chờ khiếu kiện — khép vòng"],
  loopNote:"Vòng của zkEVM khép đúng, nhưng câu chuyện thật của Polygon nằm ở AggLayer chứ không ở chuỗi này. zkEVM giống bản trình diễn kỹ thuật hơn là thành phố đông dân — và số liệu hoạt động phản ánh đúng như vậy."},

 "blast":{parent:"eth",n:"Blast",
  theme:{acc:"#8F8C00", accT:"#F7F6D8", brand:"blast", mark:"burst",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Blast. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"OP Stack (bản Blast)", badge:"Bộ quy chuẩn xây thành phố L2",
    s:"Dùng bản vẽ OP Stack nhưng thêm một cơ chế riêng: tài sản gửi vào được đem đi sinh lợi suất ở Ethereum, rồi trả lại cho người giữ.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố dựng quanh một lời hứa kinh tế chứ không quanh một cải tiến kỹ thuật: để tiền ở đây thì tự sinh lãi.",
  machine:{
   note:"Bộ máy giống OP Stack. Điểm thêm nằm ngoài bộ máy: tài sản trong cầu được đem đi staking và cho vay ở Ethereum để sinh lợi suất.",
   foot:"Hai chân cuối cắm về Ethereum. Nhưng phần sinh lợi suất thì phụ thuộc thêm các giao thức bên ngoài — đó là rủi ro không nằm trong kiến trúc rollup.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch, do đội Blast vận hành",plead:"Phần mềm chạy khâu này",p:["op-node","op-geth"]},
    {ic:"layers",n:"Batch / block production",s:"Gom giao dịch thành lô và gửi đi",plead:"Phần mềm chạy khâu này",p:["op-batcher"]},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM",plead:"Phần mềm chạy khâu này",p:["op-geth"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối"},
    {ic:"scale",n:"Fault proofs",s:"Cho phép tố cáo một kết quả sai và chứng minh trên Ethereum",plead:"Phần mềm chạy khâu này",p:["Cannon","op-challenger"]},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum chốt cuối cùng",plead:"Phần mềm chạy khâu này",p:["op-proposer"]},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Blastscan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Blast RPC công cộng","Ankr","QuickNode"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","RedStone"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Blast Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Across"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","viem / wagmi"])],
  econ:{note:"Đặc điểm riêng: ETH và stablecoin để trong thành phố tự sinh lợi suất, tiền lãi đến từ staking và cho vay ở Ethereum.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"BLAST",s:"token quản trị và phần thưởng"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby"]}]}]},
  districts:{note:"Hệ ứng dụng dựng nhanh trong đợt phát token rồi mỏng đi rõ rệt. Đây là ví dụ sống về việc phần thưởng kéo được người đến nhưng không giữ được họ.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Thruster",s:"trao đổi"},{ic:"coin",n:"Juice",s:"đòn bẩy"}]},
    {name:"Giải trí", ic:"game", items:[
     {ic:"game",n:"Game & NFT",s:"nhóm ứng dụng chính trong đợt đầu"}]}]},
  gate:{n:"Blast Bridge",q:"Cổng thành",tabs:["Bridge","dApp","Points"],
        note:"Cầu chính thức, gắn liền với hệ thống điểm thưởng.",
        foot:"Cửa vào thiết kế quanh việc gửi tiền vào để nhận điểm — mô hình kéo người rất mạnh trong ngắn hạn."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi qua op-geth","Sequencer xếp thứ tự và đóng khối",
        "op-batcher nén và gửi lô đi","Nơi nhận giữ dữ liệu và quyết toán",
        "Bảo mật chảy ngược về thành phố","Ứng dụng và vốn dám ở lại",
        "Có thêm ứng dụng thì kéo thêm người dùng — khép vòng"],
  loopNote:"Vòng này có một nhánh không nằm trong kiến trúc rollup: tài sản trong cầu được đem đi sinh lợi suất ở nơi khác. Nghĩa là người dùng chịu thêm rủi ro của những giao thức đó, chứ không chỉ rủi ro của Blast. Bản đồ nào vẽ Blast giống Base là bỏ sót đúng chỗ quan trọng nhất."},
 "mantle":{parent:"eth",n:"Mantle",
  theme:{acc:"#2E2E2E", accT:"#EDEDED", brand:"mantle", mark:"shellm",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Mantle. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"OP Stack + lớp DA riêng", badge:"Bộ quy chuẩn kiểu mô-đun",
    s:"Lấy phần thực thi từ OP Stack nhưng tách khâu lưu dữ liệu ra một hệ khác để rẻ hơn. Đây là kiến trúc mô-đun: mỗi tầng chọn nhà cung cấp riêng thay vì mua trọn gói của Ethereum.",
    linkUp:"settlement", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố thử tách rời các tầng: thực thi một nơi, lưu dữ liệu một nơi khác. Rẻ hơn nhiều, nhưng thêm một bên phải tin.",
  machine:{
   note:"Bộ máy giống OP Stack ở phần thực thi, nhưng khác ở chân cuối: dữ liệu không đăng thẳng lên Ethereum mà gửi sang một lớp khả dụng dữ liệu riêng.",
   foot:"Chân quyết toán vẫn ở Ethereum. Chân dữ liệu thì không — và đó là chỗ hồ sơ rủi ro của Mantle khác Base.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch, do Mantle vận hành",plead:"Phần mềm chạy khâu này",p:["op-node","op-geth"]},
    {ic:"layers",n:"Batch / block production",s:"Gom giao dịch thành lô và gửi đi",plead:"Phần mềm chạy khâu này",p:["op-batcher"]},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM",plead:"Phần mềm chạy khâu này",p:["op-geth"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối"},
    {ic:"scale",n:"Fault proofs",s:"Cho phép tố cáo một kết quả sai và chứng minh trên Ethereum",plead:"Phần mềm chạy khâu này",p:["Cannon","op-challenger"]},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum chốt cuối cùng",plead:"Phần mềm chạy khâu này",p:["op-proposer"]},
    {ic:"box",n:"Data availability",s:"Dữ liệu gửi sang lớp DA riêng, rẻ hơn blob nhiều lần",plead:"Chuẩn dùng ở đây",p:["EigenDA","Mantle DA"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["MantleScan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Mantle RPC công cộng","Ankr","QuickNode"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Mantle Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Across"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","viem / wagmi"])],
  econ:{note:"Mantle trả phí bằng MNT chứ không phải ETH — hiếm trong nhóm rollup Ethereum, và là lựa chọn có hệ quả về mặt phụ thuộc.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"MNT",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"MNT",s:"token trả phí, đặt cọc và quản trị"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Bybit Wallet","Rabby"]}]}]},
  districts:{note:"Điểm đáng chú ý của Mantle không nằm ở số ứng dụng mà ở kho bạc: đây là một trong những ngân quỹ DAO lớn nhất ngành, và nó tự đầu tư để kéo dự án về.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Merchant Moe",s:"trao đổi"},{ic:"coin",n:"mETH",s:"staking thanh khoản của chính Mantle"},
     {ic:"bank",n:"Lendle",s:"tín dụng"}]},
    {name:"Quản trị", ic:"columns", items:[
     {ic:"coin",n:"Kho bạc Mantle",s:"ngân quỹ lớn, chủ động rót vốn vào hệ sinh thái"}]}]},
  gate:{n:"Mantle Bridge",q:"Cổng thành",tabs:["Bridge","dApp","Stake"],
        note:"Cầu chính thức và danh mục ứng dụng.",
        foot:"Gắn khá chặt với sàn Bybit — nguồn người dùng chính của thành phố này."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi qua op-geth","Sequencer xếp thứ tự và đóng khối",
        "op-batcher nén và gửi lô đi","Nơi nhận giữ dữ liệu và quyết toán",
        "Bảo mật chảy ngược về thành phố","Ứng dụng và vốn dám ở lại",
        "Có thêm ứng dụng thì kéo thêm người dùng — khép vòng"],
  loopNote:"Mantle đổi một phần bảo mật lấy chi phí. Dữ liệu không nằm trên Ethereum nghĩa là muốn dựng lại trạng thái thì phải tin lớp DA kia còn sống và còn trung thực. Rẻ hơn là thật, và rủi ro thêm cũng là thật — đây đúng nghĩa là đánh đổi, không phải nâng cấp."},
 "metis":{parent:"eth",n:"Metis",
  theme:{acc:"#00857D", accT:"#DEF1EF", brand:"metis", mark:"ringm",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Metis. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Optimistic rollup (nhánh riêng)", badge:"Bộ quy chuẩn xây thành phố L2",
    s:"Xuất phát từ nhánh mã nguồn optimistic đời đầu rồi đi hướng riêng. Điểm nhận dạng: nó là một trong những rollup đầu tiên thực sự chạy nhiều sequencer thay vì một.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố nhỏ nhưng chọn giải đúng bài toán khó nhất của cả nhóm rollup: không để một bên duy nhất nắm quyền xếp thứ tự giao dịch.",
  machine:{
   note:"Bộ máy optimistic quen thuộc, nhưng khác ở khâu đầu: sequencer không phải một bên duy nhất mà là một nhóm luân phiên, có đặt cọc và bị phạt nếu làm sai.",
   foot:"Hai chân cuối vẫn cắm về Ethereum.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Nhóm sequencer luân phiên, có đặt cọc — không phải một bên duy nhất",plead:"Phần mềm chạy khâu này",p:["op-node","op-geth"]},
    {ic:"layers",n:"Batch / block production",s:"Gom giao dịch thành lô và gửi đi",plead:"Phần mềm chạy khâu này",p:["op-batcher"]},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM",plead:"Phần mềm chạy khâu này",p:["op-geth"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối"},
    {ic:"scale",n:"Fault proofs",s:"Cho phép tố cáo một kết quả sai và chứng minh trên Ethereum",plead:"Phần mềm chạy khâu này",p:["Cannon","op-challenger"]},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum chốt cuối cùng",plead:"Phần mềm chạy khâu này",p:["op-proposer"]},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Metis Explorer","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph"]),
      "đọc trạng thái",["Metis RPC công cộng","Ankr"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Metis Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Across"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","viem / wagmi"])],
  econ:{note:"Metis trả phí bằng METIS. Một phần token bị khoá làm tài sản đặt cọc cho các sequencer.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"METIS",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"METIS",s:"trả phí, đặt cọc sequencer và quản trị"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby"]}]}]},
  districts:{note:"Hệ ứng dụng nhỏ. Giá trị của Metis nằm ở chỗ nó chứng minh phi tập trung hoá sequencer làm được, chứ không nằm ở quy mô kinh tế.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Hercules",s:"trao đổi"},{ic:"coin",n:"Netswap",s:"chợ thanh khoản"}]},
    {name:"Công nghệ", ic:"robot", items:[
     {ic:"gear",n:"Sequencer pool",s:"nhóm sequencer luân phiên có đặt cọc"}]}]},
  gate:{n:"Metis Bridge",q:"Cổng thành",tabs:["Bridge","dApp","Stake"],
        note:"Cầu chính thức và danh mục ứng dụng.",
        foot:"Cửa vào đơn giản, không có cổng hợp nhất."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi qua op-geth","Sequencer xếp thứ tự và đóng khối",
        "op-batcher nén và gửi lô đi","Nơi nhận giữ dữ liệu và quyết toán",
        "Bảo mật chảy ngược về thành phố","Ứng dụng và vốn dám ở lại",
        "Có thêm ứng dụng thì kéo thêm người dùng — khép vòng"],
  loopNote:"Vòng của Metis có một điểm mà cả Base lẫn Arbitrum đều chưa làm xong: khâu xếp thứ tự giao dịch không nằm trong tay một công ty. Đổi lại, thành phố nhỏ nên số validator thực tế vẫn ít — phi tập trung về cơ chế chưa đồng nghĩa phi tập trung về quy mô."},
 "mode":{parent:"eth",n:"Mode",
  theme:{acc:"#6C7A00", accT:"#F1F5D6", brand:"mode", mark:"ringm",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Mode. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"OP Stack", badge:"Bộ quy chuẩn xây thành phố L2",
    s:"Một thành phố Superchain, cùng bản vẽ với Base và Optimism. Không tuỳ biến kiến trúc — điểm riêng nằm ở cơ chế chia doanh thu cho người xây ứng dụng.",
    linkUp:"settlement + bảo mật", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố nhỏ trong Superchain, dựng quanh một ý: chia lại phí cho người xây ứng dụng và người giới thiệu người dùng.",
  machine:{
   note:"Bộ máy giống hệt Base vì cùng bản vẽ OP Stack. Không có tuỳ biến ở tầng này.",
   foot:"Hai chân cuối cắm về Ethereum, và đi lại với các thành phố Superchain khác qua đường nội bộ.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch, do đội Mode vận hành",plead:"Phần mềm chạy khâu này",p:["op-node","op-geth"]},
    {ic:"layers",n:"Batch / block production",s:"Gom giao dịch thành lô và gửi đi",plead:"Phần mềm chạy khâu này",p:["op-batcher"]},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM",plead:"Phần mềm chạy khâu này",p:["op-geth"]},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi khối"},
    {ic:"scale",n:"Fault proofs",s:"Cho phép tố cáo một kết quả sai và chứng minh trên Ethereum",plead:"Phần mềm chạy khâu này",p:["Cannon","op-challenger"]},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum chốt cuối cùng",plead:"Phần mềm chạy khâu này",p:["op-proposer"]},
    {ic:"box",n:"Data availability",s:"Dữ liệu đăng lên Ethereum dạng blob",plead:"Chuẩn dùng ở đây",p:["EIP-4844 blob"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Mode Explorer","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Mode RPC công cộng","Ankr"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink","Pyth Network"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Mode Bridge","Superbridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["Superchain interop","LayerZero"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","viem / wagmi"])],
  econ:{note:"Điểm riêng: một phần phí giao dịch được chia lại cho ứng dụng tạo ra giao dịch đó, thay vì chảy hết về đội vận hành chuỗi.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"ETH",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"MODE",s:"token quản trị và phần thưởng"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","ERC-4337"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Rabby"]}]}]},
  districts:{note:"Hệ ứng dụng nhỏ, thiên hẳn về tài chính. Mode gần với một thử nghiệm kinh tế hơn là một thành phố đông dân.",
   groups:[
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Ionic",s:"tín dụng"},{ic:"coin",n:"Velodrome",s:"chợ thanh khoản dùng chung Superchain"}]},
    {name:"Kinh tế ứng dụng", ic:"coin", items:[
     {ic:"coin",n:"Sequencer Fee Sharing",s:"chia lại phí cho ứng dụng tạo ra giao dịch"}]}]},
  gate:{n:"Superbridge",q:"Cổng thành",tabs:["Bridge","dApp"],
        note:"Dùng chung cổng cầu nối của cả Superchain.",
        foot:"Lợi thế của việc dùng chung bản vẽ: không phải tự dựng cổng riêng."},
  loop:["Người dùng mở ứng dụng trong thành phố","Ứng dụng sinh ra giao dịch",
        "Thành phố thực thi qua op-geth","Sequencer xếp thứ tự và đóng khối",
        "op-batcher nén và gửi lô đi","Nơi nhận giữ dữ liệu và quyết toán",
        "Bảo mật chảy ngược về thành phố","Ứng dụng và vốn dám ở lại",
        "Có thêm ứng dụng thì kéo thêm người dùng — khép vòng"],
  loopNote:"Mode thêm một nhánh đáng chú ý: phí chảy ngược một phần về ứng dụng. Ý tưởng đúng hướng — người xây được chia phần thay vì chỉ chuỗi thu. Nhưng quy mô hiện quá nhỏ để biết cơ chế này có giữ được người xây hay không."},
 "immutable zkevm":{parent:"eth",n:"Immutable zkEVM",
  theme:{acc:"#0E4A9E", accT:"#E2ECFA", brand:"imx", mark:"crystal",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Immutable. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Polygon CDK (validium)", badge:"Bộ quy chuẩn xây thành phố ZK",
    s:"Dựng từ bộ khung CDK nhưng chọn chế độ validium: bằng chứng vẫn gửi lên Ethereum, còn dữ liệu giao dịch thì giữ ngoài chuỗi. Rẻ hơn rất nhiều — đó là điều kiện sống của một chuỗi game.",
    linkUp:"settlement", linkDown:"xây theo tiêu chuẩn"},
  intro:"Thành phố xây riêng cho game. Mọi lựa chọn kiến trúc ở đây đều nhằm một mục tiêu: phí gần bằng không cho hàng triệu thao tác nhỏ.",
  machine:{
   note:"Đây là chỗ khác biệt lớn nhất và phải đọc kỹ. Đây là validium, không phải rollup đầy đủ: bằng chứng lên Ethereum, nhưng dữ liệu giao dịch giữ ngoài chuỗi.",
   foot:"Chỉ có một chân cắm về Ethereum, không phải hai. Chân dữ liệu bị cắt — đó là cái giá của phí gần bằng không.",
   items:[
    {ic:"sequence",n:"Sequencer",s:"Xếp thứ tự giao dịch, do Immutable vận hành"},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM"},
    {ic:"ledger",n:"State",s:"Sổ trạng thái sau mỗi lô"},
    {ic:"scale",n:"Prover",s:"Sinh bằng chứng toán học cho cả lô",plead:"Hệ chứng minh dùng ở đây",p:["Plonky2","CDK prover"]},
    {ic:"shield",n:"Verifier trên Ethereum",s:"Hợp đồng trên Ethereum kiểm bằng chứng"},
    {ic:"anchor",n:"L1 settlement",s:"Ethereum chốt tính đúng đắn của trạng thái"},
    {ic:"box",n:"Data availability ngoài chuỗi",s:"Dữ liệu KHÔNG đăng lên Ethereum — do một uỷ ban giữ",plead:"Ai giữ dữ liệu",p:["Uỷ ban khả dụng dữ liệu"]}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["Immutable Explorer","Blockscout"]),
         "API / cơ sở dữ liệu",["Immutable API","The Graph"]),
      "đọc trạng thái",["Immutable RPC","Ankr"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ thành phố này, do kiến trúc định nghĩa",null,null,["Immutable Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Immutable SDK","Foundry"])],
  econ:{note:"Phí trả bằng IMX. Cả nền kinh tế xoay quanh vật phẩm game chứ không quanh tài chính.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"IMX",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"IMX",s:"trả phí, đặt cọc và quản trị"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["Immutable Passport"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["Immutable Passport","MetaMask"]}]}]},
  districts:{note:"Đây là thành phố một ngành duy nhất: game. Không có khu tài chính đáng kể, và đó là chủ ý chứ không phải thiếu sót.",
   groups:[
    {name:"Giải trí", ic:"game", items:[
     {ic:"game",n:"Game studios",s:"các tựa game phát hành trên chuỗi này"},
     {ic:"game",n:"Immutable Play",s:"cổng khám phá game"}]},
    {name:"Vật phẩm", ic:"box", items:[
     {ic:"box",n:"Immutable Marketplace",s:"chợ giao dịch vật phẩm trong game"},
     {ic:"id",n:"Immutable Passport",s:"tài khoản người chơi, không cần biết ví là gì"}]}]},
  gate:{n:"Immutable Passport",q:"Cổng thành",tabs:["Đăng nhập","Ví","Chợ vật phẩm","Game"],
        note:"Người chơi đăng nhập như mọi game khác — phần ví nằm ẩn phía sau.",
        foot:"Đây là cổng thành giấu blockchain kỹ nhất trong cả bản đồ. Người chơi không biết mình đang dùng chuỗi nào, và đó là mục tiêu."},
  loop:["Người chơi đăng nhập bằng Passport","Chơi game và sinh ra hàng loạt thao tác nhỏ",
        "Chuỗi thực thi với phí gần bằng không","Sequencer gom thành lô",
        "Prover sinh bằng chứng cho cả lô","Bằng chứng gửi lên Ethereum, dữ liệu giữ ngoài chuỗi",
        "Ethereum xác nhận trạng thái đúng","Vật phẩm mang ra chợ bán được",
        "Kinh tế vật phẩm giữ người chơi ở lại — khép vòng"],
  loopNote:"Vòng này thiếu một chân so với Base. Ethereum xác nhận trạng thái đúng, nhưng không giữ dữ liệu. Nếu uỷ ban giữ dữ liệu biến mất thì người dùng không tự dựng lại được trạng thái để rút tài sản. Với vật phẩm game giá vài đô thì đánh đổi này hợp lý; với tài sản lớn thì không."},
 "gnosis chain":{parent:"eth",n:"Gnosis Chain",
  theme:{acc:"#0F5132", accT:"#E1EFE7", brand:"gnosis", mark:"shield",
    note:"Màu và hình hiệu dựng theo phong cách nhận diện của Gnosis. Bản tôi vẽ lại, không phải tệp logo chính thức."},
  standard:{n:"Chuỗi PoS độc lập", badge:"Không phải bản vẽ rollup",
    s:"Đây không phải L2. Gnosis Chain là một chuỗi EVM độc lập có bộ validator riêng, chạy đúng phần mềm đồng thuận của Ethereum nhưng không quyết toán về Ethereum. Bản đồ gốc xếp nó vào nhóm L2 — chỗ đó cần đính chính.",
    linkUp:"chỉ nối bằng cầu", linkDown:"chuỗi độc lập"},
  intro:"Thành phố này thật ra là một quốc gia nhỏ. Nó nằm trong danh sách L2 của nhiều bản đồ, nhưng bảo mật của nó do chính validator của nó lo, không phải Ethereum.",
  machine:{
   note:"Đọc kỹ chỗ này: không có sequencer, không có bằng chứng gửi về Ethereum, không có thời hạn khiếu kiện. Bộ máy ở đây là bộ máy của một chuỗi độc lập.",
   foot:"Không có chân nào cắm về Ethereum. Muốn qua lại thì phải bắc cầu — và cầu là điểm rủi ro thật sự của thành phố này.",
   items:[
    {ic:"scale",n:"Validator set",s:"Hơn một trăm nghìn validator đặt cọc GNO — đông bất ngờ so với quy mô chuỗi"},
    {ic:"sequence",n:"Block production",s:"Đề xuất và chứng thực khối theo cơ chế giống Ethereum"},
    {ic:"cpu",n:"Execution",s:"Chạy giao dịch qua máy ảo EVM"},
    {ic:"ledger",n:"State",s:"Sổ trạng thái của chính chuỗi này"},
    {ic:"shield",n:"Bảo mật tự lo",s:"Không kế thừa từ đâu — validator của chuỗi là lớp bảo vệ duy nhất"},
    {ic:"bridge",n:"Cầu Omni",s:"Đường duy nhất qua lại với Ethereum, do một nhóm người xác nhận vận hành"},
    {ic:"anchor",n:"Không quyết toán ở đâu",s:"Khối chốt trên chính chuỗi này, không gửi bằng chứng đi đâu cả"}]},
  infra:[
   C_("antenna","RPC / Nodes","cửa vào chuỗi cho ứng dụng",
      C_("database","Indexer","thu thập và sắp xếp dữ liệu thô",
         C_("satellite","Explorer","cổng tra cứu công khai",null,null,["GnosisScan","Blockscout"]),
         "API / cơ sở dữ liệu",["The Graph","Goldsky"]),
      "đọc trạng thái",["Gnosis RPC công cộng","Ankr","Blast API"]),
   C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",null,null,["Chainlink"]),
   C_("bridge","Cầu chính thức","Ethereum ↔ Gnosis, do một nhóm xác nhận vận hành — không phải cầu rollup",null,null,["Omni Bridge"]),
   C_("network","Interoperability","đi ra chuỗi khác",null,null,["LayerZero","Connext"]),
   C_("gear","Hạ tầng lập trình","bộ đồ nghề dựng ứng dụng",null,null,["Foundry","viem / wagmi"])],
  econ:{note:"Kinh tế ở đây khác hẳn: phí trả bằng xDAI — một stablecoin — nên chi phí giao dịch ổn định theo đô la chứ không nhảy theo giá token.",
   groups:[
    {name:"Tiền tệ", items:[
     {ic:"coin",n:"xDAI",s:"gas · thế chấp · tài sản dự trữ gốc"},
     {ic:"card",n:"USDC",s:"thanh toán và thanh khoản DeFi",plead:"Ai phát hành",p:["Circle"]},
     {ic:"layers",n:"GNO",s:"token đặt cọc validator và quản trị"}]},
    {name:"Cư dân", items:[
     {ic:"id",n:"Identity / Account",s:"hộ tịch của cư dân",plead:"Sản phẩm và chuẩn",p:["ENS","Gnosis Safe"]},
     {ic:"wallet",n:"Wallet",s:"chìa khoá: ký giao dịch và giữ tài sản",plead:"Ví đang được dùng",p:["MetaMask","Gnosis Safe","Rabby"]}]}]},
  districts:{note:"Thiên hẳn về thanh toán và công cụ tổ chức, không phải đầu cơ. Đây là nơi Gnosis Safe và thẻ chi tiêu onchain ra đời.",
   groups:[
    {name:"Thanh toán", ic:"card", items:[
     {ic:"card",n:"Gnosis Pay",s:"thẻ chi tiêu gắn thẳng vào ví onchain"},
     {ic:"card",n:"xDAI payments",s:"thanh toán bằng stablecoin với phí gần bằng không"}]},
    {name:"Công cụ tổ chức", ic:"columns", items:[
     {ic:"shield",n:"Gnosis Safe",s:"ví nhiều chữ ký, chuẩn giữ quỹ của cả ngành"},
     {ic:"columns",n:"Snapshot",s:"bỏ phiếu ngoài chuỗi, không tốn phí"}]},
    {name:"Tài chính", ic:"bank", items:[
     {ic:"bank",n:"Balancer",s:"chợ thanh khoản"},{ic:"bank",n:"Agave",s:"tín dụng"}]}]},
  gate:{n:"Gnosis Bridge + Safe",q:"Cổng thành",tabs:["Bridge","Safe","dApp","Pay"],
        note:"Cầu Omni và ví Safe là hai cửa vào chính.",
        foot:"Cửa vào hướng tổ chức nhiều hơn hướng cá nhân — đúng với bản sắc của chuỗi này."},
  loop:["Người dùng hoặc tổ chức mở ví Safe","Giao dịch sinh ra, trả phí bằng xDAI",
        "Chuỗi thực thi qua máy ảo EVM","Validator đề xuất và chứng thực khối",
        "Khối chốt ngay trên chính chuỗi này","Phí chảy về validator đặt cọc GNO",
        "Tài sản qua lại Ethereum bằng cầu Omni","Chi phí ổn định giữ tổ chức ở lại",
        "Thêm tổ chức thì thêm validator — khép vòng"],
  loopNote:"Vòng này khép hoàn toàn trong chính chuỗi, giống Osmosis chứ không giống Base. Điểm mạnh: phí ổn định theo đô la và số validator rất đông. Điểm yếu: cầu Omni là chỗ duy nhất nối với Ethereum, và cầu luôn là mắt xích yếu nhất. Xếp Gnosis chung nhóm L2 với Base là so sánh hai thứ khác loại."}
};

window.KT_DATA = window.KT_DATA || {};
window.KT_DATA.C_          = C_;
window.KT_DATA.O_          = O_;
window.KT_DATA.LINKWORD    = LINKWORD;
window.KT_DATA.CITY_OK     = CITY_OK;
window.KT_DATA.LOOPS       = LOOPS;
window.KT_DATA.RETURN_NOTE = RETURN_NOTE;
window.KT_DATA.CITIES      = CITIES;
})();
