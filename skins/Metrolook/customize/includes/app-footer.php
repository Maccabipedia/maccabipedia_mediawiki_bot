<?php
/**
 * Page footer for the Metrolook skin: about-section links + social
 * links + last-mod credit + powered-by-MediaWiki image.
 */

$mwResourceURL = $GLOBALS['wgServer'] . $GLOBALS['wgScriptPath']
    . '/resources/assets/';
$pageURL = static function (string $titleText): string {
    $t = Title::newFromText($titleText);
    return $t ? $t->getLocalURL() : '#';
};

$aboutLinks = [
    'תרומות' => 'מכביפדיה: תרומות',
    'יצירת קשר' => 'מכביפדיה: צור קשר',
];
$socialLinks = [
    'fa-facebook-f' => 'https://bit.ly/visit_mp_fb',
    'fa-x-twitter' => 'https://bit.ly/visit_mp_x',
    'fa-instagram' => 'https://bit.ly/visit_mp_i',
    'fa-youtube' => 'https://bit.ly/visit_mp_y',
];
?>

<footer>
    <section class="about-maccabipedia">
        <div class="content">
            <div class="usefull-links">
                <?php foreach ($aboutLinks as $label => $titleText): ?>
                    <a href="<?php echo htmlspecialchars($pageURL($titleText)); ?>"><?php echo htmlspecialchars($label); ?></a>
                <?php endforeach; ?>
            </div>

            <div class="social-networks">
                <div class="title">עקבו אחרינו</div>
                <div class="links-container">
                    <?php foreach ($socialLinks as $iconClass => $url): ?>
                        <a href="<?php echo htmlspecialchars($url); ?>"><i class="fa-brands <?php echo htmlspecialchars($iconClass); ?>"></i></a>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    </section>

    <section class="credits">
        <div class="content">
            <div class="last-edited">
                <?php if (!empty($this->data['lastmod'])): ?>
                    <span id="lastmod"><?php $this->html('lastmod'); ?></span>
                <?php endif; ?>
            </div>

            <div class="all-rights-reserved">
                &copy; מכביפדיה כל הזכויות שמורות
            </div>

            <a href="https://www.mediawiki.org" target="_blank">
                <img src="<?php echo htmlspecialchars($mwResourceURL . 'poweredby_mediawiki_88x31.png'); ?>" />
            </a>
        </div>
    </section>
</footer>
