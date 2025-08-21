;(function($, undef) {
	$(function() {
		$("#id_username").focus();
		$("#id_username").blur(function(){
			var stuname = $(this).val();
			$.post("/student/getbyname/",
				{'stuname':stuname,"csrfmiddlewaretoken":csrfvalue},
				function(payload){
				if (payload['state'] == 'success'){
					$('#id_gender').val( payload['gender']);
					$('#id_email').val( payload['email']);
				}
			  },'json');
		});

	});
})(jQuery);

function submitform(){
	document.forms[0].submit();
}
