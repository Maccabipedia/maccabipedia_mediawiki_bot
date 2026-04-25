function initExpandCollapseParagraph($, $element) {
    if ($element.hasClass('close')) {
        $element.children('.text').hide()
    }

    $element.children('h3').on('click', function (ev) {
        ev.stopPropagation()
        $element.toggleClass('close')
        $(this).siblings('.text, .profile-container').toggle('fast', 'linear')
    })
}

function initLongTextTeaser($, $element) {
    function longTextTeaserCtaButtonTextAdjust() {
        const $ctaButton = $element.find('.cta-button-container')
        $ctaButton.text($element.hasClass('collapsed') ? 'קרא עוד' : 'צמצם טקסט')
    }

    const $ctaButton = $element.find('.cta-button-container')
    const minHeight = $(window).height() * 0.2
    if ($element.height() < minHeight){
        $ctaButton.hide()
        return
    }

    longTextTeaserCtaButtonTextAdjust()

    $element.find('.controller').on('click', function (ev) {
        ev.stopPropagation()
        $element.toggleClass('collapsed')
        longTextTeaserCtaButtonTextAdjust()
    })
}