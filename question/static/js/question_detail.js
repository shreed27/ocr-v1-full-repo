(function($, undef) {
    var questionid = intemass.util.getUrl('questionid');
    var itempoolid = intemass.util.getUrl('itempoolid');
    var view = intemass.util.getUrl('view');
    var stdthumbnail_ids = [];
	var mathequation,mathque_tab2;
	window.mathequation= true;
	window.mathque_tab2= 1;
    var config = {
        toolbar: [],
        height: 500,
        toolbarStartupExpanded: false,
        readOnly: true,
        keystrokes: [],
        blockedKeystrokes: [CKEDITOR.CTRL + 67,CKEDITOR.CTRL +66]
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


    var quploadsettings = {
        // Backend Settings
        flash_url : "/static/js/swfupload/swfupload.swf",
        upload_url: "/question/imageupload/",
        custom_settings : {
            progressTarget : "fsUploadProgress",
            upload_target : "divFileProgressContainer",
            cancelButtonId : "btnCancel"
        },

        // File Upload Settings
        file_size_limit : "20 MB",	// 2MB
        file_types : "*.*",
        file_types_description : "Images Files",
        file_upload_limit : "0",

        //events
        file_queued_handler : fileQueued,
        file_queue_error_handler : fileQueueError,
        file_dialog_complete_handler : fileDialogComplete,
        upload_start_handler : uploadStart,
        upload_progress_handler : uploadProgress,
        upload_error_handler : uploadError,
        upload_success_handler : uploadSuccess,
        upload_complete_handler : uploadComplete,
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


    var suploadsettings = {
        // Backend Settings
        flash_url : "/static/js/swfupload/swfupload.swf",
        upload_url: "/question/imageupload/",
        custom_settings : {
            progressTarget : "fsUploadProgress1",
            upload_target : "divFileProgressContainer1",
            cancelButtonId : "btnCancel1"
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
        upload_complete_handler : uploadCompleteForStd,
        queue_complete_handler : queueComplete,

        // Button Settings
        button_image_url : "/static/css/swfimages/XPButtonNoText_61x22x4.png",
        button_placeholder_id : "supload",
        button_width: 61,
        button_height: 22,
        button_text : '<span class="swfbutton">Upload</span>',
        button_text_style : '.swfbutton {font-family: Arial; font-size:14pt ;text-align:center;background-color:#339933;}',
        button_window_mode: SWFUpload.WINDOW_MODE.TRANSPARENT,
        button_cursor: SWFUpload.CURSOR.HAND
        // Debug Settings
        //debug: true
    };


    var setEditableText = function(){
        var selquestionname = $('#question_id').children('option:selected').text() || 'New Question';
        $("span.editable").text(selquestionname);
    };


    var updateQuestionName = function(newname){
        var curquestionid = $('#question_id').val();
        var curitempoolid = $('#itempool_id').val();
        $.ajax({
            type: "POST",
            url: "/question/updatename/",
            dataType: "json",
            data: {
                "questionid": curquestionid,
                "itempoolid": curitempoolid,
                "questionname": newname,
                "csrfmiddlewaretoken": csrfvalue
            },
            success: function(payload) {
                if (payload['questionid']) {
                    questionid = payload['questionid'];
                    $('#question_id').children('option:selected').text(newname);
                    $('#question_id').children('option:selected').val(questionid);
                    $("#question_type").val(payload['questiontype']);
                    $("#min_closeness_band").val(payload['min_closeness_band']);
                    $("#question_description").val(payload['description'] || '');
                }
                bindcanvas(questionid, [], []);
                pullThumbnails();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                return this;
            }
        });
    };



    var questioncanvas_bindnm;
    questioncanvas_bindnm = function(questionid, view){
	var test = document.getElementById("question_canvas")
	//' +  $(this).text() + uid + '
	var canvasurl =  '/canvas/?canvasname=1&questionid=' + questionid + '&view=' + view;
	test.setAttribute("class","nyroModal populate greenBtn");
	test.setAttribute("href", canvasurl)
	test.setAttribute("target", "_blank")
	$("#question_canvas").unbind('click').click(function(event){
	    $('#question_canvas').off();
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
				$("#question_canvas").trigger('click');
			},
		error: function(e){
				alert('Error:');
			}
	    });
	});
	};

    var stdanswercanvas_bindnm;
    stdanswercanvas_bindnm = function (questionid, view) {
        var test = document.getElementById("stdanswer_canvas")
		//' +  $(this).text() + uid + '
		var canvasurl =  '/canvas/?canvasname=1&questionid=' + questionid + '&stdanswerid=' + questionid + '&view=' + view;
		test.setAttribute("class","nyroModal populate greenBtn");
		test.setAttribute("href", canvasurl)
		test.setAttribute("target", "_blank")
		$("#stdanswer_canvas").unbind('click').click(function(event){
			$('#stdanswer_canvas').off();
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
					$("#stdanswer_canvas").trigger('click');
				},
			error: function(e){
					alert('Error:');
				}
			});

		});
    };

	//stdanswercanvas_bindnm = function (questionid, view) {
        //$("#s2id_stdanswer_canvas").find("ul li div").click(function () {
            //var canvasurl = '/canvas/?canvasname=' +  $(this).text().replace(/[Dd]iagram_/g, '') + '&questionid=' + questionid + '&stdanswerid=' + questionid + '&view=' + view;
            //$(this).attr({
                //'class': 'nyroModal',
                //'href': canvasurl,
                //'target': '_blank'
            //});
            //$(this).nm(nmopts);
            //$(this).next().attr({
                //'onclick':function () {
                    //return false;
                //}
            //});
        //});
    //};


    var initcanvasarea = function(){
                questioncanvas_bindnm(questionid, view);
                stdanswercanvas_bindnm(questionid, view);
		 };

    var setcanvasreadOnly = function() {
            $("#question_canvas").click(function () {return false;});
            $("#stdanswer_canvas").click(function () {return false;});
    };


    var pullQuestionDetail;
    pullQuestionDetail = function () {
        questionid = parseInt($('#question_id').val()) || -1;
        $.post("/question/get/",
        {
            'questionid': questionid,
            'csrfmiddlewaretoken': csrfvalue
        },
        function (payload){
            clearquestiondetail();
            //TODO: Write for alternate mark scheme
            if (payload.state === "success") {
                var question_canvas_name = [];
                var stdanswer_canvas_name = [];
                var alt_stdanswer_canvas_name = [];
                var question_canvas = payload['question_canvas'];
                var stdanswer_canvas = payload['stdanswer_canvas'];

                //alternative answer implementation
                var alt_stdanswer_canvas = payload['alt_stdanswer_canvas'];
                for (var qname in question_canvas) question_canvas_name.push(qname);
                for (var stdname in stdanswer_canvas) stdanswer_canvas_name.push(stdname);
                for (var alt_stdname in alt_stdanswer_canvas) alt_stdanswer_canvas_name.push(alt_stdname);

                $('#question_editor').val(payload['question_content']);
                $('#standard_editor').val(payload['standard_content']);
                $('#alt_standard_editor').val(payload['alt_standard_content']);
                $("#question_description").val(payload['question_desc']);
                $("#question_type").val(payload['question_type']);
                $("#min_closeness_band").val(payload['min_closeness_band']);
                $("#itempool_id").val(payload['question_item']);

                bindcanvas(questionid, question_canvas_name, stdanswer_canvas_name);
                pullCanvasRulelistForStd(stdanswer_canvas);

                var templatelist = payload['question_markscheme'] || [];
                var alt_templatelist = payload['alt_question_markscheme'] || [];

                var $markscheme = $("#markschemetbody");
                var $alt_markscheme = $("#alt_markschemetbody");

                var $canvasmarkscheme = $("#canvasruletbody");
                var $alt_canvasmarkscheme = $("#alt_canvasruletbody");
                // console.log($canvasmarkscheme, "$canvasmarkscheme", (new Error).lineNumber);
                if (view){
                    for (var i = 0; i < templatelist.length; i += 1) {
                        $markscheme.append("<tr><td>" + dispMarkScheme(templatelist[i][0]) + "</td><td>" + templatelist[i][1] + "</td><td></td></tr>");
                    }
                    //for alternate mark scheme
                    for (var i = 0; i < alt_templatelist.length; i += 1) {
                        $alt_markscheme.append("<tr><td>" + dispMarkScheme(alt_templatelist[i][0]) + "</td><td>" + alt_templatelist[i][1] + "</td><td></td></tr>");
                    }

                    for (var canvasname in stdanswer_canvas){
                        var canvasmarkscheme = stdanswer_canvas[canvasname]['markscheme'];
                        for(var i = 0; i < canvasmarkscheme.length; i += 1){
                            $canvasmarkscheme.append("<tr><td>" + canvasname + ": " + dispMarkScheme(canvasmarkscheme[i][0]) + "</td><td>" + canvasmarkscheme[i][1] + "</td><td></td></tr>");
                        }
                    }

                    //for alternate mark scheme
                    for (var canvasname in stdanswer_canvas){
                        var alt_canvasmarkscheme = stdanswer_canvas[canvasname]['markscheme'];
                        for(var i = 0; i < alt_canvasmarkscheme.length; i += 1){
                            $alt_canvasmarkscheme.append("<tr><td>" + canvasname + ": " + dispMarkScheme(alt_canvasmarkscheme[i][0]) + "</td><td>" + alt_canvasmarkscheme[i][1] + "</td><td></td></tr>");
                        }
                    }
                } else {
                    //noinspection JSDuplicatedDeclaration
                    for (var i = 0; i < templatelist.length; i += 1) {
                        $markscheme.append("<tr><td>" + dispMarkScheme(templatelist[i][0]) + "</td><td>" + templatelist[i][1] + "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                    }
                    //for alternate mark scheme
                    for (var i = 0; i < alt_templatelist.length; i += 1) {
                        $alt_markscheme.append("<tr><td>" + dispMarkScheme(alt_templatelist[i][0]) + "</td><td>" + alt_templatelist[i][1] + "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                    }
                    for (var canvasname in stdanswer_canvas){
                        var canvasmarkscheme = stdanswer_canvas[canvasname]['markscheme'];
                        for(var i = 0; i < canvasmarkscheme.length; i += 1){
                            $canvasmarkscheme.append("<tr><td>" + canvasname + ": " + dispMarkScheme(canvasmarkscheme[i][0]) + "</td><td>" + canvasmarkscheme[i][1]  + "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                        }
                    }
                    //for alternate mark scheme
                    for (var canvasname in stdanswer_canvas){
                        var alt_canvasmarkscheme = stdanswer_canvas[canvasname]['markscheme'];
                        for(var i = 0; i < alt_canvasmarkscheme.length; i += 1){
                            $alt_canvasmarkscheme.append("<tr><td>" + canvasname + ": " + dispMarkScheme(alt_canvasmarkscheme[i][0]) + "</td><td>" + alt_canvasmarkscheme[i][1]  + "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                        }
                    }
                }

                $("#rulecount").text("Converted Rules(" + (payload['rulecount'] || '0') + " rules total)");
                $("#alt_rulecount").text("Converted Rules(" + (payload['alt_rulecount'] || '0') + " rules total)");

                for (var canvasname in stdanswer_canvas){
                    var canvasrulelist = stdanswer_canvas[canvasname]['pointlist'];
                    for(var i = 0; i < canvasrulelist.length; i += 1){
                        var canvasrule = canvasrulelist[i];
                        $("#rulestbody").append("<tr><td> Graph "+ canvasname + ":" + canvasrule['Point']+"</td><td>"+ canvasrule['Mark']+"</td></tr>");
                        // alternate standard answer does not have any canvas. so can be reused.
                        //$("#alt_rulestbody").append("<tr><td> Graph "+ canvasname + ":" + canvasrule['Point']+"</td><td>"+ canvasrule['Mark']+"</td></tr>");
                    }
                }

                for (var ruleidx in payload['rulelist']) {
                    rule = payload['rulelist'][ruleidx];
                    $("#rulestbody").append("<tr><td>" + rule['Point'] + "</td><td>" + rule['Mark'] + "</td></tr>");
                }
                // for alternate mark scheme
                for (var ruleidx in payload['alt_rulelist']) {
                    alt_rule = payload['alt_rulelist'][ruleidx];
                    $("#alt_rulestbody").append("<tr><td>" + alt_rule['Point'] + "</td><td>" + alt_rule['Mark'] + "</td></tr>");
                }
            }
        }, 'json');
    };


    var clearquestiondetail = function(){
        $('#question_editor').val('');
        $('#standard_editor').val('');
        $("#question_description").val('');
        $("#question_type").val('');
		$("#min_closeness_band").val(0);
        //$("#question_canvas").find("textarea").select2('val', '');
        //$("#stdanswer_canvas").find("textarea").select2('val', '');
        $("#markschemetbody").find("tr").remove();
        $("#canvasruletbody").find("tr").remove();
        $("#templates_table").find("#tbody tr").remove();
        $("#rulecount").text("Converted Rules(0 rule total)");
        $("#rulestbody").find("tr").remove();

        // clearing for standard answer
        $('#alt_standard_editor').val('');
        $("#alt_markschemetbody").find("tr").remove();
        $("#alt_canvasruletbody").find("tr").remove();
        $("#alt_templates_table").find("#tbody tr").remove();
        $("#alt_rulecount").text("Converted Rules(0 rule total)");
        $("#alt_rulestbody").find("tr").remove();
    };


    var bindImageIconClick = function(){
        var deleteImage = function($item) {
            var id = parseInt($item.attr("id"));
            $.post("/question/deleteimage/",
                {
                    'imageid': id,
                    'csrfmiddlewaretoken': csrfvalue
                },
                function(payload) {
                    if(payload.state === "success"){
                        $item.parent().remove();
                    }
                },'json');
        };


    var downloadFiles = function( $link ) {
            window.open("http://www.intemass.com" + $link.attr('href'), '_blank');

            };


        var viewLargerImage = function($link) {
//            console.log("print" + link)
            var src = $link.attr("href");
            var title = $link.siblings("img").attr("alt");
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
					}
        };


        // resolve the icons behavior with event delegation
        $("#thumbnails").find("a").click(function(event){
            var $item = $(this);
			var $target = $(event.target);
            if ($item.is("a.ui-icon-zoomin" )){
                viewLargerImage($item);
            }
            else if ( $target.is( "a.ui-icon-arrowthickstop-1-s" ) ) {
                downloadFiles($item);
            }
			else if ($item.is(".ui-icon-closethick")){
                deleteImage($item);
            }
            return false;
        });

    };


    var bindImageIconClickForStd = function(){

        var deleteImage = function($item){
            var id = parseInt($item.children("a:last").attr("id"));
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

            if ( $target.is( "a.ui-icon-zoomin" ) ) {
                viewLargerImage( $target );
            } else if ( $target.is( "a.ui-icon-closethick" ) ) {
                deleteImage( $item );
            }

            return false;
        });
    };

    var bindcanvas = function(questionid, question_canvas_name, stdanswer_canvas_name){
        questioncanvas_bindnm(questionid, view);
        stdanswercanvas_bindnm(questionid, view);
    };

    var pullThumbnails = function(){
        var questionid = parseInt($('#question_id').val()) || -1;
        if (questionid === -1){
            $("#thumbnails li").remove();
            return;
        }
        $.post("/question/thumbnails/",
            {
                'questionid': questionid,
                'csrfmiddlewaretoken': csrfvalue
            },
            function(payload){
                if(payload.state === "success"){
                    thumbnails = payload['thumbnails'];
                    var thumbhtml = '';
                    for (var t in thumbnails){
                        thumbhtml += '<li class="ui-widget-content ui-corner-tr">';

            var extension = thumbnails[t][2].replace(/^.*\./, '');
            extension = extension.toLowerCase();

            switch (extension) {
                case 'jpg': thumbhtml += '<h6 class="ui-widget-header">' + thumbnails[t][1] + '...' + '</h6>';
                            thumbhtml += '<img src="/static/' + thumbnails[t][0] + '" id=' + thumbnails[t][3] +' alt="' + thumbnails[t][1] + '" width="96" height="72"></img>';
                            thumbhtml += '<a href="/static/' + thumbnails[t][2] + '" title="View Larger Image" class="ui-icon ui-icon-zoomin">View Larger</a>';
                            thumbhtml += '<a href="/static/' + thumbnails[t][2] + '" title="Download" class="ui-icon ui-icon-arrowthickstop-1-s">Download</a>';

                break;
                case 'jpeg': thumbhtml += '<h6 class="ui-widget-header">' + thumbnails[t][1] + '...' + '</h6>';
                             thumbhtml += '<img src="/static/' + thumbnails[t][0] + '" id=' + thumbnails[t][3] +' alt="' + thumbnails[t][1] + '" width="96" height="72"></img>';
                             thumbhtml += '<a href="/static/' + thumbnails[t][2] + '" title="View Larger Image" class="ui-icon ui-icon-zoomin">View Larger</a>';
                             thumbhtml += '<a href="/static/' + thumbnails[t][2] + '" title="Download" class="ui-icon ui-icon-arrowthickstop-1-s">Download</a>';
                break;
                case 'pdf': thumbhtml += '<h6 class="ui-widget-header">' + thumbnails[t][1] + '...' + '</h6>';
                            thumbhtml += '<a href="/static/' + thumbnails[t][2] + '" title="Download" class="ui-icon ui-icon-arrowthickstop-1-s">Download</a>';

                break;
                case 'docx': thumbhtml += '<h6 class="ui-widget-header">' + thumbnails[t][1] + '...' + '</h6>';
                              thumbhtml += '<a href="/static/' + thumbnails[t][2] + '" title="Download" class="ui-icon ui-icon-arrowthickstop-1-s">Download</a>';

                break;

        }


                        if(!view){

                            thumbhtml += '<a href="#" title="Delete Image" id=' + thumbnails[t][3] + ' class = "ui-icon ui-icon-closethick">Delete</a>';
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

    var pullThumbnailsForStd = function(){
        var questionid = parseInt($('#question_id').val()) || -1;
        if (questionid === -1){
            $("#std_thumbnails li").remove();
            return;
        }
        $.post("/question/thumbnails/",
            {
                'questionid': questionid,
                'iscorrect': 'yes',
                'csrfmiddlewaretoken': csrfvalue
            },
            function(payload) {
                if(payload.state === "success"){
                    thumbnails = payload['thumbnails'];
                    stdthumbnail_ids = payload['stdthumbnail_ids'];
                    var thumbhtml = '';
                    for (t in thumbnails){
                        thumbhtml += '<li class="ui-widget-content ui-corner-tr">';
                        thumbhtml += '<h6 class="ui-widget-header">'+thumbnails[t][1].slice(0,4)+'</h6>';
                        thumbhtml += '<img src="/static/'+thumbnails[t][0]+'"  alt="'+thumbnails[t][1]+'" width="96" height="72"></img>';
                        thumbhtml += '<a href="/static/'+thumbnails[t][2]+'" title="View Larger Image" class="ui-icon ui-icon-zoomin">View Larger</a>';
                        if(!view){
                            thumbhtml+='<a href="#" title="Delete Image" id='+ thumbnails[t][3]+ ' class="ui-icon ui-icon-closethick">Delete</a>';
                        }
                    }
                    var $list = $( "ul", $("#std_thumbnails"));
                    $( "#std_thumbnails li").remove();
                    $(thumbhtml).appendTo($list);
                    bindImageIconClickForStd();
                }else{
                    $("#std_thumbnails li").remove();
                }
            },'json');
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
            initcanvasarea();
            setcanvasreadOnly();
            $("#question_editor").ckeditor(config);
            $("#standard_editor").ckeditor(config);
            $(".editable").unbind('click.editable');
            $("#submit1").hide();
            $("#submit2").hide();
            $("#submit3").hide();
            $("#submit4").hide();
            $("#submit5").hide();
            $("#choose_some_images_1").hide();
            $("#choose_some_images_2").hide();
            $("#question_description").attr("disabled", true);
            $("#question_type").attr("disabled", true);
	    $("#min_closeness_band").attr("disabled", true);
	     $("#videoupload").attr("disabled", true);
	      $("#uploadvid").attr("disabled", true);
            $("#itempool_id").attr("disabled", true);
            $("#btnCancel").hide();
            $("#btnCancel1").hide();
            $("#rule_templates").hide();
	    //$(".question_canvas").trigger('click');
	    //$(".stdanswer_canvas").trigger('click');
        }else{
            var swfu = new SWFUpload(quploadsettings);
            var swfu1 = new SWFUpload(suploadsettings);
            var curquestionid = $('#question_id').val();

            initcanvasarea();
	    //$(".question_canvas").trigger('click');
	    //$(".stdanswer_canvas").trigger('click');
            $("#question_editor").ckeditor({readOnly: false});
            $("#standard_editor").ckeditor({readOnly: false});
            $("#alt_standard_editor").ckeditor({readOnly: false});

            $("#SWFUpload_0").live("mousedown", function(){
				curquestionid = $('#question_id').val();
                var postobj = {"questionid": curquestionid};
                swfu.setPostParams(postobj);
            });
            $("#SWFUpload_1").live("mousedown", function(){
				curquestionid = $('#question_id').val();
                var postobj = {"questionid": curquestionid, 'standard_image': 'yes'};
                swfu1.setPostParams(postobj);
            });

            if(!curquestionid || curquestionid === '-1'){
                $("#question_canvas").click(function () {return false;});
				$("#stdanswer_canvas").click(function () {return false;});
            }

            $("#sample_template_t1").mask("ALL LESS 9.9 OR 9.9");
            $("#sample_template_t2").mask("All LESS 9.9 AND 9.9");
            $("#sample_template_t3").mask("ALL LESS 2 COMBINATION OF 9.9 AND 9.9 AND 9.9 AND 9.9");
            $("#sample_template_t4").mask("ANY 2 COMBINATIONS OF 9.9;9.9;9.9;9.9");

            $("#alt_sample_template_t1").mask("ALL LESS 9.9 OR 9.9");
            $("#alt_sample_template_t2").mask("All LESS 9.9 AND 9.9");
            $("#alt_sample_template_t3").mask("ALL LESS 2 COMBINATION OF 9.9 AND 9.9 AND 9.9 AND 9.9");
            $("#alt_sample_template_t4").mask("ANY 2 COMBINATIONS OF 9.9;9.9;9.9;9.9");
            $("#rule_templates input").keypress(function(event){
                enterkeyaction(event);
            });
            $("#alt_rule_templates input").keypress(function(event){
                alt_enterkeyaction(event);
            });
        }

        pullQuestionDetail();
        pullThumbnails();
        pullThumbnailsForStd();
        setEditableText();
		$("#q_tab1").add("#q_tab2").add("#q_tab3").add("#q_tab4").add("#q_tab5").on("click",function(){
			window.mathequation= true;
			return false;
		});
		$("#question_content").on("change", function(){
			pullQuestionDetail();
        pullThumbnails();
        pullThumbnailsForStd();
        setEditableText();
		questioncanvas_bindnm(questionid, view);
		stdanswercanvas_bindnm(questionid, view);
		});

        $("#submit1").click(function(){
	    console.log("question_detail submit1")
		window.mathequation= true;
		processing_dialogue.dialog('open');
		var question_name = $("#question_name").text();
		var question_content = $('#question_editor').val();
		var question_desc = $("#question_description").val();
		var question_type = $("#question_type").val();
	    var min_closeness_band = $("#min_closeness_band").val();
            var canvasname = [1];
            questionid = $('#question_id').val();
            itempoolid = $('#itempool_id').val();
            $.post("/question/submit/",
                {
                    'questionid': questionid,
                    'canvasname': $.toJSON(canvasname),
                    'itempoolid': itempoolid,
                    'question_name': question_name,
                    'question_desc': question_desc,
                    'question_content': question_content,
                    'question_type': question_type,
		    'min_closeness_band': min_closeness_band,
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

        $("#submit2").click(function(){
	        console.log("question_detail submit2");
            processing_dialogue.dialog('open');
            var questionid = parseInt($("#question_id").val());
            var standard_content = $('#standard_editor').val();
            var canvasname = [];
			canvasname.push(1);
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
            pullThumbnails();
            pullThumbnailsForStd();
            setEditableText();
			questionid = $(this).val()
			questioncanvas_bindnm(questionid);
			stdanswercanvas_bindnm(questionid);
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

    /* Alternative standard answer & marking scheme scripts begins here */
        /*TODO:
        1. submit the answer and save to alternative fields
        2. change the tab automatically to the alternative mark scheme
        3.
        */

        /* Alternative standard answer */
        $("#submit4").click(function(){
            console.log("question_detail submit4");
            processing_dialogue.dialog('open');
            var questionid = parseInt($("#question_id").val());
            var standard_content = $('#alt_standard_editor').val();
            var canvasname = [];
            canvasname.push(1);
            $.post("/question/alt_submitstandard/",
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
                        // leave the canvas for now.
                        //var stdanswer_canvas = payload['stdanswer_canvas'];
                        //pullCanvasRulelistForStd(stdanswer_canvas);
                        var dialogue = $("#dialog-success-alt-stdanswer").dialog({
                            resizable: false,
                            height:150,
                            modal: true,
                            buttons: {
                                OK: function() {
                                    $(this).dialog( "close" );
                                }
                            }});
                        $tabs3.tabs('select', 4);
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
        /* Alternative standard answer ends here.*/

        /* Alternative mark scheme */
        $("#submit5").click(function(){
        console.log("question_detail submit3")
            processing_dialogue.dialog('open');
            var markschemeArr = [];
            var $alt_markscheme_tr = $("#alt_markschemetbody").find("tr");
            console.log($alt_markscheme_tr, "$alt_markscheme_tr", (new Error).lineNumber);
            var markscheme_tr_size = $alt_markscheme_tr.size();
            console.log(markscheme_tr_size, "markscheme_tr_size", (new Error).lineNumber);
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
                var $alt_selected_td = $alt_markscheme_tr.eq(i).find("td");
                var arrayitem = [];
                text0 = $alt_selected_td.eq(0).text();
                text1 = $alt_selected_td.eq(1).text();
                text00 = parseMarkScheme(text0);
                arrayitem.push(text00);
                arrayitem.push(text1);
                markschemeArr.push(arrayitem);
            }

            var canvasruleArr = [];
            var $canvasrule_tr = $("#alt_canvasruletbody").find("tr");
            var canvasrule_tr_size = $canvasrule_tr.size();
            for(var i = 0; i < canvasrule_tr_size; i += 1){
                var $alt_selected_td = $canvasrule_tr.eq(i).find("td");
                var arrayitem = [];
                text0 = $alt_selected_td.eq(0).text();
                text1 = $alt_selected_td.eq(1).text();
                text00 = parseMarkScheme(text0);
                arrayitem.push(text00.replace(/[Dd]iagram_/g, ''));
                arrayitem.push(text1);
                canvasruleArr.push(arrayitem);
            }

            if (markscheme_tr_size > 0 || canvasrule_tr_size > 0){
                var questionid = parseInt($('#question_id').val());
                $.post("/question/alt_submitmark/",
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
                            $('#alt_rulecount').text("Converted Rules(" + payload['rulecount'] || '0' + " rules total)");
                            $("#alt_rulestbody").find("tr").remove();
                            for (var ruleidx in payload['canvasrulelist']){
                                var canvasrule = payload['canvasrulelist'][ruleidx];
                                $("#alt_rulestbody").append("<tr><td> diagram_"+ canvasrule['Name'] + ":" + canvasrule['Point']+"</td><td>"+ canvasrule['Mark']+"</td></tr>");
                            }
                            for (var ruleidx in payload['rulelist']){
                                var rule = payload['rulelist'][ruleidx];
                                $("#alt_rulestbody").append("<tr><td>"+rule['Point']+"</td><td>"+rule['Mark']+"</td></tr>");
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
        /* Alternative mark scheme ends here.*/
    /* Alternative standard answer & marking scheme scripts ends here */

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

    //alternative mark scheme template
    var alt_enterkeyaction = function(evt){
        var evt = (evt) ? evt : ((window.event) ? window.event : "");
        var key = evt.keyCode ? evt.keyCode : evt.which;
        //enter key press
        if(key == 13){
            var lastchar = evt.target.id[16];
            var numchar = evt.target.id[17];
            var $alt_sampletemplatemark = $("#alt_sample_template_mark_" + numchar);
            var $alt_markscheme = $("#alt_markschemetbody");
            var $alt_canvasscheme = $("#alt_canvasruletbody");
            if(lastchar === "t"){
                $alt_sampletemplatemark.focus();
            }else if(lastchar === "m") {
                numchar = evt.target.id[21];
                if($alt_sampletemplatemark != "" && $alt_sampletemplatemark.val() !== "")
                    $alt_markscheme.append("<tr><td>"+$("#alt_sample_template_t"+numchar).val()+"</td><td>"+
                                       alt_sampletemplatemark.val()+
                                       "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
            }else{
                var $alt_custtemplate = $("#alt_cust_template");
                var $alt_custtemplatemark = $("#alt_cust_template_mark");
                var scheme = $alt_custtemplate.val();
                var schemetype = scheme.split(':');
                if(schemetype[1]){
                    $alt_canvasscheme.append("<tr><td>" + $alt_custtemplate.val() + "</td><td>" +
                                        $alt_custtemplatemark.val() +
                                        "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                }else{
                    $alt_markscheme.append("<tr><td>" + $alt_custtemplate.val() + "</td><td>" +
                                    $alt_custtemplatemark.val() +
                                    "</td><td class='action'><input type=button value='delete' class='delete' onclick='javascript:deletetr(this)'/></td></tr>");
                }
            }
        }
    };

})(jQuery);

function deletetr($obj){
    $($obj).parents("tr").remove();
}
