<?php
/**
 * Page footer for the Maccabipedia skin (SkinMustache-based).
 *
 * Identical-output port of skins/Metrolook/customize/includes/app-footer.php
 * adapted for SkinMustache: receives `$skin` and `$lastmodHtml` (pre-rendered
 * "last modified" line, may be empty) from SkinMaccabipedia::getTemplateData()
 * instead of `$this->data['lastmod']` / `$this->html('lastmod')`.
 */

require_once __DIR__ . '/menu-helpers.php';

$mwResourceURL = mp_static_base_url() . '/resources/assets/';

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
                    <a href="<?php echo htmlspecialchars(mp_page_url($titleText)); ?>"><?php echo htmlspecialchars($label); ?></a>
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
                <?php if (!empty($lastmodHtml)): ?>
                    <span id="lastmod"><?php echo $lastmodHtml; ?></span>
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
