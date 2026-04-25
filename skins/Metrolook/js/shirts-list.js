function initShirtsListPageScripts($, $pageContainer) {
    const $shirtsListTabs = $pageContainer.find('.shirts-navigation-tab-container li')
    $shirtsListTabs.each(function (index, element) {
        $(element).on('click', function () {
            setTimeout(function () {
                $pageContainer.find('.mp-image-slider-container').slick('refresh')
            }, 100)
        })
    })
}