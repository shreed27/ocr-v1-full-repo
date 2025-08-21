
    var questionid = intemass.util.getUrl('questionid');
    var itempoolid = intemass.util.getUrl('itempoolid');
    var view = intemass.util.getUrl('view');
    var stdthumbnail_ids = [];

    var URL_UPDATENAME="/cpm/question/updatename/";
    var URL_QUESTION_GET = "/cpm/question/get/";

    var config = {
        toolbar: [],
        height: 50,
        toolbarStartupExpanded: false,
        readOnly: true,
        keystrokes: [],
        blockedKeystrokes: [CKEDITOR.CTRL + 67,CKEDITOR.CTRL +66]
    };



;(function($, undef) {  
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

	var optionlist_table = null;
	var url_mcq_getall_optionlist="/cpm/clozeanswer/getbyquestion/";

	var js_get_alloptionlist = function(){

		var url_mcq_getall_optionlist="/cpm/clozeanswer/getbyquestion/";
		valueForURL=url_mcq_getall_optionlist + "?questionid=" + $('#question_id').val();
			console.log('valueForURL: ', valueForURL);
			optionlist_table = $('#optionlist').dataTable( {
				"bJQueryUI": true,
				"bProcessing": true,
				"sAjaxSource": valueForURL,
				"bDestroy": true,
			}); 
	};

	
     

    
    var setEditableText = function(){
        var selquestionname = $('#question_id').children('option:selected').text() || 'New Question';
        $("span.editable").text(selquestionname);
    };

	$("#questioncategory_id").change(function(){
		updateQuestionName();
	});
    var updateQuestionName = function(newname){
        var curquestionid = $('#question_id').val();
        var curitempoolid = $('#itempool_id').val();
        var curcategoryid = $('#category_id').val();
        var curquestiontype = $('#question_type').val();
        var curquestionmark = $('#question_mark').val();
        var curquestioncategory = $('#questioncategory_id').val();
	console.log('mark is ...', curquestionmark);
        $.ajax({
            type: "POST",
            url: URL_UPDATENAME,
            dataType: "json",
            data: {
                "questionid": curquestionid,
                "itempoolid": curitempoolid,
                "questionname": newname,
                "questiontype": curquestiontype,
                "questionmark": curquestionmark,
		"curcategoryid":curcategoryid,
		"curquestioncategory":curquestioncategory,
                "csrfmiddlewaretoken": csrfvalue
            },
            success: function(payload) {
                if (payload['questionid']) {
                    questionid = payload['questionid'];
                    $('#question_id').children('option:selected').text(newname);
                    $('#question_id').children('option:selected').val(questionid);
                    $("#question_type").val(payload['questiontype']);
                    $("#question_description").val(payload['description'] || '');
                } 
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
		console.log(XMLHttpRequest.responseText);
                return this;
            }
        });
    };


	 


    

    
    var pullQuestionDetail;
    pullQuestionDetail = function () {
        questionid = parseInt($('#question_id').val()) || -1;
	console.log('/cpm/question/get/');
        $.post("/cpm/question/get/",
        {
            'questionid': questionid,
            'csrfmiddlewaretoken': csrfvalue
        },
        function (payload){
            clearquestiondetail();
            if (payload.state === "success") {
                var question_canvas_name = [];
                var stdanswer_canvas_name = [];
                $('#question_editor').val(payload['question_content']);
                $('#standard_editor').val(payload['standard_content']);
                $("#question_description").val(payload['question_desc']);
                $("#question_type").val(payload['question_type']);
                $("#itempool_id").val(payload['question_item']);
                $("#question_mark").val(payload['question_mark']);
		console.log('testing ' , payload['question_questioncategory']);
                $("#questioncategory_id").val(payload['question_questioncategory']);
                
		js_get_alloptionlist();
                 

                
            }
        }, 'json');
    };

 	$("a[href = '#tabs3-2']").click(function(){
           
            initTab2();
        });
    var clearquestiondetail = function(){
        $('#question_editor').val('');
        $('#standard_editor').val('');
        $("#question_description").val('');
        $("#question_type").val('');
	$("#min_closeness_band").val(0);
        $("#question_canvas").find("textarea").select2('val', '');
        $("#stdanswer_canvas").find("textarea").select2('val', '');
        $("#markschemetbody").find("tr").remove();
        $("#canvasruletbody").find("tr").remove();
        $("#templates_table").find("#tbody tr").remove();
        $("#rulecount").text("Converted Rules(0 rule total)");
        $("#rulestbody").find("tr").remove();
    };


    var bindImageIconClick = function(){
        var deleteImage = function($item) {
            var id = parseInt($item.children("a:last").attr("id"));
	    console.log('delete image:' , id , 'csrfvalue:' ,csrfvalue);
		/*$.post("/cpm/question/deleteimage/",
		{
		    'imageid': id,
		    'csrfmiddlewaretoken': csrfvalue
		},
		function(payload) {
		    if(payload.state === "success"){
			$item.remove();
		    }
		},'json');*/
		$.ajax({
			url: "/cpm/question/deleteimage/" ,
			type: "POST",
			dataType: "json",
			data: {
				'imageid': id,
                    		'csrfmiddlewaretoken': csrfvalue
			},
			success: function (resp) {
				console.log('resp.state:', resp.state);
				if(resp.state === "success"){
					$item.remove();
				}
			},
			error: function(e){
				console.log('error:',e);
			}  
		}); 
        };

        var viewLargerImage = function($link) {
            var src = $link.attr("href");
            var title = $link.siblings("img").attr("alt");
            var $modal = $("img[src$='" + src + "']");
            if ($modal.length) {
                $modal.dialog("open");
            }else {
                var img = $("<img alt='" + title + "' width='768' height='576' style='display: none; padding: 8px;' />")
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

            if ($target.is("a.ui-icon-zoomin")){
                viewLargerImage($target);
            }else if ($target.is("a.ui-icon-closethick")){
		console.log('going to call deleteImage: ' , $item);
                deleteImage($item);
            }
            return false;
        });
    };

    var bindImageIconClickForStd = function(){
        /*var deleteImage = function($item){
            var id = parseInt($item.children("a:last").attr("id"));
		console.log('heer again?');
            $.post("/question/deleteimage/",
                {
                    'imageid': id,
                    'csrfmiddlewaretoken': csrfvalue
                },
                function(payload) {
                    if(payload.state === "success"){
                        $item.remove();
                    }
                },'json');
            for (var i = 0; i < stdthumbnail_ids.length; i += 1){
                if (id === stdthumbnail_ids[i]){
                    stdthumbnail_ids.splice(i, 1);
                }
            }
        };
	*/
        var viewLargerImage = function($link){
            var src = $link.attr("href");
            var title = $link.siblings("img").attr("alt");
            var $modal = $("img[src$='" + src + "']");

            if ($modal.length) {
                $modal.dialog("open");
            }else {
                var img = $("<img alt='" + title + "' width='768' height='576' style='display: none; padding: 8px;'/>")
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
        $("#std_thumbnails li").click(function(event){
            var $item = $(this);
            var $target = $(event.target);

            if ($target.is("a.ui-icon-zoomin")){
                viewLargerImage($target);
            }else if ($target.is("a.ui-icon-closethick")){
                deleteImage($item);
            }
            return false;
        });
    };

    var bindcanvas = function(questionid, question_canvas_name, stdanswer_canvas_name){
        $("#question_canvas").select2("val", question_canvas_name);
        $("#stdanswer_canvas").select2("val", stdanswer_canvas_name);
        questioncanvas_bindnm(questionid, view);
        //stdanswercanvas_bindnm(questionid, view);
    };

    
    var pullCanvasRulelistForStd = function(stdanswer_canvas){
        var $canvasrules = $('#canvasrules');
        $canvasrules.html("");
        for (var canvasname in stdanswer_canvas){
            var rules = stdanswer_canvas[canvasname]['rulelist'];
            var canvasrulehtml = '<div><h5>diagram_' + canvasname + "</h5><table class='templates'><thead>";
            for (var i = 0; i < rules.length; i += 1){
                canvasrulehtml += '<tr>';
                for (var j = 0; j < 4; j += 1){
                    canvasrulehtml += '<td>' + rules[i][j] + '</td>';
                }
                canvasrulehtml += '</tr>';
            }
            canvasrulehtml += '</thead></table></div>';
            $canvasrules.append(canvasrulehtml);
        }
    };

    $(function(){
        var processing_dialogue = $("#dialog-process").dialog({
            autoOpen: false,
            resizable: false,
            height: 150,
            width: 550,
            modal: true
        });
        $("#progressbar").progressbar({
            value: 100
        });

        itempoolid = itempoolid || -1;
        questionid = questionid || -1;

        $tabs3 = $("#question_detail_tabs").tabs({});
        $('#question_id').val(questionid);
        $('#itempool_id').val(itempoolid);
        //retreive question infomation

        $("span.editable").editable(function(value, settings){
            updateQuestionName(value);
            return value;
        }, {
            type: "text",
            onblur: "submit",
            tooltip: "Click to Edit Name...",
            style: 'display:inline'
        });

        if (view){
            console.log('log view ');
            setcanvasreadOnly();
            $("#question_editor").ckeditor(config);
            $("#standard_editor").ckeditor(config);
            $(".editable").unbind('click.editable');
            $("#submit1").hide();
            $("#submit2").hide();
            $("#submit3").hide();
            $("#choose_some_images_1").hide();
            $("#choose_some_images_2").hide();
            $("#question_description").attr("disabled", true);
            $("#question_type").attr("disabled", true);
	    $("#min_closeness_band").attr("disabled", true);
            $("#itempool_id").attr("disabled", true);
            $("#btnCancel").hide();
            $("#btnCancel1").hide();
            $("#rule_templates").hide();
        }else{
		            console.log('log non view ');
             
            var curquestionid = $('#question_id').val();

             
            $("#question_editor").ckeditor({readOnly: false});
            $("#standard_editor").ckeditor({readOnly: false});

             

            if(!curquestionid || curquestionid === '-1'){
                $('#question_canvas').hide();
                $('#stdanswer_canvas').hide();
            }

            $("#sample_template_t1").mask("ALL LESS 9.9 OR 9.9");
            $("#sample_template_t2").mask("All LESS 9.9 AND 9.9");
            $("#sample_template_t3").mask("ALL LESS 2 COMBINATION OF 9.9 AND 9.9 AND 9.9 AND 9.9");
            $("#sample_template_t4").mask("ANY 2 COMBINATIONS OF 9.9;9.9;9.9;9.9");
            $("#rule_templates input").keypress(function(event){
                enterkeyaction(event);
            });
        }

        pullQuestionDetail();
        //pullThumbnails();
        //pullThumbnailsForStd();
        setEditableText();

        $("#submit1").click(function(){
	    console.log("question_detail submit1")
            processing_dialogue.dialog('open');
            var question_name = $("#question_name").text();
            var question_content = $('#question_editor').val();
            var question_desc = $("#question_description").val();
            var question_type = $("#question_type").val();
	    var question_mark = $("#question_mark").val();
	    var curquestioncategory = $('#questioncategory_id').val();

	    console.log('submit ..check curquestioncategory:' , curquestioncategory);
            questionid = $('#question_id').val();
            itempoolid = $('#itempool_id').val();
            $.post("/cpm/question/submit/",
                {
                    'questionid': questionid,
                    'itempoolid': itempoolid,
                    'question_name': question_name,
                    'question_desc': question_desc,
                    'question_content': question_content,
                    'question_type': question_type,
		    'curquestioncategory':curquestioncategory ,
                    'question_mark': question_mark,
                    'csrfmiddlewaretoken': csrfvalue
                },
                function(payload){
                    if(payload.state === "success"){
                        processing_dialogue.dialog('close');
                        var dialogue = $("#dialog-success").dialog({
                            resizable: false,
                            height:150,
                            modal: true,
                            buttons: {
                                OK: function() {
                                    $(this).dialog("close");
                                }
                            }});
                        $tabs3.tabs('select', 1);
			js_get_alloptionlist();
                    }else if(payload.state === "failure"){
                        processing_dialogue.dialog('close');
                        var dialogue = $("#dialog-failure").dialog({
                            resizable: false,
                            height:150,
                            modal: true,
                            buttons: {
                                OK: function() {
                                    $( this ).dialog( "close" );
                                }
                            }});
                    }
                },'json');
        });
	$("#tab-optionlist").click(function(){
		js_get_alloptionlist();
	});

        $("#submit2").click(function(){
	    console.log("question_detail submit2")
            processing_dialogue.dialog('open');
            var questionid = parseInt($("#question_id").val());
            var standard_content = $('#standard_editor').val();
            var canvasname = [];
            var canvasdata = $('#stdanswer_canvas').select2("data");
            for (var i = 0; i < canvasdata.length; i += 1){
                canvasname.push(canvasdata[i]['id']);
            }
            $.post("/question/submitstandard/",
                {
                    'questionid': questionid,
                    'canvasname': $.toJSON(canvasname),
                    'stdthumbnail_ids': stdthumbnail_ids.join(),
                    'standard_content': standard_content,
                    'csrfmiddlewaretoken': csrfvalue
                },
                function(payload) {
                    if(payload.state === "success"){
                        processing_dialogue.dialog('close');
                        var stdanswer_canvas = payload['stdanswer_canvas'];
                        pullCanvasRulelistForStd(stdanswer_canvas);
                        var dialogue = $("#dialog-success-stdanswer").dialog({
                            resizable: false,
                            height:150,
                            modal: true,
                            buttons: {
                                OK: function() {
                                    $(this).dialog( "close" );
                                }
                            }});
                        $tabs3.tabs('select', 2);
                    }else if(payload.state === "failure"){
                        processing_dialogue.dialog('close');
                        var dialogue = $( "#dialog-failure" ).dialog({
                            resizable: false,
                            height:150,
                            modal: true,
                            buttons: {
                                OK: function() {
                                    $(this).dialog("close");
                                }
                            }});
                    }
                },'json');
        });
		
        $('#question_id').change(function(){
            pullQuestionDetail();
		
            //pullThumbnails();
            //pullThumbnailsForStd();
            setEditableText();
        });

        $("#submit3").click(function(){
	    console.log("question_detail submit3")
            processing_dialogue.dialog('open');
            var markschemeArr = [];
            var $markscheme_tr = $("#markschemetbody").find("tr");
            var markscheme_tr_size = $markscheme_tr.size();
            if(markscheme_tr_size < 1){
                processing_dialogue.dialog('close');
                $("#dialog-failure").dialog({
                    resizable: false,
                    height: 150,
                    modal: true,
                    buttons: {
                        OK: function() {
                            $(this).dialog("close");
                        }
                    }
                });
                return;
            }

            for(var i = 0; i < markscheme_tr_size; i += 1){
                var $selected_td = $markscheme_tr.eq(i).find("td");
                var arrayitem = [];
                text0 = $selected_td.eq(0).text();
                text1 = $selected_td.eq(1).text();
                text00 = parseMarkScheme(text0);
                arrayitem.push(text00);
                arrayitem.push(text1);
                markschemeArr.push(arrayitem);
            }

            var canvasruleArr = [];
            var $canvasrule_tr = $("#canvasruletbody").find("tr");
            var canvasrule_tr_size = $canvasrule_tr.size();
            for(var i = 0; i < canvasrule_tr_size; i += 1){
                var $selected_td = $canvasrule_tr.eq(i).find("td");
                var arrayitem = [];
                text0 = $selected_td.eq(0).text();
                text1 = $selected_td.eq(1).text();
                text00 = parseMarkScheme(text0);
                arrayitem.push(text00.replace(/[Dd]iagram_/g, ''));
                arrayitem.push(text1);
                canvasruleArr.push(arrayitem);
            }

            if (markscheme_tr_size > 0 || canvasrule_tr_size > 0){
                var questionid = parseInt($('#question_id').val());
                $.post("/question/submitmark/",
                    {
                        'questionid': questionid,
                        'schemes': markschemeArr.toString(),
                        'canvasschemes': canvasruleArr.toString(),
                        'csrfmiddlewaretoken': csrfvalue
                    },
                    function(payload) {
                        if(payload.state === "success"){
                            processing_dialogue.dialog('close');
                            $("#dialog-success").dialog({
                                resizable: false,
                                height: 150,
                                modal: true,
                                buttons: {
                                    OK: function (){
                                        $(this).dialog("close");
                                    }
                                }});
                            $('#rulecount').text("Converted Rules(" + payload['rulecount'] || '0' + " rules total)");
                            $("#rulestbody").find("tr").remove();
                            for (var ruleidx in payload['canvasrulelist']){
                                var canvasrule = payload['canvasrulelist'][ruleidx];
                                $("#rulestbody").append("<tr><td> diagram_"+ canvasrule['Name'] + ":" + canvasrule['Point']+"</td><td>"+ canvasrule['Mark']+"</td></tr>");
                            }
                            for (var ruleidx in payload['rulelist']){
                                var rule = payload['rulelist'][ruleidx];
                                $("#rulestbody").append("<tr><td>"+rule['Point']+"</td><td>"+rule['Mark']+"</td></tr>");
                            }
                        }else if(payload.state === "failure"){
                            processing_dialogue.dialog('close');
                            $("#dialog-failure").dialog({
                                resizable: false,
                                height: 150,
                                modal: true,
                                buttons: {
                                    OK: function() {
                                        $(this).dialog("close");
                                    }
                                }
                            });
                        }
                },'json');
            }
        });

    });

    var parseMarkScheme = function(text0){
        var rst0 = text0.toLowerCase();
        var reg1 = /(\d+)\.(\d+)/g;
        var rst1 = rst0.replace(reg1, 'P$1.$2');
        var reg2 = /\.0\b/g;
        return rst1.replace(reg2, '');
    };

    var dispMarkScheme = function(text0){
        var rst0 = text0.toLowerCase();
        var reg1 = /p(\d+)\.(\d+)/g;
        var rst1 = rst0.replace(reg1,'$1.$2');
        var reg2 = /p(\d+)\b/g;
        return rst1.replace(reg2,'$1.0');
    };

    var enterkeyaction = function(evt){
        var evt = (evt) ? evt : ((window.event) ? window.event : "");
        var key = evt.keyCode ? evt.keyCode : evt.which;

        //enter key press
        if(key == 13){
            var lastchar = evt.target.id[16];
            var numchar = evt.target.id[17];
            var $sampletemplatemark = $("#sample_template_mark_" + numchar);
            var $markscheme = $("#markschemetbody");
            var $canvasscheme = $("#canvasruletbody");
            if(lastchar === "t"){
                $sampletemplatemark.focus();
            }else if(lastchar === "m") {
                numchar = evt.target.id[21];
                if($sampletemplatemark != "" && $sampletemplatemark.val() !== "")
                    $markscheme.append("<tr><td>"+$("#sample_template_t"+numchar).val()+"</td><td>"+
                                       sampletemplatemark.val()+
                                       "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
            }else{
                var $custtemplate = $("#cust_template");
                var $custtemplatemark = $("#cust_template_mark");
                var scheme = $custtemplate.val();
                var schemetype = scheme.split(':');
                if(schemetype[1]){
                    $canvasscheme.append("<tr><td>" + $custtemplate.val() + "</td><td>" +
                                        $custtemplatemark.val() +
                                        "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                }else{
                    $markscheme.append("<tr><td>" + $custtemplate.val() + "</td><td>" +
                                    $custtemplatemark.val() +
                                    "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                }
            }
        }
    };




})(jQuery);
function onAddClozeList(varURL)
{
	varURL=varURL+"?questionid=" + $('#question_id').val();
	window.location.href=varURL;
}
function deletetr($obj){
    $($obj).parents("tr").remove();
}
var URL_OPTIONLIST_DELETE="/cpm/clozelist/del/";
function deletecloze(optionid){
    var dialogue = $( "#dialog-confirm" ).dialog({
        resizable: false,
        height:150,
        modal: true,
        buttons: {
            "Delete": function() {
		console.log( {optionlistid:optionid});
                
		$.ajax({
		    type: "POST",
		    url: URL_OPTIONLIST_DELETE,
		    dataType: "json",
		    data:  {optionlistid:optionid, 'csrfmiddlewaretoken': csrfvalue},
		    success: function(payload) {
			
		    },
		    error: function(XMLHttpRequest, textStatus, errorThrown) {
			//alert(XMLHttpRequest.responseText);
		        return this;
		    }
		});
		var url_mcq_getall_optionlist="/cpm/clozeanswer/getbyquestion/";
		var valueForURL=url_mcq_getall_optionlist + "?questionid=" + $('#question_id').val();
		
		console.log('valueForURL: ', valueForURL);
		optionlist_table = $('#optionlist').dataTable( {
		"bJQueryUI": true,
		"bProcessing": true,
		"sAjaxSource": valueForURL,
		"bDestroy": true,
		});
                $( this ).dialog( "close" );

            },
        Cancel: function() {
                    $( this ).dialog( "close" );
                }
        }
    });
}

