$("#std_thumbnails").find("a").click(function(event){
	var $item = $(this);
	viewLargerImage($item);
	return false;
});

$("#stu_thumbnails").find("a").click(function(event){
	var $item = $(this);
	viewLargerImage($item);
	return false;
});

var viewLargerImage = function($link) {
	var src = $link.attr("href");
	var $modal = $("img[src$='" + src + "']");
	if ($modal.length) {
		$modal.dialog("open");
	}else {
		var file_type = src.substring(src.lastIndexOf("."))
		if (file_type.indexOf("pdf") > -1 || 
			file_type.indexOf("xls") > -1 || 
			file_type.indexOf("docx") > -1 || 
			file_type.indexOf("doc") > -1 || 
			file_type.indexOf("txt") > -1 || 
			file_type.indexOf("odt") > -1 ||
			file_type.indexOf("ods") > -1 )
			{window.open(
							  src,
							  '_blank' 
							);
				}
		else{
			var img = $("<img alt='View Large Image' width='768' height='576' style='display: none; padding: 8px; ' />")
				.attr("src", src).appendTo($( "#colorbox" ));
			setTimeout(function(){
				img.dialog({
					width: 960,
					modal: true
					});
				}, 1);
			}
	}
};