const $pageOverlay = $('.maccabipedia-site-container .page-overlay').first()
let isOverlayActive = false

function openOverlay(shouldCoverMenu) {
    $pageOverlay.addClass('active')
    $('body').css('overflow', 'hidden')

    if (shouldCoverMenu) {
        $pageOverlay.addClass('cover-menu')
    }

    isOverlayActive = true
}

(function ($) {
    $pageOverlay.click(() => {
        closeAppHeader($)
        closeOverlay()
    })
}(jQuery))

function closeOverlay() {
    $pageOverlay.removeClass('active')
    $pageOverlay.removeClass('cover-menu')
    $('body').css('overflow', 'auto')

    isOverlayActive = false
}

function toggleOpenOverlay(shouldCoverMenu) {
    if (isOverlayActive) {
        closeOverlay()
    } else {
        openOverlay(shouldCoverMenu)
    }
}