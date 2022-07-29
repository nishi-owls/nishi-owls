$(function () {
	// nav bar
	$("ul.sub").hide();
	$("#menu li").hover(
		function () {
			$("ul:not(:animated)", this).slideDown("fast");
		},
		function () {
			$("ul", this).slideUp("fast");
		});

	// game report accordion.
	$(".game-report-detail h3").next().slideToggle(0);
	$(".game-report-detail h3").on('click', function () {
		$(this).next().slideToggle(500);
		$(this).toggleClass('open', 500);
	})
});

$(function () {
	// top page games horizontal dragging.
	const gamesSlider = $('.top-games');
	let isMouseDown = false;
	let startX;
	let scrollX;
	gamesSlider.on('mousedown', (e) => {
		isMouseDown = true;
		startX = e.pageX;
		scrollX = gamesSlider.scrollLeft();
	});
	gamesSlider.on('mouseleave', () => {
		isMouseDown = false;
	});
	gamesSlider.on('mouseup', () => {
		isMouseDown = false;
	})
	gamesSlider.on('mousemove', (e) => {
		if (!isMouseDown) return;
		e.preventDefault();
		gamesSlider.scrollLeft(scrollX - (e.pageX - startX));
	})
});
