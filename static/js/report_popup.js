$(function(){
	  $(".popbox").live('click', function(event){
	      event.preventDefault();
	      $(this).colorbox();
	  });
  
});
