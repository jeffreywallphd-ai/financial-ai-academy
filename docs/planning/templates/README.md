# Planning Templates

Use these templates for new planning artifacts:

- [Capability plan](capability-template.md)
- [Vertical slice](vertical-slice-template.md)
- [Agent work packet](work-packet-template.md)
- [Decision request](decision-request-template.md)

Replace every placeholder, remove inapplicable prompts, and retain the machine-readable metadata block. Add the new artifact to [the planning register](../register.md) in the same change.

Reserve a collision-resistant ID first with `python dev-tools/planning/reserve_id.py reserve --kind <CAP|DEC|SLI|WRK> --owner <owner>`. For work packets, declare bounded repository-relative write scopes and generated artifacts before planning approval; leave activation claim fields null until authorized implementation begins.

Do not add approval fields or approval-history sections. Record authorized human decisions only in the ignored local ledger; never use an earlier approval to populate a later stage. A consolidated response may cover only an explicitly enumerated homogeneous DEC or slice-packet set, with one local record per artifact. The [planning skill suite](../skills/README.md) validates and operates these templates.
