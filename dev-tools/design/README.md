# Design-System Verification

Run from the repository root:

```powershell
python dev-tools/design/check_design_system.py
```

The check uses only the Python standard library. It verifies:

- required semantic tokens exist in light, dark, and system-dark themes;
- system-dark values remain identical to explicit dark-mode values;
- documented text, action, navigation, status, focus, and chart combinations meet their contrast thresholds;
- the SVG sprite is parseable and follows the 24 px, 1.75 px, rounded-stroke, `currentColor` contract;
- SVG symbol IDs and the manifest have exact one-to-one parity;
- manifest names are unique and sorted; and
- icon CSS remains token-based rather than embedding theme colors.

This check does not replace browser, visual-regression, forced-color, keyboard, screen-reader, zoom, or responsive testing.
