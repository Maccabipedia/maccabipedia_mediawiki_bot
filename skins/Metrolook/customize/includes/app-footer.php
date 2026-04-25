<?php
$mpURL = "https://www.maccabipedia.co.il/";
?>

<footer>
    <section class="about-maccabipedia">
        <div class="content">
            <div class="usefull-links">
                <a href="<?php echo $mpURL . 'מכביפדיה: תרומות'; ?>">תרומות</a>
                <a href="<?php echo $mpURL . 'מכביפדיה: צור קשר'; ?>">יצירת קשר</a>
            </div>

            <div class="social-networks">
                <div class="title">עקבו אחרינו</div>
                <div class="links-container">
                    <a href="https://bit.ly/visit_mp_fb"><i class="fa-brands fa-facebook-f"></i></a>
                    <a href="https://bit.ly/visit_mp_x"><i class="fa-brands fa-x-twitter"></i></a>
                    <a href="https://bit.ly/visit_mp_i"><i class="fa-brands fa-instagram"></i></a>
                    <a href="https://bit.ly/visit_mp_y"><i class="fa-brands fa-youtube"></i></a>
                </div>
            </div>
        </div>
    </section>

    <section class="credits">
        <div class="content">
            <div class="last-edited">
                <?php
                $footerlinks = array('lastmod');
                foreach ($footerlinks as $aLink) {
                    if (isset($this->data[$aLink]) && $this->data[$aLink]) {
                ?> <span id="<?php echo $aLink ?>"><?php $this->html($aLink) ?></span>
                <?php
                    }
                }
                ?>
            </div>

            <div class="all-rights-reserved">
                &copy; מכביפדיה כל הזכויות שמורות
            </div>

            <a href="https://www.mediawiki.org" target="_blank">
                <img src="<?php echo $mpURL; ?>resources/assets/poweredby_mediawiki_88x31.png" />
            </a>
        </div>
    </section>
</footer>