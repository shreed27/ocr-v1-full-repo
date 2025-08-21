/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */
var oTable=null;
var questionid=null;
var optionlistid = intemass.util.getUrl('optionlistid');
var view = intemass.util.getUrl('view');
var URL_optionlist_GETQUESTION="/mcq/optionlist/getquestions/";
var URL_optionlist_UPDATENAME="/mcq/optionlist/updatename/";
var URL_optionlist_UPDATEDESC="/mcq/optionlist/updatedesc/";
var URL_QUESTION_DELETE="/mcq/optionlist/del";
var URL_UPDATENAME="/mcq/optionlist/updatename/";
var config = {
        toolbar: [],
        height: 50,
        toolbarStartupExpanded: false,
        readOnly: true,
        keystrokes: [],
        blockedKeystrokes: [CKEDITOR.CTRL + 67,CKEDITOR.CTRL +66]
    };
var quploadsettings = {
		// Backend Settings
		flash_url : "/static/js/swfupload/swfupload.swf",
		upload_url: "/mcq/optionlist/uploadimage/",
		custom_settings : {
		progressTarget : "fsUploadProgress",
		upload_target : "divFileProgressContainer",
		cancelButtonId : "btnCancel"
		},

		// File Upload Settings
		file_size_limit : "20 MB",	// 2MB
		file_types : "*.*",
		file_types_description : "Images",
		file_upload_limit : "0",

		//events
		file_queued_handler : fileQueued,
		file_queue_error_handler : fileQueueError,
		file_dialog_complete_handler : fileDialogComplete,
		upload_start_handler : uploadStart,
		upload_progress_handler : uploadProgress,
		upload_error_handler : uploadError,
		upload_success_handler : uploadSuccess,
		upload_complete_handler : pullThumbnails,
		queue_complete_handler : queueComplete,

		// Button Settings
		button_image_url : "/static/css/swfimages/XPButtonNoText_61x22x4.png",
		button_placeholder_id : "qupload",
		button_width: 61,
		button_height: 22,
		button_text : '<span class="swfbutton">Upload</span>',
		button_text_style : '.swfbutton {font-family: Arial; font-size:14pt ;text-align:center;background-color:#339933;}',
		button_window_mode: SWFUpload.WINDOW_MODE.TRANSPARENT,
		button_cursor: SWFUpload.CURSOR.HAND
	};



var bindImageIconClick = function(){
	var deleteImage = function($item) {
	    var id = parseInt($item.children("a:last").attr("id"));
	    $.post("/mcq/optionlist/deleteimage/",
		{
		    'imageid': id,
		    'csrfmiddlewaretoken': csrfvalue
		},
		function(payload) {
		    if(payload.state === "success"){
		        $item.remove();
		    }
		},'json');
	};

	var viewLargerImage = function($link) {
	    var src = $link.attr("href");
	    var title = $link.siblings("img").attr("alt");
	    var $modal = $(".modalpop");
	console.log('$modal.length : ' , $modal.length);
	    if ($modal.length) {
		console.log('viewlargeimage 1');
		$modal.dialog("open");
	    }else {
		console.log('viewlargeimage 2', src);
		var img = $("<img alt='" + title + "' width='768' height='576' class='modalpop' style='display: none; padding: 8px;' />")
		    .attr("src", src).appendTo("body");
		setTimeout(function(){
		    img.dialog({
		        title: title,
		        width: 960,
		        modal: true
		    });
		}, 1);
	    }
	};

	// resolve the icons behavior with event delegation
	$("#thumbnails").find("li").click(function(event){
	    var $item = $(this);
	    var $target = $(event.target);
		console.log('event.target : ' , event.target);
	    if ($target.is("a.ui-icon-zoomin")){
		viewLargerImage($target);
	    }else if ($target.is("a.ui-icon-closethick")){
		deleteImage($item);
	    }
	    return false;
	});
};









var pullThumbnails = function(){
		var questionid = parseInt($('#optionlist_id').val()) || -1;
		if (questionid === -1){
			$("#thumbnails li").remove();
			return;
		}
		console.log(' ok ... get mcq quetion thumbnails');
	$.post("/mcq/optionlist/thumbnails/",
		{
			'optionlist_id': questionid,
			'csrfmiddlewaretoken': csrfvalue
		},
		function(payload){
			console.log('payload.state test test', payload.state);
			if(payload.state === "success"){
				thumbnails = payload['thumbnails'];
				var thumbhtml = '';
				for (var t in thumbnails){
					thumbhtml += '<li class="ui-widget-content ui-corner-tr">';
					thumbhtml += '<h6 class="ui-widget-header">'+thumbnails[t][1].slice(0,5)+'</h6>';
					thumbhtml += '<img src="/static/'+thumbnails[t][0]+'"  alt="'+thumbnails[t][1]+'" width="96" height="72"></img>';
					thumbhtml += '<a href="/static/'+thumbnails[t][0]+'" title="View Larger Image" class="ui-icon ui-icon-zoomin">View Larger</a>';
					if(!view){
						thumbhtml += '<a href="#" title="Delete Image" id=' + thumbnails[t][3] + ' class="ui-icon ui-icon-closethick">Delete</a>';
					}
				}

				var $list = $("ul", $("#thumbnails"));
				$("#thumbnails li").remove();
				$(thumbhtml).appendTo($list);
				bindImageIconClick();
			}else{
				$("#thumbnails li").remove();
			}
			},'json');
	    };

$(function(){

	$("#optionlist_option").ckeditor({readOnly: false});
	var swfu = new SWFUpload(quploadsettings);
	var curoptionid = $('#optionlist_id').val();
	$("#SWFUpload_0").live("mousedown", function(){
		curoptionid = $('#optionlist_id').val();
		var postobj = {"optionlistid": curoptionid};
		swfu.setPostParams(postobj);
	});
	$("#SWFUpload_1").live("mousedown", function(){
		curoptionid = $('#optionlist_id').val();
		var postobj = {"optionlistid": curoptionid, 'standard_image': 'yes'};
		swfu1.setPostParams(postobj);
});


});
(function($, undef) {
	///=========== User define ========================
	var PRIMARY_KEY_ID="optionlist_id";
	var PULL_FROMPRIMARYKEY_URL="/mcq/optionlist/get/"; /// use for drop down list.
	var NEW_KEY_WORDING="New Option";
	var PRIMARY_NAME_FIELD="optionlist_name";
	var JSON_FIELDS_TO_UPDATE = {"optionlist_name":"", "optionlist_description":"", "optionlist_option":"","optionlist_correct":""};
	///=========== End of User define ========================
	var PARAMETER_FORKEY=PRIMARY_KEY_ID;
	var viewCheck = intemass.util.getUrl('view');
	//console.log('check viewCheck', viewCheck);


	













	

	 var JSON_FIELDS_TO_UPDATE_TEMP= jQuery.extend(true, {}, JSON_FIELDS_TO_UPDATE);
	$('#'+PRIMARY_KEY_ID).change(function(){
		optionlistid= parseInt($('#'+PRIMARY_KEY_ID).val()) || -1;
			
	    console.log(PRIMARY_KEY_ID , ' on changed');
	    pull_PrimaryKeySelected_Detail();
	    setEditableText();
		pullThumbnails();
	});


 $(function(){

});
	$( document ).ready(function() {
		console.log('debug3-1');
		
		var viewstatus = intemass.util.getUrl('view');
		if(viewstatus=="1")
		{
			console.log('debug3-1a');
			for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
				$('input[name=' + field + ']').attr("disabled",true);	
				$('select').attr("disabled",true);		
				$('textarea').attr("disabled",true);	
				
			}
			console.log('here disable all ',viewstatus);
		}
		
                pullThumbnails();
		initcanvasarea();
	});
	var clearquestiondetail = function(){
		console.log('clearquestiondetail');
		for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
			var targetType = $('#'+field);
			if(targetType.is("text")||targetType.is("textarea"))
			{
				$('#'+field).val("");
			}
			if (field=="optionlist_correct") {
				$("input:radio").attr("checked", false);
			}
			if (field == "optionlist_name"){
				$("#optionlist_name").html(NEW_KEY_WORDING);
			}
		}
		
	};


	var nmwidth = 1330;
	var nmheight = 700;
	var nmopts = {
	sizes: { 
	    initW: nmwidth,
	    initH: nmheight,
	    w: nmwidth,
	    h: nmheight,
	    minW: nmwidth,
	    minH: nmheight
	},
	callbacks: {
	    beforeShowCont: function() {
		var structure = $('.nyroModalCont');
		var iframe = $('.nyroModalCont iframe');
		nmwidth = structure.width();
		nmheight = structure.height();
		iframe.css('width', nmwidth).css('height', nmheight);
	    }
	}
	};
	var initcanvasarea = function(){
		console.log('prepare init');
		questioncanvas_bindnm(optionlistid, view);
	};

	
	var setcanvasreadOnly = function() {
	    $("#option_canvas").click(function () {return false;});
	};

	var questioncanvas_bindnm;
	questioncanvas_bindnm = function(optionid, view){
		console.log('prepare init 1');
		var test = document.getElementById("option_canvas")
		//' +  $(this).text() + uid + '
		var canvasurl =  '/mcq/optioncanvas/?canvasname=1&optionid=' + optionid + '&view=' + view; 
		console.log('canvasurl:' , canvasurl);
		test.setAttribute("class","nyroModal populate greenBtn");
		test.setAttribute("href", canvasurl)
		test.setAttribute("target", "_blank")
		$("#option_canvas").unbind('click').click(function(event){
			$('#option_canvas').off();
			width: "copy"
			tokenSeparators: [",", " "]
			event.preventDefault()
			$(this).nm(nmopts);
			$(this).next().attr({
			'onclick': function () {
				return false;
			}
		});
		$.ajax({
			url: canvasurl ,
			success: function (resp) {
					$("#option_canvas").trigger('click');
				},
			error: function(e){
					alert('Error:');
				}  
			});
		});
	};



	var setEditableText = function(){
		console.log("ok ...i'm here");
		var SELECT_RECORD_NAME = $('#'+PRIMARY_KEY_ID).children('option:selected').text() || NEW_KEY_WORDING;
		$("span.editable").text(SELECT_RECORD_NAME);
	};
	///==== if the dropdown list is selected old value;
	var pull_PrimaryKeySelected_Detail = function () {
		console.log('pull_PrimaryKeySelected_Detail');
		primarykey_value = parseInt($('#'+PRIMARY_KEY_ID).val()) || -1;
		$.post(PULL_FROMPRIMARYKEY_URL,
		{
		    KEYVALUE : primarykey_value,
		    'csrfmiddlewaretoken': csrfvalue
		},
		function (payload){
			console.log('debug2-4');
		    clearquestiondetail();
		    optionlist_id = parseInt($('#'+PRIMARY_KEY_ID).val()) || -1;
		    if (payload.state === "success") {
			$('input[name="optionlist_correct"]').prop('checked', false);
			for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
				console.log('field:' , field);
				if(field != PRIMARY_KEY_ID)
					if( field != "optionlist_name")
						$('#'+field).val(payload[field]);
					else
						$('#'+field).html(payload[field]);
				
			}
			var $radios = $('input:radio[name=optionlist_correct]');
			//alert($radios);			
			console.log('payload ' , payload['optionlist_correct']);
			 $radios.filter('[value='+ firstToUpperCase(payload['optionlist_correct'].toString()) + ']').prop('checked', true);
		    }
		}, 'json');
	};
	function firstToUpperCase( str ) {
	    return str.substr(0, 1).toUpperCase() + str.substr(1);
	}
	$(function(){
		if(viewCheck!="1"){
			console.log('debug1');
			$("span.editable").editable(function(value, settings){
				console.log('here is the log' , value) ;
				updateToDataBase(value); // This is to update to database once there are any editable field onblur.
				return value;
			}, {
				type: "text",
				onblur: "submit",
				tooltip: "Click to Edit...",
				style: 'display:inline'
			});
		}
		$("#btnSave").click(function( ){
			var value = $("#optionlist_name").val();
			if(value=="")
				value = $("#optionlist_name").html();
			//console.log(value);
			//alert(value);
			updateToDataBase(value); // This is to update to database once there are any editable field onblur.
			return value;
		});
		$("textarea").blur(function(value, settings){
			updateToDataBase(value); // This is to update to database once there are any editable field onblur.
			return value;
		});
		///==== manual here===========
		$('input[type=radio][name=optionlist_correct]').change(function(value,settings){
			console.log('debug2-1');
			updateToDataBase(value); // This is to update to database once there are any editable field onblur.
			return value;
		});

		 $('#'+PRIMARY_KEY_ID).change(function(){
			optionlistid= parseInt($('#'+PRIMARY_KEY_ID).val()) || -1;
			console.log('debug2-2');
			pull_PrimaryKeySelected_Detail();
			pullThumbnails();
			//pullThumbnailsForStd();
			//setEditableText();
		});
		
		if(viewCheck != "1")
			setEditableText();
	});

	
	var updateToDataBase = function(value){
		console.log('debug2-3');
		//console.log('value:' , value);
		var PRIMARY_NAME = ""; /// this will always refer to 
		var toString = Object.prototype.toString;
		var int_key=parseInt($('#'+PRIMARY_KEY_ID).val());
		if(toString.call(value) == '[object String]' && int_key=="-1") /// if is string, meaning is going to add new record.
		{	
			console.log("value:" , value , "NEW_KEY_WORDING:" ,NEW_KEY_WORDING);
			if(value==NEW_KEY_WORDING) /// if doesn't change anything. and use back the original name. will prompt error.
			{
				ShowAddError();
				return;
			}
			
			JSON_FIELDS_TO_UPDATE_TEMP= jQuery.extend(true, {}, JSON_FIELDS_TO_UPDATE);
			JSON_FIELDS_TO_UPDATE_TEMP[PRIMARY_NAME_FIELD]=value;	
			JSON_FIELDS_TO_UPDATE_TEMP[PRIMARY_KEY_ID] = -1;		
		}
		else{
			if(int_key==-1)
				return; // just return, this is not create new value.
			for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
				var fieldValue = $('#'+field).val();
				var targetType = $('#'+field);
				if(targetType.is("span"))
				{
					if(toString.call(value) == '[object String]')
					{
						fieldValue = value;
					}
					else{
						fieldValue = targetType.text();}
					JSON_FIELDS_TO_UPDATE_TEMP[field]=fieldValue;
				}
				if(targetType.is("text")||targetType.is("textarea"))
				{
					fieldValue = $('#'+field).val();
					JSON_FIELDS_TO_UPDATE_TEMP[field]=fieldValue;
				}
				if (field=="optionlist_correct") {
					var valueRadio = $('input[name="' + field + '"]:checked').val();
					JSON_FIELDS_TO_UPDATE_TEMP[field]=valueRadio;
				}
			}
			JSON_FIELDS_TO_UPDATE_TEMP[PRIMARY_KEY_ID]=parseInt($('#'+PRIMARY_KEY_ID).val());
		}

		/// ===================== User manual potion=====================================
		/// ===================== this is to define foreign key =========================
		var questionid = intemass.util.getUrl('questionid');
    		JSON_FIELDS_TO_UPDATE_TEMP["questionid"]=questionid;
		/// =============================================================================
		console.log(JSON_FIELDS_TO_UPDATE_TEMP);
		$.ajax({
		    type: "POST",
		    url: URL_UPDATENAME,
		    dataType: "json",
		    data: JSON_FIELDS_TO_UPDATE_TEMP,
		    success: function(payload) {
			if (payload['optionlist_id']) {
				var optionID=payload['optionlist_id'];
				var optionName=payload['optionlist_name'];
				var optionDesc=payload['optionlist_description'];
				var optionOption=payload['optionlist_option'];
				var optionCorrect=payload['optionlist_correct'];
				
				$("#optionlist_description").val(optionDesc || '');
				$("#optionlist_name").val(optionName || '');
				$("#optionlist_option").val(optionOption || '');
				$('#optionlist_id').children('option:selected').text(optionName);
		        	$('#optionlist_id').children('option:selected').val(optionID);
		        }
		    },
		    error: function(XMLHttpRequest, textStatus, errorThrown) {
			alert(XMLHttpRequest.responseText);
		        return this;
		    }
		});
	    };


	
})(jQuery);

/// ============Main Function Call============
function ShowAddError()
{
	$(function(){ //define dialogue box
		var dialogue_add_error = $("#dialog-add-error").dialog({
		    resizable: false,
		    height:170,
		    weight:300,
		    modal: true,
		    buttons: {
			OK: function() {
			    $( this ).dialog( "close" );
			}
		    }});
	}); /// end of define dialogue box;
}

