<?php
/**
 * URL helpers shared by the MaccabiPedia skin templates
 * (app-header.php, app-footer.php).
 *
 * Plain functions over closures so the templates don't need `use`
 * clauses to capture them; function_exists() guards keep the file
 * idempotent under repeated require_once.
 */

if (!function_exists('mp_static_base_url')) {
    /**
     * $wgServer + $wgScriptPath, no trailing slash. Used to build
     * direct URLs to static skin assets that bypass MediaWiki's
     * article router (logo image, powered-by banner, etc.).
     */
    function mp_static_base_url(): string {
        return $GLOBALS['wgServer'] . $GLOBALS['wgScriptPath'];
    }
}

if (!function_exists('mp_page_url')) {
    /**
     * Local URL for a wiki page given its full title text (Hebrew
     * or English, with namespace prefix). Returns '#' if the title
     * can't be parsed so a typo'd menu entry degrades to a dead
     * link instead of a PHP fatal.
     */
    function mp_page_url(string $titleText): string {
        $title = Title::newFromText($titleText);
        return $title ? $title->getLocalURL() : '#';
    }
}
