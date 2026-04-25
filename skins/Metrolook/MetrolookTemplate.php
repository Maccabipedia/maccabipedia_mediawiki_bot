<?php

/**
 * Metrolook - Metro look for website.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * http://www.gnu.org/copyleft/gpl.html
 *
 * @file
 * @ingroup Skins
 */

use MediaWiki\MediaWikiServices;

/**
 * QuickTemplate class for Metrolook skin
 * @ingroup Skins
 */
class MetrolookTemplate extends BaseTemplate
{
	/* Functions */

	/** @var string Saves the personal Tools */
	private $mPersonalTools = '';
	/** @var string Saves Echo notifications */
	private $mPersonalToolsEcho = '';

	/**
	 * @param string $messageName
	 * @return string
	 */
	private function getTiles($messageName = 'metrolook-tiles')
	{
		/**
		 * The message's format is:
		 * * URL to the site|alternative text|image URL
		 *
		 * For example:
		 * * https://www.pidgi.net/wiki/|PidgiWiki|https://images.pidgi.net/pidgiwikitiletop.png
		 * * https://www.pidgi.net/press/|PidgiWiki Press|https://images.pidgi.net/pidgipresstiletop.png
		 * * https://www.pidgi.net/jcc/|The JCC|https://images.pidgi.net/jcctiletop.png
		 * * https://www.petalburgwoods.com/|Petalburg Woods|https://images.pidgi.net/pwntiletop.png
		 */
		$tileMessage = $this->getSkin()->msg($messageName);
		$tiles = '';
		if ($tileMessage->isDisabled()) {
			return $tiles;
		}

		$lines = explode("\n", $tileMessage->text());

		foreach ($lines as $line) {
			if (strpos($line, '*') !== 0) {
				continue;
			} else {
				$line = explode('|', trim($line, '* '), 3);
				$siteURL = $line[0];
				$altText = $line[1];

				// Maybe it's the name of a MediaWiki: message? I18n is
				// always nice, so at least try it and see what happens...
				$linkMsgObj = $this->getSkin()->msg($altText);
				if (!$linkMsgObj->isDisabled()) {
					$altText = $linkMsgObj->parse();
				}

				$imageURL = $line[2];
				$tiles .= '<div class="tile-wrapper"><div class="tile">' .
					'<a href="' . htmlspecialchars($siteURL, ENT_QUOTES) . '"><img src="' .
					htmlspecialchars($imageURL, ENT_QUOTES) .
					'" alt="' . htmlspecialchars($altText, ENT_QUOTES) . '" /></a>' .
					'</div></div>';
			}
		}

		return $tiles;
	}


	/**
	 * Outputs the entire contents of the (X)HTML page
	 */
	public function execute()
	{
		$skin = $this->getSkin();
		$this->data['namespace_urls'] = $this->data['content_navigation']['namespaces'];
		$this->data['view_urls'] = $this->data['content_navigation']['views'];
		$this->data['action_urls'] = $this->data['content_navigation']['actions'];
		$this->data['variant_urls'] = $this->data['content_navigation']['variants'];

		// Move the watch/unwatch star outside of the collapsed "actions" menu to the main "views" menu
		if ($this->config->get('MetrolookUseIconWatch')) {
			$mode = MediaWikiServices::getInstance()->getWatchlistManager()
				->isWatched($skin->getUser(), $skin->getRelevantTitle())
				? 'unwatch'
				: 'watch';

			if (isset($this->data['action_urls'][$mode])) {
				$this->data['view_urls'][$mode] = $this->data['action_urls'][$mode];
				unset($this->data['action_urls'][$mode]);
			}
		}

		$personalTools = $this->getPersonalTools();

		foreach ($personalTools as $key => $item) {
			// Echo notifications go to their own, special place; other personal tools are handled more normally
			if (in_array($key, ['notifications-alert', 'notifications-notice'])) {
				$this->mPersonalToolsEcho .= $this->makeMetroLookListItem($key, $item);
			} else {
				$this->mPersonalTools .= $this->makeMetroLookListItem($key, $item);
			}
		}

		$this->data['pageLanguage'] =
			$skin->getTitle()->getPageViewLanguage()->getHtmlCode();

		// Output HTML Page
?>

		<div class="maccabipedia-site-container">
			<div class="page-overlay"></div>

			<?php include 'customize/includes/app-header.php' ?>

			<div class="maccabipedia-page-title">
				<div class="content">
					<?php
					$this->html('title');
					?>
				</div>
			</div>

			<main>
				<a id="top"></a>

				<?php
				// Loose comparison with '!=' is intentional, to catch null and false too, but not '0'
				if ($this->data['title'] != '') {
				?>
				<?php
				} ?>
				<?php $this->html('prebodyhtml') ?>
				<div id="bodyContent" class="mw-body-content">
					<?php
					if ($this->data['isarticle']) {
					?>
						<div id="siteSub" class="noprint"><?php $this->msg('tagline') ?></div>
					<?php
					}
					?>
					<div id="contentSub" <?php $this->html('userlangattributes') ?>><?php
																					$this->html('subtitle')
																					?></div>
					<?php
					if ($this->data['undelete']) {
					?>
						<div id="contentSub2"><?php $this->html('undelete') ?></div>
					<?php
					}
					?>
					<?php
					if ($this->data['newtalk']) {
					?>
						<div class="usermessage"><?php $this->html('newtalk') ?></div>
					<?php
					}
					?>
					<?php
					$this->html('bodycontent');

					if ($this->data['catlinks']) {
						$this->html('catlinks');
					}
					?>
					<div class="visualClear"></div>
					<?php
					if ($this->data['dataAfterContent']) {
						$this->html('dataAfterContent');
					}
					?>
					<div class="visualClear"></div>
					<?php $this->html('debughtml'); ?>
				</div>
			</main>

			<?php include 'customize/includes/app-footer.php' ?>
		</div>

	<?php
	}

	/**
	 * Render a series of portals
	 *
	 * @param array $portals
	 */
	protected function renderPortals($portals)
	{
		// Force the rendering of the following portals
		if (!isset($portals['SEARCH'])) {
			$portals['SEARCH'] = true;
		}
		if (!isset($portals['TOOLBOX'])) {
			$portals['TOOLBOX'] = true;
		}
		if (!isset($portals['LANGUAGES'])) {
			$portals['LANGUAGES'] = true;
		}
		// Render portals
		foreach ($portals as $name => $content) {
			if ($content === false) {
				continue;
			}

			// Numeric strings gets an integer when set as key, cast back - T73639
			$name = (string)$name;

			switch ($name) {
				case 'SEARCH':
					break;
				case 'TOOLBOX':
					$this->renderPortal('tb', $this->data['sidebar']['TOOLBOX'], 'toolbox', 'SkinTemplateToolboxEnd');
					// Hook point for the ShoutWiki Ads extension
					$skin = $this;
					Hooks::run('MetrolookAfterToolbox', [&$skin]);
					break;
				case 'LANGUAGES':
					if ($this->data['language_urls'] !== false) {
						$this->renderPortal('lang', $this->data['language_urls'], 'otherlanguages');
					}
					break;
				default:
					$this->renderPortal($name, $content);
					break;
			}
		}
	}

	/**
	 * @param string $name
	 * @param array $content
	 * @param null|string $msg
	 * @param null|string|array $hook
	 */
	protected function renderPortal($name, $content, $msg = null, $hook = null)
	{
		if ($msg === null) {
			$msg = $name;
		}
		$msgObj = $this->getMsg($msg);
		$labelId = Sanitizer::escapeIdForAttribute("p-$name-label");
	?>
		<div class="portal" role="navigation" id='<?php
													echo Sanitizer::escapeIdForAttribute("p-$name")
													?>' <?php
														echo Linker::tooltip('p-' . $name)
														?> aria-labelledby='<?php echo $labelId ?>'>
			<h5<?php $this->html('userlangattributes') ?> id='<?php echo $labelId ?>'><?php
																						echo htmlspecialchars($msgObj->exists() ? $msgObj->text() : $msg);
																						?></h5>
				<div class="body">
					<?php
					if (is_array($content)) {
					?>
						<ul>
							<?php
							foreach ($content as $key => $val) {
								echo $this->makeMetroLookListItem($key, $val);
							}
							if ($hook !== null) {
								$skin = $this;
								Hooks::run($hook, [&$skin, true]);
							}
							?>
						</ul>
					<?php
					} else {
						// Allow raw HTML block to be defined by extensions
						echo $content;
					}

					$afterPortlet = '';
					$content = $this->getSkin()->getAfterPortlet($name);
					if ($content !== '') {
						$afterPortlet = Html::rawElement(
							'div',
							['class' => ['after-portlet', 'after-portlet-' . $name]],
							$content
						);
					}

					echo $afterPortlet;
					?>
				</div>
		</div>
		<?php
	}

	/**
	 * Render one or more navigations elements by name, automatically reversed by css
	 * when UI is in RTL mode
	 *
	 * @param array $elements
	 */
	protected function renderNavigation($elements)
	{
		// If only one element was given, wrap it in an array, allowing more
		// flexible arguments
		if (!is_array($elements)) {
			$elements = [$elements];
		}
		// Render elements
		foreach ($elements as $name => $element) {
			switch ($element) {
				case 'NAMESPACES':
		?>
					<div id="p-namespaces" role="navigation" class="vectorTabs<?php
																				if (count($this->data['namespace_urls']) == 0) {
																					echo ' emptyPortlet';
																				}
																				?>" aria-labelledby="p-namespaces-label">
						<h5 id="p-namespaces-label"><?php $this->msg('namespaces') ?></h5>
						<ul<?php $this->html('userlangattributes') ?>>
							<?php
							foreach ($this->data['namespace_urls'] as $key => $item) {
								echo "\t\t\t\t\t\t\t" . $this->makeMetroLookListItem($key, $item, [
									'metrolook-wrap' => true,
								]) . "\n";
							}
							?>
							</ul>
					</div>
				<?php
					break;
				case 'VARIANTS':
				?>
					<div id="p-variants" role="navigation" class="vectorMenu<?php
																			if (count($this->data['variant_urls']) == 0) {
																				echo ' emptyPortlet';
																			}
																			?>" aria-labelledby="p-variants-label">
						<?php
						// Replace the label with the name of currently chosen variant, if any
						$variantLabel = $this->getMsg('variants')->text();
						foreach ($this->data['variant_urls'] as $item) {
							if (isset($item['class']) && stripos($item['class'], 'selected') !== false) {
								$variantLabel = $item['text'];
								break;
							}
						}
						?>
						<h5 id="p-variants-label">
							<span><?php echo htmlspecialchars($variantLabel) ?></span>
						</h5>

						<div class="menu">
							<ul>
								<?php
								foreach ($this->data['variant_urls'] as $key => $item) {
									echo "\t\t\t\t\t\t\t\t" . $this->makeMetroLookListItem($key, $item) . "\n";
								}
								?>
							</ul>
						</div>
					</div>
				<?php
					break;
				case 'VIEWS':
				?>
					<div id="p-views" role="navigation" class="vectorTabs<?php
																			if (count($this->data['view_urls']) == 0) {
																				echo ' emptyPortlet';
																			}
																			?>" aria-labelledby="p-views-label">
						<h5 id="p-views-label"><?php $this->msg('views') ?></h5>
						<ul<?php $this->html('userlangattributes') ?>>
							<?php
							foreach ($this->data['view_urls'] as $key => $item) {
								echo "\t\t\t\t\t\t\t" . $this->makeMetroLookListItem($key, $item, [
									'metrolook-wrap' => true,
									'metrolook-collapsible' => true,
								]) . "\n";
							}
							?>
							</ul>
					</div>
				<?php
					break;
				case 'ACTIONS':
				?>
					<div id="p-cactions" role="navigation" class="vectorMenu actionmenu<?php
																						if (count($this->data['action_urls']) == 0) {
																							echo ' emptyPortlet';
																						}
																						?>" aria-labelledby="p-cactions-label">
						<h5 id="p-cactions-label"><span></span></h5>

						<div class="menu">
							<ul<?php $this->html('userlangattributes') ?>>
								<?php
								foreach ($this->data['action_urls'] as $key => $item) {
									echo "\t\t\t\t\t\t\t\t" . $this->makeMetroLookListItem($key, $item) . "\n";
								}
								?>
								</ul>
						</div>
					</div>
				<?php
					break;
				case 'PERSONAL':
				?>
					<div id="p-personal" role="navigation" class="<?php
																	if (count($this->data['personal_urls']) == 0) {
																		echo ' emptyPortlet';
																	}
																	?>" aria-labelledby="p-personal-label">
						<h5 id="p-personal-label"><?php $this->msg('personaltools') ?></h5>
						<ul<?php $this->html('userlangattributes') ?>>
							<?php
							echo $this->mPersonalTools;
							?>
							</ul>
					</div>
				<?php
					break;
				case 'SEARCH':
				?>
					<div class="search-content" role="search">
						<form action="<?php $this->text('wgScript') ?>" id="searchform">
							<div
								<?php echo $this->config->get('MetrolookUseSimpleSearch') ? ' id="simpleSearch"' : '' ?>>
								<?php
								echo $this->makeSearchInput(['id' => 'searchInput', 'class' => 'text-field']);
								echo Html::hidden('title', $this->get('searchtitle'));
								/* We construct two buttons (for 'go' and 'fulltext' search modes),
							 * but only one will be visible and actionable at a time (they are
							 * overlaid on top of each other in CSS).
							 * * Browsers will use the 'fulltext' one by default (as it's the
							 *   first in tree-order), which is desirable when they are unable
							 *   to show search suggestions (either due to being broken or
							 *   having JavaScript turned off).
							 * * The mediawiki.searchSuggest module, after doing tests for the
							 *   broken browsers, removes the 'fulltext' button and handles
							 *   'fulltext' search itself; this will reveal the 'go' button and
							 *   cause it to be used.
							 */
								echo $this->makeSearchButton(
									'fulltext',
									['id' => 'mw-searchButton', 'class' => 'searchButton mw-fallbackSearchButton']
								);
								echo $this->makeSearchButton(
									'go',
									['id' => 'searchButton', 'class' => 'searchButton']
								);
								?>
							</div>
						</form>
					</div>

<?php
					break;
			}
		}
	}

	/**
	 * @inheritDoc
	 */
	public function makeLink($key, $item, $options = [])
	{
		$html = parent::makeLink($key, $item, $options);
		// Add an extra wrapper because our CSS is weird
		if (isset($options['metrolook-wrap']) && $options['metrolook-wrap']) {
			$html = Html::rawElement('span', [], $html);
		}
		return $html;
	}

	/**
	 * Helper function for calling Skin::makeListItem
	 * @param string $key
	 * @param array $item
	 * @param array $options
	 * @return array
	 */
	public function makeMetroLookListItem($key, $item, $options = [])
	{
		// For fancy styling of watch/unwatch star
		if (
			$this->config->get('MetrolookUseIconWatch')
			&& ($key === 'watch' || $key === 'unwatch')
		) {
			$item['class'] = rtrim('icon ' . $item['class'], ' ');
			$item['primary'] = true;
		}
		// Add CSS class 'collapsible' to links which are not marked as "primary"
		if (
			isset($options['metrolook-collapsible']) && $options['metrolook-collapsible']
		) {
			$item['class'] = rtrim('collapsible ' . $item['class'], ' ');
		}
		return $this->getSkin()->makeListItem($key, $item, $options);
	}
}
?>

<script type="text/javascript">
	function closeOverlay(overlay) {
		overlay.classList.remove('active')
		closeNavigationBar()
	}

	function closeNavigationBar() {
		const navigationBarToggler = document.querySelector('.maccabipedia-navigation-bar .activation-toggler')
		navigationBarToggler.checked = false
	}
</script>