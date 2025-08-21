// Support for report_studentanswer.html (see question_getstureport in question/views.py)

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

var global_questionID = 0;
;(function($, undef) {
    var config = {
        toolbar: [],
        height: 150,
	width:420,
        resize_enabled: false,
        toolbarStartupExpanded: false,
        readOnly: true,
        font_style: {
            element: 'span',
            styles: {'font-size': '24px'}
        },
        pasteFromWordRemoveStyles : true
    };
    var configQuestion = {
        toolbar: [],
        height: 150,
	width:600,
        resize_enabled: false,
        toolbarStartupExpanded: false,
        readOnly: true,
        font_style: {
            element: 'span',
            styles: {'font-size': '24px'}
        },
        pasteFromWordRemoveStyles : true
    };
    var qids = [];
    var qnames = [];
    var qlength = 0;
    var qindex = 0;
    var pindex = 0;
    var originmark;

    $(function(){
        if(group === 'teachers'){
            $("#question_editor").ckeditor(configQuestion);
            $("#stuanswer_editor").ckeditor(config);
            $("#omitted_editor").ckeditor(config);
            //$("#grammar_editor").ckeditor(config);
            studentid = stuids[0];
            $('#backbutton').attr("href", '/mcq/report/teacher');
            //$('#backbutton').text("Back to Teacher's Assignment Record");
            mkmarkeditable();
        }else{
            var readonlyconfig = config;
            readonlyconfig['contentsCss'] = '/static/css/preventpaste.css'; 
            $("#question_editor").ckeditor(configQuestion);
            $("#stuanswer_editor").ckeditor(readonlyconfig);
            $("#omitted_editor").ckeditor(readonlyconfig);
            //$("#grammar_editor").ckeditor(readonlyconfig);
            var $omitted_editor = $('#omitted_editor').ckeditorGet();
            var $stuanswer_editor = $('#stuanswer_editor').ckeditorGet();
            //var $grammar_editor = $('#grammar_editor').ckeditorGet();
            $('#backbutton').attr("href", '/mcq/report/student');
            //$('#backbutton').text("Back to Student's Assignment Record");
            preventpaste([$omitted_editor, $stuanswer_editor]);
        }

        initloadquestion();
        bindbtnclickevent();
    });


    var mkmarkeditable = function(){
        console.log("mkmarkeditable")
        $('#editmark').editable(function(mark, settings){
            console.log("mkmarkeditable editable: mark=" + (mark || "null"))
            var reg = /^[0-9]*$/;
            if (reg.test(mark)){


		console.log("==========================================================");
		console.log("====== teacher/updatemark/                            ====");
		console.log("==========================================================");
                originmark = mark;
                $.ajax({
                    type: "post",
                    url: "/mcq/teacher/updatemark/",
                    datatype: "json",
                    data: {"studentid": studentid,
                           "questionid": qids[qindex],
                           "mark": mark,
                           "csrfmiddlewaretoken": csrfvalue
                          },
                    success: function(payload) {
                        if(payload['state'] === 'success'){
                            $('#editmark').text(payload['mark']);
                        }
                    },
                    error: function(xmlhttprequest, textstatus, errorthrown) {
                        $('#editmark').text(originmark);
                        return this;
                    }
                });
            }else{
                $("#editmark").text(originmark);
            }
        },{
            type: "text",
            onblur: "submit",
            style: 'display:inline'
        });
    };

    var preventpaste = function($editorlist){
        var ctrlDown = false;
        var ctrlKey = 17, vKey = 86, cKey = 67;
        
        for (var i = 0; i < $editorlist.length; i += 1){
            var $editor = $editorlist[i];
            $editor.on('contentDom', function(){
                $editor.document.$.onselectstart = function(){
                    return false;
                };
            });
        }

    };
    
    var initloadquestion = function(){
        if(paperid !== '' && studentid !== ''){
            var questionfound = false;
            for(var k = 0, length = pids.length; k < length; k += 1){
                if(paperid == pids[k] && studentid == stuids[k]){
                    pindex = k;
                    loadpaperinfo(pids[k]);
                    getquestionid(pids[k], stuids[k]);
                    questionfound = true;
                    break;
                }
            }
            if(!questionfound){
                loadpaperinfo(pids[0]);
                getquestionid(pids[0], stuids[0]);
            }
        }else{
            loadpaperinfo(pids[0]);
            getquestionid(pids[0], stuids[0]);
        }
	initcanvasarea();
    };  


    var bindbtnclickevent = function(){
        // resolve the icons behavior with event delegation
        $("ul.gallery > li").click(function(event){
            var $item = $(this);
            var $target = $(event.target);
            if ($target.is("a.ui-icon-zoomin")){
                viewLargerImage($target);
            }
            return false;
        });

        $("#previous").click(function(){
            if(qindex !== 0){
                qindex -= 1;
                $("#omitted_editor").val("");
                $("#question_name_show").text(qnames[qindex]);
                $("#question_process_show").text(String(qindex+1) + "/" + String(qlength+1));
                loadquestion(qids[qindex], stuids[0]);
                //alert(qids[qindex]);
                var qid_seq = qids[qindex]; 
                //alert(qid_seq);
                var feedback_url = $("#feedback_btn").attr("href")
                
                //feedback_url = feedback_url.replace('?question_id=698','?question_id='+qid_seq)
                //var ft = feedback_url.split('?question_id=');
                //alert(ft[1]);
                //feedback_url = feedback_url.replace('question_id='+ft[1],'question_id='+qid_seq)
                $("#feedback_btn").attr("href", feedback_url);
                
                //alert(feedback_url);
                pullThumbnails(qids[qindex], stuids[0]);
            }
        });

        $("#next").click(function(){
            if(qindex !== qlength){
                qindex += 1;
                
                $("#omitted_editor").val("");
                $("#question_name_show").text(qnames[qindex]);
                $("#question_process_show").text(String(qindex+1) + "/" + String(qlength+1));
                loadquestion(qids[qindex], stuids[0]);
               
                //alert(qids[qindex]);
                var qid_seq = qids[qindex]; 
                //alert(qid_seq);
                var feedback_url = $("#feedback_btn").attr("href")
                
                //feedback_url = feedback_url.replace('?question_id=698','?question_id='+qid_seq)
                //var ft = feedback_url.split('?question_id=');
                //alert(ft[1]);
                //feedback_url = feedback_url.replace('question_id='+ft[1],'question_id='+qid_seq)
                $("#feedback_btn").attr("href", feedback_url);
                
                //alert(feedback_url);
                
                pullThumbnails(qids[qindex], stuids[0]);
            }
        });

        $("#first").click(function(){
            if(qindex !== 0){
                $("#omitted_editor").val("");
                $("#question_name_show").text(qnames[0]);
                $("#question_process_show").text(1+"/"+String(qlength+1));
                loadquestion(qids[0], stuids[0]);
                // alert(qids[0]);
                var qid_seq = qids[0]; 
                //alert(qid_seq);
                var feedback_url = $("#feedback_btn").attr("href")
                
                //feedback_url = feedback_url.replace('?question_id=698','?question_id='+qid_seq)
                //var ft = feedback_url.split('?question_id=');
                //alert(ft[1]);
                //feedback_url = feedback_url.replace('question_id='+ft[1],'question_id='+qid_seq)
                $("#feedback_btn").attr("href", feedback_url);
                
                //alert(feedback_url);
                pullThumbnails(qids[qindex], stuids[0]);
                qindex = 0;
            }
        });

        $("#last").click(function(){
            if(qindex !== qlength){
                $("#omitted_editor").val("");
                $("#question_name_show").text(qnames[qlength]);
                $("#question_process_show").text(String(qindex+1) + "/" + String(qlength+1));
                loadquestion(qids[qlength], stuids[0]);
                 //alert(qids[qlength]);
                var qid_seq = qids[qlength]; 
                //alert(qid_seq);
                var feedback_url = $("#feedback_btn").attr("href")
                
                //feedback_url = feedback_url.replace('?question_id=698','?question_id='+qid_seq)
                //var ft = feedback_url.split('?question_id=');
                //alert(ft[1]);
                //feedback_url = feedback_url.replace('question_id='+ft[1],'question_id='+qid_seq)
                $("#feedback_btn").attr("href", feedback_url);
                
                //alert(feedback_url);
                pullThumbnails(qids[qlength], stuids[0]);
                qindex = qlength;
            }
        });


        $("#next_paper").click(function(){
            if(pindex !== pids.length - 1){
                pindex += 1;
                loadpaperinfo(pids[pindex]);
                getquestionid(pids[pindex], stuids[pindex]);
            }
            
        });

        $("#pre_paper").click(function(){
            if(pindex !== 0){
                pindex -= 1;
                loadpaperinfo(pids[pindex]);
                getquestionid(pids[pindex], stuids[pindex]);
            }
        });
    };

    
    var loadcanvasbtngroup = function(canvaslist, questionid){
        if (canvaslist['stucanvas'] && canvaslist['stucanvas'].length > 0){
            if ($('#stucanvas').length === 0){
                $("#stucanvasbtn").append("<div><h5>Your Graph Answer:</h5><p class='longp btngroup' id='stucanvas'></p><p /><div>");
            }
            for (var i = 0; i < canvaslist['stucanvas'].length; i += 1){
                var canvasname = canvaslist['stucanvas'][i][1];
                $('#stucanvas').append("<a class='nyroModal blueBtn' id='stucanvas" + canvasname + "'>" + canvasname + "</a>");
                pullstucanvas(canvasname, questionid, canvaslist['stucanvas'][i][0]);
            }        
        }
        if (canvaslist['stdcanvas'] && canvaslist['stdcanvas'].length > 0){
            if ($('#stdcanvas').length === 0){
                $("#stdcanvasbtn").append("<div><h5>Standard Graph Answer:</h5><p class='longp btngroup' id='stdcanvas'></p><p /><div>");
            }
            for (var i = 0; i < canvaslist['stdcanvas'].length; i += 1){
                var canvasname = canvaslist['stdcanvas'][i][1];
                $('#stdcanvas').append("<a class='nyroModal blueBtn' id='stdcanvas" + canvasname + "'>" + canvasname + "</a>");
                pullstdcanvas(canvasname, questionid, canvaslist['stdcanvas'][i][0]);
            }  
        }
    };


    var getnmopts = function(){ 
        var width = 1330;
        var height = 700;
        return nmopts = {
            sizes: { 
                initW: width,
                initH: height,
                w: width,
                h: height,
                minW: width,
                minH: height
            },
            callbacks: {
                beforeShowCont: function() { 
                    width = $('.nyroModalCont').width();
                    height = $('.nyroModalCont').height();
                    $('.nyroModalCont iframe').css('width', width);
                    $('.nyroModalCont iframe').css('height', height);
                }
            }
        };
    };


    var pullstucanvas = function(canvasname, questionid, stuanswerid){
        var canvasid = '#stucanvas' + canvasname;
	var strURLCanvas = "";
	if(isRetake)
	{
		strURLCanvas = "/mcq/canvas/";
	}
	else{
		strURLCanvas = "/mcq/canvas/";
	}
        $(canvasid).attr({
            'href': strURLCanvas + '?canvasname=' + canvasname + '&questionid=' + questionid + '&stuanswerid=' + stuanswerid + '&view=1&paperid=' + paperid + '&isRetake=' + isRetake,
            'target': '_blank',
        });
        $(canvasid).nm(getnmopts());
    };



    var updateomitted = function(){
        var omitted = $('#omitted_editor').val();
        $.post("/mcq/teacher/updateomitted/",
               {
                   "studentid": studentid,
                   "questionid": qids[qindex],
                   "omitted": omitted,
                   'csrfmiddlewaretoken': csrfvalue
               },
               function(payload) {

               },'json');
    }

    /********************
     *
     * get all the questions'id in the paper of a student
     *
     ********************/
    var getquestionid = function(paperid, student_id){
	console.log('getquestionid');
        $.post("/mcq/question/getid/",
               {
                   'paperid': paperid,
                   'csrfmiddlewaretoken': csrfvalue
               },
               function(payload){
                   if(payload.state === "success"){
                       qids = payload['qids'];
                       qnames = payload['qnames'];
                       qlength = qids.length - 1;
                       qindex = 0;
                       $("#question_process_show").text(String(qindex+1)+"/"+String(qlength+1));
                       $("#question_name_show").text(qnames[0]);
                       loadquestion(qids[0], student_id);
                       pullThumbnails(qids[0], student_id);
                       
                      
                       //var feedback_url = $("#feedback_btn").attr("href");
                       //feedback_url = feedback_url + "?question_id=" + qids[0];
                       //$("#feedback_btn").attr("href", feedback_url);
                       
                       
                       if($("#feedback_btn").attr("href") == "#"){
                            var feedback_url = "/mcq/report/popup/" + paperid + "/" +  student_id + "/?question_id="  + qids[0];
                            $("#feedback_btn").attr("href", feedback_url);
                            //alert("URL set") ;
                       }
                       else{
                            var feedback_url = $("#feedback_btn").attr("href");
                            feedback_url = feedback_url + "?question_id=" + qids[0];
                            $("#feedback_btn").attr("href", feedback_url);
                            //alert("URL set again") ;                        
                       }
                       
                   }
               },
               'json');
    };

    var loadpaperinfo = function(paperid){
	console.log('loadpaperinfo');
        _getProcessDialog().dialog('open');
        $.post("/mcq/paper/info/",
               {
                   'paperid': paperid,
                   'csrfmiddlewaretoken': csrfvalue
               },
               function(payload){
                   if(payload.state === "success"){
                       // OLD: _getProcessDialog().dialog('close');
                       $("#paper_id_show").text(payload['papername']);
                       $("#year_show").text(payload['year']);
                       $("#subject_show").text(payload['subject']);
                       $("#level_show").text(payload['level']);
                       $("#assignment_show").text(payload['assignment']);
			$("#question_mark_show").text(payload['markshow']);
                   }
                   _getProcessDialog().dialog('close');
               },
               'json');
    };

    var loadquestion = function(questionid, studentid){
         //alert(questionid);
	console.log('loadquestion');
        _getProcessDialog().dialog('open');

        
	global_questionID = questionid;
        if(questionid !== -1){
		questioncanvas_bindnm();
		console.log('D1_V1');
		console.log('paperid',paperid);
            //alert(questionid);
		$.ajax({
		  type: "POST",
		  url: "/mcq/question/stureport/",
		  data: {
                       'questionid': questionid,
                       'studentid': studentid,
			'paperid':paperid,
                       'csrfmiddlewaretoken': csrfvalue,
			'isRetake': isRetake
                   },
		  dataType: 'json',
		  success: function(payload){
			console.log("loadquestion payload", payload.state);
                       // DEBUG: console.log("loadquestion payload=" + JSON.stringify(payload))
			if(payload.state === "success"){
				var omitted = '';
				// OLD: _getProcessDialog().dialog('close');
				$("#student_name").text(payload['stuname']);
				$("#question_editor").val(payload['question']);
				$("#question_mark_show").html(payload['total_mark']);
				console.log('now ..mark is ', payload['total_mark']);
				$("#editmark").text(payload['mark']);
				originmark = payload['mark'];
				for (var i = 0, length = payload['omitted'].length; i < length; i+=1){
				if (payload['omitted'][i][0] === 'C'){
				omitted += "<span style='color:green'><p>" + payload['omitted'][i].substring(1) + "</p><span>";
				}else if(payload['omitted'][i][0] === 'W'){
				omitted += "<span style='color:red'><p>" + payload['omitted'][i].substring(1) + "</p><span>";
			}
			else omitted += "<span style='color:red'><p>" + payload['omitted'][i] + '</p></span>';
			}
			$("#stuanswer_editor").val(payload['stuanswer']);
			//$("#omitted_editor").val(omitted);
			$("#closeness").text(payload['closeness']);
			$("#closeness_band").text(payload['closeness_band']);
			$("#num_closeness_bands").text(payload['num_closeness_bands']);
			$("#omitted_editor").val(payload['stdanswer']);
			$("#stdcanvas").attr('href','/mcq/optioncanvas/?canvasname=1&optionid=' + payload['optionid_stdanswer']);
			$("#stucanvas").attr('href','/mcq/optioncanvas/?canvasname=1&optionid=' + payload['optionid_stuanswer']);
			//$("#grammar_editor").val(payload['grammar_issues']);
			loadcanvasbtngroup(payload['canvas'], questionid);




			}
			_getProcessDialog().dialog('close');
		  },
		  error: function(XMLHttpRequest, textStatus, errorThrown) {
		     alert(XMLHttpRequest.responseText);
		  }
		});

		
            
        }
    };

    var pullThumbnails = function(questionid, studentid){
	console.log('pullThumbnails');
	$.ajax({
		type: "POST",
		url: "/mcq/question/reportthumbnails/",
		data: {
                   'questionid': questionid,
                   'studentid': studentid,
                   'csrfmiddlewaretoken':csrfvalue,
		   'isRetake': isRetake
               },
		dataType: 'json',
		success: function(payload){
			console.log('reportthumbnails' , 'payload.state:' , payload.state);
			if(payload.state === "success"){
				console.log('step 1');
				console.log(payload['questionthumbnails']);
				console.log('step 2');
				questionthumbnails = payload['questionthumbnails'];
				stdthumbnails = payload['stdthumbnails'];
				stuthumbnails = payload['stuthumbnails'];
				console.log(payload['stuthumbnails']);
				console.log(payload['stuthumbnails']);
				questionthumbhtml = makeimagethumbnailhtml(questionthumbnails);
				var $questionlist = $( "ul", $("#questionthumbnails"));
				$( "#questionthumbnails li").remove();
				$(questionthumbhtml).appendTo($questionlist);

				stdthumbhtml = makeimagethumbnailhtml(stdthumbnails);
				var $stdlist = $( "ul", $("#stdthumbnails"));
				$( "#stdthumbnails li").remove();
				$(stdthumbhtml).appendTo($stdlist);

				stuthumbhtml = makeimagethumbnailhtml(stuthumbnails);
				var $stulist = $( "ul", $("#stuthumbnails"));
				$( "#stuthumbnails li").remove();
				$(stuthumbhtml).appendTo($stulist);
				bindImageIconClick();
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			alert(XMLHttpRequest.responseText);
		}
	});


    };


    var makeimagethumbnailhtml = function(thumbnails){
	console.log('makeimagethumbnailhtml');
        var thumbhtml = '';
        for (t in thumbnails){
            thumbhtml += '<li class="ui-widget-content ui-corner-tr">';
            thumbhtml += '<h6 class="ui-widget-header">'+thumbnails[t][1].slice(0,5)+'...'+'</h6>';
            thumbhtml += '<img src="/static/'+thumbnails[t][0]+'"  alt="'+thumbnails[t][1]+'" width="96" height="72"></img>';
            thumbhtml += '<a href="/static/'+thumbnails[t][2]+'" title="View Larger Image" class="ui-icon ui-icon-zoomin">View Larger</a>';
        }
        return thumbhtml;
    };


    var bindImageIconClick= function(){
	console.log('bindImageIconClick');

        var $imagesfrom = $( "#selected_diagrams" );
        var $imagesto = $( "#correct_diagrams" );

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
        }
    };

    var _getProcessDialog = function(){
	console.log('getProcessDialog');
        var processing_dialogue = $( "#dialog-process" ).dialog({
            autoOpen: false,
            resizable: false,
            height:150,
            width:550,
            modal: true
        });
        $( "#progressbar" ).progressbar({
            value: 100
        });
        return processing_dialogue;
    };


    var disableSelection = function($editor){
	console.log('disableSelection');       
        $editor.addCss('no_select');              
        if($.browser.msie)
        {
            $editor.attr('unselectable', 'on').on('selectstart', false);            
        }
    };
////============================== 2nd object ====================================================

var bindImageIconClick = function(){

        var $imagesfrom = $( "#possible_diagrams" );
        var $imagesto = $( "#stuthumbnails" );
        var unselect_icon = "<a href='#' title='Unselect this image' class='ui-icon ui-icon-closethick'>Unselect</a>";
        var selectImage = function( $item ) {
            $item.fadeOut(function() {
                var thumbnails = [];              
                var $list = $( "ul", $imagesto );		
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

/// ===================================== Question Canvas ========================================
var answercanvas_bindnm;
    answercanvas_bindnm = function(questionid, stuanswerid) {
	console.log('answercanvas_bindnm');
        $(".Graphic").click(function() {
            var canvasurl = $(this).attr('href');
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
var  questioncanvas_bindnm = function(){
	
		var test = document.getElementById("question_canvas")
		var canvasurl =  '/mcq/canvas/?canvasname=1&questionid=' + global_questionID + '&view=' + ''; 
		console.log('canvasurl:' , canvasurl);
		test.setAttribute("class","nyroModal populate greenBtn");
		test.setAttribute("href", canvasurl)
		test.setAttribute("target", "_blank")
		$("#question_canvas").unbind('click').click(function(event){
			    $("#question_canvas").off();
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
				url: $("#question_canvas").attr("href") ,
				success: function (resp) {
						$("#question_canvas").trigger('click');
					},
				error: function(e){
						alert('Error:');
					}  
			    });
			});
		


		$( ".Graphic" ).each(function( index ) {
			var strID ="#" +  $(this).attr("id");
			$(strID).unbind('click').click(function(event){
			    $(strID).off();
			    width: "copy"
			    tokenSeparators: [",", " "]
			    event.preventDefault()
			    $(this).nm(nmopts);
				$(this).next().attr({
						'onclick': function () {
							return false;
						}
					});
				console.log('$(strID).attr("href")', $(strID).attr("href"));
			    $.ajax({
				url: $(strID).attr("href") ,
				success: function (resp) {
						$(strID).trigger('click');
					},
				error: function(e){
						alert('Error:');
					}  
			    });
			});
		});
	
	};

var initcanvasarea = function(){
	console.log('initcanvasarea ');
        $(".Graphic").select2('val',[]);
	$("question_canvas").select2('val',[]);
	questioncanvas_bindnm();	
    };
/// ======================================End of Question Canvas =================================




		

})(jQuery);

function submitform(){
	console.log('submitform');     
    $('#stuids').val(stuids);
    $('#pids').val(pids);
    //var que_display = $("#question_name_show").val(qids)
    //alert(que_display);
    //var feedback_url = $("#feedback_btn").attr("href");
    //                   feedback_url = feedback_url + "?question_id=" + qids[0];
    //                   $("#feedback_btn").attr("href", feedback_url);
    //alert(stuids);
    document.forms[0].submit();
}
