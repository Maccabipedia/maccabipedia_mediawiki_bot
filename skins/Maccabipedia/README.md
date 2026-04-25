# Maccabipedia skin

Modern `SkinMustache`-based replacement for the Metrolook skin. Vendored under `skins/Maccabipedia/` and tracked in this repo (no upstream — this is a from-scratch MaccabiPedia skin, not a fork).

## Status

Phase 1 (this branch): scaffold only. Renders pages without PHP errors but is not yet visually polished.

Phase 2: port styles + templates so visual diff against Metrolook is clean.

Phase 3: port JavaScript + audit jQuery dependencies.

Phase 4: cutover (`$wgDefaultSkin = "Maccabipedia"`) + delete `skins/Metrolook/`.

See `docs/superpowers/specs/2026-04-25-maccabipedia-skin-rewrite.md` for the full design.

## Local development

The skin loads alongside Metrolook in the local Docker stack. Default skin stays `Metrolook`; visit any page with `?useskin=maccabipedia` to render with the new skin.

```bash
cd infra/local-wiki && docker compose up -d
# Then visit http://localhost:8080/עמוד_ראשי?useskin=maccabipedia
```

## License

GPL-2.0-or-later (see `COPYING`).
