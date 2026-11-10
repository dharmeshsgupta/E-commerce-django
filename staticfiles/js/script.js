// some scripts

// jquery ready start
$(document).ready(function() {
	// jQuery code


    /* ///////////////////////////////////////

    THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
    For sliders, interactions and other

    */ ///////////////////////////////////////
    

	//////////////////////// Prevent closing from click inside dropdown
    $(document).on('click', '.dropdown-menu', function (e) {
      e.stopPropagation();
    });


    $('.js-check :radio').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');

        } else {
            item.removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });


    $('.js-check :checkbox').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');
        } else {
            $(this).closest('.js-check').removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });



	//////////////////////// Bootstrap tooltip
	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
		$('[data-toggle="tooltip"]').tooltip()
	} // end if




    
}); 
// jquery end


// Thumbnail click swap (fallback if template JS not loaded)
document.addEventListener('DOMContentLoaded', function(){
    try{
        var mainImg = document.querySelector('.img-big-wrap img');
        var thumbs = document.querySelectorAll('ul.thumb a');
        if(mainImg && thumbs.length){
            thumbs.forEach(function(a){
                a.addEventListener('click', function(e){
                    e.preventDefault();
                    var href = this.getAttribute('href');
                    if(href) mainImg.src = href;
                    thumbs.forEach(function(t){ t.classList.remove('active-thumb'); });
                    this.classList.add('active-thumb');
                });
            });
        }
    }catch(err){
        // ignore
    }
});

// fade out message if present (keeps existing setTimeout behavior)
setTimeout((function() {
    var msg = document.getElementById('message');
    if(msg) msg.style.transition = 'opacity 0.6s';
    if(msg) msg.style.opacity = 0;
}), 4000);

