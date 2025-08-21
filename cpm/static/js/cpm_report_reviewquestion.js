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
    var qids = [];
    var qnames = [];
    var qlength = 0;
    var qindex = 0;
    var pindex = 0;
    var originmark;

    $(function(){
        if(group === 'teachers'){
             
            studentid = stuids[0];
            $('#backbutton').attr("href", '/cpm/report/teacher');
            //$('#backbutton').text("Back to Teacher's Assignment Record");
            mkmarkeditable();
        }else{
             
            $('#backbutton').attr("href", '/cpm/report/student');
            //$('#backbutton').text("Back to Student's Assignment Record");
            //preventpaste([$omitted_editor, $stuanswer_editor]);
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
                    url: "/cpm/teacher/updatemark/",
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
    };  


    var bindbtnclickevent = function(){
       

        $("#previous").click(function(){
            if(qindex !== 0){
                qindex -= 1; 
                $("#question_name_show").text(qnames[qindex]);
                $("#question_process_show").text(String(qindex+1) + "/" + String(qlength+1));
                loadquestion(qids[qindex], stuids[0]); 
                var qid_seq = qids[qindex];  
                var feedback_url = $("#feedback_btn").attr("href") 
                $("#feedback_btn").attr("href", feedback_url);
                 
            }
        });

        $("#next").click(function(){
            if(qindex !== qlength){
                qindex += 1;
                 
                $("#question_name_show").text(qnames[qindex]);
                $("#question_process_show").text(String(qindex+1) + "/" + String(qlength+1));
                loadquestion(qids[qindex], stuids[0]);
                
                var qid_seq = qids[qindex];  
                var feedback_url = $("#feedback_btn").attr("href") 
                $("#feedback_btn").attr("href", feedback_url); 
            }
        });

        $("#first").click(function(){
            if(qindex !== 0){
                $("#omitted_editor").val("");
                $("#question_name_show").text(qnames[0]);
                $("#question_process_show").text(1+"/"+String(qlength+1));
                loadquestion(qids[0], stuids[0]); 
                var qid_seq = qids[0];  
                var feedback_url = $("#feedback_btn").attr("href") 
                $("#feedback_btn").attr("href", feedback_url); 
                qindex = 0;
            }
        });

        $("#last").click(function(){
            if(qindex !== qlength){
                $("#omitted_editor").val("");
                $("#question_name_show").text(qnames[qlength]);
                $("#question_process_show").text(String(qindex+1) + "/" + String(qlength+1));
                loadquestion(qids[qlength], stuids[0]); 
                var qid_seq = qids[qlength];  
                var feedback_url = $("#feedback_btn").attr("href") 
                $("#feedback_btn").attr("href", feedback_url);  
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

 


    var updateomitted = function(){
        var omitted = $('#omitted_editor').val();
        $.post("/cpm/teacher/updateomitted/",
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
        $.post("/cpm/question/getid/",
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
                       
                      
                       //var feedback_url = $("#feedback_btn").attr("href");
                       //feedback_url = feedback_url + "?question_id=" + qids[0];
                       //$("#feedback_btn").attr("href", feedback_url);
                       
                       
                       if($("#feedback_btn").attr("href") == "#"){
                            var feedback_url = "/cpm/report/popup/" + paperid + "/" +  student_id + "/?question_id="  + qids[0];
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
        $.post("/cpm/paper/info/",
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
		//questioncanvas_bindnm();
		console.log('D1_V1');
		console.log('paperid',paperid);
            //alert(questionid);
		$.ajax({
		  type: "POST",
		  url: "/cpm/question/stureport/",
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
				$("#editmark").text(payload['mark']);
				$("#questionanswer_container").html(payload["clozepassage_content"]);
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
			$("#stdcanvas").attr('href','/cpm/optioncanvas/?canvasname=1&optionid=' + payload['optionid_stdanswer']);
			$("#stucanvas").attr('href','/cpm/optioncanvas/?canvasname=1&optionid=' + payload['optionid_stuanswer']); 




			}
			_getProcessDialog().dialog('close');
		  },
		  error: function(XMLHttpRequest, textStatus, errorThrown) {
		     alert(XMLHttpRequest.responseText);
		  }
		});

		
            
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
