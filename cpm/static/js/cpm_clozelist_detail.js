/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */
var oTable=null;
var questionid=null;
var clozelistid = intemass.util.getUrl('clozelistid');
var view = intemass.util.getUrl('view');
var URL_clozelist_GETQUESTION="/cpm/clozelist/getquestions/";
var URL_clozelist_UPDATENAME="/cpm/clozelist/updatename/";
var URL_clozelist_UPDATEDESC="/cpm/clozelist/updatedesc/";
var URL_QUESTION_DELETE="/cpm/clozelist/del";
var URL_UPDATENAME="/cpm/clozelist/updatename/";
var config = {
        toolbar: [],
        height: 50,
        toolbarStartupExpanded: false,
        readOnly: true,
        keystrokes: [],
        blockedKeystrokes: [CKEDITOR.CTRL + 67,CKEDITOR.CTRL +66]
    };
 

  
$(function(){

	 
	var curoptionid = $('#clozelist_id').val();
	 
});

 
(function($, undef) {
	///=========== User define ========================
	var PRIMARY_KEY_ID="clozelist_id";
	var PULL_FROMPRIMARYKEY_URL="/cpm/clozelist/get/"; /// use for drop down list.
	var NEW_KEY_WORDING="New Cloze";
	var PRIMARY_NAME_FIELD="clozelist_name";
	var JSON_FIELDS_TO_UPDATE = {"clozelist_name":"", "clozelist_mark":"", "clozelist_answer":"", "clozelist_mark":""};
	///=========== End of User define ========================
	var PARAMETER_FORKEY=PRIMARY_KEY_ID;
	var viewCheck = intemass.util.getUrl('view'); 
	 var JSON_FIELDS_TO_UPDATE_TEMP= jQuery.extend(true, {}, JSON_FIELDS_TO_UPDATE);
	$('#'+PRIMARY_KEY_ID).change(function(){
		clozelistid= parseInt($('#'+PRIMARY_KEY_ID).val()) || -1;
			
	    console.log(PRIMARY_KEY_ID , ' on changed');
	    pull_PrimaryKeySelected_Detail(); 
	});


 $(function(){

});
	$( document ).ready(function() { 
		
		var viewstatus = intemass.util.getUrl('view');
		if(viewstatus=="1")
		{
			console.log('viewstatus=="1"', JSON_FIELDS_TO_UPDATE_TEMP);
			for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
				console.log('field: ' ,field);
				$('input[name=' + field + ']').attr("disabled",true);	
				$('#' + field ).attr("disabled",true);	
				$('select').attr("disabled",true);		
				$('textarea').attr("disabled",true);	
				
			}
			console.log('here disable all ',viewstatus);
		}
		 
	});
	var clearquestiondetail = function(){
		console.log('clearquestiondetail');
		for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
			var targetType = $('#'+field);
			if(targetType.is("text")||targetType.is("textarea"))
			{
				$('#'+field).val("");
			}
			if (field=="clozelist_correct") {
				$("input:radio").attr("checked", false);
			}
			if (field == "clozelist_name"){
				$("#clozelist_name").html(NEW_KEY_WORDING);
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
		    clozelist_id = parseInt($('#'+PRIMARY_KEY_ID).val()) || -1;
		    if (payload.state === "success") {
			for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
				console.log('field:' , field);
				if(field != PRIMARY_KEY_ID)
					if( field != "clozelist_name")
						$('#'+field).val(payload[field]);
					else
						$('#'+field).html(payload[field]);
				
			} 
			//alert($radios);			
			console.log('payload ' , payload['clozelist_name']);
			// $radios.filter('[value='+ firstToUpperCase(payload['clozelist_correct'].toString()) + ']').prop('checked', true);
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
				style: 'display:inline;width:90%'
			});
		}
		$("#btnSave").click(function( ){
			var value = $("#clozelist_name").val();
			if(value=="")
				value = $("#clozelist_name").html();
			//console.log(value);
			//alert(value);
			updateToDataBase(value); // This is to update to database once there are any editable field onblur.
			intemass.ui.showclientmsg("Cloze Answer Saved Successfully");
			return value;
		});
		$("textarea").blur(function(value, settings){
			updateToDataBase(value); // This is to update to database once there are any editable field onblur.
			return value;
		});
		///==== manual here===========
		$('input[type=radio][name=clozelist_correct]').change(function(value,settings){
			console.log('debug2-1');
			updateToDataBase(value); // This is to update to database once there are any editable field onblur.
			return value;
		});

		 $('#'+PRIMARY_KEY_ID).change(function(){
			clozelistid= parseInt($('#'+PRIMARY_KEY_ID).val()) || -1;
			console.log('debug2-2');
			pull_PrimaryKeySelected_Detail(); 
		});
		 
	});

	
	var updateToDataBase = function(value){
		console.log('debug2-3');
		console.log('value:' , value);
		var PRIMARY_NAME = ""; /// this will always refer to 
		var toString = Object.prototype.toString;
		var int_key=parseInt($('#'+PRIMARY_KEY_ID).val());
		if(toString.call(value) == '[object String]' && int_key=="-1") /// if is string, meaning is going to add new record.
		{	
			console.log("value:" , value , "NEW_KEY_WORDING:" ,NEW_KEY_WORDING, " PRIMARY_NAME_FIELD:" ,PRIMARY_NAME_FIELD);
			if(value==NEW_KEY_WORDING) /// if doesn't change anything. and use back the original name. will prompt error.
			{
				ShowAddError();
				return;
			}
			
			JSON_FIELDS_TO_UPDATE_TEMP= jQuery.extend(true, {}, JSON_FIELDS_TO_UPDATE);
			JSON_FIELDS_TO_UPDATE_TEMP[PRIMARY_NAME_FIELD]=value;	
			JSON_FIELDS_TO_UPDATE_TEMP[PRIMARY_KEY_ID] = -1;
			console.log('JSON_FIELDS_TO_UPDATE_TEMP: ' , JSON_FIELDS_TO_UPDATE_TEMP);		
		}
		else{
			if(int_key==-1)
				return; // just return, this is not create new value.
			for(var field in JSON_FIELDS_TO_UPDATE_TEMP) {
				var fieldValue = $('#'+field).val();
				var targetType = $('#'+field);
				console.log('targetType: ' , targetType);
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
				console.log('fieldValue: ' , fieldValue);
				//if (field=="clozelist_correct") {
				//	var valueRadio = $('input[name="' + field + '"]:checked').val();
				//	JSON_FIELDS_TO_UPDATE_TEMP[field]=valueRadio;
				//}
				JSON_FIELDS_TO_UPDATE_TEMP[field]=fieldValue;
			}
			JSON_FIELDS_TO_UPDATE_TEMP[PRIMARY_KEY_ID]=parseInt($('#'+PRIMARY_KEY_ID).val());
			console.log('JSON_FIELDS_TO_UPDATE_TEMP:' , JSON_FIELDS_TO_UPDATE_TEMP);
		}
		if (JSON_FIELDS_TO_UPDATE_TEMP['clozelist_name']=="")
		{
			ShowAddError();
			return;
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
			if (payload['clozelist_id']) {
				var optionID=payload['clozelist_id'];
				var optionName=payload['clozelist_name'];
				var optionDesc=payload['clozelist_description'];
				var optionOption=payload['clozelist_option'];
				var optionCorrect=payload['clozelist_correct'];
				console.log('payload : returned: ' , payload);
				$("#clozelist_description").val(optionDesc || '');
				$("#clozelist_name").val(optionName || '');
				$("#clozelist_option").val(optionOption || '');
				$('#clozelist_id').children('option:selected').text(optionName);
		        	$('#clozelist_id').children('option:selected').val(optionID);
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

