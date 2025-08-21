/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */

var stuthumbnail_ids = '';
function onChangedOptionList(questionID, optionID)
{

	var dialogue = $( "#dialog-confirm" ).dialog({
		resizable: false,
		height:150,
		modal: true,
		buttons: {
		    "Confirm": function() {
			console.log('questionid', questionID  , 'optionID', optionID);
			$.ajax({type: "POST",
			    url: "/mcq/student/selectedoption_retakepaper/",
			    dataType: "json",
			    data: {
				"questionid": questionID, 
				"optionID": optionID,
				"csrfmiddlewaretoken": csrfvalue,
			    },
			    success: function(payload){
				console.log('payload',payload);
				$('input[name=question_multiselection_option]').attr('disabled','true');
				if(payload['state'] == 'success')
				{
					console.log("option sent successful");
				}
				else{
					intemass.ui.showclientmsg(payload['message']);
				}
				//getProcessDialog().dialog('close');
			    },
			    error: function(MLHttpRequest, textStatus, errorThrown){
				//getProcessDialog().dialog('close');
				console.log('error on select option');
			    }
			});
			$( this ).dialog( "close" );

		    },
		Cancel: function() {
			var optionlistobj = $('input[name=question_multiselection_option]:checked');
			optionlistobj.removeAttr('checked')
			//$(this).prop('checked', false);
			    $( this ).dialog( "close" );
			}
		}});




	
}
;(function($, undef) {

    // OLD: var timeoutTimer = setInterval(refreshtimeout, 60000);
    var timeoutTimer = setInterval(refreshtimeout, 300000);
    var config = {
        toolbar: [],
        height: 500,
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
        $("#question_name_show").text(qnames[0]);
        $("#question_process_show").text(1 + "/" + qids.length);
        $("#question_editor").ckeditor(config);
        loadquestion(qids[0]);
        pullThumbnails(qids[0]);
        $("#answer_editor").ckeditor();
        
        refreshtimeout();
        $(window).bind('beforeunload', function(e){
            $.post("/mcq/student/checktime_retake/",
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
                pullThumbnails(qids[i]);
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
		
		//submitanswer(qids[i]);
		if(i !== count){
			i += 1;
			$("#answer_editor").val("");
			$("#question_name_show").text(qnames[i]);
			$("#question_process_show").text(i+1+"/"+qids.length);
			loadquestion(qids[i]);
			pullThumbnails(qids[i]);
		}
	});

        $("#first").click(function(){
            //submitanswer(qids[i]);
            $("#answer_editor").val("");
            $("#question_name_show").text(qnames[0]);
            $("#question_process_show").text(1+"/"+qids.length);
            loadquestion(qids[0]);
            pullThumbnails(qids[0]);
            i = 0;
        });

        $("#last").click(function(){
            //submitanswer(qids[i]);
            $("#answer_editor").val("");
            $("#question_name_show").text(qnames[count]);
            $("#question_process_show").text(count+1+"/"+qids.length);
            loadquestion(qids[count]);
            pullThumbnails(qids[count]);
            i = count;
        });
	$("#btnBack").click(function(){
		console.log('back is clicked');
		window.location.href = "/mcq/student/index/";
	});
        $("#submit1").click(function(){
            submitpaper(qids[i], paperid);
        });

        // resolve the icons behavior with event delegation
        $("ul.gallery > li").click(function(event) {
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
        });
    });

    var answercanvas_bindnm;
    answercanvas_bindnm = function(questionid, stuanswerid) {
        $("#s2id_answer_canvas").find("ul li div").click(function() {
            var canvasurl = '/canvas/?canvasname=' +  $(this).text() + '&questionid=' + questionid + '&stuanswerid=' + stuanswerid + '&view=undefined';
            $(this).attr({
                'class': 'nyroModal',
                'href': canvasurl,
                'target': '_blank'
            });
            $(this).nm(nmopts);
            $(this).next().attr({
                'onclick': function () {
                    return false;
                }
            });
        });
    };

    var initcanvasarea = function(question_canvas_name, questionid, stuanswerid){
        $("#answer_canvas").select2(
        {
            width: "copy",
            tokenSeparators: [",", " "]
        }).on("change", function(){
              answercanvas_bindnm(questionid, stuanswerid);
        });
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


    var loadquestion = function(questionid){
        if(questionid != -1){
            $.post("/mcq/question/stu_retake_get/",
            {
                'questionid': questionid,
                'csrfmiddlewaretoken': csrfvalue
            },
            function(payload){
		console.log('retake and get question here')
                if(payload.state === "success"){
                    var retake = intemass.util.getUrl('retake');
                    $("#question_editor").val(payload['question_content']);
                    if(!retake){
                        $("#answer_editor").val(payload['question_stuanswer']);
                    }
		    console.log("this is the multiselect",payload['question_multiselection']);
                    initcanvasarea(payload['question_canvas'], questionid, payload['stuanswerid']);
  	    		$("#question_multiselection")
			.html(payload['question_multiselection']);
                }
            },
            'json');
        }
    };

    var pullThumbnails = function(questionid){
	return;
        $.post("/question/studentthumbnails/",
        {
            'questionid': questionid,
            'csrfmiddlewaretoken': csrfvalue
        },
        function(payload) {
            if(payload.state === "success"){
                thumbnails = payload['thumbnails'];
                stuthumbnails = payload['stuthumbnails'];
                thumbhtml = makeimagethumbnailhtml(thumbnails, false);
                stuthumbhtml = makeimagethumbnailhtml(stuthumbnails, true);
                var $list = $("ul", $("#thumbnails"));
                $("#thumbnails li").remove();
                $(thumbhtml).appendTo($list);
                $list = $( "ul", $("#stuthumbnails"));
                $("#stuthumbnails li").remove();
                $(stuthumbhtml).appendTo($list);
                bindImageIconClick();
            }
        }, 'json');
    };


    var makeimagethumbnailhtml = function(thumbnails, selected){
        var thumbhtml = '';
        for (var t in thumbnails){
            thumbhtml += '<li class="ui-widget-content ui-corner-tr">';
            thumbhtml += '<h6 class="ui-widget-header">' + thumbnails[t][1].slice(0,5) + '...' + '</h6>';
            thumbhtml += '<img src="/static/' + thumbnails[t][0] + '" id=' + thumbnails[t][3] +' alt="' + thumbnails[t][1] + '" width="96" height="72"></img>';
            thumbhtml += '<a href="/static/' + thumbnails[t][2] + '" title="View Larger Image" class="ui-icon ui-icon-zoomin">View Larger</a>';
            if (selected){
                thumbhtml += '<a href="#" title="Unselect Image" class="ui-icon ui-icon-closethick">unselect</a>';
            }else{
                thumbhtml += '<a href="#" title="Select Image" class="ui-icon ui-icon-check">select</a>';
            }
        }
        return thumbhtml;
    };


    var bindImageIconClick = function(){

        var $imagesfrom = $( "#possible_diagrams" );
        var $imagesto = $( "#stuthumbnails" );

        $( "li", $imagesfrom ).draggable({
            cancel: "a.ui-icon", // clicking an icon won't initiate dragging
            revert: "invalid", // when not dropped, the item will revert back to its initial position
            helper: "clone",
        });

        $imagesto.droppable({
            accept: "#possible_diagrams > li",
            activeClass: "ui-state-highlight",
            drop: function(event, ui){
                selectImage(ui.draggable);
            }
        });

        $imagesfrom.droppable({
            accept: "#selected_diagrams li",
            activeClass: "ui-state-highlight",
            drop: function(event, ui) {
                unselectImage(ui.draggable);
            }
        });

        var unselect_icon = "<a href='#' title='Unselect this image' class='ui-icon ui-icon-closethick'>Unselect</a>";
        var selectImage = function( $item ) {
            $item.fadeOut(function() {
                var thumbnails = [];
                /*
                   var $list = $( "ul", $imagesto ).length ?
                   $( "ul", $imagesto ) :
                   $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $imagesto );
                   */
                var $list = $( "ul", $imagesto );

                $item.find( "a.ui-icon-check" ).remove();
                $item.append( unselect_icon ).appendTo( $list ).fadeIn();
            });
        };

        // image recycle function
        var check_icon = "<a href='#' title='Select this image' class='ui-icon ui-icon-check'>Select image</a>";
        var unselectImage = function( $item ) {
            $item.fadeOut(function() {
                $item
                .find( "a.ui-icon-closethick" )
                .remove()
                .end()
                .css( "width", "96px")
                .append( check_icon )
                .find( "img" )
                .css( "height", "72px" )
                .end()
                .appendTo( $imagesfrom )
                .fadeIn();
            });
        };

        var viewLargerImage = function( $link ) {
            var src = $link.attr( "href" ),
                title = $link.siblings( "img" ).attr( "alt" ),
                $modal = $( "img[src$='" + src + "']" );

            if ( $modal.length ) {
                $modal.dialog( "open" );
            } else {
                var img = $( "<img alt='" + title + "' width='768' height='576' style='display: none; padding: 8px;' />" )
                    .attr( "src", src ).appendTo( "body" );
                setTimeout(function() {
                    img.dialog({
                        title: title,
                        width: 960,
                        modal: true
                    });
                }, 1 );
            }
        };

        // resolve the icons behavior with event delegation
        $( "ul.gallery > li" ).click(function( event ) {
            var $item = $( this );
            var $target = $( event.target );
            if ( $target.is( "a.ui-icon-check" ) ) {
                selectImage( $item );
            } else if ( $target.is( "a.ui-icon-zoomin" ) ) {
                viewLargerImage( $target );
            } else if ( $target.is( "a.ui-icon-closethick" ) ) {
                unselectImage( $item );
            }
            return false;
        });
    } 


    var gotosummarize = function(paperid, passed){
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
        $.post("/student/checktime_retake/",
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

