# Module Dependency Rules

- Status: accepted
- Canonical for: source dependency direction and cross-module access
- Planned verification: automated architecture check

## Direction

```text
web -> generated API client -> API host

hosts/bootstrap -> modules and platform composition
adapters        -> ports + public contracts
application     -> domain + owned ports
domain          -> standard library + explicitly approved value libraries
```

## Rules

1. Domain code cannot import application, ports, adapters, hosts, platform infrastructure, FastAPI, database libraries, or provider SDKs.
2. Application code cannot import concrete adapters or hosts.
3. Adapters implement ports; application code never selects an adapter.
4. Hosts and bootstrap select adapters from validated configuration.
5. A module cannot import another module's `domain`, `adapters`, or persistence internals.
6. Cross-module synchronous calls use the target module's published application facade.
7. Cross-module asynchronous calls use registered versioned events.
8. The web application uses the generated API client rather than database, provider, or backend-internal interfaces.
9. Extensions depend on the public provider SDK and executable contracts, not backend internals.
10. A shared package may contain technical primitives only when ownership cannot sensibly belong to one domain. It must not become a miscellaneous business-policy container.

## Temporary Exceptions

Any exception must be narrow, recorded in the architecture verification configuration, linked to a remediation decision, and assigned an expiration or review trigger.

