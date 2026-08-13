/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-l2beat.mjs — ĐỪNG SỬA TAY.
   Nguồn: l2beat.com/api/scaling/summary
   Lấy lúc: 2026-08-13T07:56:42.619Z
   106 dự án · tổng tài sản $39.47b
   ═══════════════════════════════════════════════════════ */
window.DSV_DATA = {
 "generatedAt": "2026-08-13T07:56:42.619Z",
 "date": "13/08/2026",
 "nguon": "l2beat.com/api/scaling/summary",
 "tongTvs": 39469671315.37677,
 "projects": [
  {
   "id": "base",
   "slug": "base",
   "ten": "Base Chain",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 11652349952,
   "d7": -0.005513385643173829,
   "chiaTvs": {
    "native": 4662407300.5546875,
    "canonical": 2199458469.5807123,
    "external": 4790485529.714844
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) prove the validity of a state proposal, only requiring a single transaction to resolve. A fault proof eliminates a state proposal by proving that any intermediate state transition in the proposal results in a different state root. For either, a ZK proof is used."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable. Upgrades need to be approved by 2 parties: the Base Coordinator Multisig and the Base Security Council."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "arbitrum",
   "slug": "arbitrum",
   "ten": "Arbitrum One",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 10074299392,
   "d7": -0.0010299212272217861,
   "chiaTvs": {
    "native": 3117447514.908203,
    "canonical": 2949673444.803271,
    "external": 4007185449.077194
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "hyperliquid",
   "slug": "hyperliquid",
   "ten": "Hyperliquid",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Arbitrum One",
   "stack": null,
   "tvs": 5855652352,
   "d7": -0.012475708698138188,
   "chiaTvs": {
    "native": 0,
    "canonical": 5855652352,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is ultimately NOT published on Ethereum."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "polygon-pos",
   "slug": "polygon-pos",
   "ten": "Polygon PoS",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 3679412736,
   "d7": -0.019280106986835688,
   "chiaTvs": {
    "native": 8513873.21875,
    "canonical": 2223660711.1177244,
    "external": 1447238549
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Decentralized Sequencer Set",
     "s": "warning",
     "d": "Although there is a sequencer set of 105 (called validators), if the cap of 105 is reached, no new stakers can join. A minimum of 100,000 POL stake is required to obtain block production rights. There is no specific censorship resistance mechanism against selective censorship by parts of the active validator set nor a way to force transactions from Ethereum L1. The canonical bridge between Polygon PoS and Ethereum allows for queuing transactions from the Ethereum and Polygon PoS sides, which cannot be skipped, except for halting the queue entirely."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "PoS network",
     "s": "warning",
     "d": "Data is guaranteed to be available by an external proof of stake network of validators. On Ethereum, DA is attested via signed block headers."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "warning",
     "d": "The PoS network is composed of 105 validators. Blocks are included in the chain only if signed by 2/3+1 of the network stake. It's currently not possible to join the set if the validator cap is reached. The current validator cap is set to 105. In the event of a failure in reaching consensus, withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "optimism",
   "slug": "op-mainnet",
   "ten": "OP Mainnet",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1394032512,
   "d7": -0.029184166014828428,
   "chiaTvs": {
    "native": 230356001.71875,
    "canonical": 917297732.6851766,
    "external": 246378595.85836792
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "mantle",
   "slug": "mantle",
   "ten": "Mantle",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1237978880,
   "d7": -0.009926318579271287,
   "chiaTvs": {
    "native": 60060490.875,
    "canonical": 584926021.0300416,
    "external": 592992428.5
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "robinhood",
   "slug": "robinhood",
   "ten": "Robinhood Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 1117627264,
   "d7": 0.11221035468852492,
   "chiaTvs": {
    "native": 546731310.3359375,
    "canonical": 306675623.73763883,
    "external": 264220400
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no guaranteed mechanism to have transactions included if the sequencer is down or censoring. Although users can enqueue messages in the L1 delayed inbox and call forceInclusion on the SequencerInbox, the chain runs ArbOS 61 transaction filtering: an authorized filterer can register any transaction hash in the ArbFilteredTransactionsManager precompile (0x00…0074), after which the state transition function forcibly fails that transaction, including force-included ones, without delay."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 28d of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lighter",
   "slug": "lighter",
   "ten": "Lighter",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 904233472,
   "d7": 0.0509596857024861,
   "chiaTvs": {
    "native": 0,
    "canonical": 904233453.5009766,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Force via L1",
     "s": "good",
     "d": "Users can force the sequencer to include a transaction by submitting a request through L1. If the sequencer censors or is down for  for more than 14d, users can use the exit hatch to withdraw their funds."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain (SD)",
     "s": "good",
     "d": "All of the data (SD = state diffs) needed for proof construction is published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Use escape hatch",
     "s": "good",
     "d": "Users are able to trustlessly exit by submitting a zero knowledge proof of funds."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "starknet",
   "slug": "starknet",
   "ten": "Starknet",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "SN Stack",
   "tvs": 352163968,
   "d7": -0.05312139896575008,
   "chiaTvs": {
    "native": 147154479.953125,
    "canonical": 137846939.02165294,
    "external": 67162489.45751953
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Log via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 map, but can't force them. When users “complain” that their transaction is stuck on L1 and not picked up by the sequencer, the Security Council minority can bypass the sequencer by posting a state root that includes it."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST)",
     "s": "good",
     "d": "STARKs are zero knowledge proofs that ensure state correctness."
    },
    {
     "n": "Data Availability",
     "v": "Onchain (SD)",
     "s": "good",
     "d": "All of the data (SD = state diffs) needed for proof construction is published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Security Council minority",
     "s": "warning",
     "d": "Only the whitelisted proposer can update state roots on L1, so in the event of failure the withdrawals are frozen. The Security Council minority can be alerted to enforce censorship resistance because they are a permissioned Operator."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "linea",
   "slug": "linea",
   "ten": "Linea",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 341856448,
   "d7": -0.017294870116687178,
   "chiaTvs": {
    "native": 1050729.4575195312,
    "canonical": 161289447.30025983,
    "external": 179516275.46679688
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Eventually (after 6 months of no finalized blocks) the Operator role becomes public, theoretically allowing anyone to post data."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1. Unlike most ZK rollups, transaction data is posted instead of state diffs."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. Eventually (after 6 months of no finalized blocks) the Operator role becomes public, theoretically allowing anyone to propose state with valid proofs."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "worldchain",
   "slug": "world",
   "ten": "World Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 338979072,
   "d7": 0.06615742250903334,
   "chiaTvs": {
    "native": 0,
    "canonical": 322607136.0500002,
    "external": 16371929
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "celo",
   "slug": "celo",
   "ten": "Celo",
   "loai": "layer2",
   "dang": "Optimium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 251448208,
   "d7": 0.048222881661734274,
   "chiaTvs": {
    "native": 232088818.34765625,
    "canonical": 2812888.7624929845,
    "external": 16546468.75
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "warning",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. The system currently operates with at least 5 whitelisted challengers external to the team."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are checked against the DACert Verifier data roots, signed off by EigenDA operators."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "gnosis",
   "slug": "gnosis",
   "ten": "Gnosis Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 238263920,
   "d7": -0.016166026490026852,
   "chiaTvs": {
    "native": 0,
    "canonical": 238263892.47045317,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Decentralized Sequencer Set",
     "s": "good",
     "d": "Users can permissionlessly become a sequencer (validator) by staking a minimum of 1 GNO to join the queue and wait to obtain block production rights. There is no specific censorship resistance mechanism against selective censorship by parts of the active validator set nor a way to force transactions from Ethereum L1."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Ethereum contracts do not validate Gnosis Chain state transitions. Bridge messages are accepted after threshold signatures from dedicated bridge validators."
    },
    {
     "n": "Data Availability",
     "v": "PoS network",
     "s": "bad",
     "d": "Data is made available by an external proof of stake network of validators. Since there is no DA bridge, Ethereum cannot verify whether any data was made available on Gnosis Chain or whether incoming messages originate from state that was attested to by the PoS network."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "The Gnosis Chain bridge is not validated by its PoS validator set. Withdrawals through the xDAI bridge require 4/7 validator signatures, while AMB and Omnibridge withdrawals require 4/7 validator signatures. The bridge validators can freeze bridge transactions and/or steal bridge-locked and minted assets. Transactions on Gnosis Chain itself cannot be forced from Ethereum. If the chain has a liveness failure due to blanket censorship or operator walkaway the only recourse are new validators joining the open validator set."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zksync2",
   "slug": "zksync-era",
   "ten": "ZKsync Era",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 193749600,
   "d7": -0.041943527015913196,
   "chiaTvs": {
    "native": 73948252.09570312,
    "canonical": 107837965.78326021,
    "external": 11963396.108154297
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain (SD)",
     "s": "good",
     "d": "All of the data (SD = state diffs) needed for proof construction is published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "roninnetwork",
   "slug": "ronin-network",
   "ten": "Ronin",
   "loai": "layer2",
   "dang": "Optimium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 188942640,
   "d7": -0.01615896999292421,
   "chiaTvs": {
    "native": 56978121.40625,
    "canonical": 0,
    "external": 131964510.80222656
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) prove the validity of a state proposal, only requiring a single transaction to resolve. A fault proof eliminates a state proposal by proving that any intermediate state transition in the proposal results in a different state root. For either, a ZK proof is used."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are checked against the DACert Verifier data roots, signed off by EigenDA operators."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "The primary whitelisted proposer has an optimistic advantage, letting them win by default if no conflicting proposals are made. This privilege is dropped after 1mo of inactivity, and anyone can leverage the source available zk prover to prove a fault or a conflicting valid proposal to win against the privileged proposer and/or supply a bond and make a counter proposal at any time."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "fraxtal",
   "slug": "fraxtal",
   "ten": "Fraxtal",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 154863472,
   "d7": 0.0023175890198059435,
   "chiaTvs": {
    "native": 0,
    "canonical": 154334968.30916584,
    "external": 528521.328125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published on chain. Fraxtal uses a separate data availability module developed by the Frax Core Team, and data availability attestations are not published on chain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ink",
   "slug": "ink",
   "ten": "Ink",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 151285840,
   "d7": -0.07496803602310109,
   "chiaTvs": {
    "native": 0,
    "canonical": 22213427.39999962,
    "external": 129072432
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "morph",
   "slug": "morph",
   "ten": "Morph",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 118705744,
   "d7": 0.07561682507340661,
   "chiaTvs": {
    "native": 0,
    "canonical": 12659844.609999537,
    "external": 106045909.33188629
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Force via L1",
     "s": "good",
     "d": "Users can force the sequencer to include a transaction by submitting a request through L1. If the sequencer censors or is down for 7d, new L1 batches must include at least 1 transaction from the queue."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "warning",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. The system currently operates with at least 5 whitelisted challengers external to the team."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 7d of inactivity from the currently whitelisted Proposers. This requires using the source-available prover to submit a zk proof of validity for the proposal."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "xlayer",
   "slug": "xlayer",
   "ten": "X Layer",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 117912384,
   "d7": 0.0021756231075829024,
   "chiaTvs": {
    "native": 0,
    "canonical": 4463725.755343894,
    "external": 113448648
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. Challenges are currently restricted to 1 whitelisted challenger and proposals are restricted to 1 whitelisted proposer."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only whitelisted proposers can publish state roots. Permissionless proposing becomes available only after 1000y of proposer inactivity, which is not a practical recovery path."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "mantapacific",
   "slug": "mantapacific",
   "ten": "Manta Pacific",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 86113880,
   "d7": -0.014250021726502804,
   "chiaTvs": {
    "native": 27209526,
    "canonical": 22376053.76703453,
    "external": 36528305.08979797
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lyra",
   "slug": "derive",
   "ten": "Derive",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 76112512,
   "d7": -0.02142885648446624,
   "chiaTvs": {
    "native": 0,
    "canonical": 86462.63624954224,
    "external": 76026050.86916092
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "unichain",
   "slug": "unichain",
   "ten": "Unichain",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 70002008,
   "d7": -0.034258024064716786,
   "chiaTvs": {
    "native": 0,
    "canonical": 28965414.31941177,
    "external": 41036604.25542927
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "blast",
   "slug": "blast",
   "ten": "Blast",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 67316280,
   "d7": -0.004875610264338137,
   "chiaTvs": {
    "native": 16577679.986328125,
    "canonical": 37078327.819619656,
    "external": 13660271.556152344
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "katana",
   "slug": "katana",
   "ten": "Katana",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 61651280,
   "d7": -0.10453565858153957,
   "chiaTvs": {
    "native": 995333.4564843178,
    "canonical": 59509630.139708504,
    "external": 1146318.1401367188
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since the Security Council can remove the delay on upgrades."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "bob",
   "slug": "bob",
   "ten": "BOB",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 61387980,
   "d7": -0.01341713279781287,
   "chiaTvs": {
    "native": 12654480,
    "canonical": 3199169.1915773004,
    "external": 45534330.824157715
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) prove the validity of a state proposal, only requiring a single transaction to resolve. A fault proof eliminates a state proposal by proving that any intermediate state transition in the proposal results in a different state root. For either, a ZK proof is used."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "The primary whitelisted proposer has an optimistic advantage, letting them win by default if no conflicting proposals are made. This privilege is dropped after 1mo of inactivity, and anyone can leverage the source available zk prover to prove a fault or a conflicting valid proposal to win against the privileged proposer and/or supply a bond and make a counter proposal at any time."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "plumenetwork",
   "slug": "plumenetwork",
   "ten": "Plume Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 60514980,
   "d7": 0.047630710909295715,
   "chiaTvs": {
    "native": 24709.80078125,
    "canonical": 55733253.77005005,
    "external": 4757020.96875
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "abstract",
   "slug": "abstract",
   "ten": "Abstract",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 45596696,
   "d7": -0.008665758747419261,
   "chiaTvs": {
    "native": 1287385.7734375,
    "canonical": 20649075,
    "external": 23660235.75
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain (SD)",
     "s": "good",
     "d": "All of the data (SD = state diffs) needed for proof construction is published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "scroll",
   "slug": "scroll",
   "ten": "Scroll",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 41919284,
   "d7": -0.022357516902402508,
   "chiaTvs": {
    "native": 3883650.5,
    "canonical": 35392847.141402245,
    "external": 2642788.048828125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 7d delay on this operation. Proposing new blocks requires creating ZK proofs."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "If the Proposer fails, users can leverage the source available prover to submit proofs to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "cronoszkevm",
   "slug": "cronoszkevm",
   "ten": "Cronos zkEVM",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 33754944,
   "d7": -0.001630874386470027,
   "chiaTvs": {
    "native": 0,
    "canonical": 19554048.23046875,
    "external": 14200894.25
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "edgex",
   "slug": "edgex",
   "ten": "EdgeX",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "SN Stack",
   "tvs": 32497142,
   "d7": -0.5302520845632175,
   "chiaTvs": {
    "native": 0,
    "canonical": 32497142,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Force via L1",
     "s": "good",
     "d": "Users can force the sequencer to include a trade or a withdrawal transaction by submitting a request through L1. If the sequencer censors or is down for 7d, users can use the exit hatch to withdraw their funds. Users are required to find a counterparty for the trade by out of system means."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST)",
     "s": "good",
     "d": "STARKs are zero knowledge proofs that ensure state correctness."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/6 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Use escape hatch",
     "s": "good",
     "d": "Users are able to trustlessly exit by submitting a Merkle proof of funds. Positions will be closed using the average price from the last batch state update."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lisk",
   "slug": "lisk",
   "ten": "Lisk",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 31375032,
   "d7": 0.033769006256248346,
   "chiaTvs": {
    "native": 0,
    "canonical": 31004807.11871338,
    "external": 370226.21630859375
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "megaeth",
   "slug": "megaeth",
   "ten": "MegaETH",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 28212044,
   "d7": -0.003310563874084682,
   "chiaTvs": {
    "native": 0,
    "canonical": 8115015.529999504,
    "external": 20097029.220703125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) prove the validity of a state proposal, only requiring a single transaction to resolve. A fault proof eliminates a state proposal by proving that any intermediate state transition in the proposal results in a different state root. For either, a ZK proof is used. Since the node source is not available, challengers cannot watch the chain independently. `vanguardAdvantage` applies to every proposal and is set to 36558901084y 8mo, so only the Vanguard can submit state proposals; faulty proposals can be flagged but not replaced, halting the chain until the Vanguard proposes a correct state root."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are not checked against the DACert Verifier onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "apex-omni",
   "slug": "apex-omni",
   "ten": "ApeX Omni",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": null,
   "tvs": 25835372,
   "d7": -0.0015494214905672488,
   "chiaTvs": {
    "native": 0,
    "canonical": 5546439.1748046875,
    "external": 20288935.997168064
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs",
     "s": "good",
     "d": "Zero knowledge cryptography is used to ensure state correctness. Proofs are first verified on Arbitrum One and finally on Ethereum."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on the base chain, which ultimately gets published on Ethereum."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "sxnetwork",
   "slug": "sxnetwork",
   "ten": "SX Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 23376136,
   "d7": 0.02820835560460022,
   "chiaTvs": {
    "native": 0,
    "canonical": 23376137.44000244,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 4d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow 6 WHITELISTED actors watching the chain to prove that the state is incorrect. There are fewer than 5 Challengers external to the Operator among these. Interactive proofs (INT) require multiple transactions over time to resolve. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "metis",
   "slug": "metis",
   "ten": "Metis Andromeda",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OVM",
   "tvs": 23246302,
   "d7": -0.015236148353344192,
   "chiaTvs": {
    "native": 0,
    "canonical": 23246303.248272657,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The single address acting as a sequencer on L1 is not trustlessly linkable to the claim of multiple decentralized sequencers being used."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve.Anyone can submit challenge requests. However, permissioned actors are needed to create the challenge and to delete successfully disputed state roots. Additionally, the current permissioned actors (GameCreator and Security Council minority) can collude and finalize malicious state roots."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Security Council minority",
     "s": "warning",
     "d": "Only the whitelisted proposer can update state roots on L1, so in the event of failure the withdrawals are frozen. The Security Council minority can be alerted to enforce censorship resistance because they own the proposer registry, controlling the active whitelisted proposer."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "galxegravity",
   "slug": "galxegravity",
   "ten": "Gravity",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 22820510,
   "d7": -0.02313299503041788,
   "chiaTvs": {
    "native": 0,
    "canonical": 21945578,
    "external": 874934.046875
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2y 9mo delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "immutablezkevm",
   "slug": "immutablezkevm",
   "ten": "Immutable zkEVM",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 20326546,
   "d7": -0.0021069773853646945,
   "chiaTvs": {
    "native": 24276.419921875,
    "canonical": 20302269.162109375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "rise",
   "slug": "rise",
   "ten": "RISE",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 19363712,
   "d7": 0.02294172706025388,
   "chiaTvs": {
    "native": 0,
    "canonical": 109646.3112487793,
    "external": 19254066
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "warning",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. The system currently operates with a closed set of 1 whitelisted challenger."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are checked against the DACert Verifier data roots, signed off by EigenDA operators."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "soneium",
   "slug": "soneium",
   "ten": "Soneium",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 19025286,
   "d7": -0.02009614811123217,
   "chiaTvs": {
    "native": 820992.7475585938,
    "canonical": 7692466.101583481,
    "external": 10511829.222587824
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "fuel",
   "slug": "fuel",
   "ten": "Fuel Ignition",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 17404586,
   "d7": 0.008490293810544225,
   "chiaTvs": {
    "native": 0,
    "canonical": 17404586.788772583,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are not checked against the DACert Verifier onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "paradex",
   "slug": "paradex",
   "ten": "Paradex",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "SN Stack",
   "tvs": 17296430,
   "d7": -0.022015082848461764,
   "chiaTvs": {
    "native": 0,
    "canonical": 17296430,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST)",
     "s": "good",
     "d": "STARKs are zero knowledge proofs that ensure state correctness."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Encrypted data is posted on Ethereum as blobs, and a privacy council of 3 members holds the decryption keys. Users are not able to independetly reconstruct the L2 state without relying on the council members."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "apechain",
   "slug": "apechain",
   "ten": "ApeChain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 15674019,
   "d7": -0.08769411795657234,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 15674019
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 4d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 5/7 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "aevo",
   "slug": "aevo",
   "ten": "Aevo",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 14729150,
   "d7": -0.0004598964150677176,
   "chiaTvs": {
    "native": 0,
    "canonical": 12321337.1171875,
    "external": 2407813.125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are not checked against the DACert Verifier onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lumia",
   "slug": "lumia",
   "ten": "Lumia Prism",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 12401900,
   "d7": 0.04747519870051886,
   "chiaTvs": {
    "native": 0,
    "canonical": 12401900.450020812,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. 'Pessimistic' proofs only validate the bridge accounting."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "adi",
   "slug": "adi",
   "ten": "ADI Chain",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 11947094,
   "d7": -0.03421301955001976,
   "chiaTvs": {
    "native": 0,
    "canonical": 4515795,
    "external": 7431298.5
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain (SD)",
     "s": "good",
     "d": "All of the data (SD = state diffs) needed for proof construction is published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "nova",
   "slug": "nova",
   "ten": "Arbitrum Nova",
   "loai": "layer2",
   "dang": "Optimium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 11655034,
   "d7": -0.00882209543837531,
   "chiaTvs": {
    "native": 0,
    "canonical": 11655036.33518009,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "warning",
     "d": "Fraud proofs allow 10 WHITELISTED actors watching the chain to prove that the state is incorrect. At least 5 Challengers are external to the Operator. Interactive proofs (INT) require multiple transactions over time to resolve. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "warning",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 5/6 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 28d of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "haust",
   "slug": "haust",
   "ten": "Haust Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 11330473,
   "d7": -0.0010648398230698186,
   "chiaTvs": {
    "native": 0,
    "canonical": 11330474.050446272,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. 'Pessimistic' proofs only validate the bridge accounting."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zklinknova",
   "slug": "zklinknova",
   "ten": "zkLink Nova",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Linea",
   "stack": null,
   "tvs": 11166568,
   "d7": 0.008332724565884186,
   "chiaTvs": {
    "native": 0,
    "canonical": 10256013.914218038,
    "external": 910553.631834723
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs",
     "s": "good",
     "d": "Zero knowledge cryptography is used to ensure state correctness. Proofs are first verified on Linea and finally on Ethereum."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is ultimately NOT published on Ethereum."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ethereal",
   "slug": "ethereal",
   "ten": "Ethereal",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 11053326,
   "d7": -0.0401518691477194,
   "chiaTvs": {
    "native": 0,
    "canonical": 96.5,
    "external": 11053230
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "taiko",
   "slug": "taiko",
   "ten": "Taiko Alethia",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Taiko",
   "tvs": 10633111,
   "d7": -0.04912535737910095,
   "chiaTvs": {
    "native": 0,
    "canonical": 10422509.766862154,
    "external": 210601.87063598633
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone. An inclusion becomes due after 9m 36s. From then on, a whitelisted proposer cannot publish another proposal without processing up to ten due inclusions."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs",
     "s": "good",
     "d": "Every proposal range is verified by exactly two proofs chosen from SGX (Geth), SGX (Reth), SP1 and RISC0, with at least one SP1 or RISC0 proof required. Proof submission is gated by ProverWhitelist, which has 2 whitelisted provers. This can affect liveness but does not allow finalizing invalid state."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. Proposing is gated by PreconfWhitelist, which selects a single active operator for the current epoch and has no permissionless fallback."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "sophon",
   "slug": "sophon",
   "ten": "Sophon",
   "loai": "layer2",
   "dang": "Validium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 10333598,
   "d7": -0.15378732572389253,
   "chiaTvs": {
    "native": 0,
    "canonical": 10333597.390966892,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The Operator actively uses a TransactionFilterer contract, which requires accounts that enqueue or force transactions from L1 to be whitelisted."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on Avail. Transaction data is checked against the Vector bridge data roots, signed off by Avail validators."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zircuit",
   "slug": "zircuit",
   "ten": "Zircuit",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 9414539,
   "d7": -0.0071278318807406205,
   "chiaTvs": {
    "native": 0,
    "canonical": 6275361.995083809,
    "external": 3139176.8520703316
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The L2 code has been modified to allow the sequencer to explicitly censor selected L1->L2 transactions."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Use escape hatch",
     "s": "warning",
     "d": "Users are able to trustlessly exit by submitting a Merkle proof of funds after 1mo with no new state proposals have passed. The escape of ETH and ERC-20 balances is permissionless while the escape of DeFi contract balances is trusted."
    }
   ],
   "xemXet": true,
   "luuTru": false
  },
  {
   "id": "silicon",
   "slug": "silicon",
   "ten": "Silicon",
   "loai": "layer2",
   "dang": "Validium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 8922251,
   "d7": -0.005534276782275027,
   "chiaTvs": {
    "native": 0,
    "canonical": 8922251.568122521,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/3 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since the Security Council can remove the delay on upgrades."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "polygonzkevm",
   "slug": "polygonzkevm",
   "ten": "Polygon zkEVM",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 8081601,
   "d7": -0.005543183023112186,
   "chiaTvs": {
    "native": 0,
    "canonical": 6627342.281955119,
    "external": 1454259.09765625
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. 'Pessimistic' proofs only validate the bridge accounting."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "orderly",
   "slug": "orderly",
   "ten": "Orderly Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 6898943,
   "d7": -0.027015046767551953,
   "chiaTvs": {
    "native": 0,
    "canonical": 247776.78125,
    "external": 6651166.4375
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "mode",
   "slug": "mode",
   "ten": "Mode Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 6811956.5,
   "d7": -0.06429413164993114,
   "chiaTvs": {
    "native": 308679.84375,
    "canonical": 5011075.307198465,
    "external": 1492201.7829589844
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "hashkey",
   "slug": "hashkey",
   "ten": "HashKey Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 6612003.5,
   "d7": 0.009587102455248298,
   "chiaTvs": {
    "native": 0,
    "canonical": 6612003.97265625,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": true,
   "luuTru": false
  },
  {
   "id": "lighter-robinhood",
   "slug": "lighter-robinhood",
   "ten": "Lighter on Robinhood",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Robinhood Chain",
   "stack": null,
   "tvs": 6525401.5,
   "d7": 0.04232822150052651,
   "chiaTvs": {
    "native": 0,
    "canonical": 6525401.350097656,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no guaranteed mechanism to have transactions included if the sequencer is down or censoring. Although users can enqueue messages in the L1 delayed inbox and call forceInclusion on the SequencerInbox, the chain runs ArbOS 61 transaction filtering: an authorized filterer can register any transaction hash in the ArbFilteredTransactionsManager precompile (0x00…0074), after which the state transition function forcibly fails that transaction, including force-included ones, without delay."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on the base chain, which ultimately gets published on Ethereum."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Use escape hatch",
     "s": "good",
     "d": "Users are able to trustlessly exit by submitting a zero knowledge proof of funds."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "eclipse",
   "slug": "eclipse",
   "ten": "Eclipse",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 5623496.5,
   "d7": -0.01387813728680154,
   "chiaTvs": {
    "native": 0,
    "canonical": 5623496.5,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "reya",
   "slug": "reya",
   "ten": "Reya",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 5542148.5,
   "d7": 0.0005977788660527228,
   "chiaTvs": {
    "native": 0,
    "canonical": 99411.2421875,
    "external": 5442737.449999809
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "bobanetwork",
   "slug": "bobanetwork",
   "ten": "Boba Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 5279627,
   "d7": -0.011213962944872757,
   "chiaTvs": {
    "native": 0,
    "canonical": 5209259.29354465,
    "external": 70367.59375
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zora",
   "slug": "zora",
   "ten": "Zora",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 4393910.5,
   "d7": -0.05232822721810182,
   "chiaTvs": {
    "native": 0,
    "canonical": 4393910.2578125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "karak",
   "slug": "k2",
   "ten": "K2",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 4136125.25,
   "d7": -0.00893441571701914,
   "chiaTvs": {
    "native": 0,
    "canonical": 4136125.296875,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "cyber",
   "slug": "cyber",
   "ten": "Cyber",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 2641046,
   "d7": -0.016740071704870796,
   "chiaTvs": {
    "native": 0,
    "canonical": 432802.6052246094,
    "external": 2208243.25
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain. A custom data availability (DA) provider without attestations is used, but data unavailability can be challenged."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "degen",
   "slug": "degen",
   "ten": "Degen Chain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Base Chain",
   "stack": "Arbitrum",
   "tvs": 2152569.25,
   "d7": -0.024263110036915836,
   "chiaTvs": {
    "native": 0,
    "canonical": 2137862.5,
    "external": 14706.819580078125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 4d 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/3 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 6d 15h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "penchain",
   "slug": "penchain",
   "ten": "Pentagon Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 1989931.625,
   "d7": 0.008926517901931108,
   "chiaTvs": {
    "native": 0,
    "canonical": 1989931.669998169,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. 'Pessimistic' proofs only validate the bridge accounting."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "educhain",
   "slug": "edu-chain",
   "ten": "EDU Chain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 1671621.375,
   "d7": 0.023907013452848958,
   "chiaTvs": {
    "native": 26645.869140625,
    "canonical": 1644975.5018226504,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 5d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "fluent",
   "slug": "fluent",
   "ten": "Fluent",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 1648535,
   "d7": 0.18190448374821733,
   "chiaTvs": {
    "native": 0,
    "canonical": 1648534.919380188,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "TEE attestations",
     "s": "bad",
     "d": "State roots are accepted on the basis of an AWS Nitro Enclave preconfirmation and a 2d time delay; the SP1 ZK proof system exists in the contracts but is currently unreachable because CHALLENGER_ROLE has no holders. Effective security reduces to trust the TEE and wait the delay. See the State Validation section below for details."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "dbk",
   "slug": "dbk",
   "ten": "DeBank Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1318704.875,
   "d7": -0.10976590683360321,
   "chiaTvs": {
    "native": 0,
    "canonical": 1318704.875,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "superseed",
   "slug": "superseed",
   "ten": "Superseed",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1099245.5,
   "d7": -0.009793780884955638,
   "chiaTvs": {
    "native": 896422.875,
    "canonical": 161971.09375,
    "external": 40851.47900390625
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "nillion",
   "slug": "nillion",
   "ten": "Nillion",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 870364.5,
   "d7": 0.1902233332398875,
   "chiaTvs": {
    "native": 0,
    "canonical": 870364.5048828125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "shape",
   "slug": "shape",
   "ten": "Shape",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 866306.4375,
   "d7": -0.027127819215346127,
   "chiaTvs": {
    "native": 0,
    "canonical": 866306.4375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lens",
   "slug": "lens",
   "ten": "Lens",
   "loai": "layer2",
   "dang": "Validium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 793334.9375,
   "d7": -0.033257573172708166,
   "chiaTvs": {
    "native": 0,
    "canonical": 793334.953125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on Avail. Transaction data is checked against the Vector bridge data roots, signed off by Avail validators."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lasernet",
   "slug": "lasernet",
   "ten": "Lasernet",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 776297.125,
   "d7": 0.08100735762748434,
   "chiaTvs": {
    "native": 0,
    "canonical": 776297.125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lightlink",
   "slug": "lightlink",
   "ten": "LightLink",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 703839.875,
   "d7": 0.0010804243185611462,
   "chiaTvs": {
    "native": 0,
    "canonical": 703839.8606757373,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "hemi",
   "slug": "hemi",
   "ten": "Hemi",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 625262.5625,
   "d7": 0.0120382996803301,
   "chiaTvs": {
    "native": 0,
    "canonical": 625262.7033850551,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "shibarium",
   "slug": "shibarium",
   "ten": "Shibarium",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 547098.5,
   "d7": -0.034434650319135174,
   "chiaTvs": {
    "native": 0,
    "canonical": 547098.5649280623,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 8/11 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "facet",
   "slug": "facet",
   "ten": "Facet",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": null,
   "tvs": 505559.375,
   "d7": -0.010651734904884913,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 505559.3612499237
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "Users can self sequence transactions by sending them on L1. There is no privileged operator."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "good",
     "d": "Actors watching the chain can challenge state proposals, and challenged proposals must provide ZK proofs. SNARKs are zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "∞",
     "s": "good",
     "d": "Users can exit funds at any time because contracts are not upgradeable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can propose blocks if accompanied by a validity proof. Only the whitelisted proposers can propose state roots for recent blocks optimistically. Anyone can propose optimistically for L2 blocks that are older than 14d."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "xai",
   "slug": "xai",
   "ten": "Xai",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 499891.84375,
   "d7": 0.014557483342911404,
   "chiaTvs": {
    "native": 0,
    "canonical": 499891.8572598025,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 3/5 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "soon",
   "slug": "soon",
   "ten": "Soon Alpha Mainnet",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 383910.21875,
   "d7": -0.03397054446618675,
   "chiaTvs": {
    "native": 0,
    "canonical": 383910.16737627983,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. Sequencer transaction data roots are not checked against the ServiceManager DA bridge data roots onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "superposition",
   "slug": "superposition",
   "ten": "Superposition",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 333626.875,
   "d7": -0.08169449637384907,
   "chiaTvs": {
    "native": 0,
    "canonical": 244159.7904472351,
    "external": 89467.0703125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "metal",
   "slug": "metal",
   "ten": "Metal",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 310170.125,
   "d7": -0.26454592688557543,
   "chiaTvs": {
    "native": 0,
    "canonical": 310170.1299804747,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "b3",
   "slug": "b3",
   "ten": "B3",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Base Chain",
   "stack": "OP Stack",
   "tvs": 277765.28125,
   "d7": -0.00871011261919108,
   "chiaTvs": {
    "native": 0,
    "canonical": 277765.27734375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "alienx",
   "slug": "alienx",
   "ten": "AlienX",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 247201.765625,
   "d7": -0.008436577102486686,
   "chiaTvs": {
    "native": 0,
    "canonical": 247201.75939941406,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "river",
   "slug": "towns",
   "ten": "Towns",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 227984.328125,
   "d7": -0.009146198399924588,
   "chiaTvs": {
    "native": 0,
    "canonical": 227984.328125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "pepeunchained2",
   "slug": "pepe-unchained",
   "ten": "Pepe Unchained",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 202080.953125,
   "d7": -0.14152088667776286,
   "chiaTvs": {
    "native": 0,
    "canonical": 202080.953125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ancient",
   "slug": "ancient8",
   "ten": "Ancient8",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 197328.3125,
   "d7": -0.008400751130417383,
   "chiaTvs": {
    "native": 0,
    "canonical": 197328.3154296875,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "phala",
   "slug": "phala",
   "ten": "Phala",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 164792.59375,
   "d7": 0.07223702187910375,
   "chiaTvs": {
    "native": 0,
    "canonical": 164792.59375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "funki",
   "slug": "funki",
   "ten": "Funki",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 123289.8359375,
   "d7": -0.022238861315976077,
   "chiaTvs": {
    "native": 0,
    "canonical": 123289.83343887329,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain. A custom data availability (DA) provider without attestations is used, but data unavailability can be challenged."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "intmax",
   "slug": "intmax",
   "ten": "INTMAX",
   "loai": "layer3",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Scroll",
   "stack": null,
   "tvs": 106127.3828125,
   "d7": -0.015111650074357996,
   "chiaTvs": {
    "native": 0,
    "canonical": 106127.38091856241,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 7d delay on this operation. Proposing new blocks requires creating ZK proofs."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Self custodied",
     "s": "good",
     "d": "All data required for payments and withdrawals is self custodied by users."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "If the Proposer fails, users can leverage the source available prover to submit proofs to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "swan",
   "slug": "swan",
   "ten": "Swan Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 79889.90625,
   "d7": -0.009517665826889732,
   "chiaTvs": {
    "native": 0,
    "canonical": 79889.90625,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zkfair",
   "slug": "zkfair",
   "ten": "ZKFair",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 61673.91796875,
   "d7": -0.0009928996789780875,
   "chiaTvs": {
    "native": 48955.8984375,
    "canonical": 12718.01962518692,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 3/5 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "If the Proposer fails, users can leverage the source available prover to submit proofs to the L1 bridge. There is a 5d delay for proving and a 5d delay for finalizing state proven in this way. These delays can only be lowered except during the emergency state."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "edgechain",
   "slug": "edgechain",
   "ten": "Edge Chain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 59351.16796875,
   "d7": -0.002257052179925889,
   "chiaTvs": {
    "native": 0,
    "canonical": 59351.1689453125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 5d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 3 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 7d challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/5 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 13d 8h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "appchain",
   "slug": "appchain",
   "ten": "Appchain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 39185.7109375,
   "d7": -0.009146258348857295,
   "chiaTvs": {
    "native": 0,
    "canonical": 39185.7109375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 3d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "r0ar",
   "slug": "r0ar",
   "ten": "R0ar",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 35298.4296875,
   "d7": -0.004957156461062873,
   "chiaTvs": {
    "native": 0,
    "canonical": 35298.4306640625,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "wirex",
   "slug": "wirex",
   "ten": "Wirex Pay Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 24363.80078125,
   "d7": -0.0006537190767244017,
   "chiaTvs": {
    "native": 0,
    "canonical": 24363.79949951172,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/2 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since the Security Council can remove the delay on upgrades."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "deri",
   "slug": "deri",
   "ten": "Deri",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 10932.5400390625,
   "d7": -0.009146715738516664,
   "chiaTvs": {
    "native": 0,
    "canonical": 10932.5400390625,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 1d challenge period."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 7d 8h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "cartesi-prt-honeypot-v2",
   "slug": "cartesi-prt-honeypot-v2",
   "ten": "Cartesi PRT Honeypot v2",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": "Cartesi Rollups",
   "tvs": 1239.0899658203125,
   "d7": 0.040945932905474436,
   "chiaTvs": {
    "native": 0,
    "canonical": 1239.0899658203125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "Users can self sequence transactions by sending them on L1. There is no privileged operator."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "good",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "Not applicable",
     "s": "neutral",
     "d": "Users cannot exit their funds as all deposits are considered donations."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "forknet",
   "slug": "forknet",
   "ten": "Forknet",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 1077.9600830078125,
   "d7": -0.00637851360874464,
   "chiaTvs": {
    "native": 0,
    "canonical": 1077.9599649906158,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. 'Pessimistic' proofs only validate the bridge accounting."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "settlus",
   "slug": "settlus",
   "ten": "Settlus",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 756.9199829101562,
   "d7": -0.009137375678525683,
   "chiaTvs": {
    "native": 0,
    "canonical": 756.9199829101562,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "aztecnetwork",
   "slug": "aztecnetwork",
   "ten": "Aztec Network",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": null,
   "tvs": 585.22998046875,
   "d7": -0.013734915816167481,
   "chiaTvs": {
    "native": 0,
    "canonical": 585.22998046875,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Decentralized Sequencer Set",
     "s": "good",
     "d": "Users can permissionlessly become a sequencer by staking 200 K AZTEC to join the queue and wait to obtain committee-based block production rights. If the pseudo-randomly sampled committees censor proposals, anyone who bonds 332 M AZTEC will join the escape hatch candidate set. Every 2d 23h, a candidate is pseudo-randomly selected to propose and prove checkpoints fully autonomously. A candidate remains in the set until they are selected or leave voluntarily."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain (SD)",
     "s": "good",
     "d": "State diffs needed to reconstruct the L2 state are published in Ethereum blobs. Public transaction bodies and client CHONK proofs propagate offchain, so withholding them can prevent permissionless proving; the affected pending checkpoints expire and are pruned rather than finalized."
    },
    {
     "n": "Exit Window",
     "v": "∞",
     "s": "good",
     "d": "Users can exit funds at any time because contracts are not upgradeable. Governance can register a new canonical rollup and bonus-instance validators automatically follow the latest version, but this does not mutate the current instance, its verifier, messaging contracts, or already-installed EscapeHatch. Governance can change bounded validator-entry parameters and can set the GSE proof-of-possession gas limit too low for new deposits; validators explicitly bound to this instance remain on it."
    },
    {
     "n": "Proposer Failure",
     "v": "Self Propose",
     "s": "good",
     "d": "Checkpoint proposals come from the open sequencer set, with the escape hatch providing a bonded fallback if the sampled committees are censoring or unavailable. Anyone with access to the required hardware can submit epoch root proofs which finalize the proven checkpoints."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ethscriptions",
   "slug": "ethscriptions",
   "ten": "Ethscriptions",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": null,
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "Users can self sequence transactions by sending them on L1. There is no privileged operator."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "good",
     "d": "Actors watching the chain can challenge state proposals, and challenged proposals must provide ZK proofs. SNARKs are zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "∞",
     "s": "good",
     "d": "Users can exit funds at any time because contracts are not upgradeable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can propose blocks if accompanied by a validity proof. Only the whitelisted proposers can propose state roots for recent blocks optimistically. Anyone can propose optimistically for L2 blocks that are older than 14d."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "grvt",
   "slug": "grvt",
   "ten": "GRVT",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The Operator actively uses a TransactionFilterer contract, which requires accounts that enqueue or force transactions from L1 to be whitelisted."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zkcandy",
   "slug": "zkcandy",
   "ten": "zkCandy",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "earnm",
   "slug": "earnm",
   "ten": "Earnm",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 5d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/3 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "playblock",
   "slug": "playblock",
   "ten": "PlayBlock",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum Nova",
   "stack": "Arbitrum",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 11d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 30m challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can become a Proposer after 1mo 4d of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  }
 ]
};
