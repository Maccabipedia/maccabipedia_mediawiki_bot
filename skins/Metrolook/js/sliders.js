function initImagesSlider($, $element) {
    $element.slick({
        autoplay: false,
        lazyLoad: false,
        dots: true,
        fade: false,
        infinite: true,
        rtl: true
    })
}


function initPromotionsSlider($, $element) {
    $promotionsSliderPlaceholder = $element.find('.mp-promotions-slider-placeholder')
    $promotionsSliderElement = $element.find('.mp-promotions-slider-element')

    $promotionsSliderElement.slick({
        autoplay: true,
        arrows: false,
        dots: true,
        infinite: true,
        autoplaySpeed: 10000,
        rtl: true
    })
    $promotionsSliderPlaceholder.css({ 'height': 0 })
    $promotionsSliderElement.css({ 'max-height': 'unset' })
}