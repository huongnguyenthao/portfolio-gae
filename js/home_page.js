load_template().done(function(){
       //wait for done and the run the second
       change_classes();
    });

function load_template() {
	return $.ajax();
}

change_image();
$(window).resize(function() {
	change_image();
	change_classes();
});

function change_image() {
	var image = document.getElementById('main_image');
	if (window.innerWidth < 500) {
		image.src = '/images/background_image_vertical_editted.jpg';
	} else if (window.innerWidth < 1000) {
		image.src = '/images/Background_image_tablet.jpg';
		image.src = 'images/Background_image_tablet.jpg';
	} else {
		image.src = '/images/Background_image_horizontal.jpg';
	}
}

function change_classes() {
	var homepage_link = document.getElementById('homepage_link');
	var description = document.getElementById('description');
	var footer = document.getElementById('footer');
	var footer_para = footer.getElementsByTagName('p');
	if (window.innerWidth < 500) {
		homepage_link.className = "col-xs-4 col-sm-2 col-md-2";
		description.className = "col-xs-8 col-sm-10 col-md-10";
		footer_para[0].className = "col-xs-8 col-lg-4";
		footer_para[1].className = "col-xs-8 col-lg-4";		
	} else if (window.innerWidth < 1000) {
		homepage_link.className = "col-xs-4 col-sm-2 col-md-2";
		description.className = "col-xs-8 col-sm-10 col-md-10";
		footer_para[0].className = "col-xs-8 col-lg-4";
		footer_para[1].className = "col-xs-8 col-lg-4";
	} else {
		homepage_link.className = "col-xs-12 col-md-12 col-sm-12";
		description.className = "col-xs-12 col-md-12 col-sm-12";
		footer_para[0].className = "col-xs-12 col-md-12 col-sm-12";
		footer_para[1].className = "col-xs-12 col-md-12 col-sm-12";
		console.log("change_classes");
	}	
}