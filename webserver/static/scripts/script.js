$(document).ready(function(){
	var n = $('.navbar');
	var stickyNavTop = n.offset().top;
	 
	var stickyNav = function(){
		var scrollTop = $(window).scrollTop();
		      
		if (scrollTop > stickyNavTop) { 
		    n.addClass('navbar-fixed-top');
		    n.css('margin-top', '0px');
		} else {
		    n.removeClass('navbar-fixed-top');
		    n.css('margin-top', '-50px');
		}
	};
	 
	stickyNav();
	 
	$(window).scroll(function() {
	    stickyNav();
	});
});