<?php
use MediaWiki\MediaWikiServices;

$mpURL = "https://www.maccabipedia.co.il/";
$user = $skin->getUser();
$mwPageName = str_replace('"', '&#34;', $this->getSkin()->getRelevantTitle());
$mwNamespace = $this->getSkin()->getTitle()->getNamespace();
$title = $this->getSkin()->getTitle();


# Namespaces which are forbidden for all edit actions
$ForbiddenNameSpacesAllActions = [
    NS_SPECIAL => true,
    NS_MEDIA => true,
];
$ForbiddenAllActionsExist = isset($ForbiddenNameSpacesAllActions[$mwNamespace]);

$RegularNamespaceToTalkNamespaceMapping = [
    NS_MAIN => NS_TALK,
    NS_USER => NS_USER_TALK,
    NS_PROJECT => NS_PROJECT_TALK,
    NS_FILE => NS_FILE_TALK,
    NS_MEDIAWIKI => NS_MEDIAWIKI_TALK,
    NS_TEMPLATE => NS_TEMPLATE_TALK,
    NS_HELP => NS_HELP_TALK,
    NS_CATEGORY => NS_CATEGORY_TALK,
    NS_שיר => NS_שיחת_שיר,
    NS_כדורעף => NS_שיחת_כדורעף,
    NS_כדורסל => NS_שיחת_כדורסל,
    NS_כדורגל => NS_שיחת_כדורגל,
    NS_כדוריד => NS_שיחת_כדוריד,
];

$TalkNamespaceToRegularNamespaceMapping = [
    NS_TALK=> NS_MAIN,
    NS_USER_TALK => NS_USER,
    NS_PROJECT_TALK => NS_PROJECT,
    NS_FILE_TALK => NS_FILE,
    NS_MEDIAWIKI_TALK => NS_MEDIAWIKI,
    NS_TEMPLATE_TALK => NS_TEMPLATE,
    NS_HELP_TALK => NS_HELP,
    NS_CATEGORY_TALK => NS_CATEGORY,
    NS_שיחת_שיר=> NS_שיר,
    NS_שיחת_כדורעף => NS_כדורעף,
    NS_שיחת_כדורסל => NS_כדורסל,
    NS_שיחת_כדורגל => NS_כדורגל,
    NS_שיחת_כדוריד => NS_כדוריד,

];
if ($ForbiddenAllActionsExist === true) {
    $TalkNamespaceExist  = false;
} else {
    $TalkNamespaceExist = isset($RegularNamespaceToTalkNamespaceMapping[$mwNamespace]);
    if ($TalkNamespaceExist === true) {
        $talkNamespace = $RegularNamespaceToTalkNamespaceMapping[$mwNamespace];
        $talkPageTitle = Title::makeTitle($talkNamespace, $title->getText());
        $talkPageUrl = htmlspecialchars($talkPageTitle->getLocalURL());
    } else {
        $RegularNamespace = $TalkNamespaceToRegularNamespaceMapping[$mwNamespace];
        $RegularPageTitle = Title::makeTitle($RegularNamespace, $title->getText());
        $RegularPageUrl = htmlspecialchars($RegularPageTitle->getLocalURL());
    }
}
?>

<header class="app-header">
    <div class="content">
        <i class="fas fa-bars mobile-side-menu-trigger mobile-only"></i>

        <a href="<?php echo $mpURL; ?>" class="homepage-navigation">
            <img src="<?php echo $mpURL . 'skins/Metrolook/assets/images/logo.png'; ?>" />
        </a>

        <nav class="navigation-section-container">
            <div class="pages-navigation-container">
                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <span class="text">מכבי תל אביב</span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <a href="<?php echo $mpURL . 'קטגוריה: היסטוריה'; ?>">ההיסטוריה</a>
                        <a href="<?php echo $mpURL . 'עונות'; ?>">עונות</a>
                        <a href="<?php echo $mpURL . 'פורטל מתקנים'; ?>">מתקנים</a>
                        <a href="<?php echo $mpURL . 'פורטל מפעלים'; ?>">מפעלים</a>
                        <a href="<?php echo $mpURL . 'פורטל מדים'; ?>">מדים</a>
                        <a href="<?php echo $mpURL . 'תארים'; ?>">תארים</a>
                    </div>
                </div>

                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <span class="text">שחקנים וצוות</span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <a href="<?php echo $mpURL . 'פורטל שחקנים'; ?>">שחקנים</a>
                        <a href="<?php echo $mpURL . 'פורטל אנשי צוות'; ?>">אנשי צוות</a>
                    </div>
                </div>

                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <span class="text">אוהדים ותרבות</span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <a href="<?php echo $mpURL . 'שירי קהל'; ?>">שירים</a>
                        <a href="<?php echo $mpURL . 'כרטיסים ומנויים'; ?>">כרטיסים ומנויים</a>
                        <a href="<?php echo $mpURL . 'כרזות משחק'; ?>">כרזות</a>
                        <a href="<?php echo $mpURL . 'קלפים ומדבקות'; ?>">קלפים ומדבקות</a>
                        <a href="<?php echo $mpURL . 'קטגוריה: תפאורות'; ?>">תפאורות</a>
                        <a href="<?php echo $mpURL . 'ארגוני אוהדים'; ?>">ארגונים</a>
                        <a href="<?php echo $mpURL . 'ספריה צהובה'; ?>">ספרים</a>
                        <a href="<?php echo $mpURL . 'קטגוריה: פנזינים'; ?>">פנזינים</a>
                    </div>
                </div>

                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <span class="text">משחקים</span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <a href="<?php echo $mpURL . 'חיפוש משחק'; ?>">חיפוש משחק</a>
                        <a href="<?php echo $mpURL . 'סטטיסטיקות'; ?>">סטטיסטיקות</a>

                    </div>
                </div>

                <div class="navigation-link-block">
                    <a href="<?php echo $mpURL . 'מכבימדיה'; ?>">
                        מכבימדיה
                    </a>
                </div>
            </div>

            <div class="options-navigation-container">
                <?php if ($ForbiddenAllActionsExist !== true) { ?>
                    <div class="dropdown-container">
                        <div class="dropdown-title">
                            <i class="fas fa-pencil-alt option-icon"></i>
                            <span class="text mobile-only">עריכה</span>
                            <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                            <?php if (isset($_GET['oldid'])) {
                                if (isset($_GET['action'])) {
                                    if ($_GET['action'] == "edit") { ?>
                                        <a href="<?php echo $mpURL . $mwPageName; ?>" class="icon-link desktop-only"></a>
                                    <?php }
                                } else { ?>
                                    <a href="<?php echo $mpURL . $mwPageName; ?>?oldid=<?php echo $_GET['oldid']; ?>&action=edit" class="icon-link desktop-only"></a>
                                <?php }
                            } elseif (isset($_GET['action'])) {
                                if ($_GET['action'] == "edit") { ?>
                                    <a href="<?php echo $mpURL . $mwPageName; ?>" class="icon-link desktop-only"></a>
                                <?php }
                            } else { ?>
                                <a href="<?php echo $mpURL . $mwPageName . '?action=edit'; ?>" class="icon-link desktop-only"></a>
                            <?php } ?>
                        </div>

                        <div class="dropdown-content">
                            <?php if ($user->isAllowed('edit')) { ?>
                                <?php if (isset($_GET['oldid'])) {
                                    if (isset($_GET['action'])) {
                                        if ($_GET['action'] == "edit") { ?>
                                            <a href="<?php echo $mpURL . $mwPageName; ?>">חזור לערך</a>
                                        <?php }
                                    } else { ?>
                                        <a href="<?php echo $mpURL . $mwPageName; ?>?oldid=<?php echo $_GET['oldid']; ?>&action=edit">עריכה</a>
                                    <?php }
                                } elseif (isset($_GET['action'])) {
                                    if ($_GET['action'] == "edit") { ?>
                                        <a href="<?php echo $mpURL . $mwPageName; ?>">חזור לערך</a>
                                    <?php }
                                } else { ?>
                                    <a href="<?php echo $mpURL . $mwPageName . '?action=edit'; ?>">עריכה</a>
                                <?php } ?>
                            <?php } ?>

                            <?php if ($TalkNamespaceExist == true) { ?>
                                <a href="<?php echo $talkPageUrl; ?>">שיחת עמוד</a>
                            <?php } elseif (isset($_GET['action']) === false) { ?>
                                <a href="<?php echo $RegularPageUrl ?>">חזור לערך</a>
                            <?php } ?>

                            <a href="<?php echo $mpURL . $mwPageName . '?action=history'; ?>">גרסאות קודמות</a>
                            <a href="<?php echo $mpURL . $mwPageName . '?action=purge&forcerecursivelinkupdate=1'; ?>">רענון העמוד</a>

                            <?php if ($user->isAllowed('protect')) { ?>
                                <a href="<?php echo $mpURL . $mwPageName . '?action=delete'; ?>">מחיקה</a>
                                <a href="<?php echo $mpURL . 'מיוחד:העברת דף/' . $mwPageName; ?>">העברה</a>
                                <a href="<?php echo $mpURL . $mwPageName . '?action=protect'; ?>">הגנה</a>
                            <?php } ?>
                        </div>
                    </div>
                <?php
                }
                ?>

                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <i class="far fa-user option-icon"></i>
                        <span class="text mobile-only">
                            <?php if ($user->isRegistered()) {
                                echo $user->getName();
                            } else {
                                echo 'משתמש';
                            } ?>
                        </span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <?php if ($user->isRegistered()) { ?>
                            <a href="<?php echo $mpURL . "משתמש:" . $user; ?>"><?php echo $user; ?></a>
                            <a href="<?php echo $mpURL . "שיחת משתמש:" . $user; ?>">עמוד השיחה שלי</a>
                            <a href="<?php echo $mpURL . "מיוחד:העדפות"; ?>">העדפות</a>
                            <a href="<?php echo $mpURL . "מיוחד:תרומות/" . $user; ?>">התרומות שלי</a>
                            <a href="<?php echo $mpURL . "מיוחד:יציאה מהחשבון"; ?>">התנתק</a>
                        <?php } else { ?>
                            <a href="<?php echo $mpURL . "מיוחד: כניסה לחשבון"; ?>">כניסה לחשבון</a>
                            <a href="<?php echo $mpURL . "מיוחד: הרשמה לחשבון"; ?>">יצירת חשבון</a>
                            <a href="<?php echo $mpURL . "מיוחד:השיחה שלי"; ?>">שיחה</a>
                        <?php
                        }
                        ?>
                    </div>
                </div>


                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <i class="fas fa-cogs option-icon"></i>
                        <span class="text mobile-only">אפשרויות</span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <a href="<?php echo $mpURL . 'מיוחד:שינויים אחרונים'; ?>">שינויים אחרונים</a>
                        <a href="<?php echo $mpURL . 'מיוחד:העלאה'; ?>">העלאת קובץ</a>
                        <a href="<?php echo $mpURL . 'מיוחד:דפים המקושרים לכאן?target=' . $mwPageName; ?>">דפים מקושרים</a>
                        <a href="<?php echo $mpURL . 'מיוחד:קישורי מפעיל'; ?>">קישורי מפעיל</a>
                    </div>
                </div>
            </div>
        </nav>

        <div class="search-container">
            <?php $this->renderNavigation(['SEARCH']); ?>
        </div>
    </div>
</header>