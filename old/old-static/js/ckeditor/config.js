CKEDITOR.plugins.addExternal('fmath_formula', 'plugins/fmath_formula/', 'plugin.js');
CKEDITOR.plugins.addExternal('keystrokes', 'plugins/keystrokes/', 'plugin.js');
CKEDITOR.config.keystrokes = [];

CKEDITOR.editorConfig = function( config )
{
	 //config.uiColor = 'gray';
	 config.language = 'en';
	 config.skin = 'v2';
	 config.resize_enabled =false;
	 config.height = 445;
	 config.width = 600;
     config.extraPlugins = 'keystrokes,fmath_formula';
     config.removePlugins = 'Copy,paste'
	 config.toolbar_Full =
		 [
			//{ name: 'document', items : [ 'Source','-','Save','NewPage','DocProps','Preview','Print','-','Templates' ] },
			//{ name: 'document', items : [ 'Source','-','NewPage','DocProps','Preview','Print','-','Templates' ] },
			//{ name: 'document', items : [ 'Source','-'] },
			{ name: 'insert', items : [ 'Table','HorizontalRule','SpecialChar'] },
			{ name: 'clipboard', items : [ 'Cut','Paste','PasteText','PasteFromWord','-','Undo','Redo' ] },
			//{ name: 'editing', items : [ 'Find','Replace','-','SelectAll','-','SpellChecker', 'Scayt' ] },
			{ name: 'editing', items : [ 'SpellChecker', '-', 'fmath_formula', 'keystrokes'] },
			//{ name: 'editing', items : [ 'SpellChecker', '-'] },
			{ name: 'editing', items : [ 'Find','Replace','-','SelectAll','-'] },
			//{ name: 'forms', items : [ 'Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button',
			//			        'HiddenField' ] }, '/',
			{ name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat' ] },
			{ name: 'paragraph', items : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote',
										'-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock','-','BidiLtr','BidiRtl' ] },
			//{ name: 'links', items : [ 'Link','Unlink','Anchor' ] },
			//{ name: 'insert', items : [ 'Table','HorizontalRule','Smiley','SpecialChar'] }, '/',
			{ name: 'styles', items : [ 'Styles','Format','Font','FontSize' ] },
			{ name: 'colors', items : [ 'TextColor','BGColor' ] },
			//{ name: 'tools', items : [ 'Maximize', 'ShowBlocks','-' ] }
			//{ name: 'tools', items : [,'-' ] }
	 ];
}
