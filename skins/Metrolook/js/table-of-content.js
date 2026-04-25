function initTableOfContent($, $element) {
    $element.on('click', function () {
        $(this).toggleClass('active')

        $(document).mouseup(function (e) {
            if (!$element.is(e.target) && $element.has(e.target).length === 0) {
                $element.removeClass('active')
            }
        })
    })
}