(function ($) {
    //plug-in internal globals
    var instmap = {};
    var elemap = {};
    var axismap = {};
    var colormap = {};
    var canvasmap = {};
    var global_legends = [];
    var attributes = {
        width:600,
        height:400
    };
    var clonemap = {};
    var doSelection = false;
    var selectionArea = [];
    var curSelectionArea;
    var selectionRedrawCounter = 0;
    var mousemoveCounter = 0;
    var toolbar_offset = 53;
    var activedBtn = null;
    var axisorigin = {};
    var intesectmatrix = [];

    /******************************************************************
     *
     public API
     *
     * ****************************************************************/
    var intemassCanvases = $.fn.IntemassCanvas = function(opts) {

        var options = $.extend(attributes, opts || {});
        var rulelistwidth = 400;
        var csrfvalue = options.csrfvalue;
        if (options.height < 15 || options.width < 50){
            alert("canvas size too small");
        }else{
            options.height = options.height - 13;
            options.width = options.width - 50;
            attributes = options;
            axisorigin = {
                start_x : 70,
                start_y : attributes.height - 50
            };
            this.each(function(){
                $(this).css({'float':'left', 'width':attributes.width});
            });
            this.each(function(){
                var pid = $(this).attr('id');
                buildToolBar(this, csrfvalue);
                buildDrawArea(this,options);
                buildMyMenu(this);
                var listhtml = "<div style='float:left;width:" + rulelistwidth + "px;height:" + attributes.height + "px;margin:1em auto'><h1 class='ui-widget-header'> Generated Rules:</h1>";
                listhtml  +=  "<table class='intemasscanvas-table' id='list" + pid + "'>";
                listhtml  +=  "<thead></thead>";
                listhtml  +=  "<tbody></tbody></table></div>";
                $(this).parent().append(listhtml);
                IntemassCanvasGet(pid, csrfvalue);
            });
        }
    };

    /****
     *
     * destory the IntemassCanvas
     *
     ***/
    $.fn.DestoryIntemassCanvases = function(){
        return this.each(function(){
            var pid = $(this).attr('id');
            delete instmap[pid];
            delete elemap[pid];
            delete colormap[pid];
            delete canvasmap[pid];
            $("*", this).add([this]).each(function() {
                $.event.remove(this);
                $.removeData(this);
            });
            $(this).parent().remove();
        });
    }

    //delete every element if points in the element area
    Raphael.st.undo = function (x,y) {
        var thisset = this;
        var bbox = thisset.getBBox();
        var index;
        var legend;
        var pid;
        if (bbox && Raphael.isPointInsideBBox(bbox,x,y)){
            for (var i = 0; i < global_legends.length; i++){
                legend = global_legends[i].split(':')[0];
                pid = global_legends[i].split(':')[1];
                if (typeofelset(thisset) === 'complexcurve'){
                    if (legend === thisset[9].attr('text'))
                        global_legends.splice(i,1);
                }else if (typeofelset(thisset) === 'curve'){
                    if (legend === thisset[6].attr('text'))
                        global_legends.splice(i,1);
                }else if (typeofelset(thisset) === 'line'){
                    if (legend === thisset[3].attr('text'))
                        global_legends.splice(i,1);
                }else if(typeofelset(thisset) === 'dot'){
                    if (legend === thisset[1].attr('text'))
                        global_legends.splice(i,1);
                }
            }
            thisset.forEach(function(el){
                if(el.data("what") === 'text' || el.data("what") === 'dottext'){
                    for (var elemlegend in canvasmap[pid]['drawopts']){
                        if (elemlegend === el.attr('text')){
                            delete canvasmap[pid]['drawopts'][elemlegend];
                        }
                    }
                }
                el.remove();
                el = null;
                delete el;
            });
          }

        return false;
    };


    /*************************************************************************************************************************************
    //
    //private functions
    //
     *************************************************************************************************************************************/
    //
    function typeofelset(elset){
        if (elset.length === 5){
            return 'line';
        }else if (elset.length === 8){
            return 'curve';
        }else if(elset.length === 11){
            return 'complexcurve';
        }else if(elset.length === 2){
            return 'dot';
        }
    }

    function getlegendofelset(elset){
        var legend;
        switch (typeofelset(elset)){
            case 'dot':
                legend = elset[1].attr('text');
                break;
            case 'line':
                legend = elset[3].attr('text');
                break;
            case 'curve':
                legend = elset[6].attr('text');
                break;
            case 'complexcurve':
                legend = elset[9].attr('text');
                break;
            default:
                legend = undefined;
        }
        return legend;
    }

    function buildDrawArea(parent,options){
        var pid = $(parent).attr('id');
        var drawareahtml = '<div class="intemasscanvas-canvas">';
        drawareahtml += '<div id="'+pid+'-tips-dialog" title="Give some tips" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">Please enter some tips </p>';
        drawareahtml += '<label for="'+pid+'-tips-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">Tips:</label><textarea id="'+pid+'-tips-input" style="width:200px;height:90px;" /></div>';
        drawareahtml += '<div id="'+pid+'-legend-dialog" title="Give A Legend" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">Please assign a unique legend before drawing </p>';
        drawareahtml += '<label for="'+pid+'-legend-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">Legend:</label><input id="'+pid+'-legend-input" type="text" value="Legend" style="width:200px;" /></div>';
        drawareahtml += '<div id="'+pid+'-about-dialog" title="About Us" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">About Us</p>';
        drawareahtml += '<label for="'+pid+'-legend-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">About us:</label></div>';
        drawareahtml += '<div id="'+pid+'-removeall-dialog" title="Remove All the elements" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">Are you sure?</p>';
        drawareahtml += '<label for="'+pid+'-legend-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">You will remove all the elements in the canvas.</label></div>';
        //drawareahtml += '<div id="'+pid+'-color-dialog" title="Choose A Color" style="display:none;">';
        //drawareahtml += '<input id="'+pid+'-color-widget" style="display: inline-block; vertical-align: top;"></input></div>';
        drawareahtml += '<div id="'+pid+'-axis-dialog" class="intemasscanvas-axis-dialog" title="Set Coordinates" style="display:none;">';
        drawareahtml += '<label for="'+pid+'-axis-name" class= "intemasscanvas-axis-label">Name:</label><input id="'+pid+'-axis-name" type="text" class="intemasscanvas-axis-input" />';
        drawareahtml += '<label for="'+pid+'-axis-splits" class= "intemasscanvas-axis-label">Splits:</label><input id="'+pid+'-axis-splits" type="text" value="3" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="'+pid+'-axis-unit" class= "intemasscanvas-axis-label">Units:</label><input id="'+pid+'-axis-unit" type="text" value="m" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="'+pid+'-axis-start" class= "intemasscanvas-axis-label">Start Value:</label><input id="'+pid+'-axis-start" type="text" value="0" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="'+pid+'-axis-end" class= "intemasscanvas-axis-label">End Value:</label><input id="'+pid+'-axis-end" type="text" value="10" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="'+pid+'-axis-direction" class= "intemasscanvas-axis-label">Direction:</label><select id="'+pid+'-axis-direction" class="intemasscanvas-axis-select" ><option value="0" selected="selected">Horizontal</option><option value="1">Vertical</option></select>';
        drawareahtml += '</div>';
        drawareahtml += '<div id="'+pid+'-rule-dialog" class="intemasscanvas-rule-dialog" title="Add Rules" style="display:none;">';
        drawareahtml += '</div>';
        drawareahtml += '</div>';
        $(drawareahtml).appendTo($(parent));

        //build color picker
        $("#"+pid+"-color-widget").colorpicker({
            color:'#ccc',
            parts: 'popup',
            showCloseButton: true,
            showCancelButton: false,
            init: function(event, color) {
            },
            select: function(evt,color){
                        //console.log('in color select');
                        colormap[pid] = Raphael.getRGB(color.formatted);
                    },
            close: function(evt, color){
                       colormap[pid] = Raphael.getRGB(color.formatted);
                       if (colormap[pid].error === 1)
                            colormap[pid] = "hsb(0,0,0.8)";
                   }
        });
        //build spin buttons
        $("#"+pid+"-axis-units").spinner({ min: 0, max: 100, mouseWheel:false});
        $("#"+pid+"-axis-start").spinner({ min: -99999, max: 99999, mouseWheel:false, step:0.01 });
        $("#"+pid+"-axis-end").spinner({ min: -99999, max: 99999, mouseWheel:false, step:0.01 });

        var paper = Raphael($(parent).find(".intemasscanvas-canvas")[0],options.width, options.height-10);
        //console.log("w:"+options.width+" | h:"+options.height)
        paper.rect(0, 5, options.width - 5, options.height - 15, 10).attr({stroke: "#666"});
        colormap[pid] = "hsb(0,0,0.8)";
        instmap[pid] = paper;
        elemap[pid] = paper.set();
        axismap[pid] = [];
        canvasmap[pid] = canvasmap[pid] || {'drawopts':{}, 'axis':{}, 'rulelist':{}};
    }

    function buildToolBar(parent, csrfvalue){
        var pid = $(parent).attr('id');
        var toolbarhtml='<span class="ui-widget-header ui-corner-all intemasscanvas-toolbar" style="float:left;">'; toolbarhtml += '<input type="checkbox" class="lineBtn" id="'+pid+'-lineBtn"/><label for="'+pid+'-lineBtn" style="width:40px;height:40px">Add Line</label>';
        toolbarhtml += '<input type="checkbox" class="curveBtn" id="'+pid+'-curveBtn"/><label for="'+pid+'-curveBtn" style="width:40px;height:40px">Add Simple Curve</label>';
        toolbarhtml += '<input type="checkbox" class="complexcurveBtn" id="'+pid+'-complexcurveBtn"/><label for="'+pid+'-complexcurveBtn" style="width:40px;height:40px">Add Complex Curve</label>';
        toolbarhtml += '<input type="checkbox" class="dotBtn" id="'+pid+'-dotBtn"/><label for="'+pid+'-dotBtn" style="width:40px;height:40px">Add Dot</label>';
        toolbarhtml += '<input type="checkbox" class="tipsBtn" id="'+pid+'-tipsBtn"/><label for="'+pid+'-tipsBtn" style="width:40px;height:40px">Add Tips</label>';
        toolbarhtml += '<button class="axisBtn" id="'+pid+'-axisBtn" style="width:42px;height:42px;padding-bottom:13px">Set Coordinates</button>';
        toolbarhtml += '<input type="checkbox" class="moveBtn" id="'+pid+'-moveBtn" /><label for="'+pid+'-moveBtn" style="width:40px;height:40px">Move</label>';
        toolbarhtml += '<input type="checkbox" class="viewBtn" id="'+pid+'-viewBtn"/><label for="'+pid+'-viewBtn" style="width:40px;height:40px">Preview All</label>';
        toolbarhtml += '<button class="colorBtn" id="'+pid+'-colorBtn" style="width:42px;height:42px;padding-bottom:13px">Choose Color</button>';
        toolbarhtml += '<input id="'+pid+'-color-widget" style="display: none; vertical-align: bottom;"></input>';
        toolbarhtml += '<input type="checkbox" class="ruleBtn" id="'+pid+'-ruleBtn"/><label for="'+pid+'-ruleBtn" style="width:40px;height:40px">Add Rule</label>';
        toolbarhtml += '<button class="removeallBtn" id="'+pid+'-removeallBtn" style="width:42px;height:42px;padding-bottom:13px">Remove All</button>';
        toolbarhtml += '<button class="uploadBtn" id="'+pid+'-uploadBtn" style="width:42px;height:42px;padding-bottom:13px">Upload All</button>';
        toolbarhtml += '</span>';
        $(toolbarhtml).appendTo($(parent));
        var $curveBtn = $("#"+pid+"-curveBtn" ).data('whatBtn', 'curveBtn').button({
            text: false,
            icons: {
                primary: "ui-icon-carat-1-ne"
            }
        });
        var $complexcurveBtn = $("#"+pid+"-complexcurveBtn" ).data('whatBtn', 'complexcurveBtn').button({
            text: false,
            icons: {
                primary: "ui-icon-shuffle"
            }
        });
        var $lineBtn = $("#"+pid+"-lineBtn").data('whatBtn', 'lineBtn').button({
            text: false,
            icons: {
                primary: "ui-icon-minus"
            }
        });
        var $dotBtn = $("#"+pid+"-dotBtn").data('whatBtn', 'dotBtn').button({
            text: false,
            icons: {
                primary: "ui-icon-bullet"
            }
        });
        var $tipsBtn = $("#"+pid+"-tipsBtn").data('whatBtn', 'tipsBtn').button({
            text: false,
            icons: {
                primary: "ui-icon ui-icon-document-b"
            }
        });
        var $axisBtn = $("#"+pid+"-axisBtn" ).data('whatBtn', 'axisBtn');
        var $moveBtn = $("#"+pid+"-moveBtn" ).data('whatBtn', 'moveBtn');
        var $colorBtn = $("#"+pid+"-colorBtn" ).data('whatBtn', 'colorBtn');
        var $ruleBtn = $("#"+pid+"-ruleBtn" ).data('whatBtn', 'ruleBtn');
        var $viewBtn = $("#"+pid+"-viewBtn" ).data('whatBtn', 'viewBtn');
        var $uploadBtn = $("#"+pid+"-uploadBtn" ).data('whatBtn', 'uploadBtn');
        var $removeallBtn = $("#"+pid+"-removeallBtn" ).data('whatBtn', 'removeallBtn');
        var $Btn = [$curveBtn, $complexcurveBtn, $lineBtn, $axisBtn, $moveBtn, $colorBtn, $ruleBtn, $viewBtn, $removeallBtn, $dotBtn, $tipsBtn];

        /******************************************************************
         *
         * Here we bundle draw_buttons
         *
         *****************************************************************/

        $complexcurveBtn.add($curveBtn).add($dotBtn).add($lineBtn).add($tipsBtn).click(function() {
            var whatBtn = $(this).data("whatBtn");
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            activedBtn = $(this);
            if ($(this).prop("checked")){
                $(canvas).unbind("click");
                disable_unactivedBtn($Btn, activedBtn);
                remove_dashline();
                //forbidMove();

                $(canvas).css('cursor', 'pointer');
                $(canvas).bind("click",function(evt){
                    var start_x = evt.pageX - this.offsetLeft;
                    var start_y = evt.pageY - this.offsetTop - toolbar_offset;
                    var end_x = start_x < (attributes.width - 200) ? (start_x + 200) : attributes.width;
                    var end_y = start_y < (attributes.height - 200) ? start_y + 200 : attributes.height;
                    var drawopts = {'start_x':start_x, 'start_y':start_y,
                                    'end_x':end_x, 'end_y':end_y,
                                    'custom_path':null, 'custom_handler_path':null,
                                    'dashline':false, 'color':null};
                    var pid = $(parent).attr('id');
                    switch(whatBtn)
                    {
                        case 'curveBtn':
                            addDraw(pid, drawCurve, drawopts);
                            break;

                        case 'lineBtn':
                            addDraw(pid, drawLine, drawopts);
                            break;

                        case 'complexcurveBtn':
                            drawopts['end_y'] = start_y;
                            addDraw(pid, drawComplexCurve, drawopts);
                            break;

                        case 'dotBtn':
                            drawopts['end_x'] = null;
                            drawopts['end_y'] = null;
                            addDraw(pid, drawDot, drawopts);
                            break;

                        case 'tipsBtn':
                            drawopts['end_x'] = null;
                            drawopts['end_y'] = null;
                            addDraw(pid, drawTips, drawopts);
                            break;

                        default:
                            break;
                    }
                    $(canvas).unbind("click");
                    $(canvas).css('cursor', 'auto');
                });
            }else{
                activedBtn = null;
                $(canvas).unbind("click");
                $(canvas).css('cursor', 'auto');
            }
        });

        /************************************************
         *
         * Below are functional buttons
         *
         * **********************************************/

        $uploadBtn.button({
            text: false,
            icons: {
                primary: "ui-icon-arrowthickstop-1-n"
            }
        }).click(function(){
            IntemassCanvasUpload(csrfvalue);
        });

        $axisBtn.button({
            text: false,
            icons: {
                primary: "ui-icon-newwin"
            }
        })
        .click(function(){
            disable_unactivedBtn($Btn, $(this));
            var dialogid = '#'+pid+'-axis-dialog';
            var axis = {};
            var dialogOpts = {
                modal: true,
            buttons: {
                "Done": function(){
                    axis['name'] = $("#"+pid+"-axis-name").val();
                    axis['unit'] = $("#"+pid+"-axis-unit").val();
                    axis['splits'] = $("#"+pid+"-axis-splits").val();
                    axis['start'] = $("#"+pid+"-axis-start").val();
                    axis['end'] = $("#"+pid+"-axis-end").val();
                    axis['direction'] = $("#"+pid+"-axis-direction").val();
                    drawAxis(pid,axis);
                    $(dialogid).dialog("close");
                },
                "Cancel": function(){
                    $(dialogid).dialog("close");
                }
            },
            width:350,
            draggable:false,
            resizable:false
            };
            $(dialogid).dialog(dialogOpts);
        });

        $moveBtn.button({
            text: false,
            icons: {
                primary: "ui-icon-arrow-4"
            }
        })
        .click(function() {
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            var elist=elemap[$(parent).attr('id')];
            var pid = $(parent).attr('id');
            if ($(this).prop("checked")){
                disable_unactivedBtn($Btn, $(this));
                $(canvas).disableContextMenu();
                $(canvas).css('cursor', 'pointer');
                $(canvas).unbind("click");
                elist.forEach(function(elset){
                    elset.forEach(function(el){
                        if (el.data('what')=='area') el.show();
                    });
                });
            }else{
                $(canvas).enableContextMenu();
                elist.forEach(function(elset){
                    elset.forEach(function(el){
                        if (el.data('what')=='area') el.hide();
                    });
                });
                $(canvas).css('cursor', 'auto');

            }
        });


        $viewBtn.button({
            text: false,
        icons: {
            primary: "ui-icon-search"
        }
        })
        .click(function() {
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            var elist=elemap[$(parent).attr('id')];
            if ($(this).prop("checked")){
                disable_unactivedBtn($Btn, $(this));
                $(canvas).unbind("click");
                $(canvas).css('cursor', 'auto');
                elist.forEach(function(elset){
                    elset.forEach(function(el){
                        if (el.data("what")==='circle' || el.data("what")==='handler_path'){
                            el.attr({"fill-opacity": 0, "stroke-opacity": 0});
                        }
                        if (el.data("what")==='text'){
                            el.show();
                        }
                    })
                    //elset.hide();
                });
            }
            else{
                $moveBtn.click().attr('checked', false);
                $moveBtn.next().removeClass('ui-state-active');
                elist.forEach(function(elset){
                    elset.forEach(function(el){
                        if (el.data("what")=='text'){
                            el.hide();
                        }
                        else if (el.data("what") !== 'area'){
                            el.attr({"fill-opacity": 1, "stroke-opacity": 1});
                        }
                    })
                });


            }
        });

        $colorBtn.button({
            text: false,
            icons: {
                primary: "ui-icon-calculator"
            }
        })
        .click(function(){
            $("#"+pid+"-color-widget").focus();
            disable_unactivedBtn($Btn, $(this));
          });

        $ruleBtn.button({
            text: false,
            icons: {
                primary: "ui-icon-comment"
            }
        })
        .click(function() {
            disable_unactivedBtn($Btn, $(this));
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            if ($(this).prop("checked")){
                //global variable
                mousedownSelectionFunc = function(evt){
                    var canvas_x = evt.pageX - this.offsetLeft;
                    var canvas_y = evt.pageY - this.offsetTop - toolbar_offset;
                    //console.log("Mouse Down - Canvas_X:"+canvas_x+"|Canvas_Y:"+canvas_y);
                    doSelection = true;
                    selectionArea.push(canvas_x);
                    selectionArea.push(canvas_y);
                };
                mousemoveSelectionFunc = function(evt,oldMousePositions){
                    if (doSelection === true){
                        selectionRedrawCounter  += 1;
                        if (selectionRedrawCounter % 3 != 0)return;
                        var canvas_x = evt.pageX - this.offsetLeft;
                        var canvas_y = evt.pageY - this.offsetTop - toolbar_offset;
                        selectionArea.push(canvas_x);
                        selectionArea.push(canvas_y);
                        drawSelectionArea(parent,selectionArea[0],selectionArea[1],selectionArea[2],selectionArea[3]);
                        selectionArea.pop();
                        selectionArea.pop();
                    }
                };
                mouseupSelectionFunc = function(evt){
                    var canvas_x = evt.pageX - this.offsetLeft;
                    var canvas_y = evt.pageY - this.offsetTop - toolbar_offset;
                    var thiscanvas = $(parent).attr('id');
                    //console.log("Mouse UP - Canvas_X:"+canvas_x+"|Canvas_Y:"+canvas_y);
                    $(canvas).unbind("mousedown",mousedownSelectionFunc);
                    $(canvas).unbind("mousemove",mousemoveSelectionFunc);
                    $(canvas).unbind("mouseup",mouseupSelectionFunc);
                    if (curSelectionArea){
                        var dialogid = '#'+pid+'-rule-dialog';
                        var rulelist = [];
                        var savedrule = [];
                        curSelectionArea.remove();
                        curSelectionArea = undefined;
                        rulelist = calculateRules(thiscanvas,selectionArea[0],selectionArea[1],canvas_x,canvas_y);
                        $(dialogid).empty();
                        for(var i = 0; i < rulelist.length; i++){
                            $(dialogid).append("<p><label>"+ rulelist[i] + "</label><input type='checkbox' name='" + rulelist[i] + "'></input></p>");
                        }
                        var dialogOpts = {
                            modal: true,
                            buttons: {
                                "SelectAll": function(){
                                    for (var i = 0; i < $(dialogid).find("input").length; i++){
                                        input = $(dialogid).find("input")[i];
                                        $(input).attr('checked', true);
                                    }
                                },
                                "Done": function(){
                                    var input, rule;
                                    $("#"+pid+"-ruleBtn").prop('checked',false);
                                    $("#"+pid+"-ruleBtn").button('refresh');
                                    for (var i = 0; i < $(dialogid).find("input").length; i++){
                                        input = $(dialogid).find("input")[i];
                                        if ($(input).prop('checked')){
                                            savedrule.push($(input).attr("name").split(/\s,/));
                                        }
                                    }
                                    listRules(pid, savedrule);
                                    $(dialogid).dialog("close");
                                },
                                "Cancel": function(){
                                    $(canvas).bind("mousedown",mousedownSelectionFunc);
                                    $(canvas).bind("mousemove",mousemoveSelectionFunc);
                                    $(canvas).bind("mouseup",mouseupSelectionFunc);
                                    //$(canvas).bind("mouseleave",mouseupSelectionFunc);
                                    $(dialogid).dialog("close");
                                }
                            },
                            width:600,
                            draggable:false,
                            resizable:false
                        };
                        $(dialogid).dialog(dialogOpts);
                    }
                    doSelection = false;
                    selectionArea=[];
                }; $(canvas).bind("mousedown",mousedownSelectionFunc);
                $(canvas).bind("mousemove",mousemoveSelectionFunc);
                $(canvas).bind("mouseup",mouseupSelectionFunc);
                //$(canvas).bind("mouseleave",mouseupSelectionFunc);
            }else{
                $(canvas).unbind("mousedown",mousedownSelectionFunc);
                $(canvas).unbind("mousemove",mousemoveSelectionFunc);
                $(canvas).unbind("mouseup",mouseupSelectionFunc);
                //$(canvas).unbind("mouseleave",mouseupSelectionFunc);
            }
        });

        $removeallBtn.button({
            text: false,
            icons: {
                primary: "ui-icon-trash"
            }
        })
        .click(function() {
            disable_unactivedBtn($Btn, $(this));
            var pid = $(parent).attr('id');
            var elist=elemap[pid];
                var dialogid = '#'+pid+'-removeall-dialog';
                var dialogOpts = {
                    modal: true,
                    buttons: {
                        "OK": function(){
                            elist.forEach(function(elset){
                                elset.remove();
                                elset = null;
                                delete elset;
                            });
                            //remove global_legends
                            for (var i = 0; i < global_legends.length; i  += 1){
                                var legend_pid = global_legends[i].split(':')[1];
                                if (legend_pid === pid){
                                    global_legends.splice(i,1);
                                }
                            }
                            //remove axisset
                            var axislist = axismap[pid];
                            axislist.forEach(function(axisset){
                                axisset.remove();
                                axisset = null;
                                delete axisset;
                            });

                            //remove rulelist
                            $('#list' + pid + ' thead tr').remove();
                            $('#list' + pid + ' tbody tr').remove();

                            canvasmap[pid] = {'drawopts':{}, 'axis':{}, 'rulelist':{}};

                            $(dialogid).dialog("close");
                        },
                        "Cancel":function(){
                            $(dialogid).dialog("close");
                        }
                    },
                    width:320,
                    height:200, draggable:false,
                    resizable:false
                };
                $(dialogid).dialog(dialogOpts);

        });

        function disable_unactivedBtn(btnList, activedBtn){
            for(var i = 0; i < btnList.length; i  +=  1){
                if (btnList[i].data("whatBtn") !== activedBtn.data("whatBtn")){
                    btnList[i].next().removeClass('ui-state-active');
                    btnList[i].attr('checked', false);
                }
            }
        }
        function forbidMove(){
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            var elist = elemap[$(parent).attr('id')];
            $(canvas).css('cursor', 'auto');
            elist.forEach(function(elset){
                elset.forEach(function(el){
                    if (el.data("what") === 'area' || el.data("what") === 'text'){
                        el.undrag();
                        el.hide();
                    }else if (el.data("what") === 'circle'){
                        el.undrag();
                        el.drag(move, start, end);
                    }else if (el.data("what") === 'path'){
                        el.undrag();
                    }
                })
            });
        }

        function remove_dashline(){
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            var elist=elemap[$(parent).attr('id')];
            elist.forEach(function(elset){
                elset.forEach(function(el){
                    if (el.data('what')=='area') el.hide();
                })
            });
        }

    }

    function buildMyMenu(parent){
        var pid = $(parent).attr('id');
        var menuid = pid+'_intemass_menu';
        var menuhtml = '';
        menuhtml += '<ul id="'+menuid+'" class="contextMenu">';
        menuhtml += '<li class="delete"><a href="#delete">Delete</a></li>';
        //menuhtml += '<li class="cut separator"><a href="#cut">Cut</a></li>';
        //menuhtml += '<li class="copy separator"><a href="#copy">copy</a></li>';
        //menuhtml += '<li class="paste separator"><a href="#paste">paste</a></li>';
        //menuhtml += '<li class="edit separator"><a href="#edit">edit</a></li>';
        menuhtml += '<li class="about separator"><a href="#about">about</a></li>';
        menuhtml += '</ul>';
        $(menuhtml).appendTo($(parent));
        var canvas = $(parent).find(".intemasscanvas-canvas")[0];
        var elist=elemap[$(parent).attr('id')];

        $(canvas).on('mousedown', function(e){
            var offset_Left = this.offsetLeft;
            var offset_Top = this.offsetTop - toolbar_offset;
            if (3 == e.which){
                //right click mousedown event
                var elist=elemap[$(parent).attr('id')];
                elist.forEach(function(elset){
                    var flag = 0;
                    var bbox=elset.getBBox();
                    if (Raphael.isPointInsideBBox(bbox, e.clientX - offset_Left, e.clientY - offset_Top)){
                        elset.forEach(function(el){
                            if (el.data("what")=='area'){
                                if (el.node.style.display!=""){
                                    el.show();
                                    $(canvas).one("mousedown",function(e){
                                        el.hide();
                                    });
                                }
                                flag = 1;
                                return false;
                            }
                        })
                    }
                    if (flag==1) return false;
                })
            }
        });

        $(canvas).contextMenu({
            menu: menuid
        },
        function(action, menuele, pos){

            if (action === "delete"){
                var pid = $(parent).attr('id');
                var elist=elemap[pid];
                //console.log(elist);
                elist.forEach(function(elset){
                    if (elset.undo(pos.x, pos.y-toolbar_offset) === true){
                        return false;
                    }
                });
            }

            if (action === "about"){
                var pid = $(parent).attr('id');
                var dialogid = '#'+pid+'-about-dialog';
                var dialogOpts = {
                    modal: true,
                    buttons: {
                        "Ok": function(){
                            $(dialogid).dialog("close");
                        }
                    },
                    width:320,
                    height:200,
                    draggable:false,
                    resizable:false
                };
                $(dialogid).dialog(dialogOpts);
            }

            if (action === "edit"){
                var pid = $(parent).attr('id');
                var elist=elemap[pid];
                elist.forEach(function(elset){
                    var bbox = elset.getBBox();
                    if (bbox && Raphael.isPointInsideBBox(bbox, pos.x, pos.y) === true){
                        var pid = $(parent).attr('id');
                        var dialogid = '#'+pid+'-legend-dialog';
                        var dialogOpts = {
                            modal: true,
                    buttons: {
                        "Done": function(){
                            var legend = $("#"+pid+"-legend-input").val();
                            var checklegend = legend + ':' + pid;
                            var el_text = null;
                            elset.forEach(function(el){
                                if (el.data('what')=='text')
                                el_text = el.attr('text') + ':' + pid;
                            });
                            for(var i in global_legends){
                                if (global_legends[i] == checklegend && global_legends[i] != el_text){
                                    $("#"+pid+"-legend-dialog #dialogue_warning").css("color", "red");
                                    //console.log($("#dialogue_warning"));
                                    return false;
                                }
                            }
                            global_legends.push(checklegend);
                            elset.forEach(function(el){
                                if (el.data('what')=='text')
                                el.attr({text: legend});
                            });
                            $(dialogid).dialog("close");
                            $("#"+pid+"-legend-dialog #dialogue_warning").css("color", "black");
                        },
                        "Cancel": function(){
                            $(dialogid).dialog("close");
                        }
                    },
                    width:320,
                    height:200, draggable:false,
                    resizable:false
                        };
                        $(dialogid).dialog(dialogOpts);
                        return false;
                    }
                });
            }

            if (action === "cut"){
                var elist=elemap[$(parent).attr('id')];
                elist.forEach(function(elset){
                    var cutflag = false;
                    elset.forEach(function(el){
                        if (el.data("what") ==='area')
                            clonemap['bbox'] = el.getBBox();
                        if (el.data("what") === 'path')
                            clonemap['path'] = el.attr('path');
                        if (el.data("what") === 'handler_path')
                            clonemap['handler_path'] = el.attr('path');
                        if (el.data("what") === 'text')
                            clonemap['legend'] = el.attr('text');
                        if(el.data("what") === 'dot'){
                            elset.forEach(function(el){
                                if(el.data("what") === 'text')
                                    clonemap['legend'] = el.attr('text');
                            });
                            clonemap['elset'] = elset.clone().remove();
                            if (elset.undo(pos.x, pos.y - toolbar_offset) === true){
                               // console.warn("elset delete error");
                            }
                            cutflag = true;
                            return false;
                        }
                    });
                    if (clonemap['bbox'] && Raphael.isPointInsideBBox(clonemap['bbox'], pos.x, pos.y - toolbar_offset) === true){
                        clonemap['elset'] = elset.clone().remove();
                        if (elset.undo(pos.x,pos.y - toolbar_offset) === true){
                          // console.warn("elset delete error");
                        }
                        cutflag = true;
                    }
                    if (cutflag === true)
                        return false;
                });
            }
            if (action === "copy"){
                var elist=elemap[$(parent).attr('id')];
                elist.forEach(function(elset){
                    var copyflag = false;
                    elset.forEach(function(el){
                        el.toFront();
                        if (el.data("what") ==='area')
                            clonemap['bbox'] = el.getBBox();
                        if (el.data("what") === 'path')
                            clonemap['path'] = el.attr('path');
                        if (el.data("what") === 'handler_path')
                            clonemap['handler_path'] = el.attr('path');
                        if(el.data("what")=='dot'){
                            clonemap['elset'] = elset.clone().remove();
                            copyflag = true;
                        }
                    });

                    if (clonemap['bbox'] && Raphael.isPointInsideBBox(clonemap['bbox'], pos.x, pos.y- toolbar_offset) === true){
                        clonemap['elset'] = elset.clone().remove();
                        copyflag = true;
                    }
                    if (copyflag === true)
                        return false;
                });
            }
            if (action === "paste"){
                var pid = $(parent).attr('id');
                var paper = instmap[pid];
                if (!clonemap['elset'])
                    return false;
                var drawopts = {
                    custom_path:clonemap['path'], custom_handler_path:clonemap['handler_path'],
                    legend:clonemap['legend'], dashline:false, color:colormap[pid]
                };
                if (typeofelset(clonemap['elset']) === 'line'){
                    for(var i = 0; i < clonemap['path'].length; i++){
                        for(var j = 1; j <= 2; j++){
                            if (j%2 === 0)
                                clonemap['path'][i][j] += pos.y-clonemap['bbox'].y;
                            else
                                clonemap['path'][i][j] += pos.x-clonemap['bbox'].x;
                        }
                    }
                    drawopts['start_x'] = clonemap['path'][0][1];
                    drawopts['start_y'] = clonemap['path'][0][2];
                    drawopts['end_x'] = clonemap['path'][1][1];
                    drawopts['end_y'] = clonemap['path'][1][2];
                    if (clonemap['legend'] != null){
                        drawLine(pid, drawopts);
                    }else{
                        addDraw(pid, drawLine, drawopts);
                    }
                }
                if (typeofelset(clonemap['elset']) === 'curve'){
                    clonemap['path'][0][1] += pos.x-clonemap['bbox'].x;
                    clonemap['path'][1][1] += pos.x-clonemap['bbox'].x;
                    clonemap['path'][1][3] += pos.x-clonemap['bbox'].x;
                    clonemap['path'][1][5] += pos.x-clonemap['bbox'].x;
                    clonemap['path'][0][2] += pos.y-clonemap['bbox'].y;
                    clonemap['path'][1][2] += pos.y-clonemap['bbox'].y;
                    clonemap['path'][1][4] += pos.y-clonemap['bbox'].y;
                    clonemap['path'][1][6] += pos.y-clonemap['bbox'].y;
                    clonemap['handler_path'][0][1] += pos.x-clonemap['bbox'].x;
                    clonemap['handler_path'][0][2] += pos.y-clonemap['bbox'].y;
                    clonemap['handler_path'][1][1] += pos.x-clonemap['bbox'].x;
                    clonemap['handler_path'][1][2] += pos.y-clonemap['bbox'].y;
                    clonemap['handler_path'][2][1] += pos.x-clonemap['bbox'].x;
                    clonemap['handler_path'][2][2] += pos.y-clonemap['bbox'].y;
                    clonemap['handler_path'][3][1] += pos.x-clonemap['bbox'].x;
                    clonemap['handler_path'][3][2] += pos.y-clonemap['bbox'].y;
                    drawopts['start_x'] = clonemap['path'][0][1];
                    drawopts['start_y'] = clonemap['path'][0][2];
                    drawopts['end_x'] = clonemap['path'][1][5];
                    drawopts['end_y'] = clonemap['path'][1][6];
                    if (clonemap['legend'] !== null){
                        drawCurve(pid, drawopts);
                    }else{
                        addDraw(pid, drawCurve, drawopts);
                    }
                }
                if (typeofelset(clonemap['elset']) === 'complexcurve'){
                    for(var i = 0; i < clonemap['path'].length; i++){
                        for(var j = 1; j < clonemap['path'][i].length; j++){
                            if (j % 2 === 0)
                                clonemap['path'][i][j]  +=  pos.y-clonemap['bbox'].y;
                            else
                                clonemap['path'][i][j]  +=  pos.x-clonemap['bbox'].x;
                        }
                    }
                    for(var i = 0; i < clonemap['handler_path'].length; i++){
                        for(var j = 1; j < clonemap['handler_path'][j].length; j++){
                            if (j % 2 === 0)
                                clonemap['handler_path'][i][j] += pos.y - clonemap['bbox'].y;
                            else
                                clonemap['handler_path'][i][j] += pos.x - clonemap['bbox'].x;
                        }
                    }
                    drawopts['start_x'] = clonemap['path'][0][1];
                    drawopts['start_y'] = clonemap['path'][0][2];
                    drawopts['end_x'] = clonemap['path'][3][5];
                    drawopts['end_y'] = clonemap['path'][3][6];
                    if (clonemap['legend'] !== null){
                        drawComplexCurve(pid, drawopts);
                    }else{
                        addDraw(pid, drawComplexCurve, drawopts);
                    }
                }

                if (typeofelset(clonemap['elset']) === 'dot'){
                    if (clonemap['legend'] !== null){
                        drawDot(pid, drawopts);
                    }else{
                        drawopts['start_x'] = pos.x;
                        drawopts['start_y'] = pos.y - toolbar_offset;
                        drawopts['end_x'] = null;
                        drawopts['end_y'] = null;
                        addDraw(pid, drawDot, drawopts);
                    }
                }
                //clear cloneset
                clonemap = {};
            }
        });
    }

    /*******
     *
     *      The Main Draw Function
     *
     *******/
    function addDraw(pid, draw_what, drawopts){
        var dialogid = '#'+pid+'-legend-dialog';
        var legend='L';
        var dialogOpts = {
            modal: true,
            buttons: {
                "Done": function(){
                    drawopts['color'] = colormap[pid];
                    drawopts['dashline'] = ($("#"+pid+"-legend-dashline").attr('checked') === 'checked');
                    drawopts['horizontal'] = ($("#"+pid+"-legend-horizontal").attr('checked') === 'checked');
                    drawopts['vertical'] = ($("#"+pid+"-legend-vertical").attr('checked') === 'checked');
                    if(draw_what === drawTips){
                        legend = $("#"+pid+"-tips-input").val();
                    }else{
                        legend = $("#"+pid+"-legend-input").val();
                    }
                    drawopts['legend'] = legend;
                    var checklegend = legend + ':' + pid;
                    for(var i = 0; i < global_legends.length; i  +=  1){
                        if (global_legends[i] === checklegend){
                            $("#"+pid+"-legend-dialog #dialogue_warning").css("color", "red");
                            return false;
                        }
                    }
                    global_legends.push(checklegend);
                    if(drawopts['horizontal'] || drawopts['vertical']){
                        drawopts['dashline'] = true;
                        drawLine(pid, drawopts);
                    }else{
                        draw_what(pid, drawopts);
                    }

                    if(activedBtn !== null){
                        activedBtn.next().removeClass('ui-state-active');
                        activedBtn.attr('checked', false);
                        activedBtn=null;
                    }
                    $(dialogid).dialog("close");
                    $("#"+pid+"-legend-dialog #dialogue_warning").css("color", "black");
                },
                "Cancel": function(){
                    if(activedBtn !== null){
                        activedBtn.next().removeClass('ui-state-active');
                        activedBtn.attr('checked', false);
                        activedBtn=null;
                    }
                    $(dialogid).dialog("close");
                }
            },
            open: function(e, ui){
                if(draw_what === drawLine){
                    $(e.target).parent().find('label').parent().append(
                                "<p><input id='"+ pid + "-legend-dashline' type='checkbox'>dashline</input></p>");
                }else if(draw_what === drawDot){
                    $(e.target).parent().find('label').parent().append(
                                "<form><input id='"+ pid + "-legend-horizontal' type='checkbox'>horizontal</input>" +
                                "<input id='"+ pid + "-legend-vertical' type='checkbox'>vertical</input>" +
                                "</form>");
                }
            },
            close: function(e, ui){
                $(e.target).parent().find('#'+ pid +'-legend-dashline').parent().remove();
                $(e.target).parent().find('#'+ pid +'-legend-horizontal').parent().remove();
            },
            width:320,
            height:230, draggable:false,
            resizable:false
        };

        if(draw_what === drawTips){
            dialogid = '#'+pid+'-tips-dialog';
            dialogOpts.height = 260;
        }
        $(dialogid).dialog(dialogOpts);
    }


    function drawComplexCurve(pid, drawopts) {

        var legend = drawopts['legend'];
        var paper = instmap[pid];
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr = {fill: "#00CC00", stroke: "none"};
        var color = drawopts['color'];
        var start_x =  drawopts['start_x'];
        var start_y =  drawopts['start_y'];
        var end_x = drawopts['end_x'];
        var end_y = drawopts['end_y'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var from_handler_x = start_x;
        var from_handler_y = start_y < (attributes.height - 30) ? (start_y + 30) : attributes.height;
        var to_handler_x = end_x;
        var to_handler_y = end_y < (attributes.height - 30) ? (end_y + 30) : attributes.height;
        var mid_handler_x = (start_x + end_x)/2;
        var mid_handler_y = start_y < (attributes.height - 210) ? (start_y + 210) : attributes.height;
        var pre_mid_handler_x = (start_x + end_x)/2 > 60 ? ((start_x + end_x)/2 - 60) : 0;
        var pre_mid_handler_y = start_y < (attributes.height - 210) ? (start_y + 210) : attributes.height;
        var aft_mid_handler_x = (start_x + end_x)/2 < (attributes.width -60) ? ((start_x + end_x)/2 + 60) : attributes.width;
        var aft_mid_handler_y = start_y < (attributes.height - 210) ? (start_y + 210) : attributes.height;
        var curve_path, handler_path;
        (function initcustompath(){
            if (custom_path === null){
                curve_path = [
                    ["M", start_x, start_y],
                    ["C", from_handler_x, from_handler_y, pre_mid_handler_x, pre_mid_handler_y, mid_handler_x, mid_handler_y],
                    ["M", mid_handler_x, mid_handler_y],
                    ["C", aft_mid_handler_x, aft_mid_handler_y, to_handler_x, to_handler_y, end_x, end_y]
                ];
            }else{
                curve_path = custom_path;
            }
        }());

        (function initcustomhandlerpath(){
            if (custom_handler_path === null){
                handler_path = [
                    ["M", start_x, start_y],
                    ["L", from_handler_x, from_handler_y],
                    ["M", end_x, end_y],
                    ["L", to_handler_x, to_handler_y],
                    ["M", pre_mid_handler_x, pre_mid_handler_y],
                    ["L", mid_handler_x, mid_handler_y],
                    ["M", aft_mid_handler_x, aft_mid_handler_y],
                    ["L", mid_handler_x, mid_handler_y]
                ];
            }else{
                handler_path      = custom_handler_path;
                from_handler_x    = custom_handler_path[1][1];
                from_handler_y    = custom_handler_path[1][2];
                to_handler_x      = custom_handler_path[3][1];
                to_handler_y      = custom_handler_path[3][2];
                mid_handler_x     = custom_handler_path[5][1];
                mid_handler_y     = custom_handler_path[5][2];
                pre_mid_handler_x = custom_handler_path[4][1];
                pre_mid_handler_y = custom_handler_path[4][2];
                aft_mid_handler_x = custom_handler_path[6][1];
                aft_mid_handler_y = custom_handler_path[6][2];
            }
        }());

        canvasmap[pid]['drawopts'][legend] = {
            'type':'complexcurve', 'start_x':start_x, 'start_y':start_y,
            'end_x':end_x, 'end_y':end_y, 'color':colormap[pid],
            'custom_path':curve_path, 'custom_handler_path':handler_path,
            'rcoordinate':getrcoordinate(curve_path)
        };

        var controls = paper.set(
                paper.path(curve_path).attr({stroke: color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data('what', 'path'),
                paper.path(handler_path).attr({stroke: "#996600", "stroke-dasharray": ". "}).data('what', 'handler_path'),
                paper.circle(start_x, start_y, 5).attr(discattr_drag).data('what', 'circle'),
                paper.circle(from_handler_x, from_handler_y, 5).attr(discattr).data('what', 'circle'),
                paper.circle(to_handler_x, to_handler_y, 5).attr(discattr).data('what', 'circle'),
                paper.circle(end_x, end_y, 5).attr(discattr).data('what', 'circle'),
                paper.circle(mid_handler_x, mid_handler_y, 5).attr(discattr).data('what', 'circle'),
                paper.circle(pre_mid_handler_x, pre_mid_handler_y, 5).attr(discattr).data('what', 'circle'),
                paper.circle(aft_mid_handler_x, aft_mid_handler_y, 5).attr(discattr).data('what', 'circle'),
                paper.text(curve_path[3][5]+50,curve_path[3][6], legend).attr({'font-size': '15px'}).data('what', 'text').hide(),
                paper.rect(Raphael.pathBBox(curve_path).x, Raphael.pathBBox(curve_path).y, Raphael.pathBBox(curve_path).width, Raphael.pathBBox(curve_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );

        controls[0].update = function (x, y) {
            controls[2].update(x, y);
        };
        controls[2].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[0][1] = newX;
            curve_path[0][2] = newY;
            handler_path[0][1] = newX;
            handler_path[0][2] = newY;
            controls[3].update(x, y);
            controls[5].update(x, y);
            controls[6].update(x, y);
            var bb = Raphael.pathBBox(curve_path);
            controls[10].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['start_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['start_y'] = newY;
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
            //controls[10].update(x, y);
        };
        controls[3].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[1][1] = newX;
            curve_path[1][2] = newY;
            handler_path[1][1] = newX;
            handler_path[1][2] = newY;
            controls[0].attr({path: curve_path});
            controls[1].attr({path: handler_path});
            var bb = Raphael.pathBBox(curve_path);
            controls[10].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
            //controls[10].update(x, y);
        };
        controls[4].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[3][3] = newX;
            curve_path[3][4] = newY;
            handler_path[3][1] = newX;
            handler_path[3][2] = newY;
            controls[0].attr({path: curve_path});
            controls[1].attr({path: handler_path});
            var bb = Raphael.pathBBox(curve_path);
            controls[10].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
            //controls[10].update(x, y);
        };

        controls[5].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[3][5] = newX;
            curve_path[3][6] = newY;
            handler_path[2][1] = newX;
            handler_path[2][2] = newY;
            controls[4].update(x, y);
            controls[9].attr({x:newX+50, y:newY});
            var bb = Raphael.pathBBox(curve_path);
            controls[10].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['end_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['end_y'] = newY;
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
            //controls[10].update(x, y);
        };

        controls[6].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[1][5] = newX;
            curve_path[1][6] = newY;
            curve_path[2][1] = newX;
            curve_path[2][2] = newY;
            handler_path[5][1] = newX;
            handler_path[5][2] = newY;
            handler_path[7][1] = newX;
            handler_path[7][2] = newY;
            controls[7].update(x, y);
            controls[8].update(x, y);
            var bb = Raphael.pathBBox(curve_path);
            controls[10].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
            //controls[10].update(x, y);
        };

        controls[7].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[1][3] = newX;
            curve_path[1][4] = newY;
            handler_path[4][1] = newX;
            handler_path[4][2] = newY;
            controls[0].attr({path: curve_path});
            controls[1].attr({path: handler_path});
            var bb = Raphael.pathBBox(curve_path);
            controls[10].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
            //controls[10].update(x, y);
        };

        controls[8].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[3][1] = newX;
            curve_path[3][2] = newY;
            handler_path[6][1] = newX;
            handler_path[6][2] = newY;
            controls[0].attr({path: curve_path});
            controls[1].attr({path: handler_path});
            var bb = Raphael.pathBBox(curve_path);
            controls[10].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
            //controls[10].update(x, y);
        };

        controls[10].update = function (x, y) {
            controls[2].update(x, y);
            var bb = Raphael.pathBBox(curve_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };

        controls[2].drag(move, start, end);
        controls[3].drag(move, start, end);
        controls[4].drag(move, start, end);
        controls[5].drag(move, start, end);
        controls[6].drag(move, start, end);
        controls[7].drag(move, start, end);
        controls[8].drag(move, start, end);
        controls[10].drag(move, start, end);
        controls[2].update(0, 0);
        elemap[pid].push(controls);
    }

    function drawCurve(pid, drawopts) {
        function update_rectarea(obj){
            var bb = obj.getBBox();
            obj.forEach(function(el){
                if (el.data("what")=='area'){
                    el.attr({x: bb.x, y: bb.y});
                }
            })
        }
        var legend = drawopts['legend'];
        var paper = instmap[pid];
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr = {fill: "#00CC00", stroke: "none"};
        var color = drawopts['color'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x = drawopts['end_x'];
        var end_y = drawopts['end_y'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var from_handler_x = start_x < (attributes.width - 20) ? (start_x + 20) : attributes.widthd;
        var from_handler_y = start_y;
        var to_handler_x = end_x > 40 ? (end_x - 40) : 0;
        var to_handler_y = end_y;
        var curve_path;
        var handler_path;
        if (custom_path === null){
            curve_path = [["M", start_x, start_y], ["C", from_handler_x, from_handler_y, to_handler_x, to_handler_y, end_x, end_y]];
        }else {
            curve_path = custom_path;
        }
        if (custom_handler_path === null){
            handler_path = [["M", start_x, start_y], ["L", from_handler_x, from_handler_y], ["M", end_x, end_y], ["L", to_handler_x, to_handler_y]];
        }else{
            handler_path =  custom_handler_path;
            from_handler_x = custom_handler_path[1][1];
            from_handler_y = custom_handler_path[1][2];
            to_handler_x = custom_handler_path[3][1];
            to_handler_y = custom_handler_path[3][2];
        }

        canvasmap[pid]['drawopts'][legend] = {type: 'curve',
            start_x:start_x, start_y:start_y,
            end_x:end_x, end_y:end_y, color:colormap[pid],
            custom_path:curve_path, custom_handler_path:handler_path,
            rcoordinate:getrcoordinate(curve_path)
        }

        var controls = paper.set(
                paper.path(curve_path).attr({stroke: color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
                paper.path(handler_path).attr({stroke: "#996600", "stroke-dasharray": ". "}).data("what", 'handler_path'),
                paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
                paper.circle(from_handler_x, from_handler_y, 5).attr(discattr).data("what", 'circle'),
                paper.circle(to_handler_x, to_handler_y, 5).attr(discattr).data("what", 'circle'),
                paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
                paper.text(curve_path[1][5]+50,curve_path[1][6], legend).attr({'font-size': '15px'}).data("what", 'text').hide(),
                paper.rect(Raphael.pathBBox(curve_path).x, Raphael.pathBBox(curve_path).y, Raphael.pathBBox(curve_path).width, Raphael.pathBBox(curve_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );

        controls[0].update = function (x, y) {
            //console.log("path update");
            controls[2].update(x, y);
        };
        controls[2].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[0][1] = newX;
            curve_path[0][2] = newY;
            handler_path[0][1] = newX;
            handler_path[0][2] = newY;
            controls[3].update(x, y);
            controls[5].update(x, y);
            var bb = Raphael.pathBBox(curve_path);
            controls[7].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['start_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['start_y'] = newY;
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
        };

        controls[3].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[1][1] = newX;
            curve_path[1][2] = newY;
            handler_path[1][1] = newX;
            handler_path[1][2] = newY;
            controls[0].attr({path: curve_path});
            controls[1].attr({path: handler_path});
            var bb = Raphael.pathBBox(curve_path);
            controls[7].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
        };
        controls[4].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[1][3] = newX;
            curve_path[1][4] = newY;
            handler_path[3][1] = newX;
            handler_path[3][2] = newY;
            controls[0].attr({path: curve_path});
            controls[1].attr({path: handler_path});
            var bb = Raphael.pathBBox(curve_path);
            controls[7].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
        };
        controls[5].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            curve_path[1][5] = newX;
            curve_path[1][6] = newY;
            handler_path[2][1] = newX;
            handler_path[2][2] = newY;
            controls[4].update(x, y);
            controls[6].attr({x:newX+50, y:newY});
            var bb = Raphael.pathBBox(curve_path);
            controls[7].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['end_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['end_y'] = newY;
            canvasmap[pid]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[pid]['drawopts'][legend]['custom_handler_path'] = handler_path;
        };
        controls[7].update = function (x, y) {
            controls[2].update(x, y);
            var bb = Raphael.pathBBox(curve_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };

        controls[2].drag(move, start, end);
        controls[3].drag(move, start, end);
        controls[4].drag(move, start, end);
        controls[5].drag(move, start, end);
        controls[7].drag(move, start, end);
        controls[2].update(0, 0);
        elemap[pid].push(controls);
    }

    function drawLine(pid, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[pid];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x, end_y, line_path;
        if(drawopts['horizontal']){
            end_x = axisorigin['start_x'];
            end_y = drawopts['start_y'];
        }else if(drawopts['vertical']){
            end_x = drawopts['start_x'];
            end_y = axisorigin['start_y'];
        }else{
            end_x = drawopts['end_x'];
            end_y = drawopts['end_y'];
        }

        if (drawopts['custom_path'] === null){
            line_path = [["M", start_x, start_y], ["L", end_x, end_y]];
        }else{
            line_path = drawopts['custom_path'];
        }

        canvasmap[pid]['drawopts'][legend] = {
            type: 'line', color:colormap[pid], dashline:drawopts['dashline'],
            vertical:drawopts['vertical'], horizontal:drawopts['horizontal'],
            start_x:start_x, start_y:start_y,
            end_x:end_x, end_y:end_y,
            custom_path:null, custom_handler_path:null,
            'rcoordinate':getrcoordinate(line_path)
        }

        var controls = paper.set();

        if (drawopts['dashline']){
            controls.push(
                paper.path().attr({path: line_path, stroke: color || Raphael.getColor(), fill: "#00CCCC", "fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'path')
            );
        }else{
            controls.push(
                paper.path().attr({path: line_path, stroke: color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path')
            );
        }

        if(drawopts['horizontal']){
            canvasmap[pid]['drawopts'][legend].type = 'axis-dashline';
            controls.push(
                paper.circle(start_x, start_y, 5).attr(discattr_intersect).data("what", 'dot'),
                paper.circle(end_x, end_y, 5).attr(discattr_intersect).data("what", 'horizontal'),
                paper.text(line_path[1][1]+50, line_path[1][2]-10, legend).attr({'font-size': '15px'}).data("what", 'text'));
        }else if (drawopts['vertical']){
            canvasmap[pid]['drawopts'][legend].type = 'axis-dashline';
            controls.push(
                paper.circle(start_x, start_y, 5).attr(discattr_intersect).data("what", 'dot'),
                paper.circle(end_x, end_y, 5).attr(discattr_intersect).data("what", 'vertical'),
                paper.text(line_path[1][1]+50, line_path[1][2]-10, legend).attr({'font-size': '15px'}).data("what", 'text'));
        }else{
            controls.push(
                paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
                paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
                paper.text(line_path[1][1]+50, line_path[1][2]-10, legend).attr({'font-size': '15px'}).data("what", 'text').hide());
        }

        controls.push(
            paper.rect(Raphael.pathBBox(line_path).x, Raphael.pathBBox(line_path).y, Raphael.pathBBox(line_path).width, Raphael.pathBBox(line_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );

        controls[0].update = function (x, y) {
            controls[1].update(x, y);
        };

        controls[1].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            line_path[0][1] = newX;
            line_path[0][2] = newY;
            controls[2].update(x, y);
            var bb = Raphael.pathBBox(line_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['start_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['start_y'] = newY;
            //controls[4].update(x, y);
        };

        controls[2].update = function (x, y) {
            var newX, newY;
            if( drawopts['horizontal']){
                newX = this.attr("cx");
                newY = this.attr("cy") + y;
            }else if(drawopts['vertical']){
                newX = this.attr("cx") + x;
                newY = this.attr("cy");
            }else{
                newX = this.attr("cx") + x;
                newY = this.attr("cy") + y;
            }
            this.attr({cx: newX, cy: newY});
            line_path[1][1] = newX;
            line_path[1][2] = newY;
            controls[0].attr({path: line_path});
            controls[3].attr({x:newX+50, y:newY-10});
            var bb = Raphael.pathBBox(line_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[pid]['drawopts'][legend]['end_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['end_y'] = newY;
            //controls[4].update(x, y);
        };

        controls[4].update = function (x, y) {
            controls[1].update(x, y);
            var bb = Raphael.pathBBox(line_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };

        controls[1].drag(move, start, end);
        if(!drawopts['horizontal'] && !drawopts['vertical']){
            controls[2].drag(move, start, end);
        }
        controls[4].drag(move, start, end);
        controls[1].update(0, 0);
        elemap[pid].push(controls);
    }

    function drawDot(pid, drawopts) {
        var legend = drawopts['legend'];
        var paper = instmap[pid];
        var discattr_drag = {fill: "#993300", stroke: "none"};
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x = drawopts['end_x'];
        var end_y = drawopts['end_y'];

        canvasmap[pid]['drawopts'][legend] = {
            type: 'dot',
            start_x:start_x, start_y:start_y,
            end_x:null, end_y:null, color:colormap[pid],
            custom_path:null, custom_handler_path:null,
            rcoordinate:null
        }

        var controls = paper.set(
                paper.circle(start_x, start_y, 6).attr(discattr_drag).data("what", 'dot'),
                paper.text(start_x+50, start_y+15, legend).attr({'font-size': '15px'}).data("what", 'dottext')
        );

        controls[0].update = function (x, y){
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            controls[1].attr({x: newX+50, y: newY+15});
            this.toFront();
            canvasmap[pid]['drawopts'][legend]['start_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['start_y'] = newY;
            controls[1].toFront();
        };
        controls[0].drag(move, start, end);
        elemap[pid].push(controls);
    }

    function drawTips(pid, drawopts) {
        var legend = drawopts['legend'];
        var paper = instmap[pid];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x = drawopts['end_x'];
        var end_y = drawopts['end_y'];

        canvasmap[pid]['drawopts'][legend] = {
            type: 'tips',
            start_x:start_x, start_y:start_y,
            end_x:null, end_y:null, color:colormap[pid],
            custom_path:null, custom_handler_path:null,
            rcoordinate:null
        }

        var controls = paper.set();

        controls.push(
                paper.text(start_x, start_y, legend).attr({'font-size': '15px'}).data("what", 'tipstext')
        );

        var text_bbox = controls[0].getBBox();

        controls.push(
                paper.rect(text_bbox.x, text_bbox.y, text_bbox.width, text_bbox.height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );

        controls[0].update = function (x, y){
            var newX = this.attr("x") + x;
            var newY = this.attr("y") + y;
            this.attr({x: newX, y: newY});
            canvasmap[pid]['drawopts'][legend]['start_x'] = newX;
            canvasmap[pid]['drawopts'][legend]['start_y'] = newY;
        };

        controls[1].update = function (x, y){
            var newX = this.attr("x") + x;
            var newY = this.attr("y") + y;
            this.attr({x: newX, y: newY});
            controls[0].update(x, y);
        };

        controls[1].drag(move, start, end);
        elemap[pid].push(controls);
    }


    function move(dx, dy) {
        if (this.data('what')=='area')
            this.attr({stroke: "#0000FF", "stroke-dasharray": "--."});
        mousemoveCounter += 1;
        if (mousemoveCounter%5 != 0)
            return false;
        var bb = this.getBBox();
        var width = attributes.width;
        var height = attributes.height;
        if (bb.x >= 0 && bb.y >= 0 && bb.x2 <= width && bb.y2 <= height){
            this.update(dx - (this.dx || 0), dy - (this.dy || 0));
            this.dx = dx;
            this.dy = dy;
        }
    }

    function start() {
        var animObject = null;
        if (this.data('what') === 'dot' || this.data('what') === 'circle'){
            function closeAnimate(target){
                target.animate({fill: "#993300", r:6},1000, 'bounce');
            }
            if (this.data('what') === 'dot'){
                animObject = Raphael.animation({ fill: "#FF9933", r:9 }, 1000, 'elastic',function(){});
            }else{
                animObject = Raphael.animation({ r:9 }, 1000, 'elastic',function(){});
            }
            this.animate(animObject);
        }
        if (this.data('what') === 'area'){
            this.attr({stroke: "#0000FF", "stroke-dasharray": "--."});
        }
        this.dx = this.dy = 0;
    }

    function end(){
        var animObject = null;
        if (this.data('what') === 'dot' || this.data('what') === 'circle'){
            if (this.data('what') === 'dot'){
                animObject = Raphael.animation({ r:6, fill: "#993300" }, 1000, 'bounce',function(){});
                var paper = this.paper;
                var path_list = [];
                paper.forEach(function(el){
                    if(el.data("what")=='path') path_list.push(el);
                });
                console.log(path_list);
                var moveend_x = null;
                var moveend_y = null;
                var min_dist_x = 25;
                var min_dist_y = 25;
                for(var i = 0; i < path_list.length; i+=1){
                    for(var j = i+1; j < path_list.length; j+=1){
                       var intersect_dot = Raphael.pathIntersection(path_list[i].attr('path'), path_list[j].attr('path'));
                       for(var k = 0; k < intersect_dot.length; k+=1){
                           var inter_x = intersect_dot[k].x;
                           var inter_y = intersect_dot[k].y;
                           var dist_x = Math.abs(inter_x-this.attr('cx'));
                           var dist_y = Math.abs(inter_y-this.attr('cy'));
                           if(dist_x<=25 && dist_y<=25){
                                if(dist_x<=min_dist_x && dist_y<=min_dist_y){
                                    path_list[i].toBack();
                                    path_list[j].toBack();
                                    min_dist_x = dist_x;
                                    min_dist_y = dist_y;
                                    moveend_x = inter_x;
                                    moveend_y = inter_y;
                                }
                           }
                       }
                    }
                }
                if(moveend_x !== null && moveend_y !== null){
                    this.attr({cx:moveend_x, cy:moveend_y});
                    if (this.next.data("what") === 'horizontal'){
                            this.next.attr({cy:moveend_y});
                    }
                    else if(this.next.data("what") === 'vertical'){
                            this.next.attr({cx:moveend_x});
                    }
                }
            }else{
                 animObject = Raphael.animation({ r:5 }, 1000, 'bounce',function(){});
            }
            this.animate(animObject);
        }

        if (this.data('what') === 'area')
            this.attr({stroke: "#996699", "stroke-dasharray": ". "});
        //this.update(-100, -100);
        var width = attributes.width;
        var height = attributes.height;
        var bb = this.getBBox();
        var moveend_x = 0;
        var moveend_y = 0;
        if (bb.x <= 0)
            moveend_x = -bb.x+3;
        if (bb.y <= 0)
            moveend_y = -bb.y+3;
        if (bb.x2 >= width)
            moveend_x = width-bb.x2-3;
        if (bb.y2 >= height)
            moveend_y = height-bb.y2-3;
        this.update(moveend_x, moveend_y);
        //this.dx = this.dy = 0;
    }

    function drawAxis(pid, axis){
        if (axis['direction'] === '0' && axismap[pid][0]){
           // console.log('horizontal axis already exist');
            delete canvasmap[pid]['axis']['x'];
            axismap[pid][0].remove();
            delete axismap[pid][0];
        }
        if (axis['direction'] === '1' && axismap[pid][1]){
            //console.log('vertical axis already exist');
            delete canvasmap[pid]['axis']['y'];
            axismap[pid][1].remove();
            delete axismap[pid][1];
        }
        var paper = instmap[pid];
        var axis_path = undefined;
        var axislegend = axis['name'] + '(' + axis['unit'] + ')';
        var start_x = axisorigin['start_x'];
        var start_y = axisorigin['start_y'];
        var arrow_length = 16;
        var mini_height = 3;
        var mini_width = 1;
        var idx = 0;
        var axisset = paper.set();
        var axistext;
        var step;
        // horizontal axis
        if (axis['direction'] === '0'){
            canvasmap[pid]['axis']['x'] = axis;
            var end_x = attributes.width - 60;
            step =  Math.round((end_x - start_x - axis['splits'] - arrow_length)/ axis['splits']);
            axis_path = [["M", start_x, start_y]];
            axisset.push(paper.text(start_x, start_y + 10, axis['start']));
            for (idx = 0; idx < axis['splits']; idx += 1){
                axis_path = axis_path.concat([["l", step, 0]],[["v", -mini_height]],[["h", mini_width]],[["v", mini_height]]);
                axistext = Number(axis['start']) + ((axis['end'] - axis['start'])/axis['splits']) * (idx + 1);
                axisset.push(paper.text(start_x + (idx+1) * step, start_y + 10, axistext.toFixed(2)));
            }
            axis_path = axis_path.concat(
                    [["l", arrow_length, 0]],
                    [["v", -(2*mini_height)]],
                    [["l", arrow_length/2, 2*mini_height]],
                    [["l", -(arrow_length/2), 2*mini_height]],
                    [["v", -(2*mini_height)]]);
            axisset.push(paper.text((end_x - start_x)/2 + 20, start_y + 25, axislegend).attr({"font-size":16}));
            axisset.push(paper.path(axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
            axismap[pid][0] = axisset;
        }else{
            // vertical axis
            canvasmap[pid]['axis']['y'] = axis;
            var end_y = 50;
            step =  Math.round((start_y - end_y - axis['splits'] - arrow_length)/ axis['splits']);
            axis_path = [["M", start_x, start_y]];
            axisset.push(paper.text(start_x-15, start_y-4, axis['start']));
            for (idx = 0; idx < axis['splits']; idx += 1){
                axis_path = axis_path.concat([["l",0,-step]],[["h",mini_height]],[["v",-mini_width]],[["h",-mini_height]]);
                axistext = Number(axis['start']) + ((axis['end'] - axis['start'])/axis['splits']) * (idx+1);
                axisset.push(paper.text(start_x-15, start_y-(idx+1)*step-4, axistext.toFixed(2)));
            }
            axis_path = axis_path.concat(
                    [["v", -(arrow_length)]],
                    [["h", 2*mini_height]],
                    [["l", -(2*mini_height), -(arrow_length/2)]],
                    [["l", -(2*mini_height), arrow_length/2]],
                    [["h", 2*mini_height]]);
            axisset.push(paper.text(start_x-40, (start_y-end_y)/2+10, axislegend).attr({"font-size":16}));
            axisset.push(paper.path(axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
            axismap[pid][1] = axisset;
        }
    }

    function drawSelectionArea(parent,x1,y1,x2,y2){
        //console.log('draw selectionArea | x1:'+x1+',y1:'+y1+',x2:'+x2+',y2:'+y2);
        var pid = $(parent).attr('id');
        var paper = instmap[pid];
        var start_x,start_y,selection_width,selection_height;
        if (x1 < x2){
            start_x = x1;
            selection_width = x2 - x1;
        }else{
            start_x = x2;
            selection_width = x1 - x2;
        }
        if (y1 < y2){
            start_y = y1;
            selection_height = y2 - y1;
        }else{
            start_y = y2;
            selection_height = y1 - y2;
        }
        if (curSelectionArea){
            curSelectionArea.attr({x:start_x,y:start_y,width:selection_width,height:selection_height});
        }else{
            curSelectionArea = paper.rect(start_x,start_y,selection_width,selection_height).attr({fill:"#aaa",stroke:"#eee",opacity:0.3});
        }
    }

    // exchange start and end point to ensure little one on the left
    function normalizepoint(area){
        var lx = area[0];
        var ly = area[1];
        var bx, by;
        if (area[2] <= area[0]){
            lx = area[2];
            bx = area[0];
        }else{
            bx = area[2];
        }
        if (area[3] <= area[1]){
            ly = area[3];
            by = area[1];
        }else{
            by = area[3];
        }
        return {'x':lx, 'y':ly, 'x2':bx, 'y2':by};
    }

    function isdotinselectedarea(pointset, area){
        var bound = normalizepoint(area);
        var cx, cy;
        if (pointset.hasOwnProperty('x')){
            cx = pointset['x'];
            cy = pointset['y'];
        }else {
            cx = pointset.attr('cx');
            cy = pointset.attr('cy');
        }
        if (cx >= bound['x'] && cx <= bound['x2'] && cy >= bound['y'] && cy <= bound['y2']){
            return true;
        }else{
            return false;
        }
    }

    function ispathinselectedarea(curveset, area){
        if(area.length === 0)
            return true;
        var path = curveset.attr('path');
        var box = Raphael.pathBBox(path);
        var bound = normalizepoint(area);
        //box: x,y,x2,y2  area:x, y, x2, y2
        if ((box['x'] > bound['x'] && box['x'] < bound['x2'] && box['y'] > bound['y'] && box['y'] < bound['y2'])
                && (box['x2'] > bound['x'] && box['x2'] < bound['x2'] && box['y2'] > bound['y'] && box['y2'] < bound['y2'])){
            return true;
        }else{
            return false;
        }
    }

    function getcurveintesectpoint(pid, c1, c2, area){
        var c1_elem = c1['elem'];
        var c2_elem = c2['elem'];
        var c1_path = c1_elem[c1_elem.length-1]['location'];
        var c2_path = c2_elem[c2_elem.length-1]['location'];
        if (area.length === 0){
            var bound = Raphael.pathBBox(c1_path);
            area = [bound['x'],bound['y'],bound['x2'],bound['y2']];
        }
        var dot = Raphael.pathIntersection(c1_path, c2_path);
        if ( dot.length > 0){
            return dot;
        }
        return false;
    }

    function getrelativesize(cx, cy, box){
        var x = box['x'], y = box['y'], x2 = box['x2'], y2 = box['y2'];
        var width = box['width'], height = box['height'];
        return [(cx - x)/ width, (cy - y)/ height];
    }

    function typeofpath(path){
        if(path.length === 4){
            return 'complexcurve';
        }else{
            if(path[1][0] === 'L'){
                return 'line';
            }else if(path[1][0] === 'C'){
                return 'curve';
            }
        }
    }

    function getrcoordinate(path){
        var box = Raphael.pathBBox(path);
        if (typeofpath(path) === 'complexcurve'){
            return [getrelativesize(path[0][1],path[0][2], box), getrelativesize(path[1][1], path[1][2], box),
                   getrelativesize(path[3][3],path[3][4], box), getrelativesize(path[3][5], path[3][6], box),
                   getrelativesize(path[2][1], path[2][2], box), getrelativesize(path[1][5], path[1][6], box),
                   getrelativesize(path[3][1], path[3][2], box)];
        }else if (typeofpath(path) === 'curve'){
            return [getrelativesize(path[1][1], path[1][2], box), getrelativesize(path[1][3], path[1][4], box),
                    getrelativesize(path[0][1], path[0][2], box), getrelativesize(path[1][5], path[1][6], box)];
        }else if (typeofpath(path) === 'line'){
            return [[0,0], [1,1]];
        }
    }

    function getcurvepath(curve){
        var c_elem = curve['elem'];
        var c_path = c_elem[c_elem.length-1]['location'];
        return Raphael.pathBBox(c_path);
    }

    function curvecompare3p(pid, c1, c2){
        if (getcurveintesectpoint(pid, c1, c2, [])){
            return 'Intersect';
        }else{
            var c1_pathbox = getcurvepath(c1);
            var c2_pathbox = getcurvepath(c2);
            if ((c1_pathbox['y'] + c1_pathbox['height']/2) > (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) < (c2_pathbox['x'] + c2_pathbox['width']/2))){
                return 'Below';
            }else if ((c1_pathbox['y'] + c1_pathbox['height']/2) < (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) > (c2_pathbox['x'] + c2_pathbox['width']/2))){
                return 'Above';
            }else{
                return 'Undefined';
            }
        }
        return rule;
    }

    function curvecompare2p(pid, c1, c2){
        if (getcurveintesectpoint(pid, c1, c2, [])){
            return 'Intersect';
        }else{
            var c1_pathbox = getcurvepath(c1);
            var c2_pathbox = getcurvepath(c2);
            if ((c1_pathbox['y'] + c1_pathbox['height']/2) > (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) < (c2_pathbox['x'] + c2_pathbox['width']/2))){
                return 'Below';
            }else if ((c1_pathbox['y'] + c1_pathbox['height']/2) < (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) > (c2_pathbox['x'] + c2_pathbox['width']/2))){
                return 'Above';
            }else{
                return 'Undefined';
            }
        }
        return rule;
    }

    function curvecompare2_3p(pid, c1, c2){
        if (getcurveintesectpoint(pid, c1, c2, [])){
            return 'Intersect';
        }else{
            var c1_pathbox = getcurvepath(c1);
            var c2_pathbox = getcurvepath(c2);
            if ((c1_pathbox['y'] + c1_pathbox['height']/2) > (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) < (c2_pathbox['x'] + c2_pathbox['width']/2))){
                return 'Below';
            }else if ((c1_pathbox['y'] + c1_pathbox['height']/2) < (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) > (c2_pathbox['x'] + c2_pathbox['width']/2))){
                return 'Above';
            }else{
                return 'Undefined';
            }
        }
    }

    function generatecurverule(relation, c1, c2){
        var rules = [];
        if (relation === 'Undefined'){
            rules.push([ c1['legend'] + "(" + c1['type'] + ") ",
                    'Above ',
                    c2['legend'] + "(" + c2['type'] + ") "]);
            rules.push([ c1['legend'] + "(" + c1['type'] + ") ",
                    'Below ',
                    c2['legend'] + "(" + c2['type'] + ") "]);
        }else{
            rules.push([ c1['legend'] + "(" + c1['type'] + ") ",
                    relation + " ",
                    c2['legend'] + "(" + c2['type'] + ") "]);
        }
        return rules;
    }

    function getcurverules(pid, c1, c2){
        var rules = [];
        if (c1['type'] === 'complexcurve' && c2['type'] === 'complexcurve'){
            relation = curvecompare3p(pid, c1, c2);
            rules = generatecurverule(relation, c1, c2);
        }else if (c1['type'] !== 'complexcurve' && c2['type'] !== 'complexcurve'){
            relation = curvecompare2p(pid, c1, c2);
            rules = generatecurverule(relation, c1, c2);
        }else{
            if (c1['type'] !== 'complexcurve' && c2['type'] === 'complexcurve'){
                relation = curvecompare2_3p(pid, c1, c2);
                rules = generatecurverule(relation, c1, c2);
            }else{
                relation = curvecompare2_3p(pid, c2, c1);
                rules = generatecurverule(relation, c2, c1);
            }
        }
        return rules;
    }

    function dotcompare(p1, p2){
        var rule = [];
        if (Math.abs(p1['location'][0] -  p2['location'][0]) < 8
                && Math.abs(p1['location'][1] -  p2['location'][1]) < 8){
            rule.push('Coincide');
        }else{
            if (Math.abs(p1['location'][0] -  p2['location'][0]) > 8){
                if (p1['location'][0] < p2['location'][0]){
                    rule.push('Left');
                }else if (p1['location'][0] > p2['location'][0]){
                    rule.push('Right');
                }
            }
            if (Math.abs(p1['location'][1] -  p2['location'][1]) > 8){
                if (p1['location'][1] < p2['location'][1]){
                    rule.push('Above');
                }else if (p1['location'][1] > p2['location'][1]){
                    rule.push('Below');
                }
            }
        }
        return rule;
    }

    function getpointrules(pid, c1, c2){
        var rules = [];
        var rulelang;
        //only compare points : last one (path) don't need compare
        for (var i = 0; i < c1['elem'].length - 1; i+=1){
            for (var j = 0; j < c2['elem'].length - 1; j+=1){
                rulelang = [c1['legend'] + "(" + c1['type'] + ")[" + c1['elem'][i]['name'] + "] ",
                    dotcompare(c1['elem'][i], c2['elem'][j]) + " ",
                        c2['legend'] + "(" + c2['type'] + ")[" + c1['elem'][i]['name'] + "] "];
                rules.push(rulelang);
            }
        }
        return rules;
    }

    function ispointinsidecurve(dot, curve){
        var pathindex = curve['elem'].length - 1;
        var path = curve['elem'][pathindex]['location'];
        var dot_x = dot['elem'][0]['location'][0];
        var dot_y = dot['elem'][0]['location'][1];
        var curvelegend = curve['legend'];
        if (Raphael.isPointInsidePath(path, dot_x, dot_y) || foundintesectpoint(curvelegend, dot_x, dot_y)){
            return true;
        }else{
            return false;
        }
    }

    function foundintesectpoint(curvelegend, dot_x, dot_y){
        //console.error(dot_x, dot_y);
        for (var i = 0; i < intesectmatrix.length; i+=1){
            var row = intesectmatrix[i];
            for (var j = 0; j < row.length; j+=1){
                //legend name of intesectmatrix
                if(curvelegend === row[j][0] || curvelegend === row[j][1]){
                    var intesectpoints = row[j][2];
                    if(intesectpoints.length > 0){
                        for(var k = 0; k < intesectpoints.length; k+=1){
                            if (Math.abs(dot_x - intesectpoints[k]['x']) < 8
                                    && Math.abs(dot_y - intesectpoints[k]['y']) < 8){
                                return true;
                            }
                        }
                    }else if(intesectpoints){
                        if (Math.abs(dot_x - intesectpoints['x']) < 8
                                && Math.abs(dot_y - intesectpoints['y']) < 8){
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }

    function getdotrules(pid, c1, c2, area){
        var rules = [];
        var dot, curve;
        if (c1['type'] === 'dot' && c2['type'] === 'dot'){
            rules.push([c1['legend'] + "(" + c1['type'] + ") ",
                dotcompare(c1['elem'][0], c2['elem'][0]) + " ",
                c2['legend'] + "(" + c2['type'] + ") "]);
            return rules;
        }else if(c1['type'] === 'dot'){
           dot = c1;
           curve = c2;
        }else{
           dot = c2;
           curve = c1;
        }
        if(ispointinsidecurve(dot, curve)){
            rules.push([dot['legend'] + "(" + dot['type'] + ") ", "On ",
            curve['legend'] + "(" + curve['type'] + ") "]);
        }else{
            for (var i = 0, elemlength = curve['elem'].length - 1;  i < elemlength; i  +=  1){
                rules.push([dot['legend'] + "(" + dot['type'] + ") ",
                dotcompare(dot['elem'][0], curve['elem'][i]) + " ",
                curve['legend'] + "(" + curve['type'] + ")[" + curve['elem'][i]['name'] + "] "]);
            }
        }
        return rules;
    }

    function getaxisrules(curve){
        var rules = [];
        var dot;
        if (curve['type'] === 'dot'){
            dot = curve['elem'][0];
            if(dotaxiscompare(dot)){
                rules.push(curve['legend'] + '(' + curve['type'] + ') ',
                    'On ', dotaxiscompare(dot) + ' ');
            }
        }else{
            for (var i = 0, dotcount = curve['elem'].length - 1; i < dotcount; i+=1){
                dot = curve['elem'][i];
                if(dotaxiscompare(dot)){
                    rules.push(curve['legend'] + '(' + curve['type'] + ')[' + dot['name'] + '] ',
                        'On ', dotaxiscompare(dot) + ' ');
                }
            }
        }
        return rules;
    }

    function dotaxiscompare(dot){
        if (dot['location'][0] === axisorigin['start_x'] && dot['location'][1] === axisorigin['start_y']){
            return 'coordinate origin';
        }else if(dot['location'][0] === axisorigin['start_x']){
            return 'y-axis';
        }else if(dot['location'][1] === axisorigin['start_y']){
            return 'x-axis';
        }else{
            return;
        }
    }

    function getcomplexcurveelem(elset, area){
        var complexcurveelem;
        var legend = getlegendofelset(elset);
        complexcurveelem = {'type':'complexcurve','legend':legend, 'elem':[]};
        if (isdotinselectedarea(elset[2], area)){
            complexcurveelem['elem'].push({'name':'Start','location':[elset[2].attr('cx'),elset[2].attr('cy')]});
               // console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[5], area)){
            complexcurveelem['elem'].push({'name':'End','location':[elset[5].attr('cx'),elset[5].attr('cy')]});
            //console.log('end in selectarea');
        }
        if (isdotinselectedarea(elset[6], area)){
            complexcurveelem['elem'].push({'name':'Middle','location':[elset[6].attr('cx'),elset[6].attr('cy')]});
            //console.log('middle in selectarea');
        }
        complexcurveelem['elem'].push({'name':'Path','location': elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            complexcurveelem['complete'] = true;
        }else{
            complexcurveelem['complete'] = false;
        }
        return complexcurveelem;
    }

    function getcurveelem(elset, area){
        var curveelem;
        var legend = getlegendofelset(elset);
        curveelem = {'type':'curve','legend':legend, 'elem':[]};
        if (isdotinselectedarea(elset[2], area)){
            curveelem['elem'].push({'name':'Start','location':[elset[2].attr('cx'),elset[2].attr('cy')]});
 //           console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[5], area)){
            curveelem['elem'].push({'name':'End','location':[elset[5].attr('cx'),elset[5].attr('cy')]});
   //         console.log('end in selectarea');
        }
        curveelem['elem'].push({'name':'Path','location':elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            curveelem['complete'] = true;
        }else{
            curveelem['complete'] = false;
        }
        return curveelem;
    }

    function getlineelem(elset, area){
        var lineelem;
        var legend = getlegendofelset(elset);
        lineelem = {'type':'line','legend':legend, 'elem':[]};
        if (isdotinselectedarea(elset[1], area)){
            lineelem['elem'].push({'name':'Start','location':[elset[1].attr('cx'),elset[1].attr('cy')]});
     //       console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[2], area)){
            lineelem['elem'].push({'name':'End','location':[elset[2].attr('cx'),elset[2].attr('cy')]});
       //     console.log('end in selectarea');
        }
        lineelem['elem'].push({'name':'Path','location':elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            lineelem['complete'] = true;
        }else{
            lineelem['complete'] = false;
        }
        return lineelem;
    }

    function getdotelem(elset, area){
        var dotelem, elem = [];
        var legend = getlegendofelset(elset);
        if(isdotinselectedarea(elset[0], area)){
         //   console.log('dot in selectarea');
            elem.push({'name':'Dot','location':[elset[0].attr('cx'),elset[0].attr('cy')]});
            dotelem = {'type':'dot', 'legend':legend, 'elem':elem, 'complete':false};
        }
        return dotelem;
    }

    function getcurveelemlist(elset, area){
        switch (typeofelset(elset)){
            case 'complexcurve':
                return getcomplexcurveelem(elset, area);
                break;
            case 'curve':
                return getcurveelem(elset, area);
                break;
            case 'line':
                return getlineelem(elset, area);
                break;
            case 'line':
                return getlineelem(elset, area);
                break;
            case 'dot':
                return getdotelem(elset, area);
                break;
            default:
                return;
        }
    }

    function getintesectmatrix(pid, curveelemlist, area){
        for (var i = 0 ; i < curveelemlist.length; i++){
            var intesect_row = [];
            for( var j = 0; j < i; j++){
                var intesectpoint = getcurveintesectpoint(pid, curveelemlist[i], curveelemlist[j], area);
                if(intesectpoint){
                    intesect_row.push([curveelemlist[i]['legend'], curveelemlist[j]['legend'], intesectpoint]);
                }
            }
            if(intesect_row.length > 0){
                intesectmatrix.push(intesect_row);
            }
        }
        return intesectmatrix;
    }


    function calculateRules(thiscanvas,x1,y1,x2,y2){
        //calculate all points rules in this function
       // console.log("calculateRules | x1:"+x1+",y1:"+y1+",x2:"+x2+",y2:"+y2);
        var area = [x1, y1, x2, y2];
        var elist = elemap[thiscanvas];
        var curveelemlist = [];
        var rulelist = [];

        //there should be two kinds of relationship of rule.
        //1, curve and curve(I don't think curve and point is useful)
        //2, circle and circle(start,middle,end point)
        elist.forEach(function(elset){
            var curveelem = getcurveelemlist(elset, area);
            if (curveelem){
                curveelemlist.push(curveelem);
            }
        });

        //generate intesectpoints to help fuzzy intesect check
        intesectmatrix = getintesectmatrix(thiscanvas, curveelemlist, area);

        //generate rules according to curveelemlist
        for (var i = 0 ; i < curveelemlist.length; i++){
            for( var j = 0; j < i; j++){
                var rules = [];
                if (curveelemlist[i]['complete'] === true && curveelemlist[j]['complete'] === true){
         //           console.log('curve analysis');
                    if(curveelemlist[i]['legend'] < curveelemlist[j]['legend'])
                        rules = getcurverules(thiscanvas, curveelemlist[i], curveelemlist[j]);
                    else{
                        rules = getcurverules(thiscanvas, curveelemlist[j], curveelemlist[i]);
                    }
                }else if (curveelemlist[i]['type'] !== 'dot' && curveelemlist[j]['type'] !== 'dot'){
           //         console.log('curve point analysis');
                    if(curveelemlist[i]['legend'] < curveelemlist[j]['legend'])
                        rules = getpointrules(thiscanvas, curveelemlist[i], curveelemlist[j]);
                    else{
                        rules = getpointrules(thiscanvas, curveelemlist[j], curveelemlist[i]);
                    }
                }else if (curveelemlist[i]['type'] === 'dot' || curveelemlist[j]['type'] === 'dot'){
             //       console.log('dot-curve analysis');
                    rules = getdotrules(thiscanvas, curveelemlist[i], curveelemlist[j], area);
                }
                for(var ri = 0; ri < rules.length; ri += 1){
                    rulelist.push(rules[ri]);
                }
            }
            var axisrule = getaxisrules(curveelemlist[i]);
            if (axisrule.length > 0){
                rulelist.push(axisrule);
            }
        }
        return rulelist;
    }

    function listRules(thiscanvas, rulelist){
        if (!isobjectnull(rulelist)){
            var ruletable = '#list' + thiscanvas;
            $(ruletable).css('display','table-cell');
            $(ruletable + ' thead tr').remove();
            $(ruletable + ' thead a').remove();
            $(ruletable + ' thead').append("<tr><th class='intemasscanvas-table'> Curve(Type)[Point]  </th><th class='intemasscanvas-table'> Relation  </th><th class='intemasscanvas-table'> Curve(Type)[Point]</th></tr>");
            $(ruletable + ' tbody tr').remove();
            for (var i = 0; i < rulelist.length; i += 1){
                for(var j = 0; j < 3; j += 1){
                    rulelist[i][j] = rulelist[i][j].replace(' ', '');
                }
                $(ruletable + ' tbody').append("<tr><td>" + rulelist[i][0] +"</td><td>" + rulelist[i][1] +"</td><td>" + rulelist[i][2] + "</td></tr>");
            }
            canvasmap[thiscanvas]['rulelist'] = rulelist;
        }
    }

    function IntemassCanvasGet(thiscanvas, csrfvalue){
        $.post('/canvas/get/',{'questionid':'1', 'csrfmiddlewaretoken':csrfvalue},
            function(payload){
                if (payload['state'] === 'success'){
                    var elem, type, canvas;
                    canvasmap = payload['canvasmap'];
                    for(var canvasname in canvasmap){
                        if (canvasname === thiscanvas){
                            canvas = canvasmap[canvasname];
                            for(var axisname in canvas['axis']){
                                axis = canvas['axis'][axisname];
                                drawAxis(canvasname, axis);
                            }
                            var canvas_list = [];
                            for(var legend in canvas['drawopts']){
                                global_legends.push(legend + ':' + canvasname);
                                var drawopts = canvas['drawopts'][legend];
                                drawopts['legend'] = legend;
                                canvas_list.push(drawopts);
                            }
                            var sort_canvas = function(obj1,obj2) {
                                if(obj1.type==='dot')
                                    return true;
                                if(obj1.type==='axis-dashline')
                                    return true;
                                //return  obj1.type - obj2.type;
                            }
                            console.log(canvas_list.sort(sort_canvas));
                            canvas_list = canvas_list.sort(sort_canvas);
                            for(var i in canvas_list){
                                console.log(canvas_list[i]);
                                var drawopts = canvas_list[i];
                                var type = drawopts['type'];
                                switch(type){
                                    case 'dot':
                                        drawDot(canvasname, drawopts);
                                        break;
                                    case 'line':
                                        drawLine(canvasname, drawopts);
                                        break;
                                    case 'axis-dashline':
                                        drawLine(canvasname, drawopts);
                                        break;
                                    case 'curve':
                                        drawCurve(canvasname, drawopts);
                                        break;
                                    case 'complexcurve':
                                        drawComplexCurve(canvasname, drawopts);
                                        break;
                                    case 'tips':
                                        drawTips(canvasname, drawopts);
                                        break;
                                    default:
                                        break;
                                }
                            }
                            listRules(canvasname, canvas['rulelist']);
                        }
                        var $viewBtn = $("#" + thiscanvas + "-viewBtn");
                        $viewBtn.trigger('click');
                        $viewBtn.next().addClass('ui-state-active');
                        $viewBtn.attr('checked', true);
                    }
                }
            }, 'json');
    }

    function isobjectnull(Obj){
        for(var name in Obj){
            if (Obj.hasOwnProperty(name))
            {
                return false;
            }
        }
        return true;
    }

    function checkrulelist(){
        for (var canvasname in canvasmap){
            if ( !isobjectnull(canvasmap[canvasname]['drawopts']) && isobjectnull(canvasmap[canvasname]['rulelist'])){
               rulelist = calculateRules(canvasname, 0, 0, attributes.width, attributes.height);
               canvasmap[canvasname]['rulelist'] = rulelist;
            }
        }
    }

    function IntemassCanvasUpload(csrfvalue){
        checkrulelist();
        var canvasjson = $.toJSON(canvasmap);
        $.post('/canvas/upload/',
                {'questionid':'1', 'canvasmap':canvasjson, 'csrfmiddlewaretoken': csrfvalue},
                function(payload){
                    if (payload['state'] === 'success')
                        alert('upload success');
                }, "json");
    }

})(jQuery);

