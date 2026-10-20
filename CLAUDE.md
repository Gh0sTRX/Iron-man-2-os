# Claude Code handoff — Iron Man 2 iOS -> PS Vita

**First read [AGENTS.md](AGENTS.md), in full.** It is the canonical, source-grounded engineering contract shared with Codex and other autonomous agents. Do not work before applying its NO-VPK, authenticity, source-evidence, security and stage-order rules.

Repository: private `Gh0sTRX/Iron-man-2-os`; development branch `feature/b24-unified-gameplay`, not lagging `main`. User temporarily has only the ChatGPT mobile app and will move to a PC/Claude Code in a few days; do not require a local PC from the user for ordinary source audits or GitHub CI.

**First task when starting:** inspect `research/b24_unified/g279_vita_walk_persistent_trace/` (G296 authentic ground-at-120-frame fix) and the latest G171 + G279 GitHub Actions runs; locate the earliest *real failing* gameplay-source integration gate and fix that with source-only regression, NOT another free-floating audit. G161 physical Vita user report was walk-in-place; newer G171/G279/G296 are not physically Vita tested. G295 Vita3K GitHub CPU Vulkan device initialization remains blocked; don't rerun unchanged.

After every meaningful commit, use accurate descriptions: host-tested / Vita ARM ELF-linked / Vita3K-rendered / physical Vita verified are **four different levels**. No new VPK until all gates in `research/b24_unified/g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json` are defensibly met. Keep lighting and shadow/sky/alpha stage in place.

Report in concise Turkish with actual commit URL, test run URL and next single blocker. User wants authentic PNG/GIF from captured models/game only, not HTML or AI-made mock gameplay.
