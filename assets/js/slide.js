$(function () {
    var timerId = setInterval(function () {
        $("#slideGalley .nav .next").click();
    }, 5000);
    $("#slideGalley").hover(function () {
        $("#slideGalley .nav").show();
        clearInterval(timerId);
    }, function () {
        $("#slideGalley .nav").hide();
        timerId = setInterval(function () {
            $("#slideGalley .nav .next").click();
        }, 5000);
    });

    const goNext = function () {
        $("#slideGalley .slide:not(:animated)").animate({
            "margin-left": -1 * $("#slideGalley .slide li").width()
        }, "swing", function () {
            $("#slideGalley .slide").css("margin-left", "0").append($("#slideGalley .slide li:first-child"))
        });
    }

    const goPrev = function () {
        $("#slideGalley .slide:not(:animated)")
            .css("margin-left", -1 * $("#slideGalley .slide li").width())
            .prepend($("#slideGalley .slide li:last-child"))
            .animate({
                "margin-left": 0
            }, "swing");
    }

    $("#slideGalley .nav .next").click(goNext);
    $("#slideGalley .nav .prev").click(goPrev);

    $("#slideGalley").on('swipeleft', goNext);
    $("#slideGalley").on('swiperight', goPrev);
});
