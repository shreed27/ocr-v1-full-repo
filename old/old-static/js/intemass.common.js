$(function(){
	$("#teacher_home_link").css("cursor","pointer").click(function(){
		var urlString = window.location.toString();
        if(urlString.search("student")!= -1||urlString.search("classroom")!=-1){
		location.href = "/teacher/index/?tab=1";	
		}
		else{
		location.href = "/teacher/index/?tab=2";	
		}
	});
});
