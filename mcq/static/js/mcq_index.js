/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */
var oTable0 = null;
var oTable1 = null;
var oTable2 = null;
var oTable3 = null;
var oTable4 = null;
var url_mcq_getall_itempool="/mcq/getall_itempool/";
var url_mcq_getall_paper="/mcq/getall_paper/";

var url_mcq_getall_assignment="/mcq/getall_assignment/";
;(function($, undef) {

    $(function(){

        var initTab1 = function(){
            oTable0 = $('#students').dataTable( {
                  "bJQueryUI": true,
                  "bProcessing": true,
                  "sAjaxSource": "/student/getall/",
                  "width":"100px"
            } );

            oTable1 = $('#classrooms').dataTable( {
                  "bJQueryUI": true,
                  "bProcessing": true,
                  "sAjaxSource": "/classroom/getall/",
            });
        };

        var initTab2 = function(){
            oTable2 = $('#itempools').dataTable( {
                "bJQueryUI": true,
                "bProcessing": true,
                "sAjaxSource": url_mcq_getall_itempool,
            });

            oTable3 = $('#papers').dataTable( {
                "bJQueryUI": true,
                "bProcessing": true,
                "sAjaxSource": url_mcq_getall_paper,
            } );

            oTable4 = $('#assignments').dataTable( {
                "bJQueryUI": true,
                "bProcessing": true,
                "sAjaxSource": url_mcq_getall_assignment,
                
            });
        }

        var initTab3 = function(){
            var years = [];
            var subjects = [];
            var levels = [];
            $.get('/entity/get/', function(payload){
                if(payload['state'] === 'success'){
                    years = quotation_filter(payload['year']);
                    subjects = quotation_filter(payload['subject']);
                    levels = quotation_filter(payload['level']);
                }else{
                    console.error("payloadError happened");
                }
                $('#id_year').val(years).select2({
                    width: "copy",
                    tags: years,
                    tokenSeparators: [",", " "]
                });
                $('#id_subject').val(subjects).select2({
                    width: "copy",
                    tags: subjects,
                    tokenSeparators: [",", " "]
                });
                $('#id_level').val(levels).select2({
                    width: "copy",
                    tags: levels,
                    tokenSeparators: [",", " "]
                });
            });
        };

        var quotation_filter = function(obj){
            for(var i in obj){
                obj[i] = obj[i].replace(/\"/g, "");
            }
            return obj;
        };

        var thisPage = {
            initialize: function(){
                var tab = intemass.util.getUrl("tab");
                $tabs = $("#tabs3").tabs({});
                if(tab === '2'){
                    $tabs.tabs('select', 1);
                    initTab2();
                }else if (tab === '1'){
                    $tabs.tabs('select', 0);
                    initTab1();
                }else if (tab === '3'){
                    $tabs.tabs('select', 2);
                }else{
                    initTab1();
                }
                return false;
            }
        };

        $(thisPage.initialize());
        initTab3();

        $("a[href = '#tabs3-1']").click(function(){
            if (!oTable0 || !oTable1){
                initTab1();
            }else{
                oTable0.fnDraw();
                oTable1.fnDraw();
            }

        });

        $("a[href = '#tabs3-2']").click(function(){
            if( !oTable2|| !oTable3|| !oTable4)
        {
            initTab2();
        }else{
            oTable2.fnDraw();
            oTable3.fnDraw();
            oTable4.fnDraw();
        }

        });

        $('#optionform').ajaxForm(function(){
            alert('refresh options ok');
        });

    });
})(jQuery);

var deletestudent = function(studentid){
    var dialogue = $( "#dialog-confirm" ).dialog({
        resizable: false,
        height:150,
        modal: true,
        buttons: {
            "Delete": function(){
                $.post(STUDENTDELETE_URL, {studentid: studentid}, function(){}, 'json');
                oTable0.fnDestroy();
                oTable0 = $('#students').dataTable({
                    "bJQueryUI": true,
                        "bProcessing": false,
                        "sAjaxSource": "/student/getall/"
                });
                $( this ).dialog( "close" );
            },
        Cancel: function(){
                    $( this ).dialog( "close" );
                }
        }});
};

var	deleteclassroom = function(classroomid){
    var dialogue2 = $( "#dialog-confirm2" ).dialog({
        resizable: false,
        height:150,
        modal: true,
        buttons: {
            "Delete": function() {
                $.post(CLASSROOMDELETE_URL, {classroomid: classroomid}, function(){}, 'json');
                oTable1.fnDestroy();
                oTable1 = $('#classrooms').dataTable({
                    "bJQueryUI": true,
                        "bProcessing": false,
                        "sAjaxSource": "/classroom/getall/"
                });

                $( this ).dialog( "close" );
            },
        Cancel: function() {
                    $( this ).dialog( "close" );
                }
        }
    });
};

var viewclassroom = function(classroomid){
    location.href = "teachers/manage/viewclassroom/" + classroomid;
};

var deleteitempool = function(itempoolid){
    var dialogue3 = $( "#dialog-confirm3" ).dialog({
        resizable: false,
        height:150,
        modal: true,
        buttons: {
            "Delete": function() {
		$.ajax({
		    type: "POST",
		    url: ITEMPOOLDELETE_URL,
		    dataType: "json",
		    data: {itempoolid:itempoolid},
		    success: function(payload) {
			
		    },
		    error: function(XMLHttpRequest, textStatus, errorThrown) {
			//alert(XMLHttpRequest.responseText);
		        return this;
		    }
		});



                //$.post(ITEMPOOLDELETE_URL,
                //    {itempoolid:itempoolid},
                //    function(){
		//		
		//	},
                 //   'json');
                oTable2.fnDestroy();
                oTable2 = $('#itempools').dataTable({
                    "bJQueryUI": true,
                        "bProcessing": false,
                        "sAjaxSource": url_mcq_getall_itempool
                });
                $( this ).dialog( "close" );
            },
        Cancel: function() {
                    $( this ).dialog( "close" );
                }
        }
    });
};

var deletepaper = function(paperid){
    var PAPER_URL;
    var dialogue4 = $( "#dialog-confirm4" ).dialog({
        resizable: false,
        height:150,
        modal: true,
        buttons: {
            "Delete": function() {
                

		$.ajax({
		    type: "POST",
		    url: PAPERDELETE_URL,
		    dataType: "json",
		    data:  {paperid: paperid},
		    success: function(payload) {
			
		    },
		    error: function(XMLHttpRequest, textStatus, errorThrown) {
			//alert(XMLHttpRequest.responseText);
		        return this;
			}
		    });

                oTable3.fnDestroy();
                oTable3 = $('#papers').dataTable({
                    "bJQueryUI": true,
                        "bProcessing": false,
                        "sAjaxSource": url_mcq_getall_paper




                });





                $(this).dialog("close");
            },
        Cancel: function() {
                    $(this).dialog("close");
                }
        }
    });
};

var deleteassignment = function(assignmentid){
    var dialogue5 = $("#dialog-confirm5").dialog({
        resizable: false,
        height:150,
        modal: true,
        buttons: {
            "Delete": function() {
                $.post(ASSIGNMENTDELETE_URL,
                    {assignmentid: assignmentid},
                    function(){},
                    'json');
                oTable4.fnDestroy();
                oTable4 = $('#assignments').dataTable({
                    "bJQueryUI": true,
                        "bProcessing": false,
                        "sAjaxSource": url_mcq_getall_assignment
                });
                $(this).dialog("close");
            },
        Cancel: function() {
                    $(this).dialog("close");
                }
        }
    });
};
