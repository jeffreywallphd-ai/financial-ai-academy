# Backend Bootstrap

Bootstrap selects validated adapters and composes hosts from configuration. It is the only intended location for deployment-profile provider selection.

Bootstrap must fail clearly when required capabilities, secrets, migrations, or secure configuration are unavailable. Read operations must not silently install or repair providers.

