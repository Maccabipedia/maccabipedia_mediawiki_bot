<?php
/**
 * Maccabipedia skin — successor to Metrolook.
 *
 * Modern SkinMustache-based skin. Phase 1 ships the scaffold only; styles
 * and templates port over in subsequent plans. See
 * docs/superpowers/specs/2026-04-25-maccabipedia-skin-rewrite.md.
 *
 * @file
 * @ingroup Skins
 */

namespace MediaWiki\Skin\Maccabipedia;

use SkinMustache;

class SkinMaccabipedia extends SkinMustache {

	/**
	 * Append the `skin-metrolook` compat token to the body class so any
	 * prod content (User CSS, MediaWiki:*.css overrides, parser-function
	 * branches keyed on SKINNAME) keeps applying during the soak window.
	 *
	 * The compat class is removed at Phase 2 + 2 weeks per the rewrite spec
	 * (docs/superpowers/specs/2026-04-25-maccabipedia-skin-rewrite.md).
	 *
	 * Mirrors how the legacy SkinMetrolook adds its own page classes —
	 * `getPageClasses()` is the documented MW idiom for body-class additions.
	 */
	public function getPageClasses( $title ): string {
		return parent::getPageClasses( $title ) . ' skin-metrolook';
	}
}
