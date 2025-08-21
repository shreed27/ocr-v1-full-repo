/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */

;(function($, undef) {

    $(function(){
		pullZtreeData();
		setEditableText();
		$('#id_classname').hide();

		var view = intemass.util.getUrl('view');

    $(".editable").editable(function(value,settings){
        $("#id_classname").val(value);
        var curclassid=$("#id_classid").val();
        $.ajax({
            type: "get",
            url: "/classroom/updatename/",
            datatype: "json",
            data: {"classid":curclassid,
                "roomname":value},
            success: function(data) {
                if (data['classid'] && data['roomname']){
                    $("#id_classid").children('option:selected').text(data['roomname']);
            $("#id_classid").children('option:selected').val(data['classid']);
            classid = $("#id_classid").val();
            pullztreedata();
                }
                return data;
            },
            error:function(xmlhttprequest, textstatus, errorthrown) {
                      return this;
                  }
        });
        return $('#id_classname').val();
    },{
        type:"text",
        onblur:"submit",
        tooltip:"click to edit...",
        style: 'display:inline'
    });

		$("#id_classid").change(function(){
        pullZtreeData();
        setEditableText();
		});

		if(view){
        $("#button").hide();
        $(".editable").unbind('click.editable');
		};
		//add some css for select
		$('#id_classid').css("width","140px");
		$('#id_classid').css("margin","0");
		$('#id_classid').css("padding","0");

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

	var pullZtreeData = function(){
		var classid = $('#id_classid').val();
		var view = intemass.util.getUrl('view'); 
		$.ajax({
        type: "POST",
        url: "/classroom/getstudents/",
        dataType: "json",
        data: {"classid":classid,"view":view},
        success: function(data) {
          tnum=data[0]['tnum'];
          if (tnum && tnum!=''){
            $("#tnum").text(tnum);
          }else{
            $("#tnum").text("0");
          }
          data.shift();
          $.fn.zTree.init($("#students"), setting, data);
        },
        error:function(XMLHttpRequest, textStatus, errorThrown) {
            $("#tnum").text("0");
            $("#snum").text("0");
            return this;
        }
		});
	};

	var setEditableText = function(){
      var selclassname = $('#id_classid').children('option:selected').text();
      //console.log(selclassname);
      $('#id_classname').val(selclassname);
      $(".editable").text($('#id_classname').val());
  };

})(jQuery);

	var setSelectedNodes = function(zTree){
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
	};

    function submitform(){
		var treeObj = $.fn.zTree.getZTreeObj("students");
		var sids = setSelectedNodes(treeObj);
        $("#id_stulist").val(sids);
       // if (!sids){
       //     intemass.ui.showclientmsg("You have to choose one student at least!");
       // }else{
            var selclassname=$("#id_classname").val();
            if (selclassname && selclassname =="New Class"){
            intemass.ui.showclientmsg("Please choose a better class name than \"New Class\"");
            }else{
                document.forms[0].submit();
            }
      //  }
    }
