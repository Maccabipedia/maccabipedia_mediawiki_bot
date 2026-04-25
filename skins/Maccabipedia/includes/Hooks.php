<?php
/**
 * Hook handlers for the Maccabipedia skin.
 *
 * Registered via skin.json's HookHandlers map. Currently a no-op — the
 * scaffold doesn't need any hook logic yet. Kept as a placeholder so the
 * registration plumbing is in place for Plans 3+.
 */

namespace MediaWiki\Skin\Maccabipedia;

use MediaWiki\Hook\BeforePageDisplayHook;

class Hooks implements BeforePageDisplayHook {
	/**
	 * The interface in MW 1.39 declares this method without parameter type
	 * hints (`onBeforePageDisplay($out, $skin): void`); adding them here
	 * would violate LSP and refuse to load. When prod upgrades past the MW
	 * release that adds `OutputPage`/`Skin` types to the interface, this
	 * method should grow the matching type hints — until then, leave them off.
	 *
	 * @param \OutputPage $out
	 * @param \Skin $skin
	 */
	public function onBeforePageDisplay( $out, $skin ): void {
		// Intentionally empty in Plan 1. Plans 3+ will wire skin-specific
		// modules / preferences here.
	}
}
