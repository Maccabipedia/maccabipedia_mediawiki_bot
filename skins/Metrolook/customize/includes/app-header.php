<?php
/**
 * Top navigation header for the Metrolook skin.
 *
 * Renders: logo + main-page link, four primary dropdown menus, the
 * "מכבימדיה" link block, and the right-side options panel
 * (edit/user/options dropdowns). The search box at the bottom is
 * delegated to the QuickTemplate base via renderNavigation(['SEARCH']).
 */

$user = $skin->getUser();
$title = $skin->getTitle();
// On Special:WhatLinksHere/Foo etc. the action buttons should target Foo.
$relevantTitle = $skin->getRelevantTitle();
$pageNamespace = $title->getNamespace();
$request = $skin->getRequest();
$currentAction = $request->getRawVal('action');
$currentOldid = $request->getInt('oldid', 0);
$isViewingEditForm = $currentAction === 'edit';

$skinAssetsURL = $GLOBALS['wgServer'] . $GLOBALS['wgScriptPath']
    . '/skins/Metrolook/assets/';
$mainPageURL = Title::newMainPage()->getLocalURL();

$pageURL = static function (string $titleText): string {
    $t = Title::newFromText($titleText);
    return $t ? $t->getLocalURL() : '#';
};
$specialURL = static function (string $name, ?string $subpage = null): string {
    return SpecialPage::getTitleFor($name, $subpage)->getLocalURL();
};
// Action URL on the relevant title; preserves oldid so editing/historying
// while viewing an old revision keeps targeting that revision.
$actionURL = static function (string $action, array $extra = [])
        use ($relevantTitle, $currentOldid): string {
    $params = ['action' => $action] + $extra;
    if ($currentOldid) {
        $params['oldid'] = $currentOldid;
    }
    return $relevantTitle->getLocalURL($params);
};

// Custom Hebrew namespaces in shared.php use non-standard IDs that break
// MediaWiki's even=subject / odd=talk pairing convention (e.g.
// NS_כדורעף=3001, NS_שיחת_כדורעף=3002), so we pair them explicitly here
// instead of relying on $title->getTalkPage().
$customSubjectToTalk = [
    NS_שיר => NS_שיחת_שיר,
    NS_כדורעף => NS_שיחת_כדורעף,
    NS_כדורסל => NS_שיחת_כדורסל,
    NS_כדורגל => NS_שיחת_כדורגל,
    NS_כדוריד => NS_שיחת_כדוריד,
];
$standardSubjectNamespaces = [NS_MAIN, NS_USER, NS_PROJECT, NS_FILE,
    NS_MEDIAWIKI, NS_TEMPLATE, NS_HELP, NS_CATEGORY];
$subjectToTalk = $customSubjectToTalk;
foreach ($standardSubjectNamespaces as $ns) {
    $subjectToTalk[$ns] = $ns + 1;
}
$talkToSubject = array_flip($subjectToTalk);

$showOptionsPanel = !in_array($pageNamespace, [NS_SPECIAL, NS_MEDIA], true);
$talkPageURL = null;
$subjectPageURL = null;
if ($showOptionsPanel) {
    if (isset($subjectToTalk[$pageNamespace])) {
        $talkPageURL = Title::makeTitle(
            $subjectToTalk[$pageNamespace], $title->getText())->getLocalURL();
    } elseif (isset($talkToSubject[$pageNamespace])) {
        $subjectPageURL = Title::makeTitle(
            $talkToSubject[$pageNamespace], $title->getText())->getLocalURL();
    }
}

// Heading => [Display label => Hebrew page title to link to].
// Order here is the visible order in the header.
$primaryDropdowns = [
    'מכבי תל אביב' => [
        'ההיסטוריה' => 'קטגוריה: היסטוריה',
        'עונות' => 'עונות',
        'מתקנים' => 'פורטל מתקנים',
        'מפעלים' => 'פורטל מפעלים',
        'מדים' => 'פורטל מדים',
        'תארים' => 'תארים',
    ],
    'שחקנים וצוות' => [
        'שחקנים' => 'פורטל שחקנים',
        'אנשי צוות' => 'פורטל אנשי צוות',
    ],
    'אוהדים ותרבות' => [
        'שירים' => 'שירי קהל',
        'כרטיסים ומנויים' => 'כרטיסים ומנויים',
        'כרזות' => 'כרזות משחק',
        'קלפים ומדבקות' => 'קלפים ומדבקות',
        'תפאורות' => 'קטגוריה: תפאורות',
        'ארגונים' => 'ארגוני אוהדים',
        'ספרים' => 'ספריה צהובה',
        'פנזינים' => 'קטגוריה: פנזינים',
    ],
    'משחקים' => [
        'חיפוש משחק' => 'חיפוש משחק',
        'סטטיסטיקות' => 'סטטיסטיקות',
    ],
];
?>

<header class="app-header">
    <div class="content">
        <i class="fas fa-bars mobile-side-menu-trigger mobile-only"></i>

        <a href="<?php echo htmlspecialchars($mainPageURL); ?>" class="homepage-navigation">
            <img src="<?php echo htmlspecialchars($skinAssetsURL . 'images/logo.png'); ?>" />
        </a>

        <nav class="navigation-section-container">
            <div class="pages-navigation-container">
                <?php foreach ($primaryDropdowns as $heading => $items): ?>
                    <div class="dropdown-container">
                        <div class="dropdown-title">
                            <span class="text"><?php echo htmlspecialchars($heading); ?></span>
                            <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                        </div>
                        <div class="dropdown-content">
                            <?php foreach ($items as $label => $titleText): ?>
                                <a href="<?php echo htmlspecialchars($pageURL($titleText)); ?>"><?php echo htmlspecialchars($label); ?></a>
                            <?php endforeach; ?>
                        </div>
                    </div>
                <?php endforeach; ?>

                <div class="navigation-link-block">
                    <a href="<?php echo htmlspecialchars($pageURL('מכבימדיה')); ?>">מכבימדיה</a>
                </div>
            </div>

            <div class="options-navigation-container">
                <?php if ($showOptionsPanel):
                    // Edit-icon link toggles between "open editor" and "back
                    // to article view" depending on whether we're already on
                    // action=edit.
                    $editIconURL = $isViewingEditForm
                        ? $relevantTitle->getLocalURL()
                        : $actionURL('edit');
                ?>
                    <div class="dropdown-container">
                        <div class="dropdown-title">
                            <i class="fas fa-pencil-alt option-icon"></i>
                            <span class="text mobile-only">עריכה</span>
                            <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                            <a href="<?php echo htmlspecialchars($editIconURL); ?>" class="icon-link desktop-only"></a>
                        </div>

                        <div class="dropdown-content">
                            <?php if ($user->isAllowed('edit')): ?>
                                <?php if ($isViewingEditForm): ?>
                                    <a href="<?php echo htmlspecialchars($relevantTitle->getLocalURL()); ?>">חזור לערך</a>
                                <?php else: ?>
                                    <a href="<?php echo htmlspecialchars($actionURL('edit')); ?>">עריכה</a>
                                <?php endif; ?>
                            <?php endif; ?>

                            <?php if ($talkPageURL !== null): ?>
                                <a href="<?php echo htmlspecialchars($talkPageURL); ?>">שיחת עמוד</a>
                            <?php elseif ($subjectPageURL !== null && $currentAction === null): ?>
                                <a href="<?php echo htmlspecialchars($subjectPageURL); ?>">חזור לערך</a>
                            <?php endif; ?>

                            <a href="<?php echo htmlspecialchars($actionURL('history')); ?>">גרסאות קודמות</a>
                            <a href="<?php echo htmlspecialchars($actionURL('purge', ['forcerecursivelinkupdate' => 1])); ?>">רענון העמוד</a>

                            <?php if ($user->isAllowed('protect')): ?>
                                <a href="<?php echo htmlspecialchars($actionURL('delete')); ?>">מחיקה</a>
                                <a href="<?php echo htmlspecialchars($specialURL('Movepage', $relevantTitle->getPrefixedText())); ?>">העברה</a>
                                <a href="<?php echo htmlspecialchars($actionURL('protect')); ?>">הגנה</a>
                            <?php endif; ?>
                        </div>
                    </div>
                <?php endif; ?>

                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <i class="far fa-user option-icon"></i>
                        <span class="text mobile-only">
                            <?php echo htmlspecialchars($user->isRegistered() ? $user->getName() : 'משתמש'); ?>
                        </span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <?php if ($user->isRegistered()):
                            $userName = $user->getName();
                        ?>
                            <a href="<?php echo htmlspecialchars($pageURL('משתמש:' . $userName)); ?>"><?php echo htmlspecialchars($userName); ?></a>
                            <a href="<?php echo htmlspecialchars($pageURL('שיחת משתמש:' . $userName)); ?>">עמוד השיחה שלי</a>
                            <a href="<?php echo htmlspecialchars($specialURL('Preferences')); ?>">העדפות</a>
                            <a href="<?php echo htmlspecialchars($specialURL('Contributions', $userName)); ?>">התרומות שלי</a>
                            <a href="<?php echo htmlspecialchars($specialURL('Userlogout')); ?>">התנתק</a>
                        <?php else: ?>
                            <a href="<?php echo htmlspecialchars($specialURL('Userlogin')); ?>">כניסה לחשבון</a>
                            <a href="<?php echo htmlspecialchars($specialURL('CreateAccount')); ?>">יצירת חשבון</a>
                            <a href="<?php echo htmlspecialchars($pageURL('מיוחד:השיחה שלי')); ?>">שיחה</a>
                        <?php endif; ?>
                    </div>
                </div>

                <div class="dropdown-container">
                    <div class="dropdown-title">
                        <i class="fas fa-cogs option-icon"></i>
                        <span class="text mobile-only">אפשרויות</span>
                        <i class="fas fa-caret-down dropdown-indication mobile-only"></i>
                    </div>

                    <div class="dropdown-content">
                        <a href="<?php echo htmlspecialchars($specialURL('Recentchanges')); ?>">שינויים אחרונים</a>
                        <a href="<?php echo htmlspecialchars($specialURL('Upload')); ?>">העלאת קובץ</a>
                        <a href="<?php echo htmlspecialchars($specialURL('Whatlinkshere', $relevantTitle->getPrefixedText())); ?>">דפים מקושרים</a>
                        <a href="<?php echo htmlspecialchars($pageURL('מיוחד:קישורי מפעיל')); ?>">קישורי מפעיל</a>
                    </div>
                </div>
            </div>
        </nav>

        <div class="search-container">
            <?php $this->renderNavigation(['SEARCH']); ?>
        </div>
    </div>
</header>
