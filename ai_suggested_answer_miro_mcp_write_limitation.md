# AI Suggested Answer
AI can be wrong, so ALWAYS VERIFY each answer before sending to customers. Tag the team if you are unsure.

## TL;DR
[Original question](https://miro.slack.com/archives/C09EDAVACV9/p1775556844557219)

This is usually **not a Claude bug** by itself. In most cases, it is either:
1. **Configuration/permission scope** (MCP not enabled, wrong OAuth team selected, missing board edit rights), or
2. An **actual product limitation for specific object types** (today MCP write support is scoped to selected formats, not every board object).

## Suggested answer to send
Short answer: **both are possible** depending on what “can’t write” means.

If Claude cannot write **anything at all**, that is most likely a setup or permission issue:
> check MCP enablement, OAuth/team selection, board access level, and that the board URL is explicitly included in the prompt.

If Claude can read but cannot create/update **some item types** (for example shapes/stickies/text), that is a **current MCP capability boundary**, not user misconfiguration.

What is supported today on the official MCP path is write for specific tool families (for example docs/tables/diagrams), while other board primitives may still be read-only via MCP.

## Fast triage checklist
1. Confirm MCP is enabled for org/team (Enterprise needs admin enablement).
2. Re-auth OAuth and select the team that owns the board.
3. Confirm the user has edit rights on the board itself.
4. Prompt with full board URL (MCP won’t auto-discover private boards).
5. Run a known write-capable action (`doc_create`, `table_create`, or `diagram_create`) to split “setup issue” vs “unsupported object type”.

## Internal assessment
**Estimated priority:** Medium  
**Estimated impact:** Medium (can block customer workflows expecting full object write parity)  
**Issue summary:** Customer confusion is caused by a mix of setup failures and real MCP write-scope limits by object type.  
**Difficulty of fix:** Low for misconfiguration; higher for unsupported object-type writes (requires MCP/API capability expansion).

## Resources used
1. https://miro.slack.com/archives/C09EDAVACV9/p1775556844557219
2. https://help.miro.com/hc/en-us/articles/31624028247058-Miro-MCP-Server-overview
3. https://help.miro.com/hc/en-us/articles/31625761037202-Miro-MCP-Server-admin-guide
4. https://help.miro.com/hc/en-us/articles/31625301583890-How-to-enable-Miro-s-MCP-Server-user-guide
5. https://miro.slack.com/archives/C09EDAVACV9/p1773921160593029
