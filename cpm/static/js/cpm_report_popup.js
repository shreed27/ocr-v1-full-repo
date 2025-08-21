$(function(){
	  $(".popbox").live('click', function(event){
	      event.preventDefault();
	      $(this).colorbox();
	  });
  
});

function CloseExam(var strPaperId, var strStuID)
{
	console.log('sSource:' , sSource);
	console.log('strPaperID: ' ,strPaperId , ' , strStuID:' , strStuID);

	$.ajax({
		type: "POST",
		url: sSource,
		data: oData,
		dataType: 'json',
		success: function(msg){
			fnCallback(msg);
			console.log(msg)
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			alert(XMLHttpRequest.responseText);
		}
	});
}
