$(document).ready(function(){
	$(window).data('prevWidth', $(window).width());
	$('#section-title').css('height', $(window).height());

	var rsHandler = function() {
        if ($(window).data('prevWidth') != $(window).width()) {
        	$('#section-title').css('height', $(window).height());
        }

        var overflow = $('#footer-bg').height() - $('#section-footer').offset().top + $('#contact').offset().top;
        if (overflow > 0) {
        	$('#footer-bg').css('bottom', (-overflow) + 'px');
        	$('#section-footer > div').css('bottom', (-overflow) + 'px');
        }

        $('#footer-bg').css('visibility', 'visible');
	};
	setTimeout(rsHandler, 1);
	$(window).resize(rsHandler);

	$('#nav-wp-element').waypoint({
		handler: function(direction) {
			if (direction == 'down') {
				$('.navbar').addClass('navbar-fixed-top');
		    	$('.navbar').css('margin-top', '0px');
		   		$('#nav-title').css('opacity', '0.75');
		   		$('button.navbar-toggle').css('margin-right', '0px');

				$('#sticky-nav-placeholder').css('display', 'visible');
		   		//$('#nav-container').css('margin-right', '0px');
			} else if (direction == 'up') {
				$('.navbar').removeClass('navbar-fixed-top');
		   		$('.navbar').css('margin-top', '-50px');
		   		$('#nav-title').css('opacity', '1');
		   		$('button.navbar-toggle').css('margin-right', '15px');

		   		$('#sticky-nav-placeholder').css('display', 'none');
		   		//$('#nav-container').css('margin-right', '0px');
			}
		}
	});

	var wpobj = function(prev, current) {
		return {
			handler: function(direction) {
	    		if (direction == "up") {
	    			$('#nav-title-text-old').html(current);
	    			$('#nav-title-text-old').css('animation-direction', 'reverse');
	    			$('#nav-title-text-old').css('opacity', '0');
	    			$('#nav-title-text-old').removeClass('nav-text-scrolldown-exit');
	    			$('#nav-title-text-old').addClass('nav-text-scrolldown-enter');
	    			var $temp = $('#nav-title-text-old').detach();
	    			$temp.appendTo('#nav-title-link');

	    			$('#nav-title-text').html(prev);
	    			$('#nav-title-text').css('animation-direction', 'reverse');
	    			$('#nav-title-text').css('opacity', '1');
	    			$('#nav-title-text').removeClass('nav-text-scrolldown-enter');
	    			$('#nav-title-text').addClass('nav-text-scrolldown-exit');
	    			var $temp = $('#nav-title-text').detach();
	    			$temp.appendTo('#nav-title-link');
	    		} else if (direction == "down") {
	    			$('#nav-title-text-old').remove();
	    			$('#nav-title-text').prop('id', 'nav-title-text-old');
	    			$('#nav-title-text-old').css('animation-direction', '');
	    			$('#nav-title-text-old').css('opacity', '0');
	    			$('#nav-title-text-old').removeClass('nav-text-scrolldown-enter');
	    			$('#nav-title-text-old').addClass('nav-text-scrolldown-exit');
	    			var $temp = $('#nav-title-text-old').detach();
	    			$temp.appendTo('#nav-title-link');

	    			$('#nav-title-link').append('<div id="nav-title-text"></div>');
	    			$('#nav-title-text').html(current);
	    			$('#nav-title-text').css('animation-direction', '');
	    			$('#nav-title-text').css('opacity', '1');
	    			$('#nav-title-text').removeClass('nav-text-scrolldown-exit');
	    			$('#nav-title-text').addClass('nav-text-scrolldown-enter');

	    			var $temp = $('#nav-title-text').detach();
	    			$temp.appendTo('#nav-title-link');
	    		}
	  		},
	  		offset: '120px'
	  	};
	}


	$('#nav-title-wp-eh').waypoint(wpobj('', 'Hack'));

  	$('#nav-title-wp-el').waypoint(wpobj('Hack', 'Loan'));

  	$('#nav-title-wp-sched1').waypoint(wpobj('Loan', 'Schedule'));

  	$('#nav-title-wp-hw').waypoint(wpobj('Schedule', 'Hardware'));

  	$('#nav-title-wp-sp').waypoint(wpobj('Hardware', 'Sponsors'));

  	$('#nav-title-wp-contact').waypoint(wpobj('Sponsors', 'Contact'));

  	var addLink = function(button, target) {
  		if (window._page_id == 'home') {
	  		$(button).click(function(e) {
	  			e.preventDefault();

	  			var offset;
	  			if ($('.navbar').hasClass('navbar-fixed-top') || $('.navbar-header > button').hasClass('collapsed')) {
	  				offset = 0;
	  			} else {
	  				offset = -240;
	  			}

	  			if (target == '#about')
	  				offset += -15;
	  			else
	  				offset += 0;

	    		$('html, body').animate({
	       			scrollTop: $(target).offset().top + offset
	    		}, 500);

	    		if (location.toString().indexOf('#') >= 0)
	    			history.replaceState(null, null, location.toString().substring(0, location.toString().indexOf('#')));
			});
  		}
  	}
  	addLink('#nav-link-about', '#about');
  	addLink('#nav-link-sched', '#schedule');
  	addLink('#nav-link-contact', '#contact');

  	$('ul.navbar-nav > li').click(function() {
  		var b = $('.navbar-header > button');
  		if (!b.hasClass('collapsed'))
  			b.click();
  	});
  	$('button.navbar-toggle').click(function() {
  		var overflow = $('#section-nav').offset().top + 263 - $(document).scrollTop() - $(window).height();
  		if (overflow > 0 && $('.navbar-header > button').hasClass('collapsed')) {
  			$('html, body').animate({
       			scrollTop: $(document).scrollTop() + overflow
    		}, 200);
  		}
  	});
  	
  	var animation = false;
  	var cookieStr = "eh_a_wait_M6jpdLHHM8d2dgg";

  	if (document.cookie.indexOf(cookieStr) == -1) {
  		animation = true;

  		var exp = new Date();
		exp.setTime(exp.getTime() + 5*60*1000);
		document.cookie = cookieStr+'=swag'+';expires='+exp.toGMTString()+';path=/';
		console.log(cookieStr+'=swag'+';expires='+exp.toGMTString()+';path=/');
  	}

  	if (animation) {
  		$('.tp-a-parts').each(function() {
  			$(this).css('animation-name', $(this).attr('id')+'-ani');
  		});
  		$('#section-title div.row, #nav-container').each(function() {
  			$(this).css('animation-name', 'fade-in');
  		});
  	} else {
  		$('.tp-a-parts').css('opacity', '1');
  		$('#section-title div.row, #nav-container').css('opacity', '1');
  	}
});