(function () {
"use strict";

/* ══ hồ sơ chi tiết từng thành phần ═══════════════════ */
/* khoá = <thành phố>::<tên đã chuẩn hoá> */
var ENTITIES={

"base::op stack":{
 role:"Bộ quy chuẩn xây thành phố L2",
 what:"OP Stack là bộ mã nguồn mở và tiêu chuẩn kỹ thuật do Optimism phát triển để dựng một rollup. Nó quy định sequencer chạy thế nào, dữ liệu đăng về L1 ra sao, cầu nối và fault proof hoạt động theo cơ chế nào.",
 metaphor:"Trong phép ví kinh thành: Ethereum là triều đình và nền chủ quyền. OP Stack là bộ luật xây dựng và tiêu chuẩn hạ tầng đô thị. Base là một thành phố cụ thể được xây theo bộ tiêu chuẩn ấy — không phải nơi tự nghĩ ra kiến trúc của mình.",
 chain:["Ethereum — nền chủ quyền, quyết toán và bảo mật","OP Stack — bộ quy chuẩn dựng rollup","Base, Optimism, Mode, Ink… cùng xây theo một bản vẽ","Các thành phố cùng chuẩn nối nhau thành Superchain","Nâng cấp ở bản vẽ chảy xuống mọi thành phố dùng nó"],
 special:"Hệ quả ít người để ý: vì cùng bản vẽ, các thành phố này đi lại với nhau dễ hơn nhiều so với đi sang một rollup kiến trúc khác. Nhưng cũng vì thế, một lỗi trong OP Stack là lỗi của cả nhóm chứ không riêng ai.",
 uses:[],
 compare:[
  {n:"OP Stack",s:"Optimistic rollup, mã nguồn mở, nhiều thành phố dùng chung — Base, Mode, Ink, Zora."},
  {n:"Arbitrum Orbit",s:"Bản vẽ của Arbitrum, có Stylus cho Rust và C, hệ đặc khu L3 riêng."},
  {n:"ZK Stack / Polygon CDK",s:"Dựng rollup chứng minh bằng toán học thay vì chờ thời gian tranh chấp."}],
 where:"Là mã nguồn mở. Base chạy một phiên bản của nó, có tuỳ chỉnh riêng nhưng vẫn theo chuẩn chung."},

"base::sequencer":{
 role:"Bộ máy — người sắp thứ tự",
 what:"Sequencer nhận giao dịch từ người dùng, quyết định thứ tự trước sau, thực thi và trả kết quả gần như tức thì — trước cả khi Ethereum biết chuyện gì vừa xảy ra.",
 metaphor:"Là ban điều hành giao thông của thành phố. Ai đi trước ai đi sau là do nó quyết. Người dân thấy đường thông thoáng chính là nhờ khâu này.",
 chain:["Người dùng gửi giao dịch","Sequencer xếp thứ tự và thực thi","Trả kết quả cho người dùng trong chưa tới một giây","Gom lại thành lô để gửi về Ethereum"],
 special:"Đây là điểm tập trung hoá lớn nhất của Base: sequencer hiện do Coinbase vận hành. Nó có thể trì hoãn hoặc sắp xếp lại giao dịch. Nó không thể lấy tiền của ai — phần đó Ethereum giữ — nhưng quyền quyết định thứ tự vẫn nằm ở một chỗ. Phi tập trung hoá sequencer là việc chưa xong, không riêng Base.",
 uses:["Execution","Batch / block production"],
 compare:[
  {n:"Sequencer tập trung",s:"Nhanh, rẻ, dễ vận hành — nhưng phụ thuộc một bên và có thể kiểm duyệt."},
  {n:"Sequencer chia sẻ",s:"Nhiều bên luân phiên, khó kiểm duyệt hơn, nhưng phức tạp và chậm hơn."}],
 where:"Mọi rollup đều có sequencer. Gần như tất cả hiện vẫn do một đơn vị vận hành."},

"base::batch / block production":{
 role:"Bộ máy — đóng gói và gửi về",
 what:"Sau khi sequencer xếp xong, giao dịch được gom thành lô, nén lại rồi đăng lên Ethereum. Nén càng tốt thì phí người dùng càng rẻ.",
 metaphor:"Là bộ phận đóng gói hồ sơ và gửi công văn về triều đình. Không gửi thì thành phố coi như chưa khai báo gì.",
 chain:["Sequencer sản xuất khối","Gom nhiều khối thành một lô","Nén dữ liệu để tiết kiệm chỗ","Đăng lô lên Ethereum dưới dạng blob"],
 special:"Chi phí đăng dữ liệu về Ethereum từng là phần đắt nhất trong giá một giao dịch L2. EIP-4844 đưa blob vào và kéo phần này xuống rất mạnh — đó là lý do phí trên Base rẻ đi hẳn.",
 uses:["Data availability"],
 compare:[],
 where:"Là khâu bắt buộc của mọi rollup — thứ phân biệt rollup thật với sidechain."},

"base::execution":{
 role:"Bộ máy — thực thi luật",
 what:"Execution là khâu chạy từng giao dịch qua máy ảo EVM để ra kết quả: số dư đổi thế nào, hợp đồng chuyển sang trạng thái gì.",
 metaphor:"Là toà án và văn phòng thi hành án của thành phố — nơi luật trên giấy biến thành kết quả cụ thể.",
 chain:["Nhận giao dịch đã xếp thứ tự","Chạy qua máy ảo EVM","Tính ra trạng thái mới","Ghi vào sổ trạng thái của thành phố"],
 special:"Base dùng đúng EVM của Ethereum, nên hợp đồng viết cho Ethereum chạy được gần như nguyên trạng. Đây là lý do hệ ứng dụng của Base lớn nhanh: không ai phải viết lại từ đầu.",
 uses:[],
 compare:[],
 where:"Cùng máy ảo với Ethereum. Solana dùng SVM, Sui dùng Move — code không mang qua lại được."},

"base::state":{
 role:"Bộ máy — sổ đăng ký trạng thái",
 what:"State là bản ghi chính thức sau mỗi khối: ví nào giữ bao nhiêu, hợp đồng nào đang ở tình trạng nào. Mọi câu hỏi về số dư đều là câu hỏi về state.",
 metaphor:"Là sổ đăng ký đất đai và hộ tịch của thành phố. Không phải lịch sử giao dịch — mà là hiện trạng ai đang sở hữu cái gì.",
 chain:["Execution tính ra kết quả","State cập nhật theo","State root được tóm lại thành một mã băm","Mã băm đó gửi về Ethereum làm bằng chứng"],
 special:"Điều quan trọng: Ethereum không giữ toàn bộ state của Base, chỉ giữ mã băm tóm tắt. Nếu ai đó công bố một state sai, cơ chế fault proof mới là thứ phát hiện ra.",
 uses:["Execution"],
 compare:[],
 where:"Mọi chuỗi đều có khái niệm này — đúng cái “blockchain state” trong bảng khái niệm ở phần Ethereum."},

"base::fault proofs":{
 role:"Bộ máy — cơ chế phân xử",
 what:"Optimistic rollup mặc định tin rằng kết quả sequencer công bố là đúng. Fault proof là cửa để bất kỳ ai tố cáo một kết quả sai và chứng minh điều đó ngay trên Ethereum.",
 metaphor:"Là quyền khiếu kiện lên triều đình. Thành phố tự xử hằng ngày, nhưng dân vẫn có đường kêu lên trên nếu bị xử sai.",
 chain:["Sequencer công bố kết quả","Có một khoảng thời gian để ai đó phản đối","Người phản đối nộp bằng chứng lên Ethereum","Ethereum phân xử — sai thì kết quả bị huỷ"],
 special:"Đây là thứ khiến rollup khác sidechain về bản chất. Nhưng nó cũng là lý do rút tài sản từ L2 về Ethereum phải chờ khoảng bảy ngày: đó chính là thời hạn khiếu kiện. Cầu bên thứ ba nhanh hơn vì họ ứng tiền trước và tự gánh rủi ro chờ.",
 uses:["State","L1 settlement"],
 compare:[
  {n:"Fault proof (optimistic)",s:"Tin trước, kiểm sau. Rẻ, nhưng phải chờ hết hạn khiếu kiện."},
  {n:"Validity proof (ZK)",s:"Chứng minh bằng toán ngay từ đầu. Rút nhanh, nhưng tốn sức tính toán."}],
 where:"Base bật fault proof theo lộ trình chung của OP Stack — đây là tiêu chí quan trọng nhất khi đánh giá độ trưởng thành của một rollup."},

"base::l1 settlement":{
 role:"Bộ máy — chốt cuối cùng",
 what:"Mọi thứ xảy ra trên Base chỉ thật sự không thể đảo ngược khi đã được Ethereum chốt. Rút tài sản từ Base về Ethereum bắt buộc đi qua cửa này.",
 metaphor:"Là con dấu của triều đình. Thành phố ký giấy tờ cả ngày, nhưng chỉ khi đóng dấu trên mới có hiệu lực vĩnh viễn.",
 chain:["Base gửi kết quả và bằng chứng về Ethereum","Hết thời hạn khiếu kiện","Ethereum chốt — không đảo ngược được nữa","Tài sản rút về L1 được mở khoá"],
 special:"Đây chính là chỗ Base trả lại chủ quyền cho Ethereum. Base tự chạy hằng ngày, nhưng không tự tuyên bố cái gì là cuối cùng. Đó là khác biệt gốc giữa một thành phố L2 và một quốc gia L1.",
 uses:[],
 compare:[],
 where:"Hợp đồng settlement của Base nằm trên Ethereum, không nằm trên Base."},

"base::data availability":{
 role:"Bộ máy — dữ liệu công khai",
 what:"Dữ liệu giao dịch của Base được đăng lên Ethereum dưới dạng blob, để bất kỳ ai cũng tải về và dựng lại được toàn bộ trạng thái mà không cần xin phép Coinbase.",
 metaphor:"Là kho lưu trữ công khai đặt ở triều đình. Nếu chính quyền thành phố biến mất, dân vẫn dựng lại được sổ sách từ kho ấy.",
 chain:["Lô giao dịch được nén","Đăng lên Ethereum dạng blob","Ai cũng tải về được","Dựng lại toàn bộ trạng thái Base từ dữ liệu đó"],
 special:"Đây là ranh giới thật giữa rollup và sidechain. Nếu dữ liệu không công khai ở L1, người dùng phải tin nhóm vận hành mới rút được tài sản — lúc đó nó không còn là rollup nữa, dù tự gọi là gì.",
 uses:["L1 settlement"],
 compare:[
  {n:"Đăng về Ethereum",s:"Đắt hơn, nhưng thừa hưởng trọn bảo mật của L1."},
  {n:"Lớp DA riêng",s:"Celestia, EigenDA, hoặc lớp riêng như Mantle — rẻ hơn nhiều, đổi lại phải tin thêm một hệ nữa."}],
 where:"Base đăng blob về Ethereum. Blob rẻ đi sau EIP-4844 là lý do phí Base giảm mạnh."},

"*::alchemy":{
 role:"Nhà cung cấp RPC",
 of:"RPC / Nodes",
 what:"Alchemy là nhà cung cấp RPC lớn nhất ngành: ứng dụng gọi vào endpoint của họ để đọc trạng thái chuỗi và gửi giao dịch, kèm bộ công cụ theo dõi, webhook và API dữ liệu nâng cao.",
 special:"Gói miễn phí rộng nên rất nhiều dự án khởi đầu ở đây rồi ở lại luôn. Đó không phải tình cờ mà là mô hình kinh doanh — và cũng là lý do một phần lớn lưu lượng của cả ngành đi qua vài công ty.",
 compare:[{n:"Alchemy",s:"Nhiều công cụ nhất, hợp đội cần theo dõi và gỡ lỗi sâu."},{n:"Tự chạy node",s:"Không phụ thuộc ai, nhưng tốn máy và công bảo trì."}],
 where:"Có mặt trên Base, Ethereum và hàng chục chuỗi khác."},

"*::quicknode":{
 role:"Nhà cung cấp RPC",
 of:"RPC / Nodes",
 what:"QuickNode bán endpoint riêng cho từng khách với điểm mạnh là độ trễ thấp và khả năng chịu tải cao.",
 special:"Hợp ứng dụng nhạy thời gian — sàn giao dịch, bot, game. Chênh lệch vài chục mili giây ở khâu này đủ đổi kết quả một lệnh.",
 where:"Đa chuỗi, trong đó có Base."},

"base::base rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"Endpoint miễn phí do chính Base vận hành, ai cũng gọi được mà không cần đăng ký.",
 special:"Có giới hạn tần suất nên hợp thử nghiệm và học, không hợp sản phẩm thật. Nhưng sự tồn tại của nó quan trọng: nếu không có endpoint công cộng thì muốn đọc chuỗi cũng phải xin phép một công ty.",
 where:"mainnet.base.org — do Base công bố."},

"*::ankr":{
 role:"RPC phân tán",
 of:"RPC / Nodes",
 what:"Ankr định tuyến yêu cầu qua nhiều nhà vận hành node độc lập thay vì một trung tâm duy nhất.",
 special:"Giảm được rủi ro một nhà cung cấp sập kéo cả ứng dụng chết theo, đổi lại chất lượng không đều giữa các node."},

"*::the graph":{
 role:"Mạng đánh chỉ mục",
 of:"Indexer",
 what:"The Graph để lập trình viên viết subgraph — mô tả cần theo dõi sự kiện nào — rồi mạng lưới indexer chạy và phục vụ truy vấn bằng GraphQL.",
 special:"Điểm đáng chú ý là nó phi tập trung hoá cả khâu đọc dữ liệu, thứ mà phần lớn hệ sinh thái vẫn để một công ty nắm.",
 where:"Có subgraph cho Base và hầu hết chuỗi EVM."},

"*::goldsky":{
 role:"Đường ống dữ liệu",
 of:"Indexer",
 what:"Goldsky đẩy dữ liệu chuỗi theo thời gian thực thẳng vào kho dữ liệu của bạn — Postgres, BigQuery — thay vì bắt bạn truy vấn qua API của họ.",
 special:"Hợp đội đã có sẵn hạ tầng phân tích và muốn dữ liệu onchain nằm chung chỗ với dữ liệu kinh doanh."},

"*::envio":{
 role:"Bộ chỉ mục tốc độ cao",
 of:"Indexer",
 what:"Envio tối ưu cho việc dựng lại lịch sử lớn thật nhanh — thứ mà indexer đời cũ làm mất nhiều giờ."},

"base::basescan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Basescan là explorer chính thức của Base, do đội Etherscan vận hành. Tra giao dịch, khối, địa chỉ, và xem mã nguồn hợp đồng đã xác minh.",
 special:"Chức năng xác minh mã nguồn quan trọng hơn vẻ ngoài: nó là cách duy nhất người thường kiểm tra được hợp đồng mình sắp ký có đúng như dự án công bố hay không."},

"*::blockscout":{
 role:"Explorer mã nguồn mở",
 of:"Explorer",
 what:"Blockscout là explorer mã nguồn mở, ai cũng tự chạy được một bản.",
 special:"Quan trọng về nguyên tắc: nếu chỉ có một explorer đóng, thì việc tra cứu công khai lại phụ thuộc vào một công ty. Chuỗi mở mà cửa tra cứu đóng thì tính công khai chỉ còn trên giấy.",
 compare:[{n:"Basescan",s:"Đầy đủ tính năng nhất, nhưng là dịch vụ đóng."},{n:"Blockscout",s:"Tự chạy được, dữ liệu không phụ thuộc ai."}]},

"*::chainlink":{
 role:"Mạng oracle",
 of:"Oracle",
 what:"Chainlink dùng mạng node độc lập tổng hợp giá từ nhiều nguồn rồi đẩy lên chuỗi khi giá lệch quá ngưỡng.",
 special:"Là nguồn giá của phần lớn giao thức cho vay. Hệ quả ít ai để ý: rất nhiều tiền trong DeFi cùng phụ thuộc vào một mạng oracle — đó là rủi ro hệ thống, không phải rủi ro của riêng dự án nào.",
 where:"Có mặt trên Base và gần như mọi chuỗi lớn."},

"*::pyth network":{
 role:"Oracle giá thời gian thực",
 of:"Oracle",
 what:"Pyth lấy giá thẳng từ các nhà tạo lập thị trường và sàn, rồi nạp lên chuỗi theo yêu cầu thay vì đẩy liên tục.",
 special:"Cách nạp theo yêu cầu rẻ hơn nhiều và cập nhật nhanh hơn, nhưng đẩy trách nhiệm sang ứng dụng: gọi sai nhịp thì đọc phải giá cũ.",
 compare:[{n:"Chainlink",s:"Đẩy định kỳ, ổn định, phí ghi cao hơn."},{n:"Pyth",s:"Nạp theo yêu cầu, nhanh và rẻ, phức tạp hơn khi tích hợp."}]},

"*::redstone":{
 role:"Oracle nạp theo yêu cầu",
 of:"Oracle",
 what:"RedStone gói dữ liệu giá kèm ngay trong giao dịch của người dùng, nên không phải trả phí ghi liên tục lên chuỗi."},

"base::base bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Base Bridge là bộ hợp đồng cầu nằm trên Ethereum, do chính giao thức rollup định nghĩa — không phải dịch vụ của bên thứ ba.",
 special:"Đây là cầu duy nhất mà độ an toàn ngang với chính Base. Đổi lại, rút về Ethereum phải chờ hết thời hạn khiếu kiện, khoảng bảy ngày."},

"*::superbridge":{
 role:"Giao diện cầu chung",
 of:"Cầu chính thức",
 what:"Superbridge là giao diện dùng chung cho các chuỗi OP Stack. Bên dưới nó vẫn gọi vào cầu chính thức, chỉ gom trải nghiệm lại một chỗ.",
 special:"Đừng nhầm giao diện với cầu. Superbridge sập thì người dùng vẫn rút được qua hợp đồng gốc — đó là khác biệt cốt lõi giữa lớp giao diện và lớp giao thức."},

"*::layerzero":{
 role:"Lớp nhắn tin xuyên chuỗi",
 of:"Interoperability",
 what:"LayerZero cho hợp đồng ở hai chuỗi khác nhau gửi thông điệp cho nhau, thông qua một cặp thành phần xác minh do ứng dụng tự chọn cấu hình.",
 special:"Mô hình tin cậy nằm ở cấu hình chứ không cố định — hai ứng dụng cùng dùng LayerZero có thể có mức an toàn khác nhau. Đây là chỗ người dùng gần như không bao giờ kiểm tra."},

"*::wormhole":{
 role:"Mạng truyền thông điệp",
 of:"Interoperability",
 what:"Wormhole dùng một nhóm node guardian ký xác nhận sự kiện ở chuỗi nguồn để chuỗi đích tin theo. Phủ được cả chuỗi ngoài EVM như Solana và Sui.",
 special:"Từng bị tấn công mất khoảng 320 triệu đô năm 2022 do lỗi xác minh chữ ký. Nhắc lại không phải để chê — mà vì lịch sử cầu nối là phần lịch sử đắt nhất của ngành này."},

"*::chainlink ccip":{
 role:"Đường truyền liên chuỗi",
 of:"Interoperability",
 what:"CCIP dùng lại mạng oracle sẵn có của Chainlink để chuyển token và thông điệp giữa các chuỗi, hướng tới khách tổ chức."},

"*::across":{
 role:"Cầu ứng vốn trước",
 of:"Interoperability",
 what:"Across để người chuyển nhận tiền ở chuỗi đích gần như tức thì, nhờ có bên ứng vốn trước rồi tự đi đòi lại qua cầu chính thức.",
 special:"Đây là cách người ta lách thời gian chờ bảy ngày: không phải rút nhanh hơn, mà là có người chịu chờ thay và lấy phí."},

"base::onchainkit":{
 role:"Bộ component của Coinbase",
 of:"Hạ tầng lập trình",
 what:"OnchainKit là bộ component React sẵn dùng để gắn ví, thanh toán, danh tính và giao dịch vào ứng dụng chỉ trong vài dòng.",
 special:"Đây là một phần lý do hệ ứng dụng Base lớn nhanh: Coinbase không chỉ làm chuỗi mà làm cả bộ đồ nghề, rút thời gian dựng sản phẩm từ vài tuần xuống vài ngày."},

"*::viem / wagmi":{
 role:"Thư viện chuẩn",
 of:"Hạ tầng lập trình",
 what:"viem là thư viện TypeScript để nói chuyện với chuỗi EVM, wagmi là lớp React dựng trên nó. Đây là bộ đôi mặc định của phần lớn ứng dụng mới.",
 special:"Chúng thay thế ethers.js và web3.js đời cũ ở các dự án mới, chủ yếu nhờ gõ kiểu chặt và báo lỗi rõ."},

"*::foundry":{
 role:"Bộ công cụ hợp đồng",
 of:"Hạ tầng lập trình",
 what:"Foundry viết bằng Rust, cho phép test hợp đồng bằng chính Solidity thay vì JavaScript, và chạy rất nhanh."},

"*::op-node":{
 role:"Thành phần OP Stack",
 of:"Sequencer",
 what:"op-node là bộ não điều phối: nó đọc dữ liệu từ Ethereum để suy ra chuỗi Base phải như thế nào, và khi chạy ở chế độ sequencer thì nó quyết định thứ tự giao dịch.",
 special:"Cơ chế suy ra chuỗi từ dữ liệu L1 chính là thứ khiến rollup không phụ thuộc vào lời hứa của người vận hành: ai cũng chạy được op-node và tự dựng lại toàn bộ Base."},

"*::op-geth":{
 role:"Thành phần OP Stack",
 of:"Execution",
 what:"op-geth là bản chỉnh sửa của Geth — phần mềm node Ethereum — đảm nhận khâu thực thi giao dịch qua máy ảo EVM.",
 special:"Việc dùng lại Geth thay vì viết mới là lý do hợp đồng Ethereum chạy được trên Base gần như nguyên trạng."},

"*::op-batcher":{
 role:"Thành phần OP Stack",
 of:"Batch / block production",
 what:"op-batcher gom các khối Base, nén lại và gửi lên Ethereum dưới dạng blob.",
 special:"Đây là thành phần trực tiếp tiêu tiền: mỗi lần gửi là một khoản phí trả cho Ethereum. Nén tốt hơn nghĩa là phí người dùng rẻ hơn."},

"*::op-proposer":{
 role:"Thành phần OP Stack",
 of:"L1 settlement",
 what:"op-proposer đăng state root — bản tóm tắt trạng thái Base — lên Ethereum để làm mốc cho việc rút tài sản và cho fault proof.",
 special:"Nếu nó đăng một state root sai, hệ thống không tự phát hiện. Cannon và op-challenger mới là thứ bắt lỗi đó."},

"*::cannon":{
 role:"Máy ảo phân xử",
 of:"Fault proofs",
 what:"Cannon là máy ảo cho phép chạy lại đúng một bước tính toán đang tranh chấp ngay trên Ethereum, để trọng tài phân xử ai đúng.",
 special:"Ý tưởng cốt lõi: không cần chạy lại cả chuỗi trên Ethereum, chỉ cần thu hẹp tranh chấp xuống một bước rồi chạy đúng bước đó. Đó là thứ khiến fault proof khả thi về chi phí."},

"*::op-challenger":{
 role:"Người tố cáo tự động",
 of:"Fault proofs",
 what:"op-challenger là phần mềm theo dõi các state root được đăng lên và tự động khởi kiện nếu thấy sai.",
 special:"Fault proof chỉ có tác dụng khi thật sự có người canh. Nếu không ai chạy challenger thì cơ chế tồn tại trên giấy mà không ai bấm nút."},

"*::eip-4844 blob":{
 role:"Chuẩn dữ liệu",
 of:"Data availability",
 what:"EIP-4844 tạo ra một loại chỗ chứa riêng trên Ethereum gọi là blob, rẻ hơn nhiều so với ghi dữ liệu vào calldata, và tự xoá sau khoảng hai tuần.",
 special:"Đây là thay đổi kéo phí L2 xuống mạnh nhất từ trước tới nay. Việc blob tự xoá sau hai tuần là chủ ý: đủ lâu để ai muốn cũng tải về được, không đủ lâu để bắt Ethereum lưu trữ vĩnh viễn."},

"*::circle":{
 role:"Đơn vị phát hành",
 of:"USDC",
 what:"Circle phát hành USDC, giữ khoản dự trữ đô la tương ứng và công bố báo cáo kiểm toán định kỳ.",
 special:"USDC là stablecoin có công ty đứng sau. Nghĩa là nó ổn định nhờ pháp lý và dự trữ thật, nhưng cũng nghĩa là Circle có thể đóng băng một địa chỉ. Đó là đánh đổi, không phải khuyết điểm giấu được."},

"base::coinbase":{
 role:"Công ty đứng sau Base",
 of:"USDC",
 what:"Coinbase vừa là đơn vị xây và vận hành Base, vừa là cửa quy đổi tiền pháp định lớn nhất cho hệ sinh thái này, vừa đồng phát triển USDC cùng Circle.",
 special:"Ba vai cùng lúc là điểm mạnh về phân phối và là điểm yếu về tập trung hoá. Sequencer, cổng vào và cửa quy đổi đều nằm ở một công ty — Base công khai lộ trình phi tập trung hoá, nhưng hiện tại thì đúng là như vậy."},

"base::base account":{
 role:"Tài khoản hợp đồng",
 of:"Identity / Account",
 what:"Base Account là tài khoản dạng hợp đồng đại diện cho người dùng, đăng nhập bằng passkey trên thiết bị thay vì cụm từ khôi phục.",
 special:"Bỏ được cụm mười hai từ là bỏ được rào cản lớn nhất với người mới, và bỏ luôn kiểu mất sạch vì chép nhầm một chữ."},

"base::basenames":{
 role:"Tên miền của Base",
 of:"Identity / Account",
 what:"Basenames gắn một cái tên .base.eth vào tài khoản, thay cho chuỗi ký tự dài."},

"*::erc-4337":{
 role:"Chuẩn tài khoản trừu tượng",
 of:"Identity / Account",
 what:"ERC-4337 là chuẩn chung cho phép tài khoản là hợp đồng: đặt hạn mức chi tiêu, cho người khác trả phí hộ, khôi phục bằng nhiều người thân.",
 special:"Là chuẩn chung của cả hệ Ethereum chứ không riêng Base — nghĩa là ví dựng theo chuẩn này mang được sang chuỗi khác."},

"*::privy":{
 role:"Ví nhúng",
 of:"Identity / Account",
 what:"Privy tạo ví ngay trong ứng dụng từ email hoặc tài khoản mạng xã hội, khoá được chia mảnh để không ai giữ trọn.",
 special:"Hợp ứng dụng muốn người dùng vào được ngay mà chưa cần biết crypto là gì. Đổi lại người dùng phụ thuộc thêm một dịch vụ nữa."},

"*::coinbase wallet":{
 role:"Ví",
 of:"Wallet",
 what:"Ví tự giữ khoá của Coinbase, nối thẳng với tài khoản sàn để nạp rút dễ, và hỗ trợ ví thông minh."},

"*::metamask":{
 role:"Ví",
 of:"Wallet",
 what:"Ví trình duyệt phổ biến nhất ngành, dùng khoá riêng truyền thống với cụm từ khôi phục.",
 special:"Vẫn là mặc định của người dùng cũ, nhưng chính mô hình cụm từ khôi phục là thứ ví thông minh sinh ra để thay thế."},

"*::rainbow":{
 role:"Ví",
 of:"Wallet",
 what:"Ví chú trọng trải nghiệm và giao diện, mã nguồn mở."},

"*::rabby":{
 role:"Ví",
 of:"Wallet",
 what:"Ví cho người dùng nhiều chuỗi cùng lúc, mạnh ở chỗ mô phỏng trước hậu quả của giao dịch trước khi ký.",
 special:"Tính năng mô phỏng trước khi ký là thứ chặn được phần lớn giao dịch lừa đảo — đáng ra phải là mặc định ở mọi ví."},

"base::morpho vaults":{
 role:"Quỹ tự động",
 of:"Vaults",
 what:"Vault xây trên Morpho, do một bên quản lý chọn chiến lược và chịu trách nhiệm đặt tham số rủi ro.",
 special:"Người gửi thấy con số lợi suất nhưng thường không thấy ai đang chọn tham số rủi ro cho mình. Đó là câu nên hỏi đầu tiên."},

"*::beefy":{
 role:"Quỹ tự động cộng dồn",
 of:"Vaults",
 what:"Beefy tự động thu lợi suất và tái đầu tư vào vốn gốc, chạy trên nhiều chuỗi."},

"*::opensea":{
 role:"Chợ NFT",
 of:"NFT & Collectibles",
 what:"Chợ giao dịch NFT lâu đời nhất, có hỗ trợ Base."},

"base::coinbase commerce":{
 role:"Cổng thanh toán",
 of:"Commerce",
 what:"Cổng cho phép cửa hàng nhận thanh toán bằng stablecoin và tự quy đổi, không phải tự xử lý phần onchain."},

"base::shopify":{
 role:"Nền tảng thương mại",
 of:"Commerce",
 what:"Shopify hỗ trợ người bán nhận thanh toán bằng USDC trên Base.",
 special:"Đây là loại tích hợp đáng chú ý hơn phần lớn tin tức trong ngành: người mua không cần biết mình đang dùng blockchain, chỉ thấy một cách trả tiền rẻ hơn."},

"arbitrum one::arbitrum nitro + orbit":{
 role:"Bộ quy chuẩn xây thành phố L2",
 of:"",
 what:"Nitro là bộ máy rollup của Offchain Labs: chạy nhân Geth để thực thi, rồi biên dịch phần lõi sang WASM để khi có tranh chấp thì chạy lại được ngay trên Ethereum. Orbit là quyền dùng lại bản vẽ đó để dựng đặc khu L3 riêng.",
 special:"Khác OP Stack ở khâu phân xử. OP Stack thu hẹp tranh chấp rồi chạy một bước trên Ethereum. Nitro cho hai bên hỏi đáp nhiều vòng để khoanh vùng trước, nên chi phí phân xử thấp hơn nhưng quy trình dài hơn. Không có bản nào rõ ràng tốt hơn — chúng chọn khác nhau ở chỗ đặt độ phức tạp.",
 compare:[{n:"OP Stack",s:"Nhiều thành phố dùng chung, có Superchain và chuẩn liên thông sẵn."},{n:"Arbitrum Nitro",s:"Hiệu năng thực thi tốt, có Stylus cho Rust và C, hệ Orbit riêng."}],
 where:"Là mã nguồn mở. Arbitrum One, Nova và hàng chục chuỗi Orbit cùng dùng."},

"optimism::op stack":{
 role:"Bộ quy chuẩn xây thành phố L2",
 of:"",
 what:"OP Stack là bộ mã nguồn mở và tiêu chuẩn dựng rollup do Optimism viết ra: sequencer, đăng dữ liệu, cầu nối, fault proof đều theo một khuôn.",
 special:"Điểm đáng nói là Optimism cho không bản vẽ này. Base — thành phố lớn nhất về người dùng — được xây bằng chính nó. Một thành phố tự nguyện biến mình thành tiêu chuẩn thay vì giữ độc quyền công nghệ, đó là lựa chọn chiến lược hiếm thấy.",
 where:"Base, Mode, Ink, Zora, opBNB và nhiều chuỗi khác đều dựng từ đây."},

"opbnb::op stack (ban bnb)":{
 role:"Bộ quy chuẩn xây thành phố L2",
 of:"",
 what:"opBNB dùng lại nguyên bản vẽ OP Stack của Optimism, nhưng đổi nơi cắm chân: dữ liệu và quyết toán đi về BNB Smart Chain thay vì Ethereum.",
 special:"Đây là chỗ phải đọc kỹ nhất của cả thành phố này. Cùng một bản vẽ nhưng cắm vào nền móng khác thì độ an toàn khác hẳn: BSC có vài chục validator, Ethereum có hơn một triệu. Bản vẽ giống nhau không có nghĩa là an toàn giống nhau.",
 where:"Là mã nguồn mở của Optimism, BNB Chain chỉnh lại cho hệ của mình."},

"moonbeam::polkadot sdk (substrate)":{
 role:"Bộ quy chuẩn dựng một bang",
 of:"",
 what:"Substrate là bộ khung dựng chuỗi có runtime chạy WASM, nên nâng cấp giao thức không cần chia tách mạng. Moonbeam thêm lớp EVM lên trên để hợp đồng Ethereum chạy được.",
 special:"Đây không phải bản vẽ rollup. Nó dựng ra một chuỗi có đồng thuận riêng, rồi chuỗi đó thuê bảo mật của relay chain. Khác biệt căn bản: rollup chứng minh mình đúng bằng dữ liệu công khai; parachain được bảo vệ bằng việc validator cấp trên kiểm chứng hộ.",
 where:"Là bộ khung chung của cả hệ Polkadot và Kusama."},

"osmosis::cosmos sdk + cometbft":{
 role:"Bộ quy chuẩn lập một quốc gia",
 of:"",
 what:"Cosmos SDK lắp sẵn các module tiền tệ, staking, quản trị; CometBFT lo phần đồng thuận. Ghép lại là một quốc gia đầy đủ chủ quyền chỉ trong vài tuần.",
 special:"Khác hai bản vẽ kia ở chỗ căn bản nhất: nó không dựng ra thứ phụ thuộc ai. Không có chuỗi mẹ, không có nơi quyết toán, không có ai đỡ khi sập. Chủ quyền tuyệt đối và rủi ro tuyệt đối là hai mặt của cùng một lựa chọn.",
 where:"Hàng trăm chuỗi dùng, trong đó có Osmosis, Injective, dYdX Chain, Celestia."},

"arbitrum one::fraud proofs":{
 role:"Bộ máy — cơ chế phân xử",
 of:"",
 what:"Khi có tranh chấp về kết quả, hai bên không chạy lại cả chuỗi. Họ hỏi đáp nhiều vòng để khoanh dần xuống đúng một bước tính toán, rồi chỉ bước đó được chạy trên Ethereum để phân xử.",
 special:"BoLD là bản nâng cấp cho phép bất kỳ ai tham gia tố cáo chứ không giới hạn ở danh sách được duyệt trước. Đây là tiêu chí quan trọng nhất khi đánh giá độ trưởng thành của một rollup: cơ chế có mở cho mọi người hay không."},

"moonbeam::collator":{
 role:"Bộ máy — người sản xuất khối",
 of:"",
 what:"Collator gom giao dịch của bang thành khối ứng viên rồi đưa lên cho validator relay chain kiểm chứng. Nó không có quyền quyết định cuối cùng.",
 special:"Khác sequencer của rollup ở chỗ quyền lực nhỏ hơn nhiều: collator gian dối thì validator relay chain gạt khối đi ngay, không cần ai tố cáo và không phải chờ bảy ngày."},

"moonbeam::shared security":{
 role:"Bộ máy — an ninh chung",
 of:"",
 what:"Bang không tự tuyển validator. Bảo mật đến từ relay chain Polkadot, và bang trả cho việc đó bằng coretime.",
 special:"Đây là khác biệt lớn nhất giữa Polkadot và Cosmos. Ở Polkadot, một bang nhỏ vẫn được bảo vệ ngang bang lớn. Ở Cosmos, nước nhỏ phải tự nuôi validator của mình — tự do hơn nhưng mong manh hơn."},

"osmosis::chủ quyền":{
 role:"Bộ máy — không quyết toán ở đâu cả",
 of:"",
 what:"Osmosis không đăng dữ liệu về chuỗi nào và không thuê bảo mật của ai. Validator của chính nó là lớp bảo vệ duy nhất.",
 special:"Đây là lý do không nên gọi Osmosis là L2. Nó nằm trong mục thành phố của bản đồ này vì cùng một tầng chức năng, nhưng về bản chất nó là một quốc gia. Nếu validator của nó cấu kết thì không có triều đình nào phủ quyết được."},

"osmosis::instant finality":{
 role:"Bộ máy — chốt tức thì",
 of:"",
 what:"Khối được chốt ngay khi đủ hai phần ba validator bỏ phiếu. Không có khái niệm chờ xác nhận thêm, không có chuyện đảo khối.",
 special:"Đối lập hẳn với rollup: Base phải chờ khoảng bảy ngày mới rút được về Ethereum. Osmosis chốt trong vài giây. Đổi lại, cái chốt đó chỉ chắc bằng chính bộ validator của nó."},

"opbnb::data availability":{
 role:"Bộ máy — dữ liệu công khai",
 of:"",
 what:"Dữ liệu giao dịch của opBNB được đăng về BNB Smart Chain, không phải Ethereum.",
 special:"Chỗ này quyết định phần lớn hồ sơ rủi ro của opBNB. Rẻ hơn nhiều là thật. Nhưng ai muốn dựng lại trạng thái opBNB thì phải tin BSC — chuỗi có vài chục validator do một hệ sinh thái duy nhất chi phối."},

"*::arbiscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Arbitrum, do đội Etherscan vận hành."},

"*::optimistic etherscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Optimism, cùng nhà Etherscan."},

"*::mintscan":{
 role:"Cổng tra cứu liên chuỗi",
 of:"Explorer",
 what:"Explorer phủ hầu hết các chuỗi trong liên minh Cosmos, xem được cả luồng IBC giữa các nước."},

"*::subscan":{
 role:"Cổng tra cứu hệ Polkadot",
 of:"Explorer",
 what:"Explorer cho relay chain và mọi parachain, tra được cả tin nhắn XCM."},

"*::stylus":{
 role:"Môi trường lập trình",
 of:"Hạ tầng lập trình",
 what:"Stylus cho phép viết hợp đồng trên Arbitrum bằng Rust, C hoặc C++ rồi biên dịch sang WASM, chạy song song với EVM.",
 special:"Mở cửa cho lập trình viên ngoài giới Solidity, và những phép tính nặng rẻ hơn EVM nhiều lần."},

"*::xcm":{
 role:"Chuẩn liên thông",
 of:"Kênh nội bộ XCM",
 what:"XCM là ngôn ngữ chuẩn để các bang trong Polkadot gửi tài sản và lệnh cho nhau.",
 special:"Điểm khác cầu nối: XCM không khoá tài sản ở một hợp đồng do nhóm nào giữ. Nó là giao thức nội bộ có bảo mật của relay chain đứng sau — về mặt rủi ro thì khác hẳn một cây cầu."},

"*::ibc":{
 role:"Hiệp ước liên chuỗi",
 of:"Interoperability",
 what:"IBC cho hai chuỗi tự xác minh trạng thái của nhau bằng light client, rồi chuyển tài sản và tin nhắn mà không cần bên thứ ba giữ hộ.",
 special:"Đây là mô hình cầu nối an toàn nhất đang có trong ngành, và cũng là lý do liên minh Cosmos gần như không dính vụ mất tiền vì cầu nào lớn."},

"*::noble (usdc)":{
 role:"Nước phát hành stablecoin",
 of:"Cửa vào tài sản",
 what:"Noble là một chuỗi chuyên phát hành USDC gốc cho cả liên minh Cosmos, thay vì để mỗi nước dùng bản bọc qua cầu."},

"*::skip":{
 role:"Định tuyến liên chuỗi",
 of:"Interoperability",
 what:"Skip tìm đường đi tối ưu qua nhiều nước trong liên minh, gộp nhiều bước IBC thành một lần bấm."},

"*::keplr":{
 role:"Ví hệ Cosmos",
 of:"Wallet",
 what:"Ví chuẩn của liên minh Cosmos, quản lý hàng chục chuỗi cùng lúc và hỗ trợ IBC sẵn."},

"*::leap":{
 role:"Ví hệ Cosmos",
 of:"Wallet",
 what:"Ví di động và trình duyệt, tối ưu cho người mới vào hệ Cosmos."},

"*::talisman":{
 role:"Ví hệ Polkadot",
 of:"Wallet",
 what:"Ví hiểu cả relay chain lẫn parachain, và cả tài khoản EVM của Moonbeam."},

"*::binance web3 wallet":{
 role:"Ví trong sàn",
 of:"Wallet",
 what:"Ví nằm ngay trong ứng dụng Binance, không cần cài thêm gì.",
 special:"Cửa vào dễ nhất trong tất cả các thành phố ở bản đồ này, đổi lại nó nằm trong một sàn tập trung."},

"*::nodereal":{
 role:"Nhà cung cấp RPC",
 of:"RPC / Nodes",
 what:"NodeReal là nhà cung cấp RPC và dữ liệu chủ lực của hệ BNB, gồm cả opBNB."},

"*::binance oracle":{
 role:"Nguồn giá của hệ BNB",
 of:"Oracle",
 what:"Binance Oracle cung cấp giá cho hợp đồng trong hệ BNB, dữ liệu lấy từ chính sàn.",
 special:"Tiện và rẻ, nhưng nguồn giá và nơi vận hành cùng thuộc một công ty — đúng loại tập trung mà oracle sinh ra để tránh."},

"*::stargate":{
 role:"Cầu thanh khoản",
 of:"Interoperability",
 what:"Stargate dựng trên LayerZero, chuyên chuyển stablecoin giữa các chuỗi bằng hồ thanh khoản có sẵn ở hai đầu."},

"*::cosmwasm":{
 role:"Môi trường hợp đồng",
 of:"Hạ tầng lập trình",
 what:"CosmWasm cho viết hợp đồng bằng Rust rồi chạy trong máy ảo WASM trên các chuỗi Cosmos."},

"*::cometbft":{
 role:"Máy đồng thuận",
 of:"Validator set",
 what:"CometBFT là phần đồng thuận chạy dưới mọi chuỗi Cosmos SDK, cho chốt khối tức thì khi đủ hai phần ba phiếu."},

"*::nitro sequencer":{
 role:"Phần mềm sequencer",
 of:"Sequencer",
 what:"Thành phần của Nitro xếp thứ tự giao dịch và trả kết quả cho người dùng gần như tức thì.",
 special:"Hiện do Offchain Labs vận hành — điểm tập trung hoá lớn nhất của Arbitrum, giống Base."},

"*::batch poster":{
 role:"Thành phần Nitro",
 of:"Batch posting",
 what:"Nén và gửi lô giao dịch lên Ethereum. Mỗi lần gửi là một khoản phí trả cho Ethereum."},

"*::nitro":{
 role:"Bộ máy rollup",
 of:"Execution",
 what:"Nitro chạy nhân Geth để thực thi EVM, đồng thời biên dịch phần lõi sang WASM để phân xử tranh chấp được."},

"*::arbos":{
 role:"Hệ điều hành của chuỗi",
 of:"Execution",
 what:"ArbOS là lớp quản lý phí, gas và giao tiếp với Ethereum bên trong Nitro."},

"*::bold":{
 role:"Cơ chế phân xử mở",
 of:"Fraud proofs",
 what:"BoLD cho phép bất kỳ ai tham gia tố cáo kết quả sai, thay vì giới hạn ở danh sách được duyệt trước.",
 special:"Đây là tiêu chí quan trọng nhất khi đánh giá độ trưởng thành của rollup: cơ chế có mở cho mọi người không."},

"*::wavm":{
 role:"Máy ảo phân xử",
 of:"Fraud proofs",
 what:"Bản WASM dùng để chạy lại đúng một bước tính toán đang tranh chấp ngay trên Ethereum."},

"*::infura":{
 role:"Nhà cung cấp RPC",
 of:"RPC / Nodes",
 what:"Cổng RPC lâu đời của ConsenSys, mặc định của nhiều ví trong đó có MetaMask."},

"*::arbitrum bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức nằm trên Ethereum, do kiến trúc rollup định nghĩa.",
 special:"Rút về Ethereum phải chờ hết thời hạn tranh chấp, khoảng bảy ngày."},

"*::ens":{
 role:"Tên miền onchain",
 of:"Identity / Account",
 what:"Tên người đọc được thay cho địa chỉ ví, dùng chung cho cả hệ Ethereum và các L2."},

"*::op labs rpc":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do OP Labs vận hành, có giới hạn tần suất."},

"*::optimism bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Cầu chính thức giữa Ethereum và Optimism, cùng bản vẽ với cầu của Base."},

"*::superchain interop":{
 role:"Chuẩn liên thông nội bộ",
 of:"Interoperability",
 what:"Cho các thành phố cùng OP Stack đi lại với nhau mà không phải qua cầu bên thứ ba.",
 special:"Điểm mạnh của việc dùng chung bản vẽ: giữa Base và Optimism là đường nội bộ, không phải cầu."},

"*::op stack sdk":{
 role:"Bộ đồ nghề dựng chuỗi",
 of:"Hạ tầng lập trình",
 what:"Bộ công cụ để dựng hẳn một thành phố L2 mới từ bản vẽ OP Stack."},

"*::eas attestations":{
 role:"Chuẩn ghi nhận xác thực",
 of:"Identity / Account",
 what:"Cho phép bất kỳ ai ký một lời chứng thực về địa chỉ khác và ghi lên chuỗi.",
 special:"Là nền của hệ danh tiếng mà Optimism dùng để chấm Retro Funding."},

"*::bnb greenfield":{
 role:"Chuỗi lưu trữ",
 of:"Data availability",
 what:"Chuỗi riêng trong hệ BNB chuyên lưu dữ liệu lớn, quyền truy cập điều khiển bằng hợp đồng."},

"*::opbnb rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do BNB Chain vận hành."},

"*::opbnbscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer của opBNB."},

"*::opbnb bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Cầu chính thức giữa BNB Smart Chain và opBNB."},

"*::celer cbridge":{
 role:"Cầu nhiều chuỗi",
 of:"Interoperability",
 what:"Cầu phủ hàng chục chuỗi, phí thấp và thời gian ngắn."},

"*::bnb chain sdk":{
 role:"Bộ đồ nghề",
 of:"Hạ tầng lập trình",
 what:"Thư viện riêng cho opBNB và Greenfield."},

"*::tether":{
 role:"Đơn vị phát hành",
 of:"USDT / FDUSD",
 what:"Tether phát hành USDT — stablecoin lớn nhất ngành theo quy mô lưu hành.",
 special:"Minh bạch dự trữ kém hơn Circle, đổi lại phủ rộng hơn nhiều, nhất là ở châu Á."},

"*::first digital":{
 role:"Đơn vị phát hành",
 of:"USDT / FDUSD",
 what:"First Digital phát hành FDUSD, stablecoin gắn với hệ Binance."},

"*::space id":{
 role:"Dịch vụ tên miền",
 of:"Identity / Account",
 what:"Tên miền onchain cho hệ BNB và vài chuỗi khác."},

"*::trust wallet":{
 role:"Ví",
 of:"Wallet",
 what:"Ví di động đa chuỗi thuộc hệ Binance, mạnh ở thị trường châu Á."},

"*::moonbeam collators":{
 role:"Người sản xuất khối",
 of:"Collator",
 what:"Nhóm collator gom giao dịch của bang thành khối ứng viên rồi đưa lên relay chain."},

"*::frontier":{
 role:"Lớp EVM trên Substrate",
 of:"Execution",
 what:"Frontier là bộ module mang máy ảo EVM vào một chuỗi Substrate.",
 special:"Đây chính là thứ khiến Moonbeam làm được vai trò phiên dịch giữa hai thế giới."},

"*::substrate runtime":{
 role:"Runtime WASM",
 of:"Execution",
 what:"Phần logic của chuỗi chạy dưới dạng WASM, nên nâng cấp được mà không cần chia tách mạng."},

"*::polkadot validators":{
 role:"Validator relay chain",
 of:"Relay validation",
 what:"Bộ validator chung của cả đế chế, kiểm chứng khối do collator các bang đưa lên."},

"*::agile coretime":{
 role:"Cơ chế thuê năng lực",
 of:"Coretime",
 what:"Bang mua thời gian xử lý theo khối thời gian thay vì đấu giá khoá vốn hai năm như trước."},

"*::endpoint cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do dự án hoặc cộng đồng vận hành, có giới hạn tần suất."},

"*::onfinality":{
 role:"Nhà cung cấp RPC",
 of:"RPC / Nodes",
 what:"Dịch vụ RPC và node cho hệ Polkadot và nhiều chuỗi khác."},

"*::dwellir":{
 role:"Nhà cung cấp RPC",
 of:"RPC / Nodes",
 what:"Nhà vận hành node chuyên cho hệ Polkadot."},

"*::subsquid":{
 role:"Bộ chỉ mục",
 of:"Indexer",
 what:"Đánh chỉ mục dữ liệu nhiều bang cùng lúc trong hệ Polkadot."},

"*::subquery":{
 role:"Bộ khung chỉ mục",
 of:"Indexer",
 what:"Bộ khung tự dựng chỉ mục cho chuỗi Substrate và nhiều hệ khác."},

"*::moonscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer cho phần EVM của Moonbeam, giao diện quen thuộc với người dùng Ethereum."},

"*::acurast":{
 role:"Oracle phi tập trung",
 of:"Oracle",
 what:"Mạng đưa dữ liệu ngoài đời vào hợp đồng, chạy tính toán trên thiết bị di động nhàn rỗi."},

"*::snowbridge":{
 role:"Cầu không cần tin cậy",
 of:"Interoperability",
 what:"Cầu do Polkadot xây sang Ethereum, xác minh bằng chính đồng thuận hai bên chứ không qua nhóm người ký."},

"*::hyperbridge":{
 role:"Cầu dựa trên bằng chứng",
 of:"Interoperability",
 what:"Cầu xác minh bằng bằng chứng đồng thuận thay vì tin một nhóm vận hành."},

"*::polkadot.js":{
 role:"Thư viện và giao diện gốc",
 of:"Hạ tầng lập trình",
 what:"Bộ thư viện JavaScript và giao diện web để tương tác với mọi chuỗi Substrate."},

"*::people chain":{
 role:"Chuỗi hệ thống danh tính",
 of:"Identity / Account",
 what:"Chuỗi riêng trong Polkadot chuyên giữ danh tính onchain của người dùng."},

"*::subwallet":{
 role:"Ví hệ Polkadot",
 of:"Wallet",
 what:"Ví đa parachain do một đội Việt Nam phát triển."},

"*::nova wallet":{
 role:"Ví hệ Polkadot",
 of:"Wallet",
 what:"Ví di động mạnh về staking và bỏ phiếu quản trị ngay trong ứng dụng."},

"*::node cong dong":{
 role:"Node cộng đồng",
 of:"RPC / Nodes",
 what:"Endpoint do chính validator và thành viên cộng đồng vận hành, không thuộc công ty nào."},

"*::polkachu":{
 role:"Nhà vận hành node",
 of:"RPC / Nodes",
 what:"Nhà cung cấp endpoint và dịch vụ node quen thuộc trong hệ Cosmos."},

"*::numia":{
 role:"Dịch vụ dữ liệu",
 of:"Indexer",
 what:"Đánh chỉ mục và phân tích dữ liệu cho các chuỗi Cosmos."},

"*::sqd":{
 role:"Bộ chỉ mục",
 of:"Indexer",
 what:"Mạng dữ liệu phi tập trung, tiền thân là Subsquid."},

"*::celatone":{
 role:"Cổng tra cứu hợp đồng",
 of:"Explorer",
 what:"Explorer chuyên cho hợp đồng CosmWasm, xem và gọi hợp đồng ngay trên giao diện."},

"*::oracle trong giao thuc":{
 role:"Nguồn giá nội bộ",
 of:"Oracle",
 what:"Osmosis tính giá từ chính các hồ thanh khoản của mình thay vì lấy từ ngoài.",
 special:"Rẻ và không phụ thuộc ai, nhưng dễ bị thao túng hơn nếu hồ thanh khoản mỏng."},

"*::axelar":{
 role:"Mạng định tuyến liên chuỗi",
 of:"Interoperability",
 what:"Đưa tài sản từ hệ EVM vào liên minh Cosmos và ngược lại."},

"*::skip go":{
 role:"Bộ định tuyến giao dịch",
 of:"Cửa vào tài sản",
 what:"Gộp nhiều bước cầu và hoán đổi thành một lần bấm cho người dùng."},

"*::cosmos sdk":{
 role:"Bộ khung dựng chuỗi",
 of:"Hạ tầng lập trình",
 what:"Bộ khung lắp sẵn module tiền tệ, staking và quản trị để dựng một chuỗi độc lập."},

"*::keplr sdk":{
 role:"Bộ đồ nghề ví",
 of:"Hạ tầng lập trình",
 what:"Thư viện để ứng dụng nối với ví Keplr và các chuỗi Cosmos."},

"*::interchain accounts":{
 role:"Chuẩn tài khoản liên chuỗi",
 of:"Identity / Account",
 what:"Cho phép một chuỗi điều khiển tài khoản của mình đặt ở chuỗi khác qua IBC."},

"*::.osmo names":{
 role:"Dịch vụ tên miền",
 of:"Identity / Account",
 what:"Tên đọc được gắn vào địa chỉ trong hệ Osmosis."},

"*::ledger":{
 role:"Ví cứng",
 of:"Wallet",
 what:"Thiết bị giữ khoá ngoại tuyến, hỗ trợ phần lớn chuỗi trong bản đồ này."},

"*::arbitrum rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do Arbitrum vận hành, có giới hạn tần suất."},

"*::boojum":{
 role:"Hệ chứng minh",
 of:"Prover",
 what:"Hệ chứng minh của zkSync, thiết kế để chạy được trên card đồ hoạ phổ thông thay vì phải có máy chuyên dụng.",
 special:"Cho phép nhiều bên cùng sinh bằng chứng — bước cần thiết để khâu này không nằm trong tay một công ty."},

"*::stark proofs":{
 role:"Hệ chứng minh",
 of:"Prover",
 what:"Loại bằng chứng không cần buổi thiết lập tin cậy ban đầu, và mở rộng tốt khi lô giao dịch càng lớn.",
 special:"Không cần thiết lập tin cậy là ưu thế thật: không có khoảnh khắc nào mà một nhóm người nắm bí mật có thể phá cả hệ."},

"*::sharp":{
 role:"Dịch vụ chứng minh chung",
 of:"Prover",
 what:"Dịch vụ gộp nhiều lô từ nhiều chuỗi lại rồi sinh một bằng chứng chung, chia chi phí cho tất cả."},

"*::zkevm circuits":{
 role:"Mạch chứng minh",
 of:"Prover",
 what:"Bộ mạch mô tả lại toàn bộ máy ảo EVM dưới dạng ràng buộc toán học — phần khó nhất của một zkEVM tương thích bytecode."},

"*::halo2":{
 role:"Hệ chứng minh",
 of:"Prover",
 what:"Hệ chứng minh không cần thiết lập tin cậy, được nhiều dự án zkEVM dùng làm nền."},

"*::linea prover":{
 role:"Hệ chứng minh",
 of:"Prover",
 what:"Hệ chứng minh của ConsenSys cho Linea."},

"*::gnark":{
 role:"Thư viện chứng minh",
 of:"Prover",
 what:"Thư viện mã nguồn mở viết bằng Go để dựng mạch và sinh bằng chứng."},

"*::plonky2":{
 role:"Hệ chứng minh",
 of:"Prover",
 what:"Hệ chứng minh nhanh của Polygon, gộp được nhiều bằng chứng thành một."},

"*::cdk prover":{
 role:"Hệ chứng minh",
 of:"Prover",
 what:"Thành phần sinh bằng chứng trong bộ khung CDK của Polygon."},

"*::uy ban kha dung du lieu":{
 role:"Nhóm giữ dữ liệu",
 of:"Data availability ngoài chuỗi",
 what:"Một nhóm được chỉ định giữ dữ liệu giao dịch và cam kết cung cấp khi có người yêu cầu.",
 special:"Đây là điểm tin cậy thêm mà rollup đầy đủ không có. Nhóm này biến mất thì không ai dựng lại được trạng thái để rút tài sản."},

"*::eigenda":{
 role:"Lớp khả dụng dữ liệu",
 of:"Data availability",
 what:"Mạng chuyên bán chỗ lưu dữ liệu cho rollup, rẻ hơn blob Ethereum nhiều lần.",
 special:"Rẻ hơn vì bảo mật đến từ tài sản đặt cọc của mạng đó, không phải từ Ethereum."},

"*::mantle da":{
 role:"Lớp khả dụng dữ liệu",
 of:"Data availability",
 what:"Lớp dữ liệu riêng của Mantle, dựng trên EigenDA."},

"*::zksync bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và zkSync, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::scroll bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Scroll, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::linea bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Linea, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::polygon zkevm bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Polygon zkEVM, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::blast bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Blast, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::mantle bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Mantle, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::metis bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Metis, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::mode bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Mode, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::immutable bridge":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Bộ hợp đồng cầu chính thức giữa Ethereum và Immutable, do kiến trúc chuỗi định nghĩa chứ không phải dịch vụ bên thứ ba."},

"*::starkgate":{
 role:"Cầu gốc của giao thức",
 of:"Cầu chính thức",
 what:"Cầu chính thức giữa Ethereum và Starknet."},

"*::omni bridge":{
 role:"Cầu do nhóm xác nhận vận hành",
 of:"Cầu chính thức",
 what:"Đường qua lại giữa Ethereum và Gnosis Chain, do một nhóm người xác nhận ký duyệt.",
 special:"Khác cầu rollup ở điểm cốt lõi: an toàn của nó phụ thuộc nhóm ký, không phụ thuộc Ethereum. Đây là mắt xích yếu nhất của Gnosis Chain."},

"*::zksync era explorer":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của zkSync Era: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::starkscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Starknet: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::voyager":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Starknet: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::scrollscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Scroll: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::lineascan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Linea: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::polygonscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của hệ Polygon: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::blastscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Blast: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::mantlescan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Mantle: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::metis explorer":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Metis: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::mode explorer":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Mode: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::gnosisscan":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Gnosis Chain: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::immutable explorer":{
 role:"Cổng tra cứu chính",
 of:"Explorer",
 what:"Explorer chính của Immutable zkEVM: tra giao dịch, khối, địa chỉ và hợp đồng đã xác minh."},

"*::zksync rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::starknet rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::scroll rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::linea rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::polygon rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::blast rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::mantle rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::metis rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::mode rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::gnosis rpc cong cong":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::immutable rpc":{
 role:"Endpoint công cộng",
 of:"RPC / Nodes",
 what:"RPC miễn phí do chính chuỗi vận hành, có giới hạn tần suất — hợp thử nghiệm hơn là sản phẩm thật."},

"*::blast api":{
 role:"Nhà cung cấp RPC",
 of:"RPC / Nodes",
 what:"Dịch vụ RPC của Bware Labs, phủ nhiều chuỗi. Không liên quan tới chuỗi Blast dù trùng tên."},

"*::apibara":{
 role:"Bộ chỉ mục",
 of:"Indexer",
 what:"Đánh chỉ mục dữ liệu Starknet theo thời gian thực."},

"*::checkpoint":{
 role:"Bộ khung chỉ mục",
 of:"Indexer",
 what:"Bộ khung dựng chỉ mục cho ứng dụng trên Starknet."},

"*::immutable api":{
 role:"Dịch vụ dữ liệu",
 of:"Indexer",
 what:"API dữ liệu cho vật phẩm, người chơi và giao dịch trên Immutable."},

"*::cairo":{
 role:"Ngôn ngữ và máy ảo",
 of:"Hạ tầng lập trình",
 what:"Ngôn ngữ thiết kế riêng cho việc sinh bằng chứng. Không tương thích EVM — code Solidity không mang sang được.",
 special:"Đây là gốc của cả canh bạc Starknet: hiệu năng chứng minh đổi lấy việc phải xây lại toàn bộ hệ công cụ."},

"*::scarb":{
 role:"Trình quản lý gói",
 of:"Hạ tầng lập trình",
 what:"Công cụ dựng và quản lý thư viện cho dự án Cairo."},

"*::starknet.js":{
 role:"Thư viện client",
 of:"Hạ tầng lập trình",
 what:"Thư viện JavaScript nối ứng dụng web với Starknet."},

"*::zksync-ethers":{
 role:"Thư viện client",
 of:"Hạ tầng lập trình",
 what:"Bản mở rộng của ethers.js cho các tính năng riêng của zkSync."},

"*::metamask sdk":{
 role:"Bộ đồ nghề ví",
 of:"Hạ tầng lập trình",
 what:"Thư viện nhúng kết nối MetaMask vào ứng dụng web và di động."},

"*::immutable sdk":{
 role:"Bộ đồ nghề game",
 of:"Hạ tầng lập trình",
 what:"Bộ công cụ để studio game gắn ví, vật phẩm và chợ vào tựa game của mình."},

"*::hardhat":{
 role:"Bộ công cụ hợp đồng",
 of:"Hạ tầng lập trình",
 what:"Bộ công cụ phát triển hợp đồng bằng JavaScript, lâu đời và phổ biến."},

"*::agglayer":{
 role:"Lớp gộp liên chuỗi",
 of:"Interoperability",
 what:"Gộp bằng chứng và thanh khoản của nhiều chuỗi trong hệ Polygon để người dùng thấy như một."},

"*::orbiter":{
 role:"Cầu chuyển nhanh",
 of:"Interoperability",
 what:"Cầu ứng vốn trước giữa các L2, chuyển trong vài phút thay vì chờ khiếu kiện."},

"*::rhino.fi":{
 role:"Cầu chuyển nhanh",
 of:"Interoperability",
 what:"Dịch vụ chuyển tài sản nhanh giữa nhiều L2."},

"*::connext":{
 role:"Cầu thanh khoản",
 of:"Interoperability",
 what:"Chuyển giá trị giữa các chuỗi dựa trên thanh khoản có sẵn ở hai đầu."},

"*::pragma":{
 role:"Oracle của Starknet",
 of:"Oracle",
 what:"Oracle gốc viết bằng Cairo, cung cấp giá cho các giao thức trên Starknet."},

"*::tai khoan truu tuong goc":{
 role:"Chuẩn tài khoản gốc",
 of:"Identity / Account",
 what:"Tài khoản trừu tượng nằm sẵn trong giao thức chứ không phải chuẩn thêm vào.",
 special:"Hệ quả thực tế: trả phí bằng token khác, cho ứng dụng trả hộ, đặt hạn mức — tất cả là mặc định chứ không phải tính năng thêm."},

"*::starknet id":{
 role:"Dịch vụ tên miền",
 of:"Identity / Account",
 what:"Tên đọc được gắn vào tài khoản Starknet."},

"*::argent":{
 role:"Ví thông minh",
 of:"Wallet",
 what:"Ví hợp đồng của Starknet: khôi phục được, đặt hạn mức được, không dùng cụm từ khôi phục."},

"*::braavos":{
 role:"Ví thông minh",
 of:"Wallet",
 what:"Ví hợp đồng của Starknet, hỗ trợ đăng nhập bằng sinh trắc học."},

"*::zerion":{
 role:"Ví và bảng theo dõi",
 of:"Wallet",
 what:"Ví kèm giao diện theo dõi danh mục trên nhiều chuỗi."},

"*::okx wallet":{
 role:"Ví đa chuỗi",
 of:"Wallet",
 what:"Ví tích hợp sàn và cầu nối, phủ nhiều chuỗi."},

"*::bybit wallet":{
 role:"Ví trong sàn",
 of:"Wallet",
 what:"Ví thuộc hệ sàn Bybit — nguồn người dùng chính của Mantle."},

"*::gnosis safe":{
 role:"Ví nhiều chữ ký",
 of:"Wallet",
 what:"Ví hợp đồng nhiều chữ ký, chuẩn giữ quỹ của phần lớn tổ chức trong ngành.",
 special:"Ra đời từ hệ Gnosis nhưng nay là hạ tầng dùng chung của cả Ethereum và mọi L2."},

"*::immutable passport":{
 role:"Tài khoản người chơi",
 of:"Identity / Account",
 what:"Đăng nhập bằng email hoặc mạng xã hội, ví được tạo ẩn phía sau.",
 special:"Đây là cách giấu blockchain kỹ nhất trong bản đồ: người chơi không cần biết ví là gì."},

"base::explorer":{
 role:"Hạ tầng — cổng tra cứu công khai",
 what:"Explorer là nơi con người tra một giao dịch, một khối, một hợp đồng hay một địa chỉ. Basescan và Blockscout là hai cái phổ biến trên Base.",
 metaphor:"Indexer là sở dữ liệu nằm trong nhà; explorer là cổng tra cứu công khai ngoài cửa. Một cái để máy đọc, một cái để người đọc.",
 chain:["Indexer thu thập và tổ chức dữ liệu","Đổ vào API và cơ sở dữ liệu","Explorer dựng giao diện lên trên","Con người tra giao dịch, khối, hợp đồng, địa chỉ"],
 special:"Đây là thứ khiến chuỗi thật sự công khai chứ không chỉ trên lý thuyết. Không có explorer thì dữ liệu vẫn mở nhưng chẳng ai kiểm tra được — công khai mà không tra được thì gần như không công khai.",
 uses:["Indexer","RPC / Nodes"],
 compare:[
  {n:"Indexer",s:"Máy đọc: biến dữ liệu thô thành API cho ứng dụng dùng."},
  {n:"Explorer",s:"Người đọc: biến dữ liệu thành trang tra cứu cho bất kỳ ai."}],
 where:"Mọi chuỗi đều có. Trên Base là Basescan và Blockscout."},

"base::cau chinh thuc":{
 role:"Hạ tầng — cửa khẩu gốc",
 what:"Cầu chính thức là đường đi lại giữa Ethereum và Base do chính giao thức rollup định nghĩa. Nó không phải một dịch vụ bên ngoài mà là một phần của kiến trúc Base.",
 metaphor:"Là cửa khẩu quốc gia có triều đình đứng sau. Khác hẳn mấy con đường tắt do tư nhân mở.",
 chain:["Khoá tài sản trong hợp đồng trên Ethereum","Base ghi nhận và mở tương ứng bên này","Muốn về thì đốt bên Base","Chờ hết thời hạn khiếu kiện rồi mở khoá ở Ethereum"],
 special:"Rút về Ethereum qua cầu này phải chờ khoảng bảy ngày, đúng bằng thời hạn fault proof. Đó là cái giá của việc không phải tin ai cả.",
 uses:["L1 settlement","Fault proofs"],
 compare:[
  {n:"Cầu chính thức",s:"An toàn ngang với chính rollup, nhưng rút chậm."},
  {n:"Cầu bên thứ ba",s:"Nhanh vì có người ứng vốn trước, đổi lại phải tin nhóm vận hành."}],
 where:"Hợp đồng cầu nằm trên Ethereum — đây là điểm phân biệt rollup thật với sidechain."},

"base::interoperability":{
 role:"Hạ tầng — nhắn tin xuyên chuỗi",
 what:"Interoperability là lớp cho hợp đồng ở Base nói chuyện với chuỗi hoặc ứng dụng khác — LayerZero, Wormhole, Chainlink CCIP, và trong nhóm OP Stack là chuẩn liên thông của Superchain.",
 metaphor:"Là mạng lưới bưu chính và thương mại quốc tế, không phải cửa khẩu quốc gia. Nó nối Base với cả thế giới, không chỉ với triều đình.",
 chain:["Hợp đồng trên Base phát một thông điệp","Mạng interop chuyển sang chuỗi đích","Hợp đồng bên kia nhận và thực thi","Kết quả có thể quay ngược lại Base"],
 special:"Chỗ dễ nhầm nhất trên các bản đồ khác: gộp cầu chính thức và interoperability làm một. Cầu chính thức thuộc kiến trúc rollup, bảo mật đến từ Ethereum. Interop là dịch vụ bên ngoài, bảo mật đến từ chính nhóm vận hành nó. Đặt chung một ô là xoá mất khác biệt quan trọng nhất về rủi ro.",
 uses:[],
 compare:[
  {n:"Cầu chính thức",s:"Một tuyến duy nhất Ethereum ↔ Base, thừa hưởng bảo mật L1."},
  {n:"Interoperability",s:"Phủ hàng chục chuỗi, nhưng mỗi mạng có mô hình tin cậy riêng."}],
 where:"LayerZero, Wormhole, CCIP đều có mặt trên Base; Superchain có chuẩn liên thông nội bộ."},

"base::ha tang lap trinh":{
 role:"Hạ tầng — bộ đồ nghề",
 what:"Bộ công cụ để dựng ứng dụng trên Base: OnchainKit, SDK ví, thư viện thanh toán, mẫu hợp đồng.",
 metaphor:"Là kho vật liệu và bản vẽ mẫu của thành phố. Không phải công trình, nhưng quyết định công trình mọc nhanh hay chậm.",
 chain:["Người xây lấy SDK và bộ công cụ","Ghép ví, thanh toán, danh tính vào ứng dụng","Triển khai lên Base","Ứng dụng ra mắt trong vài ngày thay vì vài tháng"],
 special:"Đây là thứ giải thích vì sao hệ ứng dụng của Base lớn nhanh hơn nhiều L2 cùng tuổi: Coinbase đầu tư mạnh vào khâu này chứ không chỉ vào chuỗi.",
 uses:["RPC / Nodes","Identity / Account"],
 compare:[],
 where:"Phần lớn là mã nguồn mở, dùng được cả ngoài Base."},

"base::eth":{
 role:"Kinh tế — tài sản gốc",
 what:"ETH trên Base đóng ba vai: trả phí gas, làm tài sản thế chấp trong các giao thức vay, và là tài sản dự trữ mà mọi thứ khác đo giá theo.",
 metaphor:"Là vàng trong kho bạc thành phố. Người ta không mang vàng đi chợ mua rau, nhưng mọi khoản lớn và mọi khoản thuế đều tính bằng nó.",
 chain:["ETH đưa từ Ethereum sang qua cầu chính thức","Dùng trả phí mỗi giao dịch","Dùng làm thế chấp trong Morpho, Aerodrome","Phí gom lại và một phần chảy ngược về Ethereum"],
 special:"Base không phát hành token riêng để trả phí. Đó là lựa chọn có ý nghĩa: thành phố không tự in tiền, mà dùng chính tiền của triều đình.",
 uses:["Cầu chính thức"],
 compare:[
  {n:"ETH",s:"Tài sản dự trữ, biến động giá, dùng trả phí và thế chấp."},
  {n:"USDC",s:"Giá ổn định, dùng để mua bán và tính toán hằng ngày."}],
 where:"Là token phí của Base, Arbitrum, Optimism và hầu hết rollup Ethereum."},

"base::tokens":{
 role:"Kinh tế — tài sản của nền kinh tế",
 what:"Ngoài ETH và stablecoin, thành phố còn hàng nghìn token khác: token dự án, token quản trị, token thanh khoản, vật phẩm game.",
 metaphor:"Là cổ phần, giấy tờ sở hữu và hàng hoá lưu thông trong thành phố. Phần lớn giá trị nằm ở đây, và phần lớn rủi ro cũng vậy.",
 chain:["Dự án phát hành token","Mở hồ thanh khoản trên Aerodrome hoặc Uniswap","Token được giao dịch và dùng làm thế chấp","Giá trị tăng giảm theo hoạt động thật của dự án"],
 special:"Đây là chỗ bản đồ dễ đánh lừa nhất: số lượng token không nói lên sức khoẻ nền kinh tế. Rất nhiều token có giá mà không có ai dùng, và ngược lại.",
 uses:["Aerodrome","Uniswap"],
 compare:[],
 where:"Mọi chuỗi đều có. Trên Base, phần lớn token mới xuất hiện qua các hồ thanh khoản của Aerodrome."},

"base::identity / account":{
 role:"Cư dân — hộ tịch",
 what:"Base Account là tài khoản hợp đồng đại diện cho một người trên chuỗi. Basenames gắn cho nó một cái tên đọc được. Smart account cho phép đặt hạn mức, khôi phục khi mất máy, và để ứng dụng trả phí hộ.",
 metaphor:"Là hộ tịch và căn cước của cư dân. Nó trả lời câu hỏi anh là ai trong thành phố này.",
 chain:["Người dùng tạo tài khoản bằng khoá thiết bị","Hợp đồng tài khoản đại diện họ trên chuỗi","Basenames gắn tên đọc được","Mọi ứng dụng nhận diện qua tài khoản đó"],
 special:"Tách danh tính ra khỏi ví là bước tiến thật. Trước đây mất mười hai từ khôi phục là mất sạch. Tài khoản hợp đồng cho phép khôi phục, đổi khoá, phân quyền — những thứ mà một cặp khoá đơn thuần không làm được.",
 uses:[],
 compare:[
  {n:"Identity / Account",s:"Anh là ai — danh tính, tên, quyền hạn."},
  {n:"Wallet",s:"Anh ký bằng gì — công cụ giữ khoá và ký giao dịch."}],
 where:"Base Account và Basenames là hạ tầng riêng của Base; smart account là chuẩn chung ERC-4337."},

"base::wallet":{
 role:"Cư dân — chìa khoá",
 what:"Ví là công cụ ký giao dịch, giữ và quản lý tài sản, và mở cửa vào ứng dụng. Nó không phải danh tính của anh — nó là chìa khoá anh cầm.",
 metaphor:"Là chùm chìa khoá và két sắt. Căn cước nói anh là ai; chìa khoá quyết định anh mở được cái gì.",
 chain:["Ví giữ khoá ký","Người dùng phê duyệt một hành động","Ví ký và gửi giao dịch qua RPC","Ứng dụng nhận kết quả và hiển thị"],
 special:"Lý do phải tách khỏi danh tính: một người có thể dùng nhiều ví cho cùng một tài khoản, đổi ví mà không mất danh tính, hoặc để ví nóng chi tiêu hằng ngày còn ví lạnh giữ phần lớn tài sản.",
 uses:["Identity / Account","RPC / Nodes"],
 compare:[
  {n:"Coinbase Smart Wallet",s:"Ví hợp đồng, đăng nhập bằng sinh trắc, khôi phục được."},
  {n:"MetaMask",s:"Ví khoá riêng truyền thống, mất từ khôi phục là mất sạch."}],
 where:"Base hỗ trợ cả hai loại; ví thông minh là hướng Coinbase đẩy mạnh."},

"base::vaults":{
 role:"Tài chính — quỹ tự động",
 what:"Vault là quỹ nhận tiền gửi rồi tự chạy một chiến lược sinh lợi suất: cho vay, cung cấp thanh khoản, hoặc kết hợp nhiều bước.",
 metaphor:"Là quỹ tín thác của thành phố — gửi tiền vào rồi có người quản lý thay, không phải tự đi từng chợ.",
 chain:["Người gửi nạp tài sản vào vault","Vault chạy chiến lược qua Morpho, Aerodrome…","Lợi suất cộng dồn vào phần vốn","Người gửi rút cả gốc lẫn lãi"],
 special:"Vault là nơi rủi ro dễ bị giấu nhất: người gửi thấy con số lợi suất nhưng thường không thấy chiến lược bên dưới đang vay đòn bẩy tới đâu.",
 uses:["Morpho","Oracle"],
 compare:[],
 where:"Trên Base, phần lớn vault xây trên Morpho hoặc các giao thức cho vay khác."},

"base::morpho":{
 role:"Giao thức tín dụng",
 what:"Morpho là giao thức DeFi cho vay và đi vay. Nói gọn: nó dựng hạ tầng cho một thị trường tín dụng chạy trên blockchain — người có tài sản gửi vốn vào để kiếm lợi suất, người cần vốn thế chấp crypto để vay ra.",
 metaphor:"Trong cách ví thành phố, Morpho không phải đất. Đất là Ethereum và Base. Morpho là hệ thống ngân hàng và tín dụng được xây trên mảnh đất đó — nó không tạo ra chỗ đứng, nó tạo ra dòng vốn chảy giữa những người đang đứng ở đấy.",
 chain:["Ethereum / Base — đất và hạ tầng nền","Morpho — lớp tín dụng","Tạo ra các thị trường cho vay riêng biệt","Người có vốn gửi vào để kiếm lợi suất","Người cần vốn thế chấp crypto để vay ra","Vault và ứng dụng khác xây tiếp lên trên Morpho"],
 special:"Điểm khác biệt lớn nhất: Morpho hướng tới làm một lớp hạ tầng cho vay không cần xin phép. Thay vì chỉ là một ngân hàng DeFi có sẵn vài thị trường, bất kỳ ai cũng có thể dùng Morpho để mở thị trường tín dụng hoặc dựng sản phẩm tài chính của riêng mình lên trên.",
 uses:["Oracle","USDC","Wallet / Account","RPC / Nodes"],
 compare:[
  {n:"Aave",s:"Một hồ chung lớn, tham số do quản trị quyết. An toàn hơn nhờ nhiều lớp kiểm soát, nhưng chậm khi muốn mở thị trường mới."},
  {n:"Compound",s:"Mô hình đời đầu, cũng dùng hồ chung. Đơn giản và bền, nhưng ít linh hoạt hơn."},
  {n:"Morpho",s:"Chia nhỏ thành từng thị trường độc lập, mỗi thị trường tự chọn tài sản thế chấp và oracle. Rủi ro không lây từ thị trường này sang thị trường kia."}],
 where:"Chạy trên Ethereum, Base, Arbitrum, Optimism và vài chuỗi EVM khác. Trên Base, Morpho là một trong những nơi giữ nhiều tài sản nhất."},

"base::aerodrome":{
 role:"Chợ thanh khoản bản địa",
 what:"Aerodrome là sàn hoán đổi và là nơi tập trung thanh khoản chính của Base. Nó dùng mô hình ve(3,3): người khoá token quản trị sẽ bỏ phiếu xem hồ thanh khoản nào được nhận phần thưởng tuần này.",
 metaphor:"Đây là cái chợ trung tâm của thành phố. Mọi thứ mua bán đều đi qua đây, và giá cả ở các cửa hàng nhỏ hơn đều tham chiếu từ giá chợ này.",
 chain:["Base — đất và hạ tầng nền","Aerodrome — chợ thanh khoản","Các hồ thanh khoản cho từng cặp tài sản","Người cung cấp thanh khoản nhận phí và phần thưởng","Người khoá token bỏ phiếu chia phần thưởng","Ứng dụng khác lấy giá và thanh khoản từ đây"],
 special:"Aerodrome gắn chặt với Base tới mức nó gần như là hạ tầng chứ không chỉ là một ứng dụng: dự án mới lên Base thường phải mở hồ ở đây trước thì token mới có chỗ giao dịch.",
 uses:["USDC","Oracle","Wallet / Account"],
 compare:[
  {n:"Uniswap",s:"Phổ quát, có mặt ở mọi chuỗi, không thiên vị dự án nào."},
  {n:"Aerodrome",s:"Chỉ ở Base, đổi lại điều phối được phần thưởng để kéo thanh khoản về đúng chỗ hệ sinh thái cần."}],
 where:"Chỉ chạy trên Base. Bản gốc của mô hình này là Velodrome bên Optimism."},

"base::uniswap":{
 role:"Sàn hoán đổi",
 what:"Uniswap là sàn hoán đổi dùng nhóm thanh khoản thay cho sổ lệnh. Không có người khớp lệnh — giá được tính bằng công thức dựa trên tỉ lệ hai tài sản còn lại trong hồ.",
 metaphor:"Là quầy đổi tiền có mặt ở mọi thành phố. Không phải chợ trung tâm của riêng Base, nhưng ai cũng biết đường tới và tin được.",
 chain:["Base — đất và hạ tầng nền","Uniswap — sàn hoán đổi","Hồ thanh khoản cho từng cặp","Người đổi trả phí, người góp vốn nhận phí","Ứng dụng khác gọi thẳng vào để hoán đổi hộ người dùng"],
 special:"Uniswap là thứ gần nhất với một chuẩn chung: rất nhiều ứng dụng không tự làm chức năng hoán đổi mà gọi thẳng vào hợp đồng của Uniswap.",
 uses:["USDC","Wallet / Account","RPC / Nodes"],
 compare:[
  {n:"Aerodrome",s:"Thanh khoản sâu hơn cho các cặp gắn với Base."},
  {n:"Uniswap",s:"Phủ rộng hơn, cùng một giao diện dùng được ở mọi chuỗi."}],
 where:"Có mặt trên Ethereum và gần như mọi L2, trong đó có Base."},

"base::farcaster":{
 role:"Mạng xã hội giao thức mở",
 what:"Farcaster là một mạng xã hội mà phần dữ liệu — ai theo dõi ai, ai đăng gì — nằm ở giao thức chứ không nằm trong máy chủ của một công ty. Nhiều ứng dụng khác nhau cùng đọc chung một tập dữ liệu ấy.",
 metaphor:"Là quảng trường và bảng tin của thành phố. Ai cũng ra đó nói chuyện, và không ai sở hữu cái quảng trường.",
 chain:["Base — đất và hạ tầng nền","Farcaster — giao thức xã hội","Hồ sơ, người theo dõi và bài đăng nằm ở lớp giao thức","Nhiều ứng dụng khách cùng đọc và ghi vào đó","Mini app chạy thẳng trong dòng bài — mua bán, bỏ phiếu, chơi"],
 special:"Điều đáng chú ý ở Farcaster là mini app trong bài đăng: một giao dịch có thể xảy ra ngay trong lúc lướt, không phải mở sang trang khác. Đây là lý do Base và Farcaster gắn với nhau chặt.",
 uses:["Wallet / Account","USDC","Indexer"],
 compare:[
  {n:"Lens Protocol",s:"Cùng ý tưởng nhưng hồ sơ là NFT, chạy chủ yếu bên Polygon."},
  {n:"X / Threads",s:"Nhanh và đông hơn nhiều, nhưng dữ liệu nằm trong tay công ty, đổi nền tảng là mất hết."}],
 where:"Giao thức có lớp lưu trữ riêng, phần thanh toán và danh tính onchain đặt trên Base."},

"base::zora":{
 role:"Sáng tạo và NFT",
 what:"Zora là nơi tác giả đúc tác phẩm của mình thành token để bán và thu tiền trực tiếp, không qua trung gian. Mỗi bài viết, ảnh hay bài nhạc có thể trở thành một thứ mua được.",
 metaphor:"Là khu phố nghệ nhân và phòng trưng bày của thành phố — nơi người ta làm ra đồ và bán ngay tại xưởng.",
 chain:["Base — đất và hạ tầng nền","Zora — lớp đúc và bán tác phẩm","Tác giả đúc tác phẩm thành token","Người xem mua, tác giả nhận tiền ngay","Phí bán lại tiếp tục chảy về tác giả"],
 special:"Zora bỏ hẳn mô hình đấu giá đắt đỏ của NFT thời đầu, chuyển sang bán rẻ và bán nhiều — hợp với việc sáng tác hàng ngày hơn là sưu tầm.",
 uses:["Wallet / Account","USDC"],
 compare:[
  {n:"OpenSea",s:"Chợ giao dịch lại, mạnh ở mua bán đồ đã có."},
  {n:"Zora",s:"Mạnh ở khâu tạo ra và phát hành lần đầu."}],
 where:"Chủ yếu trên Base, và có chuỗi riêng Zora Network cũng dựng từ OP Stack."},

"base::games":{
 role:"Giải trí",
 what:"Nhóm game và ứng dụng giải trí chạy trên Base. Phí thấp và khối nhanh khiến những thao tác nhỏ — mở rương, đổi vật phẩm, trả thưởng — ghi thẳng lên chuỗi được mà không tốn kém.",
 metaphor:"Là khu vui chơi của thành phố. Không phải nơi tạo ra của cải chính, nhưng là thứ kéo người ta tới ở lại.",
 chain:["Base — đất và hạ tầng nền","Game và ứng dụng giải trí","Vật phẩm và điểm số ghi lên chuỗi","Người chơi thật sự sở hữu vật phẩm","Vật phẩm mang ra chợ bán được"],
 special:"Điểm chưa xong: phần lớn game onchain vẫn dựa vào phần thưởng token để giữ người chơi, chứ chưa hay đủ để giữ chân bằng chính trò chơi.",
 uses:["Wallet / Account","RPC / Nodes"],
 compare:[],
 where:"Nhiều tựa dùng Base làm lớp thanh toán, phần chơi vẫn chạy ngoài chuỗi cho mượt."},

"base::ai apps":{
 role:"Tác tử và công cụ AI",
 what:"Nhóm ứng dụng để tác tử AI có ví riêng, tự trả tiền cho dịch vụ và tự thực hiện giao dịch trong khuôn khổ chủ nó đặt ra.",
 metaphor:"Là lớp người làm thuê tự động của thành phố — không phải cư dân, nhưng đi lại, mua bán và trả phí như cư dân.",
 chain:["Base — đất và hạ tầng nền","Tác tử AI có ví riêng","Nhận hạn mức chi tiêu từ chủ","Tự trả phí cho dữ liệu, tính toán, dịch vụ","Mọi khoản chi đều để lại dấu vết kiểm tra được"],
 special:"Đây là lý do chuẩn thanh toán theo từng lượt gọi như x402 xuất hiện: máy trả tiền cho máy cần khoản rất nhỏ và rất nhiều lần, thứ mà thẻ ngân hàng không làm nổi.",
 uses:["USDC","Wallet / Account","RPC / Nodes"],
 compare:[],
 where:"Mảng còn non. Base được chọn nhiều vì phí thấp và có USDC gốc."},

"base::commerce":{
 role:"Thương mại",
 what:"Nhóm công cụ để cửa hàng thật nhận thanh toán bằng stablecoin: khách trả USDC, người bán nhận tiền gần như tức thì, phí thấp hơn thẻ.",
 metaphor:"Là các cửa hiệu mặt phố — nơi tiền trong thành phố đổi lấy hàng hoá ngoài đời thật.",
 chain:["Base — đất và hạ tầng nền","Cổng thanh toán thương mại","Khách trả bằng USDC từ ví","Người bán nhận tiền, không chờ đối soát","Có thể quy đổi ra tiền pháp định nếu muốn"],
 special:"Đây là chỗ blockchain chạm vào kinh tế thật rõ nhất: không cần người mua biết mình đang dùng chuỗi nào, chỉ cần tiền tới nơi và phí rẻ hơn.",
 uses:["USDC","Wallet / Account"],
 compare:[],
 where:"Base được Coinbase đẩy mạnh mảng này vì có sẵn hạ tầng quy đổi tiền pháp định."},

"base::xmtp":{
 role:"Nhắn tin giữa các ví",
 what:"XMTP là giao thức cho phép hai địa chỉ ví nhắn tin cho nhau, mã hoá đầu cuối, không cần biết email hay số điện thoại của nhau.",
 metaphor:"Là hệ thống bưu chính của thành phố. Không ai chú ý tới nó cho tới khi cần gửi thư cho một người mình chỉ biết địa chỉ nhà.",
 chain:["Base — đất và hạ tầng nền","XMTP — lớp truyền tin","Danh tính là chính địa chỉ ví","Tin nhắn mã hoá, ứng dụng nào cũng đọc được nếu có khoá","Ứng dụng gắn thông báo và hỗ trợ khách hàng vào đây"],
 special:"Giải quyết một khoảng trống thật: trước đó, một giao thức muốn báo cho người dùng biết vị thế sắp bị thanh lý thì không có cách nào liên hệ.",
 uses:["Wallet / Account"],
 compare:[],
 where:"Là giao thức đa chuỗi, dùng danh tính ví nên chạy được ở đâu có ví."},

"base::rpc / nodes":{
 role:"Hạ tầng — cửa vào chuỗi",
 what:"RPC là điểm mà ứng dụng gọi vào để đọc trạng thái chuỗi và gửi giao dịch. Alchemy, QuickNode và node công cộng là những nhà cung cấp chính trên Base.",
 metaphor:"Là hệ thống dây điện thoại và tổng đài của thành phố. Không ai nhìn thấy nó, nhưng cắt đi thì mọi cửa hàng đều câm.",
 chain:["Ứng dụng cần đọc hoặc ghi","Gọi tới endpoint RPC","Node đọc trạng thái chuỗi hoặc phát giao dịch ra mạng","Kết quả trả ngược về giao diện người dùng"],
 special:"Đây là điểm tập trung hoá âm thầm nhất của cả ngành: chuỗi thì phi tập trung, nhưng phần lớn ứng dụng lại đi qua vài nhà cung cấp RPC. Nhà cung cấp sập thì người dùng thấy như chuỗi sập.",
 uses:[],
 compare:[
  {n:"Node tự chạy",s:"Không phụ thuộc ai, nhưng tốn máy và công bảo trì."},
  {n:"RPC dịch vụ",s:"Nhanh, có công cụ theo dõi, đổi lại phụ thuộc một công ty."}],
 where:"Mọi ứng dụng trên Base đều đi qua lớp này, kể cả Base App."},

"base::indexer":{
 role:"Hạ tầng — đọc và sắp xếp dữ liệu",
 what:"Chuỗi lưu dữ liệu theo cách tối ưu cho việc xác thực, không phải cho việc tra cứu. Indexer như The Graph hay Goldsky đọc toàn bộ sự kiện rồi sắp lại thành dạng truy vấn được.",
 metaphor:"Là văn phòng lưu trữ hồ sơ của thành phố. Mọi giấy tờ đều có sẵn ở kho, nhưng phải có người sắp theo thứ tự thì mới tra ra được.",
 chain:["Chuỗi phát ra sự kiện","Indexer đọc và sắp xếp lại","Ứng dụng truy vấn dữ liệu đã sắp","Giao diện hiện danh mục, lịch sử, bảng xếp hạng"],
 special:"Không có indexer thì một trang đơn giản như “lịch sử giao dịch của tôi” cũng phải quét lại toàn bộ chuỗi mỗi lần mở.",
 uses:["RPC / Nodes"],
 compare:[],
 where:"Gần như mọi ứng dụng có giao diện danh sách trên Base đều dùng một indexer nào đó."},

"base::oracle":{
 role:"Hạ tầng — dữ liệu ngoài đời",
 what:"Hợp đồng thông minh không tự nhìn ra ngoài được. Oracle như Chainlink hay Pyth mang giá cả và dữ liệu thế giới thật vào để hợp đồng có cái mà quyết định.",
 metaphor:"Là đài quan sát dựng ngoài tường thành. Thành phố không tự biết giá lúa bên ngoài, phải có người đứng đó nhìn rồi báo vào.",
 chain:["Nguồn dữ liệu ngoài đời — sàn, nhà tạo lập thị trường","Oracle tổng hợp và ký","Đưa lên chuỗi","Hợp đồng đọc để quyết định thanh lý, định giá, trả thưởng"],
 special:"Đây là điểm yếu chí tử của mọi giao thức cho vay: oracle báo sai giá thì hệ thống thanh lý nhầm hàng loạt. Phần lớn vụ mất tiền lớn trong DeFi đều bắt đầu từ đây.",
 uses:[],
 compare:[
  {n:"Chainlink",s:"Mạng node độc lập, cập nhật theo ngưỡng biến động."},
  {n:"Pyth",s:"Lấy giá thẳng từ nhà tạo lập thị trường, nạp theo yêu cầu nên rẻ và nhanh hơn."}],
 where:"Morpho, Aerodrome và mọi giao thức cho vay trên Base đều phụ thuộc vào lớp này."},

"base::bridges":{
 role:"Hạ tầng — cửa khẩu",
 what:"Cầu nối đưa tài sản từ Ethereum hoặc chuỗi khác sang Base và ngược lại. Base Bridge là cầu chính thức, LayerZero và các cầu bên thứ ba lo những tuyến còn lại.",
 metaphor:"Là cửa khẩu và đường quốc lộ nối thành phố với bên ngoài. Không có nó thì thành phố có đất, có chợ, nhưng không ai vào được.",
 chain:["Người dùng khoá tài sản ở chuỗi gốc","Cầu ghi nhận và phát hành bản tương ứng trên Base","Tài sản lưu thông trong thành phố","Muốn ra thì đốt bản trên Base và mở khoá ở chuỗi gốc"],
 special:"Cầu là nơi bị tấn công nhiều nhất trong lịch sử ngành, vì nó luôn phải giữ một kho tài sản lớn ở một chỗ. Cầu chính thức của rollup an toàn hơn cầu bên thứ ba, đổi lại rút về chậm hơn nhiều.",
 uses:[],
 compare:[
  {n:"Base Bridge",s:"Cầu gốc của rollup, an toàn nhất, nhưng rút về Ethereum phải chờ."},
  {n:"Cầu bên thứ ba",s:"Nhanh hơn nhiều vì có người ứng vốn trước, đổi lại phải tin nhóm vận hành cầu."}],
 where:"Mọi tài sản trong thành phố Base đều đi qua một cửa khẩu nào đó để vào."},

"base::usdc":{
 role:"Hạ tầng — tiền lưu hành",
 what:"USDC là stablecoin do Circle phát hành, mỗi đồng có một đô la dự trữ đứng sau. Trên Base, USDC được phát hành gốc chứ không phải bản bọc qua cầu.",
 metaphor:"Là tiền mặt lưu hành trong thành phố. ETH giống vàng để đóng thuế và trả phí, còn USDC là thứ người ta thật sự dùng để mua bán hằng ngày.",
 chain:["Circle giữ dự trữ đô la ngoài đời","Phát hành USDC gốc trên Base","Người dùng và ứng dụng dùng làm đơn vị thanh toán","Đổi ngược ra tiền pháp định qua Coinbase hoặc Circle"],
 special:"Việc phát hành gốc quan trọng hơn vẻ ngoài của nó: bản bọc qua cầu sẽ mất giá trị nếu cầu bị tấn công, còn bản gốc thì không phụ thuộc vào bất kỳ cây cầu nào.",
 uses:[],
 compare:[
  {n:"USDT",s:"Lớn hơn về quy mô toàn ngành, nhưng ít hiện diện trên Base."},
  {n:"DAI",s:"Sinh ra từ thế chấp trong hợp đồng, không do công ty giữ quỹ."}],
 where:"Là đơn vị tính của gần như mọi giao dịch có giá trị thật trên Base."},

"base::base app":{
 role:"Cổng thành và quảng trường",
 what:"Base App gom ví, sàn, thanh toán, mạng xã hội và kho ứng dụng vào một chỗ. Người dùng mở app là dùng được, không phải tự đi tìm từng dịch vụ rồi nối chúng lại.",
 metaphor:"Là cổng thành và quảng trường trung tâm. Ai vào thành phố cũng đi qua đây, và đứng ở đây là nhìn thấy đường tới mọi khu khác.",
 chain:["Người dùng mở Base App","Ví được tạo sẵn, không cần chép từ khôi phục","Từ đây đi thẳng tới Trade, Pay, Social, Discover","Mỗi thao tác là một giao dịch trên Base","Phí chảy về Ethereum, khép lại vòng tuần hoàn"],
 special:"Đây là điểm phân biệt Base với các L2 khác. Arbitrum và Optimism để người dùng tự lắp ví với ứng dụng; Base xây sẵn cổng vào, đổi lại cổng ấy do một công ty vận hành.",
 uses:["Wallet / Account","USDC","Uniswap","Farcaster"],
 compare:[
  {n:"Arbitrum",s:"Không có cổng hợp nhất — vào bằng ví và trang cầu nối."},
  {n:"Base App",s:"Một cửa vào duy nhất, dễ cho người mới, nhưng tập trung hơn."}],
 where:"Là lối vào chính thức của thành phố Base."}
};

window.KT_DATA = window.KT_DATA || {};
window.KT_DATA.ENTITIES = ENTITIES;
})();
