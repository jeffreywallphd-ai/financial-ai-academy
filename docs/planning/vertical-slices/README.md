# Vertical Slice Plans

Vertical slices are the smallest end-to-end increments that produce observable user or operator value while respecting module and contract boundaries.

Name files `SLI-####-short-name.md` and start from [the vertical-slice template](../templates/vertical-slice-template.md). Each slice links one parent capability, identifies the contracts and layers it crosses, defines scenario-based acceptance, and lists its agent work packets in dependency order.

Avoid horizontal slices such as “build all persistence” or “build all UI” unless they are independently valuable platform-enabling outcomes with explicit consumers and acceptance evidence.

Use `select-vertical-slice` for deterministic eligibility and scoring. Work-packet authoring requires explicit local selection approval; closure requires separate local completion approval.
