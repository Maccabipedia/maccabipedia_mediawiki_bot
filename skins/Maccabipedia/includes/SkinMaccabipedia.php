<?php
/**
 * Maccabipedia skin — successor to Metrolook.
 *
 * Modern SkinMustache-based skin. Visual parity with Metrolook is
 * delivered (during Phases 1–3) by reusing the legacy skin's already-
 * registered ResourceLoader modules (`skins.metrolook.styles`,
 * `skins.metrolook.js`, …) — the new skin contributes the modern PHP
 * shell and the Mustache template; CSS/JS migration follows in Phase 4.
 *
 * See docs/superpowers/specs/2026-04-25-maccabipedia-skin-rewrite.md.
 *
 * @file
 * @ingroup Skins
 */

namespace MediaWiki\Skin\Maccabipedia;

use Html;
use OutputPage;
use SkinMustache;

class SkinMaccabipedia extends SkinMustache {

	/**
	 * Body classes:
	 * - `skin-maccabipedia` is auto-emitted by MW from the valid skin name.
	 * - `skin-metrolook` is a compat token so any prod content / templates
	 *   keyed on the legacy skin name keep applying during the soak window
	 *   (drops at Phase 2 + 2 weeks per the rewrite spec).
	 * - `metrolook-nav-directionality` matches what Metrolook adds in
	 *   SkinMetrolook::getPageClasses() — a number of CSS rules in
	 *   skins.metrolook.styles use this class as a directionality root,
	 *   so we must keep it while we share Metrolook's stylesheet.
	 */
	public function getPageClasses( $title ): string {
		return parent::getPageClasses( $title )
			. ' skin-metrolook'
			. ' metrolook-nav-directionality';
	}

	/**
	 * Pull in Metrolook's existing styles + scripts. The new skin contributes
	 * a modern PHP shell + Mustache template; the actual CSS rules (which
	 * MaccabiPedia authored under skins/Metrolook/customize/styles/) keep
	 * loading from the legacy module names. Phase 4's cutover will move the
	 * source LESS/JS into skins/Maccabipedia/ and rename the modules.
	 */
	public function initPage( OutputPage $out ) {
		parent::initPage( $out );
		$out->addModuleStyles( [
			'skins.metrolook.styles',
			'skins.metrolook.interface',
		] );
		$out->addModules( [ 'skins.metrolook.js' ] );
	}

	/**
	 * Build the search-box form using values from SkinMustache's
	 * `data-search-box` template-data array, in the same shape Metrolook's
	 * QuickTemplate emitted via $this->renderNavigation(['SEARCH']).
	 *
	 * Done as a separate method so getTemplateData() stays readable.
	 */
	private function buildSearchBoxHtml( array $searchBoxData ): string {
		$formAction = $searchBoxData['form-action'] ?? '';
		$pageTitle = $searchBoxData['page-title'] ?? '';
		$inputHtml = $searchBoxData['html-input'] ?? '';
		$buttonFallback = $searchBoxData['html-button-search-fallback'] ?? '';
		$buttonGo = $searchBoxData['html-button-search'] ?? '';

		$hidden = Html::hidden( 'title', $pageTitle );

		return <<<HTML
<div class="search-content" role="search">
	<form action="{$formAction}" id="searchform">
		<div id="simpleSearch">
			{$inputHtml}
			{$hidden}
			{$buttonFallback}
			{$buttonGo}
		</div>
	</form>
</div>
HTML;
	}

	/**
	 * Pluck the "Last modified" footer line out of SkinMustache's
	 * `data-footer.array-items` (key 'info'), matching what Metrolook
	 * pulled from $this->data['lastmod'] / $this->html('lastmod').
	 *
	 * Returns the lastmod HTML or empty string if absent.
	 */
	private function extractLastmodHtml( array $data ): string {
		$footerItems = $data['data-footer']['array-items'] ?? [];
		foreach ( $footerItems as $section ) {
			if ( ( $section['name'] ?? '' ) !== 'info' ) {
				continue;
			}
			// 'info' section's html-items contains the lastmod <li>.
			$html = $section['html-items'] ?? '';
			// Strip the <ul> wrapper but keep the inner content; matches
			// Metrolook's narrower output (just the lastmod line, no list).
			if ( preg_match( '/<li[^>]*id="lastmod"[^>]*>(.*?)<\/li>/s', $html, $m ) ) {
				return $m[1];
			}
		}
		return '';
	}

	/**
	 * Output-buffer the legacy customize/includes/*.php templates and
	 * surface their rendered HTML as Mustache variables. The included
	 * files reference $skin (this Skin instance) and $searchBoxHtml /
	 * $lastmodHtml (pre-rendered) — they no longer touch $this.
	 */
	public function getTemplateData() {
		$data = parent::getTemplateData();

		$skin = $this;
		$searchBoxHtml = $this->buildSearchBoxHtml( $data['data-search-box'] ?? [] );
		$lastmodHtml = $this->extractLastmodHtml( $data );

		$includesDir = __DIR__ . '/../customize/includes';

		ob_start();
		require $includesDir . '/app-header.php';
		$data['html-app-header'] = ob_get_clean();

		ob_start();
		require $includesDir . '/app-footer.php';
		$data['html-app-footer'] = ob_get_clean();

		return $data;
	}
}
