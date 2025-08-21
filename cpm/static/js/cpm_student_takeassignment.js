/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */
$(document).ready(function(){
	$('input[name=question_multiselection_option]').customInput();
	console.log($('input[name=question_multiselection_option]'));
});


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



function setAllNyroModal()
{
	
}
function onGraphicClicked(objectID, optionid)
{
	$("#" + objectID).select2("val",[]);
	console.log('onGraphicClicked:',objectID , optionid);
	questioncanvas_bindnm(optionid,objectID);

	
}
 
	


var stuthumbnail_ids = '';
function onCloseExamGotoReport( PaperID,stuID)
{
	var paperids = [];
	paperids.push("{pid:" + PaperID + ", stuid:" + stuID + "}");
	$('#paperids').val(paperids);
	 document.formx1.submit();


}
function onChangedOptionList(questionID, optionID)
{ 
	$("#selected_diagrams li img").each(function(){
		stuthumbnail_ids += $(this).attr("id") + ",";
	});
	if (stuthumbnail_ids !== ''){
		stuthumbnail_ids = stuthumbnail_ids.substring(0, stuthumbnail_ids.length - 1);
	}
	console.log('questionid', questionID  , 'optionID', optionID, 'stuthumbnail_ids', stuthumbnail_ids
		,"optionID:", optionID);
	var strURLSelectOption = "";
	if(global_isRetake)
	{
		strURLSelectOption = "/cpm/student/selectedoption_retakepaper/";
	}
	else
	{
		strURLSelectOption = "/cpm/student/selectedoption/";
	}
	$.ajax({type: "POST",
	    url: strURLSelectOption,
	    dataType: "json",
	    data: {
		"questionid": questionID, 
		"stuthumbnail_ids": '',
		"optionID": optionID,
		"paperid": paperid,
		"csrfmiddlewaretoken": csrfvalue,
	    },
	    success: function(payload){
		console.log('payload',payload);
		$('input[name=question_multiselection_option]').attr('disabled','true');
		if(payload['state'] == 'success')
		{
			console.log("option sent successful");
			$("#next").click();
		
		}
		else{
			intemass.ui.showclientmsg(payload['message']);
		}
		//getProcessDialog().dialog('close');
	    },
	    error: function(MLHttpRequest, textStatus, errorThrown){
		console.log("submitpaper success/error: " + "; " + errorThrown + "; " + MLHttpRequest);

		console.log('error on select option');
	    }
	});
	$( this ).dialog( "close" );


	
}


$(function(){
	
});
;(function($, undef) {

    // OLD: var timeoutTimer = setInterval(refreshtimeout, 60000);
    var timeoutTimer = setInterval(refreshtimeout, 300000);
    var config = {
        toolbar: [],
        height: 200,
        toolbarStartupExpanded: false,
        readOnly: true
    };
	var configOption = {
		toolbar: [],
		height: 150,
		toolbarStartupExpanded: false,
		readOnly: true
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


    $(function(){
	console.log("i'm here ");
        $("#question_name_show").text(qnames[0]);
        $("#question_process_show").text(1 + "/" + qids.length);
        ////$("#question_editor").ckeditor(config);
	$("textarea").ckeditor(config);
	//$('#optionlist_option0').nextUntil('#optionlist_option100').ckeditor(config);
        loadquestion(qids[0]); 
        $("#answer_editor").ckeditor();
        
        refreshtimeout();
        $(window).bind('beforeunload', function(e){
		var strURLCheck = "";
		if(global_isRetake)
		{
			strURLCheck = "/cpm/student/checktime_retake/";
		}
		else
		{
			strURLCheck = "/cpm/student/checktime/";			
		}
            $.post(strURLCheck,
                {
                    'save': true,
                    'paperid': paperid,
                    'csrfmiddlewaretoken': csrfvalue
                },
                function(payload) {
                    console.log('time saved');
            },'json');
        }); 

        var count = qids.length -1;
        var i = 0;
        $("#previous").click(function(){
            //submitanswer(qids[i]);
            if(i !== 0){
                i -= 1;
                $("#answer_editor").val("");
                $("#question_name_show").text(qnames[i]);
                $("#question_process_show").text(i+1+"/"+qids.length);
                loadquestion(qids[i]); 
            }
        });
	
	var setSelectedOptionList = function(){
		var selected_optionlist = $('input[name=question_multiselection_option]:checked').val();
		if(selected_optionlist==null)
		{
			console.log('nothing here..is null');
		}
		else
		{
			console.log('selected', selected_optionlist);
		}
		
	};
	$("#next").click(function(){

		setSelectedOptionList();
		console.log('next clicked');
		//submitanswer(qids[i]);
		console.log("i:",i,", Count: " , count);
		if((i   ) != count  ){
			i += 1;
			$("#answer_editor").val("");
			$("#question_name_show").text(qnames[i]);
			$("#question_process_show").text(i+1+"/"+qids.length);
			loadquestion(qids[i]); 
		}
		else
		{
			
			if((i  ) ==count ){
				$("#btnGoToReport").css("display", "block");
				$("#btnGoToReport").click();
			}
		}
	});

        $("#first").click(function(){
            //submitanswer(qids[i]);
            $("#answer_editor").val("");
            $("#question_name_show").text(qnames[0]);
            $("#question_process_show").text(1+"/"+qids.length);
            loadquestion(qids[0]); 
            i = 0;
        });

        $("#last").click(function(){
            //submitanswer(qids[i]);
            $("#answer_editor").val("");
            $("#question_name_show").text(qnames[count]);
            $("#question_process_show").text(count+1+"/"+qids.length);
            loadquestion(qids[count]); 
            i = count;
	    $("#btnGoToReport").css("display", "block"); $("#btnGoToReport").click();
        });
	$("#btnBack").click(function(){
		console.log('back is clicked');
		window.location.href = "/cpm/student/index/";
	});
        $("#submit1").click(function(){
            submitpaper(qids[i], paperid);
        });

        // resolve the icons behavior with event delegation
        /* $("ul.gallery > li").click(function(event) {
            var $item = $( this );
            var $target = $( event.target );

            if ($target.is("a.ui-icon-check")){
                selectImage($item);
            }else if ($target.is("a.ui-icon-zoomin")){
                viewLargerImage( $target );
            }else if ($target.is("a.ui-icon-closethick")){
                unselectImage($item);
            }
            return false;
        });*/
    });

     


    var initcanvasarea = function(){
	console.log('initcanvasarea ');
        $(".Graphic").select2('val',[]);
	$("question_canvas").select2('val',[]);
	questioncanvas_bindnm();	
    };

    var getProcessDialog = function(){

        var processing_dialogue = $( "#dialog-process" ).dialog({
            autoOpen: false,
            resizable: false,
            height:150,
            width:550,
            modal: true
        });

        $("#progressbar").progressbar({
            value: 100 
        });
        return processing_dialogue;
    };

    

    var submitpaper = function(questionid, paperid){
        getProcessDialog().dialog('open');
        answer_html = $("#answer_editor").val();
        $("#selected_diagrams li img").each(function(){
            stuthumbnail_ids = $(this).attr("id");
        });
        $.ajax(
            {
                type: "POST",
                url: "/student/submitanswer/",
                dataType: "json",
                data: {
                    "answer_html": answer_html, 
                    "stuthumbnail_ids": stuthumbnail_ids,
                    "csrfmiddlewaretoken": csrfvalue,
                    "questionid": questionid,
            },
            success: function(payload){
		console.log("submitpaper success");
                $.ajax(
                    {
                        type: "POST",
                        url: "/student/submitpaper/",
                        dataType: "json",
                        data: {
                            "paperid": paperid,
                            'csrfmiddlewaretoken': csrfvalue
                    },
                    success: function(payload){
			console.log("submitpaper success/success");
                        getProcessDialog().dialog('close');
                        if(payload['state'] === 'passed'){
                            gotosummarize(paperid, true);
                        }else if (payload['state'] === 'failed'){
                            gotosummarize(paperid, false);
                        }
                    },
                    error: function(MLHttpRequest, textStatus, errorThrown){
			console.log("submitpaper success/error: " + "; " + errorThrown + "; " + MLHttpRequest);
                        getProcessDialog().dialog('close');
                        }
                });
            },
            // OLD: error: function(MLHttpRequest, textStatus, errorThrown){}
	    error: function(MLHttpRequest, textStatus, errorThrown){
		console.log("submitpaper error: " + textStatus + "; " + errorThrown + "; " + MLHttpRequest);
                getProcessDialog().dialog('close');
	    }
        });
    };
var global_questionID = 0;

    /// This is to retrieve option list;
    var loadquestion = function(questionid){
	global_questionID = questionid;
	var strURL_StudentGet = "";
	if( global_isRetake)
	{
		strURL_StudentGet = "/cpm/question/stu_retake_get/";
	}
	else{
		strURL_StudentGet = "/cpm/question/stuget/";
	}
        if(questionid != -1){
            $.post(strURL_StudentGet ,
            {
                'questionid': questionid,
                'csrfmiddlewaretoken': csrfvalue,
		'paperid':paperid
            },
            function(payload){
		console.log(payload);
		//minhong
		console.log('here logging');
                if(payload.state === "success"){
		    i=1;
			console.log("payload['clozepassage_content']", payload.clozepassage_content);
		    $("#question_content").html(payload.clozepassage_content); 
                    
			 
			//bindImageIconClick();
			//initcanvasarea();


			

			 //$("#question_canvas").select2("val", question_canvas_name);
                }
		$( "textarea" ).each(function( index ) {
			if (CKEDITOR.instances[$(this).attr("id")]) {
			    CKEDITOR.remove(CKEDITOR.instances[$(this).attr("id")]);
			}
		});
		$("textarea").ckeditor(configOption);
		//setAllNyroModal();
            },
            'json');
        }
    };  


    var gotosummarize = function(paperid, passed){
	console.log('gotosummarize');
        if (passed){
            timeused = $('#time_show').text().split('/')[0];
            clearInterval(timeoutTimer);
            url = "/student/summarize/?paperid=" + paperid + "&time=" + timeused;
        }else{
            clearInterval(timeoutTimer);
            url = "/student/summarize/?paperid=" + paperid + "&passed=0";
        }
        window.location.href = url;
    };


    function refreshtimeout(){
	var paperid  = intemass.util.getUrl('paperid');
        $.post("/student/checktime/",
        {
            'paperid': paperid,
            'csrfmiddlewaretoken': csrfvalue
        },
        function(payload) {
            if(payload['timeout'] === "yes"){
                var process = $("#question_process_show").text().split('/');
                var index = Number(process[0]);
                var total = Number(process[1]);
                submitpaper(qids[index], paperid);
            }else if (payload){
                $("#time_show").text(payload['timeleft'] + '/' + payload['totaltime']);
            }
        }, 'json');
    };

    refreshtimeout();

})(jQuery);




function fillinblank(obj, questionseq , questionid,paperid)
{
	
	console.log('$(obj).val():' , $(obj).val());
	console.log('question seq:' , questionseq);
	console.log('questionid seq:' , questionid);
	$.ajax(
            {
                type: "POST",
                url: "/cpm/student/fillinanswer/",
                dataType: "json",
                data: {
                    "questionid": questionid,
                    "questionseq": questionseq,
                    "answer": $(obj).val(),
                    "paperid": paperid,
                    'csrfmiddlewaretoken': csrfvalue
            },
            success: function(payload){
		console.log("submitpaper success/success");
                 
            },
            error: function(MLHttpRequest, textStatus, errorThrown){
		console.log("submitpaper success/error: " + "; " + errorThrown + "; " + MLHttpRequest); 
                }
        });





}

