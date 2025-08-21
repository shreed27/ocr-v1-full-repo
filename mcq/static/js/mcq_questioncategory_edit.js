
	$( document ).ready(function() {
		var errorDesc = function(){
				$( "#dialog-error-desc" ).dialog({
				      modal: true,
				      buttons: {
					Ok: function() {
					  $( this ).dialog( "close" );
					}
				      }
				    });

			}
		var errorCat = function(){
				$( "#dialog-error-cat" ).dialog({
				      modal: true,
				      buttons: {
					Ok: function() {
					  $( this ).dialog( "close" );
					}
				      }
				    });

			}

		$("#btnAdd").click(function(){
			var objSeq = parseInt($("#txtseq").val()) + 1;
			window.location = "/mcq/questioncategory/add/?id=" + $("#txtid").val() + "&seq=" + objSeq;
		});
		$("#btnDelete").click(function(){
			$( "#dialog-confirm" ).dialog({
			      resizable: false,
			      height:140,
			      modal: true,
			      buttons: {
				"Delete": function() {
					var txtID = $("#txtid").val();
				  	//=======================Delete Confirmation Done====================

					$.ajax({
					    type: "POST",
					    url: '/mcq/questioncategory/delete/',
					    dataType: "json",
					    data: {
						"txtID":txtID
					    },
					    success: function(payload) {
						window.location = "/mcq/questioncategory/view/";
					    },
					    error: function(XMLHttpRequest, textStatus, errorThrown) {
						alert(XMLHttpRequest.responseText);
						return this;
					    }
					});





					//=======================Delete Confirmation done ===================

				},
				Cancel: function() {
				  $( this ).dialog( "close" );
				}
			      }
			    });
		});
		$("#btnSave").click(function(){
			var txtID = $("#txtid").val();
			var txtQuestCat = $("#txtquestionCategory").val();
			var txtDesc = $("#txtDescription").val();
			console.log("i getting the value", txtDesc)
			var txtSeq = $("#txtseq").val();
			var txtParentid = $("#txtparentid").val();
			
			if (txtQuestCat=="")
			{
				errorCat();
				return;
			}
			if (txtDesc=="")
			{
				errorDesc();
				return;
			}
			
			console.log(txtID, txtQuestCat, txtDesc , txtSeq , txtParentid);
			$.ajax({
			    type: "POST",
			    url: '/mcq/questioncategory/save/',
			    dataType: "json",
			    data: {
				"txtID":txtID,
				"txtQuestCat":txtQuestCat,
				"txtDesc":txtDesc,
				"txtSeq":txtSeq,
				"txtParentid":txtParentid
			    },
			    success: function(payload) {
				console.log('testing questioncategory save ' ,payload['state']);
				$( "#dialog-message" ).dialog({
				      modal: true,
				      buttons: {
					Ok: function() {
					  $( this ).dialog( "close" );
					}
				      }
				    });
				
			    },
			    error: function(XMLHttpRequest, textStatus, errorThrown) {
				alert(XMLHttpRequest.responseText);
				return this;
			    }
			});
		});
	});
