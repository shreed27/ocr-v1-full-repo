/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */
;(function($, undef) {

    $(function(){
        var view = intemass.util.getUrl('view');
        pullZtreeData();
        setEditableText();
        $('#id_papers').multiselect({
            selectedText: '# of # papers selected',
            noneSelectedText:'Papers'
        });

        $(".datePicker" ).datetimepicker();

        $(".editable").editable(function(value,settings){
            $("#id_assignmentname").val(value);
            $("#id_assignmentid").children('option:selected').text(value);
            return $('#id_assignmentname').val();
        },{
            type:"text",
            onblur:"submit",
            tooltip : "Click to edit",
            style: "display:inline"
        });

        $("#id_assignmentid").change(function(){

            pullZtreeData();
            setEditableText();
        });

        if(view){
            $(".editable").unbind('click.editable');
            $("#button").hide();
			$("#id_testdate").attr("disabled", true);
			$("#id_deadline").attr("disabled", true);
			$("#id_description").attr("disabled", true);
 //           $(".ui-multiselect-menu ul li input").attr("disabled", true);
        };

    });

    var setting = {
        check: {
            enable: true
        },
        data: {
            simpleData: {
                enable: true
            }
        },
    };

    var zTreeOnCheck = function(event, treeId, treeNode) {
        var treeObj = $.fn.zTree.getZTreeObj("members");
        var sids = setSelectedNodes(treeObj);
        if (sids.length > 0){
            $("#id_students").val(sids);
        }
    };

    var pullZtreeData = function(){
        var curassignmentid=$("#id_assignmentid").val();
        var view = intemass.util.getUrl('view');
        //console.log(curassignmentid);
        $.ajax({
            type: "POST",
            url: "/cpm/assignment/getstudents/",
            dataType: "json",
            data: {"assignmentid":curassignmentid, "view":view},
            success: function(data) {

                tnum=data[0]['tnum'];
		//console.log(tnum);
                if (tnum && tnum!=''){
                    $("#tnum").text(tnum);
                }else{
                    $("#tnum").text("0");
                }
                data.shift();
		console.log(data);
                $.fn.zTree.init($("#members"), setting, data);
            },
            error:function(XMLHttpRequest, textStatus, errorThrown) {
                $("#tnum").text("0");
                $("#snum").text("0");
                console.log('error:', textStatus);
                //console.log(XMLHttpRequest.status);
                //console.log(XMLHttpRequest.readyState);
                return this;
            }
        });
    };

    var setEditableText = function(){
        var selassignmentname = $('#id_assignmentid').children('option:selected').text();
        var curassignmentid = $("#id_assignmentid").val();
        $('#id_assignmentname').val(selassignmentname);
        $(".editable").text($('#id_assignmentname').val());
        if (curassignmentid != -1){
            $.ajax({
                type: "GET",
                url: "/cpm/assignment/updatename/",
                dataType: "json",
                data: {
                    "assignmentid": curassignmentid,
                    "assignmentname": selassignmentname
                },
                success: function(data) {
                    if (data['assignmentname'] && data['assignmentid']){
                        $("#id_assignmentid").children('option:selected').text(data['assignmentname']);
                        $("#id_assignmentid").children('option:selected').val(data['assignmentid']);
                        pullZtreeData();
                        $('#id_description').val(data['description']);
                        $('#id_testdate').val(data['testdate']);
                        $('#id_deadline').val(data['testdue']);
                        papers = data['papers'];
                        $('#id_papers').multiselect("uncheckAll");
                        $('#id_papers').multiselect("widget").find(":checkbox").each(function(){
                            for (var i = 0; i < papers.length; i++){
                                if (papers[i] === Number(this.value)){
                                    this.click();
                                }
                            }
                        });
                    }
                    return;
                },
                    error:function(XMLHttpRequest, textStatus, errorThrown) {
                        return this;
                    }
            });
        }else{
            $('#id_description').val("");
        }
    };


})(jQuery);


function setSelectedNodes(zTree){
    var sNodes = zTree.getCheckedNodes();
    var sids = [];
    if (sNodes.length > 0) {
        for (node in sNodes){
            if (sNodes[node].getParentNode() != null)
                sids.push(sNodes[node].sid);
        }
        $("#snum").text(sids.length);
    }else{
        $("#snum").text("0");
    }
    return sids;
}


function submitform(){
    var treeObj = $.fn.zTree.getZTreeObj("members");
    var sids = setSelectedNodes(treeObj);
    if (!sids){
        intemass.ui.showclientmsg("You have to choose one student at least!");
    }else{
        $("#id_students").val(sids);
        var selassignmentname=$("#id_assignmentname").val();
        if (selassignmentname && selassignmentname =="New Assignment"){
            intemass.ui.showclientmsg("Please choose a better Assignment name than \"New Assignment\"");
        }else{
            document.forms[0].submit();
        }
    }
}
