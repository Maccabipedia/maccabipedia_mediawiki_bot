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
use OutputPage;
use Skin;

class Hooks implements BeforePageDisplayHook {
	public function onBeforePageDisplay( OutputPage $out, Skin $skin ): void {
		// Intentionally empty in Plan 1. Plans 3+ will wire skin-specific
		// modules / preferences here.
	}
}
