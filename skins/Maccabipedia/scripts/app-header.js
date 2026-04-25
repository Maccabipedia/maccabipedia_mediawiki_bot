function initAppHeaderListener($){
    $('header.app-header .mobile-side-menu-trigger').click((ev) => {
        $(ev.currentTarget)
            .siblings('.navigation-section-container')
            .toggleClass('active')

        toggleOpenOverlay()
    })

    $('header.app-header').on('click', '.dropdown-container', (ev) => {
        const $clickedDropdown = $(ev.currentTarget)

        if ($clickedDropdown.hasClass('active')) {
            $clickedDropdown.removeClass('active')
        } else {
            $('.dropdown-container').removeClass('active')
            $clickedDropdown.addClass('active')
        }
    })
}



function closeAppHeader($) {
    $('header.app-header .navigation-section-container')
        .removeClass('active')
}