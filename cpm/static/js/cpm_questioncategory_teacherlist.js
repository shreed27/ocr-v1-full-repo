function submitform(){
    var treeObj = $.fn.zTree.getZTreeObj("teacher_list");
    var tpids = setSelectedNodes(treeObj);
    if (!tpids){
	intemass.ui.showclientmsg("You have to choose one teacher at least!");
    }else{

	var curritem_id=$("#txtid").val();
	console.log('curritem_id : ' , curritem_id);
	$.ajax({
	    url:'/cpm/questioncategory/addteacher/',
	    type:'POST',
	    dataType: "json",
	    data:{'questioncategory_id':curritem_id,'teacher_ids':JSON.stringify(tpids)},
	    success:function(data){
		console.log(' done success', data['response']);
	        if(data['response'] == 'success'){
	            intemass.ui.showclientmsg("Teacher Added successfully");
	        }
	        console.log('success')
	    },
	    error: function(XMLHttpRequest, textStatus, errorThrown) { 
		alert("Status: " + textStatus); alert("Error: " + errorThrown); 
	    }    
	});


    }
}


var setSelectedNodes = function(zTree){
	var sNodes = zTree.getCheckedNodes();
	var qids = [];
	if (sNodes.length > 0) {
		for (node in sNodes){
			if (sNodes[node].getParentNode() != null)
				console.log(sNodes[node].qid)
			qids.push(sNodes[node].qid);
		}
		$("#snum").text(qids.length);
	}else{
		$("#snum").text("0");
	}

	return qids;
};
(function($, undef) {
	$(function(){
 		pullZtreeData();
	});
	
	 //intemass.ui.showclientmsg("Teacher Added successfully");
		var setCheck = function() {
			var type, zTree;
			zTree = $.fn.zTree.getZTreeObj("teacher_list");
			type = {
				"Y": "ps",
				"N": "ps"
			};
			zTree.setting.check.chkboxType = type;
			setSelectedNodes(zTree);
		};
		var setting = {
			edit: {
				enable: true,
				showRemoveBtn: false,
				showRenameBtn: false,
				editNameSelectAll: false,
				drag: {
					isCopy: false,
					isMove: true,
					prev: true,
					next: true,
					inner: false
				}
			},
			data: {
				simpleData: {
					enable: true
				}
			},
			check: {
				enable: true
			},
			callback : {
				beforeDrag: beforeDrag,
				beforeDrop: beforeDrop
			}
		}
		var beforeDrop = function(treeId, treeNodes, targetNode, moveType) {
			console.log(targetNode);
			return (targetNode.pId === dragId) ? true : false;
		    };
		var beforeDrag = function(treeId, treeNodes) {
			for (var i = 0, l = treeNodes.length; i < l; i++) {
			    dragId = treeNodes[i].pId;
			    if (!treeNodes[i].drag) {
				return false;
			    }
			}
			return true;
		    };
		var pullZtreeData = function(){
		var curritem_id=$("#txtid").val();
		var view = intemass.util.getUrl('view');
		console.log('view' , view);
		$.ajax({
		    type: "GET",
		    url: "/cpm/optionlist/teacherlist/",
		    dataType: "json",
		    data: {"questioncategory_id":curritem_id,"view":view},
		    success: function(data) {
		        qnum=data[0]['qnum'];
		        if (qnum && qnum!=''){
				$("#qnum").text(qnum);
		        }else{
		            	$("#qnum").text("0");
		        }
		        data.shift();
		        $.fn.zTree.init($("#teacher_list"), setting, data);
		        return setCheck();
		    },
		    error:function(XMLHttpRequest, textStatus, errorThrown) {
		              $("#snum").text("0");
		              $("#qnum").text("0");
		              return this;
		          }
		});
	    };
		
})(jQuery);
























