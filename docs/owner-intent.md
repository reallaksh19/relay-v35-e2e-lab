# SYNTHETIC LAB OWNER PROMPT — NOT AN ORIGINAL CHAT AUTHENTICATION

Build a small Python application that reads an inventory CSV containing `sku`, `quantity`, and `unit_price`. Reject malformed data (including duplicate SKU, negative quantity, non-finite price and missing fields), and produce deterministic JSON with per-item inventory value and aggregate total.

Split parser/validation and reporting into independently testable responsibilities. Preserve this verbatim synthetic requirement and its first GitHub mirror. Publish only evidence from actual code/tests/PR heads. Review each candidate independently and demonstrate that a replacement agent can continue without the previous conversation.

**Non-goals:** external databases, production accounts, billing/financial authorization, privacy export, live GitHub publishing without explicit separate lab-only approval, automatic merging, inference of programme acceptance from tests alone.

**Acceptance claims:**
- C1: Valid CSV is parsed with exact decimal money semantics and reproducible row order.
- C2: Malformed/missing/duplicate/negative records fail closed with useful error messages.
- C3: CLI outputs deterministically sorted JSON with exact per-row and aggregate decimal amounts.
- C4: Evidence and current CI are SHA-pinned; changes invalidate prior evidence.
- C5: Separate reviewers and isolated successors can reconstruct the next legitimate action from GitHub only.

**Original source:** SYNTHETIC_OWNER_LAB_SEED, NOT_AUTHENTICATED_CHAT_SOURCE.
