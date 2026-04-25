function updateSongItemWidth($, $pageContainer) {
    const $firstSongListContainer = $pageContainer.find('.list-container').first()
    if (!$firstSongListContainer.length) return

    const songListContainerWidth = $firstSongListContainer.width()
    let songItemWidth = 10 * 16

    if ($(window).width() > 1280) {
        songItemWidth *= 1.2
    }

    const songItemsPerList = Math.floor(songListContainerWidth / songItemWidth)
    const songItemCalculatedWidth = (songListContainerWidth / (songItemsPerList + 0.5))

    $pageContainer.find('.list-container .song-page-list-item')
        .css({
            width: `${songItemCalculatedWidth}px`,
            flex: `0 0 ${songItemCalculatedWidth}px`
        })
}

function initSongListPageScripts($, $pageContainer) {

    function listScrollerHandler($, $pageContainer) {
        $pageContainer.find('.list-container .list').each(function () {
            $(this).data('position', 0)
        })

        $pageContainer.find('.list-container .list-scroller-next').click(function () {
            scrollerHandler.call(this, true)
        })

        $pageContainer.find('.list-container .list-scroller-prev').click(function () {
            scrollerHandler.call(this, false)
        })

        function scrollerHandler(isNextScroll) {
            const $listArrowsContainer = $(this).closest('.list-container')
            const $listContainer = $(this).siblings('.list')
            const maxScroll = $listContainer[0].scrollWidth - $listContainer.width()

            isNextScroll ? $listArrowsContainer.addClass('scrolled') : $listArrowsContainer.removeClass('scrolled')

            $listContainer.css('transform', `translateX(${isNextScroll ? maxScroll : 0}px)`)
            $listContainer.data('position', isNextScroll ? maxScroll : 0)
        }
    }

    updateSongItemWidth($, $pageContainer)
    listScrollerHandler($, $pageContainer)
}