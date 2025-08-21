(function ($) {
    //plug-in internal globals
    var instmap = {};
    var elemap = {};
    var axismap = {};
    var colormap = {};
    var canvasmap = {};
    var global_legends = [];
    var attributes = {
        width: 600,
        height: 400
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
    var intesect_set = [];
    var XYaxisorigin = {};


    /******************************************************************
     *
     public API
     *
     * ****************************************************************/
    var intemassCanvases = $.fn.IntemassCanvas = function(opts){

        var options = $.extend(attributes, opts || {});
        var rulelistwidth = 350;
        var csrfvalue = options.csrfvalue;
        var id = options.id;
        if (options.height < 15 || options.width < 50){
            alert("canvas size too small");
        }else{
            options.height = options.height - 13;
            options.width = options.width - 50;
            attributes = options;
            axisorigin = {
                start_x: 70,
                start_y: attributes.height - 50
            };
            XYaxisorigin = {
                startY_x:attributes.width / 2,
                startY_y:20,
                startX_x:20,
                startX_y:attributes.height/2,
                O_y:attributes.height/2,
                O_x:attributes.width/2,
                endY_x:attributes.width/2 ,
                endY_y:attributes.height-25,
                endX_x:attributes.width-20,
                endX_y:attributes.height/2
            };
            this.each(function(){
                $(this).css({'float': 'left', 'width': attributes.width});
            });
         
            this.each(function(){
            var canvasname = $(this).attr('id');
            if (options.view === "undefined"){
                buildToolBar(this, csrfvalue, id);
            }
            buildDrawArea(this, options);
            buildMyMenu(this);
            var listhtml = "<div style='float:left;width:" + rulelistwidth + "px;height:" + attributes.height + "px;margin:1em auto'><h2 class='ui-widget-header'> Generated Rules:</h2>";
            listhtml += "<table class='intemasscanvas-table' id='list" + canvasname + "'>";
            listhtml += "<thead></thead>";
            listhtml += "<tbody></tbody></table>";          
            $(this).parent().append(listhtml);
            IntemassCanvasGet(canvasname, csrfvalue, id);
            
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
            var canvasname = $(this).attr('id');
            delete instmap[canvasname];
            delete elemap[canvasname];
            delete colormap[canvasname];
            delete canvasmap[canvasname];
            $("*", this).add([this]).each(function() {
                $.event.remove(this);
                $.removeData(this);
            });
            $(this).parent().remove();
        });
    };
    
   
    Raphael.st.getelemtype = function(){
        var elemtype;
        if (this.length === 5){
            elemtype = 'line';
        }else if(this.length === 8){
            elemtype = 'curve';
        }else if(this.length === 6){
            elemtype = 'circle';
        }else if(this.length === 11){
            elemtype = 'complexcurve';
        }else if(this.length === 2){
            elemtype = 'dot';
        }else if(this.length === 7){
            elemtype = 'rectangle';
        }else if(this.length === 10){
            elemtype = 'ellipse';
        }else if(this.length === 9){
            elemtype = 'square';
        }else if(this.length === 12){
            elemtype = 'triangle';
        }else if(this.length === 13){
            elemtype = 'simplecurve';
        }
        
        return elemtype;
    };
    
    Raphael.st.getlegend = function(){
        var elset = this;
        var legend;
        switch (elset.getelemtype()){
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
            case 'rectangle':
                legend = elset[5].attr('text');
                break;
            case 'circle':
                legend = elset[3].attr('text');
                break;
            case 'square':
                legend = elset[5].attr('text');
                break;
            case 'ellipse':
                legend = elset[5].attr('text');
                break;
            case 'simplecurve':
                legend = elset[6].attr('text');
                break;
            case 'triangle':
                legend = elset[4].attr('text');
                break;
            
            default:
                legend = undefined;
        }
        return legend;
    };

    global_legends.remove = function(elset){
        var legend;
        var canvasname;
        for (var i = 0; i < this.length; i += 1){
            legend = this[i].split(':')[0];
            canvasname = this[i].split(':')[1];
            if(legend === elset.getlegend()){
                this.splice(i, 1);
                return canvasname;
            }
        }
    };

   global_legends.clear = function (thiscanvas) {
       for (var i = 0; i < global_legends.length; i += 1) {
           var legend_canvasname = global_legends[i].split(':')[1];
           if (legend_canvasname === thiscanvas) {
               global_legends.splice(i, 1);
           }
       }
   };


    /*delete every element if points in the element area*/
    Raphael.st.undo = function (x,y) {
        var thisset = this;
        var bbox = thisset.getBBox();
        var canvasname;
        if (bbox && Raphael.isPointInsideBBox(bbox,x,y)){
            canvasname = global_legends.remove(thisset);
            thisset.forEach(function(el){
                if(el.data("what") === 'text' || el.data("what") === 'dottext'){
                    for (var elemlegend in canvasmap[canvasname]['drawopts']){
                        if (elemlegend === el.attr('text')){
                            delete canvasmap[canvasname]['drawopts'][elemlegend];
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

    var buildDrawArea;
    buildDrawArea = function (parent, options) {
        var canvasname = $(parent).attr('id');
        
        var drawareahtml = '<div class="intemasscanvas-canvas">';
        drawareahtml += '<div id="' + canvasname + '-tips-dialog" title="Give some tips" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">Please enter some tips </p>';
        drawareahtml += '<label for="' + canvasname + '-tips-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">Tips:</label><textarea id="' + canvasname + '-tips-input" style="width:200px;height:90px;" /></div>';
        drawareahtml += '<div id="' + canvasname + '-legend-dialog" title="Give A Legend" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">Please assign a unique legend before drawing </p>';
        drawareahtml += '<label for="' + canvasname + '-legend-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">Legend:</label><input id="' + canvasname + '-legend-input" type="text" value="Legend" style="width:200px;" /></div>';
        drawareahtml += '<div id="' + canvasname + '-about-dialog" title="About Us" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">About Us</p>';
        drawareahtml += '<label for="' + canvasname + '-legend-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">About us:</label></div>';
        drawareahtml += '<div id="' + canvasname + '-removeall-dialog" title="Remove All the elements" style="display:none;">';
        drawareahtml += '<p id="dialogue_warning" style="font-style:italic;font-family: Georgia, serif;">Are you sure?</p>';
        drawareahtml += '<label for="' + canvasname + '-legend-input" style="font-family:Times,TimesNR;font-weight:bold;margin-right:1em;">You will remove all the elements in the canvas.</label></div>';
        drawareahtml += '<div id="' + canvasname + '-axis-dialog" class="intemasscanvas-axis-dialog" title="Set Coordinates" style="display:none;">';
        drawareahtml += '<label for="' + canvasname + '-axis-name" class= "intemasscanvas-axis-label">Name:</label><input id="' + canvasname + '-axis-name" type="text" class="intemasscanvas-axis-input" />';
        drawareahtml += '<label for="' + canvasname + '-axis-splits" class= "intemasscanvas-axis-label">Splits:</label><input id="' + canvasname + '-axis-splits" type="text" value="3" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-axis-unit" class= "intemasscanvas-axis-label">Units:</label><input id="' + canvasname + '-axis-unit" type="text" value="m" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-axis-start" class= "intemasscanvas-axis-label">Start Value:</label><input id="' + canvasname + '-axis-start" type="text" value="0" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-axis-end" class= "intemasscanvas-axis-label">End Value:</label><input id="' + canvasname + '-axis-end" type="text" value="10" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-axis-direction" class= "intemasscanvas-axis-label">Direction:</label><select id="' + canvasname + '-axis-direction" class="intemasscanvas-axis-select" ><option value="0" selected="selected">Horizontal</option><option value="1">Vertical</option></select>';
        drawareahtml += '</div>';
        /////////////////////////////////////////
        drawareahtml += '<div id="' + canvasname + '-XYaxis-dialog" class="intemasscanvas-axis-dialog" title="Set X-Y Coordinates" style="display:none;">';
        drawareahtml += '<label for="' + canvasname + '-Xaxis-name" class= "intemasscanvas-XYaxis-label">X-axis Name:</label><input id="' + canvasname + '-Xaxis-name" type="text" class="intemasscanvas-axis-input" />';
         drawareahtml += '<label for="' + canvasname + '-Xaxis-start" class= "intemasscanvas-XYaxis-label">Start Value:</label><input id="' + canvasname + '-Xaxis-start" type="text" value="0" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-Xaxis-end" class= "intemasscanvas-XYaxis-label">End Value:</label><input id="' + canvasname + '-Xaxis-end" type="text" value="100" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-Xaxis-splits" class= "intemasscanvas-XYaxis-label">Splits:</label><input id="' + canvasname + '-Xaxis-splits" type="text" value="3" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-Yaxis-name" class= "intemasscanvas-XYaxis-label">Y-axis Name:</label><input id="' + canvasname + '-Yaxis-name" type="text" class="intemasscanvas-axis-input" />';
        drawareahtml += '<label for="' + canvasname + '-Yaxis-start" class= "intemasscanvas-XYaxis-label">Start Value:</label><input id="' + canvasname + '-Yaxis-start" type="text" value="0" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-Yaxis-end" class= "intemasscanvas-XYaxis-label">End Value:</label><input id="' + canvasname + '-Yaxis-end" type="text" value="100" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '<label for="' + canvasname + '-Yaxis-splits" class= "intemasscanvas-XYaxis-label">Splits:</label><input id="' + canvasname + '-Yaxis-splits" type="text" value="3" class="intemasscanvas-axis-input spinner-holder" />';
        drawareahtml += '</div>';
        ////////////////////////////////////////
        drawareahtml += '<div id="' + canvasname + '-rule-dialog" class="intemasscanvas-rule-dialog" title="Add Rules" style="display:none;">';
        drawareahtml += '</div>';
        drawareahtml += '</div>';
        $(drawareahtml).appendTo($(parent));

        //build color picker
        $("#" + canvasname + "-color-widget").colorpicker({
            color: '#ccc',
            parts: 'popup',
            showCloseButton: true,
            showCancelButton: false,
            init:function (event, color) {
            },
            select:function (evt, color) {
                colormap[canvasname] = Raphael.getRGB(color.formatted);
            },
            close:function (evt, color) {
                colormap[canvasname] = Raphael.getRGB(color.formatted);
                if (colormap[canvasname].error === 1)
                    colormap[canvasname] = "hsb(0,0,0.8)";
            }
        });
        //build spin buttons
        $("#" + canvasname + "-axis-units").spinner({ min:0, max:100, mouseWheel:false});
        $("#" + canvasname + "-axis-start").spinner({ min:-99999, max:99999, mouseWheel:false, step:0.01 });
        $("#" + canvasname + "-axis-end").spinner({ min:-99999, max:99999, mouseWheel:false, step:0.01 });

        var paper = Raphael($(parent).find(".intemasscanvas-canvas")[0], options.width, options.height - 10);
        paper.rect(0, 5, options.width - 5, options.height - 15, 10).attr({stroke:"#666"});

        colormap[canvasname] = "hsb(0,0,0.8)";
        instmap[canvasname] = paper;
        elemap[canvasname] = paper.set();
        axismap[canvasname] = [];
        canvasmap[canvasname] = canvasmap[canvasname] || {'drawopts': {}, 'axis': {}, 'rulelist': {}};
    };

    var buildToolBar = function(parent, csrfvalue, id){
        var canvasname = $(parent).attr('id');
        var toolbarhtml = '<span class="ui-widget-header ui-corner-all intemasscanvas-toolbar" style="float:left;">';
        
        toolbarhtml += '<input type="checkbox" class="lineBtn" id="' + canvasname +'-lineBtn"/><label for="' + canvasname +'-lineBtn" class="lineBtn">Line</label>';
        
        toolbarhtml += '<input type="checkbox" class="triBtn" id="' + canvasname +'-triBtn"/><label for="' + canvasname +'-triBtn" >Triangle</label>';
        
        toolbarhtml += '<input type="checkbox" class="rectBtn" id="' + canvasname +'-rectBtn"/><label for="' + canvasname +'-rectBtn" >Rectangle</label>';
        
        toolbarhtml += '<input type="checkbox" class="sqrBtn" id="' + canvasname +'-sqrBtn"/><label for="' + canvasname +'-sqrBtn">Square</label>';
        
        toolbarhtml += '<input type="checkbox" class="arrowBtn" id="' + canvasname +'-arrowBtn"/><label for="' + canvasname +'-arrowBtn" >Arrow</label>';
        
        toolbarhtml += '<input type="checkbox" class="dotBtn" id="' + canvasname +'-dotBtn"/><label for="' + canvasname +'-dotBtn" >Dot</label>';
        
        toolbarhtml += '<input type="checkbox" class="circleBtn" id="' + canvasname +'-circleBtn"/><label for="' + canvasname +'-circleBtn" >Circle</label>';
        
        toolbarhtml += '<input type="checkbox" class="ellipseBtn" id="' + canvasname +'-ellipseBtn"/><label for="' + canvasname +'-ellipseBtn" >Ellipse</label>';
        
        //toolbarhtml += '</span>';
        //toolbarhtml += '<span class="ui-widget-header ui-corner-all intemasscanvas-toolbar" style="float:left;">';
        
        
        toolbarhtml += '<input type="checkbox" class="simplecurveBtn" id="' + canvasname +'-simplecurveBtn"/><label for="' + canvasname +'-simplecurveBtn" >Simple Curve</label>';
        
        toolbarhtml += '<input type="checkbox" class="curveBtn" id="' + canvasname +'-curveBtn"/><label for="' + canvasname +'-curveBtn" >Compound Curve</label>';
        
        toolbarhtml += '<input type="checkbox" class="complexcurveBtn" id="' + canvasname +'-complexcurveBtn"/><label for="' + canvasname +'-complexcurveBtn" >Complex Curve</label>';
        
        toolbarhtml += '<button class="XYaxisBtn" id="' + canvasname +'-XYaxisBtn" >X-Y Axis</button>';
        
        toolbarhtml += '<button class="axisBtn" id="' + canvasname +'-axisBtn" >Static Coordinates</button>';
        
        //toolbarhtml += '</span>';
        
        //toolbarhtml += '<span class="ui-widget-header ui-corner-all intemasscanvas-toolbar" style="float:left;">';
        
        toolbarhtml += '<input id="' + canvasname +'-color-widget" style="display: none; vertical-align: bottom;"></input>';
        toolbarhtml += '<button class="colorBtn" id="' + canvasname +'-colorBtn" >Color</button>';
        
        toolbarhtml += '<input type="checkbox" class="ruleBtn" id="' + canvasname +'-ruleBtn"/><label for="' + canvasname +'-ruleBtn" >Rule</label>';
        
        toolbarhtml += '<input type="checkbox" class="moveBtn" id="' + canvasname +'-moveBtn" /><label for="' + canvasname +'-moveBtn" >Move</label>';
        
        toolbarhtml += '<input type="checkbox" class="viewBtn" id="' + canvasname +'-viewBtn"/><label for="' + canvasname +'-viewBtn" >Preview</label>';
        
        toolbarhtml += '<button class="removeallBtn" id="' + canvasname +'-removeallBtn" >Remove All</button>';
        
        toolbarhtml += '<input type="checkbox" class="tipsBtn" id="' + canvasname +'-tipsBtn"/><label for="' + canvasname +'-tipsBtn" >Tips</label>';
        
        toolbarhtml += '<button class="uploadBtn" id="' + canvasname +'-uploadBtn" >Upload All</button>';
        
        toolbarhtml += '</span>';
        
        $(toolbarhtml).appendTo($(parent));
        
        
        var $simplecurveBtn = $("#"+ canvasname +'-simplecurveBtn').data('whatBtn', 'simplecurveBtn').button({
            //text: true
            //icons: {
             //   primary: "ui-icon-person"
            //}
        });
        var $curveBtn = $("#"+ canvasname +'-curveBtn').data('whatBtn', 'curveBtn').button({
            //text: false,
            //icons: {
             //   primary: "ui-icon-carat-1-ne"
            //}
        });
        var $complexcurveBtn = $("#"+ canvasname +"-complexcurveBtn").data('whatBtn', 'complexcurveBtn').button({
            //text: false,
            //icons: {
              //  primary: "ui-icon-shuffle"
            //}
        });
        var $lineBtn = $("#"+ canvasname +"-lineBtn").data('whatBtn', 'lineBtn').button({
            //text: false,
            //icons: {
             //   primary: "ui-icon-minus"
            //}
        });
        
        var $rectBtn = $("#"+ canvasname +"-rectBtn").data('whatBtn', 'rectBtn').button({
            //text: false,
           // icons: {
           //    primary: "/static/images/rectangle.png"
               
           // }
        });
        
        var $sqrBtn = $("#"+ canvasname +"-sqrBtn").data('whatBtn', 'sqrBtn').button({
           // text: false,
            //icons: {
             //   primary: "ui-icon-stop"
            //}
        });
        
        var $arrowBtn = $("#"+ canvasname +"-arrowBtn").data('whatBtn', 'arrowBtn').button({ 
            //text: false,
           // icons: {
          //      primary: "ui-icon-circle-arrow-e"
          //  }
        });
        
        var $triBtn = $("#"+ canvasname +"-triBtn").data('whatBtn', 'triBtn').button({
           // text: false,
           // icons: {
           //     primary: "ui-icon-triangle-1-n"
           // }
        });   
        var $dotBtn = $("#"+ canvasname +"-dotBtn").data('whatBtn', 'dotBtn').button({
           // text: false,
           // icons: {
           //     primary: "ui-icon-bullet"
           // }
        });
        var $circleBtn = $("#"+ canvasname +"-circleBtn").data('whatBtn', 'circleBtn').button({
           // text: false,
            //icons: {
            //    primary: "ui-icon-radio-on"
           // }
        });
        var $ellipseBtn = $("#"+ canvasname +"-ellipseBtn").data('whatBtn', 'ellipseBtn').button({
           // text: false,
            //icons: {
            //    primary: "ui-icon-lightbulb"
           // }
        });
        var $tipsBtn = $("#"+ canvasname +"-tipsBtn").data('whatBtn', 'tipsBtn').button({
            //text: false,
            //icons: {
            //    primary: "ui-icon ui-icon-document-b"
            //}
        
        });
        var $XYaxisBtn = $("#"+ canvasname +"-XYaxisBtn" ).data('whatBtn', 'XYaxisBtn');
        var $axisBtn = $("#"+ canvasname +"-axisBtn" ).data('whatBtn', 'axisBtn');
        var $moveBtn = $("#"+ canvasname +"-moveBtn" ).data('whatBtn', 'moveBtn');
        var $colorBtn = $("#"+ canvasname +"-colorBtn" ).data('whatBtn', 'colorBtn');
        var $ruleBtn = $("#"+ canvasname +"-ruleBtn" ).data('whatBtn', 'ruleBtn');
        var $viewBtn = $("#"+ canvasname +"-viewBtn" ).data('whatBtn', 'viewBtn');
        var $uploadBtn = $("#"+ canvasname +"-uploadBtn" ).data('whatBtn', 'uploadBtn');
        var $removeallBtn = $("#"+ canvasname +"-removeallBtn" ).data('whatBtn', 'removeallBtn');
        var $Btn = [$curveBtn, $complexcurveBtn, $lineBtn, $axisBtn, $moveBtn, $colorBtn, $ruleBtn, $viewBtn, $removeallBtn, $dotBtn, $tipsBtn,$rectBtn,$triBtn,$sqrBtn,$circleBtn,$ellipseBtn,$simplecurveBtn,$arrowBtn,$XYaxisBtn];
        /******************************************************************
         *
         * Here we bundle draw_buttons
         *
         *****************************************************************/

        $complexcurveBtn.add($curveBtn).add($dotBtn).add($lineBtn).add($tipsBtn).add($rectBtn).add($circleBtn).add($ellipseBtn).add($sqrBtn).add($triBtn).add($simplecurveBtn).add($arrowBtn).click(function() {
            var whatBtn = $(this).data("whatBtn");
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            activedBtn = $(this);
            if ($(this).prop("checked")){
                $(canvas).unbind("click");
                disable_unactivedBtn($Btn, activedBtn);
                remove_dashline();

                $(canvas).css('cursor', 'pointer');
                $(canvas).bind("click", function(evt){
                    var start_x = evt.pageX - this.offsetLeft;
                    var start_y = evt.pageY - this.offsetTop - toolbar_offset;
                    var end_x = start_x < (attributes.width - 200) ? (start_x + 200) : attributes.width;
                    var end_y = start_y < (attributes.height - 200) ? start_y + 200 : attributes.height;
                    var drawopts = {'start_x': start_x, 'start_y': start_y,
                                    'end_x': end_x, 'end_y': end_y,
                                    'custom_path': null, 'custom_handler_path': null,
                                    'dashline': false, 'color': null};
                    var canvasname = $(parent).attr('id');
                    switch(whatBtn)
                    {
                        case 'curveBtn':
                            addDraw(canvasname, drawCurve, drawopts);
                            break;

                        case 'lineBtn':
                            addDraw(canvasname, drawLine, drawopts);
                            break;

                        case 'complexcurveBtn':
                            drawopts['end_y'] = start_y;
                            addDraw(canvasname, drawComplexCurve, drawopts);
                            break;

                        case 'dotBtn':
                            drawopts['end_x'] = null;
                            drawopts['end_y'] = null;
                            addDraw(canvasname, drawDot, drawopts);
                            break;

                        case 'tipsBtn':
                            drawopts['end_x'] = null;
                            drawopts['end_y'] = null;
                            addDraw(canvasname, drawTips, drawopts);
                            break;
                        //Rectangle
                        case 'rectBtn':
                            addDraw(canvasname, drawRect, drawopts);
                            break;
                        case 'circleBtn':
                            addDraw(canvasname, drawCircle, drawopts);
                            break;
                        case 'sqrBtn':
                          addDraw(canvasname, drawSquare, drawopts);
                          break;
                        case 'triBtn':
                          addDraw(canvasname, drawTriangle, drawopts);
                          break;
                        case 'ellipseBtn':
                            addDraw(canvasname, drawEllipse, drawopts);
                            break;
                        case 'simplecurveBtn':
                            addDraw(canvasname, drawSimpleCurve, drawopts);
                            break;
                        case 'arrowBtn':
                           drawopts['color'] = "#000000"
                           addDraw(canvasname, drawArrow, drawopts);
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
            //text: false,
            //icons: {
            //    primary: "ui-icon-arrowthickstop-1-n"
            //}
        }).click(function(){
            IntemassCanvasUpload(csrfvalue, id);
            
        });
        
        $XYaxisBtn.button({
            //text: false,
            //icons: {
            //    primary: "ui-icon-plusthick"
            //}
        })
        .click(function(){
            var xyaxis = "true";
            
            disable_unactivedBtn($Btn, $(this));
            var dialogid = '#' + canvasname +'-XYaxis-dialog';
            var XYaxis = {};
            var dialogOpts = {
                modal: true,
            buttons: {
                "Done": function(){
                    $("#"+ canvasname +"-axisBtn").attr("disabled", "")
                    XYaxis['Xname'] = $("#"+ canvasname +"-Xaxis-name").val();
                    XYaxis['Xstart'] = $("#"+ canvasname +"-Xaxis-start").val();
                    XYaxis['Xend'] = $("#"+ canvasname +"-Xaxis-end").val();
                    XYaxis['Xsplits'] = $("#"+ canvasname +"-Xaxis-splits").val();
                    
                    XYaxis['Yname'] = $("#"+ canvasname +"-Yaxis-name").val();
                    XYaxis['Ystart'] = $("#"+ canvasname +"-Yaxis-start").val();
                    XYaxis['Yend'] = $("#"+ canvasname +"-Yaxis-end").val();
                    XYaxis['Ysplits'] = $("#"+ canvasname +"-Yaxis-splits").val();
                    $(dialogid).dialog("close");
                    
                    drawXYAxis(canvasname, XYaxis);
                },
                "Cancel": function(){
                    $(dialogid).dialog("close");
                }
            },
            width:380,
            draggable:false,
            resizable:false
            };
            $(dialogid).dialog(dialogOpts);
        });
        
        $axisBtn.button({
            //text: false,
            //icons: {
            //    primary: "ui-icon-newwin"
            //}
        })
        .click(function(){
            var axis = 'true';
            
            disable_unactivedBtn($Btn, $(this));
            var dialogid = '#' + canvasname +'-axis-dialog';
            var axis = {};
            var dialogOpts = {
                modal: true,
            buttons: {
                "Done": function(){
                    $("#"+ canvasname +"-XYaxisBtn").attr("disabled", "")
                    axis['name'] = $("#"+ canvasname +"-axis-name").val();
                    axis['unit'] = $("#"+ canvasname +"-axis-unit").val();
                    axis['splits'] = $("#"+ canvasname +"-axis-splits").val();
                    axis['start'] = $("#"+ canvasname +"-axis-start").val();
                    axis['end'] = $("#"+ canvasname +"-axis-end").val();
                    axis['direction'] = $("#"+ canvasname +"-axis-direction").val();
                    drawAxis(canvasname, axis);
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
            //text: false,
            //icons: {
            //    primary: "ui-icon-arrow-4"
            //}
        })
        .click(function() {
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            var elist = elemap[$(parent).attr('id')];
            var canvasname = $(parent).attr('id');
            if ($(this).prop("checked")){
                disable_unactivedBtn($Btn, $(this));
                $(canvas).disableContextMenu();
                $(canvas).css('cursor', 'pointer');
                $(canvas).unbind("click");
                elist.forEach(function(elset){
                    elset.forEach(function(el){
                        if (el.data('what') === 'area') el.show();
                    });
                });
            }else{
                $(canvas).enableContextMenu();
                elist.forEach(function(elset){
                    elset.forEach(function(el){
                        if (el.data('what') === 'area') el.hide();
                    });
                });
                $(canvas).css('cursor', 'auto');

            }
        });


        $viewBtn.button({
            //text: false,
            //icons: {
            //    primary: "ui-icon-search"
            //}
        })
        .click(function() {
            var canvas = $('#' + canvasname).find(".intemasscanvas-canvas")[0];
            var elist = elemap[canvasname];
            if ($(this).prop("checked")){
                disable_unactivedBtn($Btn, $(this));
                $(canvas).unbind("click");
                $(canvas).css('cursor', 'auto');
                enable_preview(elist);
            }else{
                $moveBtn.click().attr('checked', false);
                $moveBtn.next().removeClass('ui-state-active');
                disable_preview(elist);
            }
        });

        $colorBtn.button({
            //text: false,
            //icons: {
            //    primary: "ui-icon-calculator"
            //}
        })
        .click(function(){
            $("#"+ canvasname +"-color-widget").focus();
            disable_unactivedBtn($Btn, $(this));
          });

        $ruleBtn.button({
            //text: false,
            //icons: {
            //    primary: "ui-icon-comment"
            //}
        })
        .click(function() {
            disable_unactivedBtn($Btn, $(this));
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            if ($(this).prop("checked")){
                //global variable
                var mousedownSelectionFunc = function(evt){
                    var canvas_x = evt.pageX - this.offsetLeft;
                    var canvas_y = evt.pageY - this.offsetTop - toolbar_offset;
                    //console.log("Mouse Down - Canvas_X:"+canvas_x+"|Canvas_Y:"+canvas_y);
                    doSelection = true;
                    selectionArea.push(canvas_x);
                    selectionArea.push(canvas_y);
                };
                var mousemoveSelectionFunc = function(evt,oldMousePositions){
                    if (doSelection === true){
                        selectionRedrawCounter += 1;
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
                var mouseupSelectionFunc = function(evt){
                    var canvas_x = evt.pageX - this.offsetLeft;
                    var canvas_y = evt.pageY - this.offsetTop - toolbar_offset;
                    var thiscanvas = $(parent).attr('id');
                    //console.log("Mouse UP - Canvas_X:"+canvas_x+"|Canvas_Y:"+canvas_y);
                    $(canvas).unbind("mousedown",mousedownSelectionFunc);
                    $(canvas).unbind("mousemove",mousemoveSelectionFunc);
                    $(canvas).unbind("mouseup",mouseupSelectionFunc);
                    if (curSelectionArea){
                        var dialogid = '#' + canvasname +'-rule-dialog';
                        var rulelist = [];
                        var savedrule = [];
                        curSelectionArea.remove();
                        curSelectionArea = undefined;
                        rulelist = calculateRules(thiscanvas, selectionArea[0], selectionArea[1], canvas_x, canvas_y);
                        $(dialogid).empty();
                        for(var i = 0; i < rulelist.length; i += 1){
                            $(dialogid).append("<p><label>"+ rulelist[i] + "</label><input type='checkbox' name='" + rulelist[i] + "'></input></p>");
                        }
                        var dialogOpts = {
                            modal: true,
                            buttons: {
                                "SelectAll": function(){
                                    for (var i = 0; i < $(dialogid).find("input").length; i += 1){
                                        input = $(dialogid).find("input")[i];
                                        $(input).attr('checked', true);
                                    }
                                },
                                "Done": function(){
                                    var input, rule;
                                    var point = {};
                                    $("#"+ canvasname +"-ruleBtn").prop('checked', false);
                                    $("#"+ canvasname +"-ruleBtn").button('refresh');
                                    for (var i = 0; i < $(dialogid).find("input").length; i += 1){
                                        input = $(dialogid).find("input")[i];
                                        rule = $(input).attr("name").split(/\s,/);
                                        if ($(input).prop('checked')){
                                            rule = [getpointlist(point, $(input).attr("name").split(/\s,/))].concat(rule);
                                            savedrule.push(rule);
                                        }
                                    }
                                    listRules(canvasname, savedrule);
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
                    selectionArea = [];
                };
                $(canvas).bind("mousedown", mousedownSelectionFunc);
                $(canvas).bind("mousemove", mousemoveSelectionFunc);
                $(canvas).bind("mouseup", mouseupSelectionFunc);
                //$(canvas).bind("mouseleave",mouseupSelectionFunc);
            }else{
                $(canvas).unbind("mousedown", mousedownSelectionFunc);
                $(canvas).unbind("mousemove", mousemoveSelectionFunc);
                $(canvas).unbind("mouseup", mouseupSelectionFunc);
                //$(canvas).unbind("mouseleave",mouseupSelectionFunc);
            }
        });

        $removeallBtn.button({
            //text: false,
            //icons: {
            //    primary: "ui-icon-trash"
            //}
        })
        .click(function() {
            
            disable_unactivedBtn($Btn, $(this));
            var canvasname = $(parent).attr('id');
            
            $("#"+ canvasname +"-XYaxisBtn").removeAttr("disabled");
            $("#"+ canvasname +"-axisBtn").removeAttr("disabled");
            var elist = elemap[canvasname];
            var axislist = axismap[canvasname];
                var dialogid = '#' + canvasname +'-removeall-dialog';
                $(dialogid).dialog({
                    modal: true,
                    buttons: {
                        "OK": function(){
                            elist.forEach(function(elset){
                                elset.remove();
                                elset = null;
                                delete elset;
                            });
                            //remove global_legends
                            global_legends.clear(canvasname);
                            //remove axisset
                            axislist.forEach(function(axisset){
                                axisset.remove();
                                axisset = null;
                                delete axisset;
                            });

                            //remove rulelist
                            $('#list' + canvasname + ' thead tr').remove();
                            $('#list' + canvasname + ' tbody tr').remove();

                            canvasmap[canvasname] = {'drawopts': {}, 'axis': {}, 'rulelist': {}};
                            $(dialogid).dialog("close");
                        },
                        "Cancel":function(){
                            $(dialogid).dialog("close");
                        }
                    },
                    width: 320,
                    height: 200,
                    draggable: false,
                    resizable: false
                });
        });

        var disable_unactivedBtn = function(btnList, activedBtn){
            for(var i = 0; i < btnList.length; i += 1){
                if (btnList[i].data("whatBtn") !== activedBtn.data("whatBtn")){
                    btnList[i].next().removeClass('ui-state-active');
                    btnList[i].attr('checked', false);
                }
            }
        };

        var forbidMove = function(){
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
        };

        var remove_dashline = function(){
            var canvas = $(parent).find(".intemasscanvas-canvas")[0];
            var elist = elemap[$(parent).attr('id')];
            elist.forEach(function(elset){
                elset.forEach(function(el){
                    if (el.data('what') ==='area'){
                        el.hide();
                    }
                })
            });
        };
    };

    var buildMyMenu = function(parent){
        var canvasname = $(parent).attr('id');
        var menuid = canvasname + '_intemass_menu';
        var menuhtml = '';
        menuhtml += '<ul id="' +menuid+'" class="contextMenu">';
        menuhtml += '<li class="delete"><a href="#delete">Delete</a></li>';
        //menuhtml += '<li class="cut separator"><a href="#cut">Cut</a></li>';
        //menuhtml += '<li class="copy separator"><a href="#copy">copy</a></li>';
        //menuhtml += '<li class="paste separator"><a href="#paste">paste</a></li>';
        //menuhtml += '<li class="edit separator"><a href="#edit">edit</a></li>';
        menuhtml += '<li class="about separator"><a href="#about">about</a></li>';
        menuhtml += '<li class="vertical separator"><a href="#vertical">vertical line</a></li>';
        menuhtml += '<li class="horizontal separator"><a href="#horizontal">horizontal line</a></li>';
        menuhtml += '</ul>';
        $(menuhtml).appendTo($(parent));
        var canvas = $(parent).find(".intemasscanvas-canvas")[0];
        var elist = elemap[$(parent).attr('id')];

        $(canvas).on('mousedown', function(e){
            var offset_Left = this.offsetLeft;
            var offset_Top = this.offsetTop - toolbar_offset;
            if (3 === e.which){
                //right click mousedown event
                var elist = elemap[$(parent).attr('id')];
                elist.forEach(function(elset){
                    var flag = 0;
                    var bbox = elset.getBBox();
                    if (Raphael.isPointInsideBBox(bbox, e.clientX - offset_Left, e.clientY - offset_Top)){
                        elset.forEach(function(el){
                            if (el.data("what") === 'area'){
                                if (el.node.style.display !== ""){
                                    el.show();
                                    $(canvas).one("mousedown", function(e){
                                        el.hide();
                                    });
                                }
                                flag = 1;
                                return false;
                            }
                        })
                    }
                    if (flag === 1) return false;
                })
            }
        });

        $(canvas).contextMenu({
            menu: menuid
        },
        function(action, menuele, pos){
            var canvasname = $(parent).attr('id');
            if (action === "vertical"){
                var drawopts = {'start_x': pos.x, 'start_y': pos.y,
                                'end_x': null, 'end_y': null,
                                'custom_path': null, 'custom_handler_path': null,
                                'dashline': true, 'color': colormap[canvasname],
                                'vertical': true};
                addDraw(canvasname, drawDot, drawopts);
                var canvas = $(parent).find(".intemasscanvas-canvas")[0];
                $(canvas).unbind("click");
                $(canvas).css('cursor', 'auto');
            }

            if (action === "horizontal"){
                var drawopts = {'start_x':pos.x, 'start_y':pos.y,
                                'end_x':null, 'end_y':null,
                                'custom_path':null, 'custom_handler_path':null,
                                'dashline':true, 'color':colormap[canvasname],
                                'horizontal':true};
                addDraw(canvasname, drawDot, drawopts);
                var canvas = $(parent).find(".intemasscanvas-canvas")[0];
                $(canvas).unbind("click");
                $(canvas).css('cursor', 'auto');
            }

            if (action === "delete"){
                var elist = elemap[canvasname];
                elist.forEach(function(elset){
                    if (elset.undo(pos.x, pos.y - toolbar_offset) === true){
                        return false;
                    }
                });
            }

            if (action === "about"){
                var dialogid = '#' + canvasname + '-about-dialog';
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
                var canvasname = $(parent).attr('id');
                var elist = elemap[canvasname];
                elist.forEach(function(elset){
                    var bbox = elset.getBBox();
                    if (bbox && Raphael.isPointInsideBBox(bbox, pos.x, pos.y) === true){
                        var canvasname = $(parent).attr('id');
                        var dialogid = '#' + canvasname +'-legend-dialog';
                        var dialogOpts = {
                            modal: true,
                            buttons: {
                                "Done": function(){
                                    var legend = $("#"+ canvasname +"-legend-input").val();
                                    var checklegend = legend + ':' + canvasname;
                                    var el_text = null;
                                    elset.forEach(function(el){
                                        if (el.data('what') === 'text')
                                        el_text = el.attr('text') + ':' + canvasname;
                                    });
                                    for(var i in global_legends){
                                        if (global_legends[i] == checklegend && global_legends[i] != el_text){
                                            $("#"+ canvasname +"-legend-dialog #dialogue_warning").css("color", "red");
                                            //console.log($("#dialogue_warning"));
                                            return false;
                                        }
                                    }
                                    global_legends.push(checklegend);
                                    elset.forEach(function(el){
                                        if (el.data('what') === 'text')
                                        el.attr({text: legend});
                                    });
                                    $(dialogid).dialog("close");
                                    $("#"+ canvasname +"-legend-dialog #dialogue_warning").css("color", "black");
                                },
                                "Cancel": function(){
                                    $(dialogid).dialog("close");
                                }
                            },
                            width:320,
                            height:200,
                            draggable:false,
                            resizable:false
                        };
                        $(dialogid).dialog(dialogOpts);
                        return false;
                    }
                });
            }

            if (action === "cut"){
                var elist = elemap[$(parent).attr('id')];
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
                var elist = elemap[$(parent).attr('id')];
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
                var canvasname = $(parent).attr('id');
                var paper = instmap[canvasname];
                if (!clonemap['elset'])
                    return false;
                var drawopts = {
                    custom_path:clonemap['path'], custom_handler_path:clonemap['handler_path'],
                    legend:clonemap['legend'], dashline:false, color:colormap[canvasname]
                };
                if (clonemap['elset'].getelemtype() === 'line'){
                    for(var i = 0; i < clonemap['path'].length; i += 1){
                        for(var j = 1; j <= 2; j += 1){
                            if (j % 2 === 0)
                                clonemap['path'][i][j] += pos.y - clonemap['bbox'].y;
                            else
                                clonemap['path'][i][j] += pos.x - clonemap['bbox'].x;
                        }
                    }
                    drawopts['start_x'] = clonemap['path'][0][1];
                    drawopts['start_y'] = clonemap['path'][0][2];
                    drawopts['end_x'] = clonemap['path'][1][1];
                    drawopts['end_y'] = clonemap['path'][1][2];
                    if (clonemap['legend'] !== null){
                        drawLine(canvasname, drawopts);
                    }else{
                        addDraw(canvasname, drawLine, drawopts);
                    }
                }
                if (clonemap['elset'].getelemtype() === 'curve'){
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
                        drawCurve(canvasname, drawopts);
                    }else{
                        addDraw(canvasname, drawCurve, drawopts);
                    }
                }
                if (clonemap['elset'].getelemtype() === 'complexcurve'){
                    for(var i = 0; i < clonemap['path'].length; i += 1){
                        for(var j = 1; j < clonemap['path'][i].length; j += 1){
                            if (j % 2 === 0)
                                clonemap['path'][i][j]  +=  pos.y-clonemap['bbox'].y;
                            else
                                clonemap['path'][i][j]  +=  pos.x-clonemap['bbox'].x;
                        }
                    }
                    for(var i = 0; i < clonemap['handler_path'].length; i += 1){
                        for(var j = 1; j < clonemap['handler_path'][j].length; j += 1){
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
                        drawComplexCurve(canvasname, drawopts);
                    }else{
                        addDraw(canvasname, drawComplexCurve, drawopts);
                    }
                }

                if (clonemap['elset'].getelemtype() === 'dot'){
                    if (clonemap['legend'] !== null){
                        drawDot(canvasname, drawopts);
                    }else{
                        drawopts['start_x'] = pos.x;
                        drawopts['start_y'] = pos.y - toolbar_offset;
                        drawopts['end_x'] = null;
                        drawopts['end_y'] = null;
                        addDraw(canvasname, drawDot, drawopts);
                    }
                }
                //clear cloneset
                clonemap = {};
            }
        });
    };

    /*******
     *
     *      The Main Draw Function
     *
     *******/
    var addDraw = function(canvasname, draw_what, drawopts){
        var dialogid = '#' + canvasname +'-legend-dialog';
        var legend = 'L';
        var dialogOpts = {
            modal: true,
            buttons: {
                "Done": function(){
                    drawopts['color'] = colormap[canvasname];
                    drawopts['dashline'] = ($("#"+ canvasname +"-legend-dashline").attr('checked') === 'checked');
                    drawopts['horizontal'] = ($("#"+ canvasname +"-legend-horizontal").attr('checked') === 'checked');
                    drawopts['vertical'] = ($("#"+ canvasname +"-legend-vertical").attr('checked') === 'checked');
                    drawopts['horizontal-line'] = ($("#"+ canvasname +"-legend-horizontal-line").attr('checked') === 'checked');
                    drawopts['vertical-line'] = ($("#"+ canvasname +"-legend-vertical-line").attr('checked') === 'checked');
                    if(draw_what === drawTips){
                        legend = $("#"+ canvasname +"-tips-input").val();
                    }else{
                        legend = $("#"+ canvasname +"-legend-input").val();
                    }
                    drawopts['legend'] = legend;
                    var checklegend = legend + ':' + canvasname;
                    for(var i = 0; i < global_legends.length; i  +=  1){
                        if (global_legends[i] === checklegend){
                            $("#"+ canvasname +"-legend-dialog #dialogue_warning").css("color", "red");
                            return false;
                        }
                    }
                    global_legends.push(checklegend);
                    if(drawopts['horizontal'] || drawopts['vertical']){
                        drawopts['dashline'] = true;
                        drawLine(canvasname, drawopts);
                    }else{
                        draw_what(canvasname, drawopts);
                    }

                    if(activedBtn !== null){
                        activedBtn.next().removeClass('ui-state-active');
                        activedBtn.attr('checked', false);
                        activedBtn = null;
                    }
                    $(dialogid).dialog("close");
                    $("#"+ canvasname +"-legend-dialog #dialogue_warning").css("color", "black");
                },
                "Cancel": function(){
                    if(activedBtn !== null){
                        activedBtn.next().removeClass('ui-state-active');
                        activedBtn.attr('checked', false);
                        activedBtn = null;
                    }
                    $(dialogid).dialog("close");
                }
            },
            open: function(e, ui){
                if(draw_what === drawLine){
                    $(e.target).parent().find('label').parent().append(
                                "<p><input id='"+ canvasname + "-legend-dashline' type='checkbox'>dashline</input></p>");
                }else if(draw_what === drawDot){
                    $(e.target).parent().find('label').parent().append(
                                "<form><input id='"+ canvasname + "-legend-horizontal' type='checkbox'>horizontal</input>" +
                                "<input id='"+ canvasname + "-legend-vertical' type='checkbox'>vertical</input>" +
                                "</form>");
                    if(drawopts['vertical'] === true) $("#"+ canvasname +"-legend-vertical").attr('checked', true);
                    if(drawopts['horizontal'] === true) $("#"+ canvasname +"-legend-horizontal").attr('checked', true);
                }
            },
            close: function(e, ui){
                $(e.target).parent().find('#' + canvasname +'-legend-dashline').parent().remove();
                $(e.target).parent().find('#' + canvasname +'-legend-horizontal').parent().remove();
            },
            width:320,
            height:230, draggable:false,
            resizable:false
        };

        if(draw_what === drawTips){
            dialogid = '#' + canvasname + '-tips-dialog';
            dialogOpts.height = 260;
        }
        $(dialogid).dialog(dialogOpts);
    };

    var drawtype = {'complexcurve': drawComplexCurve, 'curve': drawCurve, 'line': drawLine, 'dot': drawDot, 'tips': drawTips, 'rectangle':drawRect,'circle':drawCircle, 'simplecurve':drawSimpleCurve, 'square':drawSquare,'triangle':drawTriangle, 'arrow':drawArrow};
    var drawComplexCurve = function(canvasname, drawopts) {

        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
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

        canvasmap[canvasname]['drawopts'][legend] = {
            'type': 'complexcurve', 'start_x':start_x, 'start_y':start_y,
            'end_x': end_x, 'end_y':end_y, 'color':colormap[canvasname],
            'custom_path': curve_path, 'custom_handler_path':handler_path,
            'rcoordinate': getrcoordinate(curve_path)
        };

        var controls = paper.set(
            paper.path(curve_path).attr({stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data('what', 'path'),
            paper.path(handler_path).attr({stroke: "#996600", "stroke-dasharray": ". "}).data('what', 'handler_path'),
            paper.circle(start_x, start_y, 5).attr(discattr_drag).data('what', 'circle'),
            paper.circle(from_handler_x, from_handler_y, 5).attr(discattr).data('what', 'handler_circle'),
            paper.circle(to_handler_x, to_handler_y, 5).attr(discattr).data('what', 'handler_circle'),
            paper.circle(end_x, end_y, 5).attr(discattr).data('what', 'circle'),
            paper.circle(mid_handler_x, mid_handler_y, 5).attr(discattr).data('what', 'handler_circle'),
            paper.circle(pre_mid_handler_x, pre_mid_handler_y, 5).attr(discattr).data('what', 'handler_circle'),
            paper.circle(aft_mid_handler_x, aft_mid_handler_y, 5).attr(discattr).data('what', 'handler_circle'),
            paper.text(curve_path[3][5]+50,curve_path[3][6], legend).attr({'font-size': '10px'}).data('what', 'text'),
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
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
        elemap[canvasname].push(controls);
    };
        
    var drawCurve = function(canvasname, drawopts) {
        function update_rectarea(obj){
            var bb = obj.getBBox();
            obj.forEach(function(el){
                if (el.data("what")=='area'){
                    el.attr({x: bb.x, y: bb.y});
                }
            })
        }
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
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

        canvasmap[canvasname]['drawopts'][legend] = {type: 'curve',
            start_x:start_x, start_y:start_y,
            end_x:end_x, end_y:end_y, color:colormap[canvasname],
            custom_path:curve_path, custom_handler_path:handler_path,
            rcoordinate:getrcoordinate(curve_path)
        }

        var controls = paper.set(
                paper.path(curve_path).attr({stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
                paper.path(handler_path).attr({stroke: "#996600", "stroke-dasharray": ". "}).data("what", 'handler_path'),
                paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
                paper.circle(from_handler_x, from_handler_y, 5).attr(discattr).data("what", 'handler_circle'),
                paper.circle(to_handler_x, to_handler_y, 5).attr(discattr).data("what", 'handler_circle'),
                paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
                paper.text(curve_path[1][5]+50,curve_path[1][6], legend).attr({'font-size': '10px'}).data("what", 'text'),
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
            var bb = Raphael.pathBBox(curve_path);
            controls[7].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
            canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = curve_path;
            canvasmap[canvasname]['drawopts'][legend]['custom_handler_path'] = handler_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(curve_path);
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
        elemap[canvasname].push(controls);
        //console.log(canvasmap[canvasname]['drawopts'][legend]);
    };
   
  
    var drawSimpleCurve = function(canvasname,drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_rotate = {fill: "#0000FF", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var x1 = (start_x+70);
        var y1 = (start_y-70);
        var end_x = (start_x+140);
        var end_y = start_y;
        var simplecurve_path;
        if (drawopts['custom_path'] === null){
            simplecurve_path = [["M" , start_x,start_y],[ "Q", x1,y1,end_x,end_y]];
        }else{
            simplecurve_path = drawopts['custom_path'];
            x1 = drawopts['x1']
            y1 = drawopts['y1']
            end_x = drawopts['end_x']
            end_y = drawopts['end_y']
        }
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'simplecurve', color:colormap[canvasname],
            start_x:start_x, start_y:start_y,
            x1:x1,y1:y1,
            end_x:end_x, end_y:end_y,
            custom_path:simplecurve_path, custom_handler_path:null,
            rcoordinate:getrcoordinate(simplecurve_path)
        }
        var controls = paper.set(
                                paper.path().attr({path: simplecurve_path, stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
                                
                                paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
                                
                                paper.circle(x1, y1, 5).attr(discattr).data("what", 'circle'),
                                
                                paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
                                
                                paper.text(simplecurve_path[1][1]+10, simplecurve_path[1][2]-15, "controler").attr({'font-size': '10px'}).data("what", 'controler'),
                                
                                paper.rect(Raphael.pathBBox(simplecurve_path).x, Raphael.pathBBox(simplecurve_path).y, Raphael.pathBBox(simplecurve_path).width, Raphael.pathBBox(simplecurve_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
                                );
        controls.push(
            paper.text(start_x, start_y-10, legend).attr({'font-size': '10px'}).data("what", 'text'),
            paper.circle(start_x, start_y-20, 5).attr(discattr_rotate).hide(),
            paper.text(start_x, start_y, legend).attr({'font-size': '10px'}).hide(),
            paper.text(start_x, start_y, legend).attr({'font-size': '10px'}).hide(),
            paper.text(start_x, start_y, legend).attr({'font-size': '10px'}).hide(),
            paper.text(start_x, start_y, legend).attr({'font-size': '10px'}).hide(),
            paper.text(start_x, start_y, legend).attr({'font-size': '10px'}).hide()
        );
        controls[1].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            start_x = newX;
            start_y = newY;            
            simplecurve_path[0][1] = start_x;
            simplecurve_path[0][2] = start_y;
            controls[2].update(x,y);
            controls[3].update(x,y);
            controls[4].update(x,y);
            controls[6].attr({x:start_x, y:start_y-10})
            //controls[7].update(x,y,"controls[1]");
            controls[0].attr({path: simplecurve_path});
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = start_x;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = start_y;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = simplecurve_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(simplecurve_path);
            }
        controls[2].update = function (x,y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            x1 = newX;
            y1 = newY;
            simplecurve_path[1][1] = x1;
            simplecurve_path[1][2] = y1;            
            var bb = Raphael.pathBBox(simplecurve_path);
            controls[4].update(x,y);
            //controls[6].update(x,y);
            controls[5].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            controls[0].attr({path: simplecurve_path});
            canvasmap[canvasname]['drawopts'][legend]['x1'] = x1;
            canvasmap[canvasname]['drawopts'][legend]['y1'] = y1;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = simplecurve_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(simplecurve_path);
        }
        
        controls[3].update = function (x,y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            end_x = newX;
            end_y = newY;
            simplecurve_path[1][3] = end_x;
            simplecurve_path[1][4] = end_y;
            var bb = Raphael.pathBBox(simplecurve_path);
            controls[5].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            controls[0].attr({path: simplecurve_path});
            canvasmap[canvasname]['drawopts'][legend]['end_x'] = end_x;
            canvasmap[canvasname]['drawopts'][legend]['end_y'] = end_y;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = simplecurve_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(simplecurve_path);
        }
        
        controls[4].update = function (x,y){
            this.attr({x:x1+10,y:y1-15})
        }
        
        controls[5].update = function (x,y){
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            controls[1].update(x, y);
            var bb = Raphael.pathBBox(simplecurve_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        }
         /*
        controls[6].update = function (x,y){
            this.attr({x:start_x,y:y1-10})
        }
       
        controls[7].update = function (x,y,which_controls){
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx:start_x,cy:start_y-20})
            if (which_controls !== "controls[1]"){
                var deg = newX - start_x
                console.log('deg == '+deg);
                rotation_handler(controls,deg);
            }
        }
        */
        
        
        
        controls[1].drag(move, start, end);
        controls[2].drag(move, start, end);
        controls[3].drag(move, start, end);
        controls[5].drag(move, start, end);
        controls[7].drag(move, start, end);
        
        //controls[1].update(0, 0);
        elemap[canvasname].push(controls);
        
    };
    var rotation_handler = function(paper_obj,deg) {
            var l_coord = paper_obj.getBBox().x,
            r_coord = paper_obj.getBBox().x2,
            t_coord = paper_obj.getBBox().y,
            b_coord = paper_obj.getBBox().y2;
            
            var cx = (l_coord + r_coord)/2,
             cy = (t_coord + b_coord)/2;
            paper_obj.rotate(deg,cx,cy);
    };
    
  
   var drawSquare = function(canvasname, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x, end_y;
        var x1 = start_x;
        var y1 = start_y+80;
        var x2 = start_x+80;
        var y2 = start_y+80;
        end_x = start_x+80;
        end_y = start_y;
        var rect_path
        
        if (drawopts['custom_path'] === null){
            square_path = [["M", start_x, start_y], ["L", x1, y1],["L", x2, y2],
                          ["L", end_x, end_y], "z"];
        }else{
            square_path = drawopts['custom_path'];
            end_x = drawopts['end_x']
            end_y = drawopts['end_y']
            x1 = drawopts['x1']
            x2 = drawopts['x2']
            y1 = drawopts['y1']
            y2 = drawopts['y2']
        }
        
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'square', color:colormap[canvasname],
            start_x:start_x, start_y:start_y,
            x1:x1, y1:y1,
            x2:x2, y2:y2,
            end_x:end_x, end_y:end_y,
            custom_path:square_path, custom_handler_path:square_path,
            rcoordinate:getrcoordinate(square_path)
        }
        
        //controls which make the SQUARE scalable
        var controls = paper.set(
            paper.path().attr({path: square_path, stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
            paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
            paper.circle(x1, y1, 5).attr(discattr).data("what", 'circle').hide(),
            paper.circle(x2, y2, 5).attr(discattr).data("what", 'circle'),
            paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle').hide(),
            paper.text(square_path[3][1]+30, square_path[3][2]-20, legend).attr({'font-size': '10px'}).data("what", 'text'),
            paper.text(square_path[3][1]+30, square_path[3][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.text(square_path[3][1]+30, square_path[3][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.rect(Raphael.pathBBox(square_path).x, Raphael.pathBBox(square_path).y, Raphael.pathBBox(square_path).width, Raphael.pathBBox(square_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );
        
        //Controls[0] will uodates the path
        controls[0].update = function (x, y) {
            controls[1].update(x, y);
        };
        
        //controls[1] update the start_x and start_y co-ordinates
        controls[1].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            square_path[0][1] = newX;
            square_path[0][2] = newY;
            controls[2].update(x, y, "controls[1]");
            controls[3].update(x, y, "controls[1]");
            controls[4].update(x, y, "controls[1]");
            start_x = newX;
            start_y = newY;
            var bb = Raphael.pathBBox(square_path);
            controls[8].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = square_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(square_path);
        };
        
        //controls[2] updates x1 and y1 co-ordinates
        controls[2].update = function (x, y,receive_control) {
            var newX, newY;
            newX = this.attr("cx") + x;
            newY = this.attr("cy") + y;
            if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                square_path[1][1] = newX;
                square_path[1][2] = newY;
                x1 = newX;
                y1 = newY;
                canvasmap[canvasname]['drawopts'][legend]['x1'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y1'] = newY;
            }
            else if (receive_control=="controls[3]") {
                a1 = x2-x1;
                var y1 = start_y+a1;
                var y2 = start_y+a1;
                end_x = start_x+a1;
                square_path[0][1] = start_x;
                square_path[0][2] = start_y;
                square_path[1][1] = x1;
                square_path[1][2] = y1;
                square_path[2][1] = x2;
                square_path[2][2] = y2;
                square_path[3][1] = end_x;
                square_path[3][2] = end_y;
                
                y1 = start_y+a1;
                y2 = start_y+a1;
                end_x = start_x+a1;
                
                canvasmap[canvasname]['drawopts'][legend]['x1'] = x1;
                canvasmap[canvasname]['drawopts'][legend]['y1'] = y1;
                controls[3].update(x,y,"controls[2]");
                this.attr({cx: x1, cy: y1});
                controls[4].update(x,y,"controls[2]")
            }
            //controls[5].attr({x:newX+30, y:newY-20});
            controls[0].attr({path: square_path});
            var bb = Raphael.pathBBox(square_path);
            controls[8].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = square_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(square_path);
        };
        
        //controls[3] updates x2 and y2 co-ordinates
        controls[3].update = function (x, y,receive_control) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                square_path[2][1] = newX;
                square_path[2][2] = newY;
                x2 = newX;
                y2 = newY;
                canvasmap[canvasname]['drawopts'][legend]['x2'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y2'] = newY;
            }
            
            else if(receive_control=="controls[2]"){
                a1 = x2-x1;
                var y2 = start_y+a1;
                this.attr({cx: x2, cy: y2});
                canvasmap[canvasname]['drawopts'][legend]['x2'] = x2;
                canvasmap[canvasname]['drawopts'][legend]['y2'] = y2;
            }
            else{
                this.attr({cx: newX, cy: newY});
                square_path[2][1] = newX;
                square_path[2][2] = newY;
                x2 = newX;
                y2 = newY;
                controls[2].update(x,y,"controls[3]")
                canvasmap[canvasname]['drawopts'][legend]['x2'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y2'] = newY;
            }
            
            //controls[5].attr({x:newX+30, y:newY-20});
            controls[0].attr({path: square_path});
            var bb = Raphael.pathBBox(square_path);
            controls[8].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = square_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(square_path);
        };
        
        //controls[4] updates end_x and end_y co-ordinates
        controls[4].update = function (x, y,receive_control) {
            var newX, newY;
            newX = this.attr("cx") + x;
            newY = this.attr("cy") + y;
            if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                square_path[3][1] = newX;
                square_path[3][2] = newY;
                end_x = newX;
                end_y = newY;
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            }
            else if (receive_control=="controls[3]") {
                this.attr({cx: newX, cy: start_y});
                square_path[3][1] = newX;
                square_path[3][2] = start_y;
                end_x = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            }
            else if (receive_control=="controls[2]") {
                a1 = x2-x1;
                end_x = start_x+a1;
                this.attr({cx: end_x, cy: end_y});
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = end_x;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = end_y;
            }
           
            controls[5].attr({x:newX+30, y:newY-20});
            controls[0].attr({path: square_path});
            var bb = Raphael.pathBBox(square_path);
            controls[8].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = square_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(square_path);
           
        };
        
        //controls[6] will useful for drag the rectangle along the paper
        controls[8].update = function (x, y) {
            controls[1].update(x, y);
            var bb = Raphael.pathBBox(square_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };
        
        controls[1].drag(move, start, end);
        controls[3].drag(move, start, end);

        controls[8].drag(move, start, end);
        //controls[1].update(0, 0);
        elemap[canvasname].push(controls);
        
   }
    
   var drawTriangle = function(canvasname, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x, end_y;
        var x1 = start_x + 150;
        var y1 = start_y;
        var triangle_path
        var end_x = (start_x+x1)/2;
        var end_y = start_y-80;
        if (drawopts['custom_path'] === null){
            triangle_path = [["M", start_x, start_y], ["L", x1, y1],["L", end_x,end_y],"z"]
            
        }else{
            triangle_path = drawopts['custom_path'];
            start_x = drawopts['start_x'];
            start_y = drawopts['start_y'];
            x1 = drawopts['x1'];
            y1 = drawopts['y1'];
            
            end_x = drawopts['end_x'];
            end_y = drawopts['end_y'];
        }
       
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'triangle', color:colormap[canvasname],
            start_x:start_x, start_y:start_y,
            x1:x1, y1:y1,
            end_x:end_x, end_y:end_y,
            custom_path:triangle_path, custom_handler_path:null,
            'rcoordinate':getrcoordinate(triangle_path, "triangle")
        }
        
        //controls which make the rectangle scalable
        var controls = paper.set(
            paper.path().attr({path: triangle_path, stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
            paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
            paper.circle(x1, y1, 5).attr(discattr).data("what", 'circle'),
            paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
            paper.text(triangle_path[2][1]+30, triangle_path[2][2]-20, legend).attr({'font-size': '10px'}).data("what", 'text'),
            paper.text(triangle_path[2][1]+30, triangle_path[2][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.text(triangle_path[2][1]+30, triangle_path[2][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.text(triangle_path[2][1]+30, triangle_path[2][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.text(triangle_path[2][1]+30, triangle_path[2][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.text(triangle_path[2][1]+30, triangle_path[2][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.text(triangle_path[2][1]+30, triangle_path[2][2]-20, legend).attr({'font-size': '0px'}).data("what", 'text').hide(),
            paper.rect(Raphael.pathBBox(triangle_path).x, Raphael.pathBBox(triangle_path).y, Raphael.pathBBox(triangle_path).width, Raphael.pathBBox(triangle_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );
        
        //Controls[0] will uodates the path
        controls[0].update = function (x, y) {
            controls[1].update(x, y);
        };
        
        //controls[1] update the start_x and start_y co-ordinates
        controls[1].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            triangle_path[0][1] = newX;
            triangle_path[0][2] = newY;
            controls[2].update(x, y,"controls[1]");
            controls[3].update(x, y,"controls[1]");
            start_x = newX;
            start_y = newY;
            var bb = Raphael.pathBBox(triangle_path);
            controls[11].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = triangle_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(triangle_path);
        };
        
        //controls[2] updates x1 and y1 co-ordinates
        controls[2].update = function (x, y,receive_control) {
            var newX, newY;
            newX = this.attr("cx") + x;
            newY = this.attr("cy") + y;
            if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                triangle_path[1][1] = newX;
                triangle_path[1][2] = newY;
                x1 = newX;
                y1 = newY;
                canvasmap[canvasname]['drawopts'][legend]['x1'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y1'] = newY;
            }
            else{
                this.attr({cx: newX, cy: y1});
                triangle_path[1][1] = newX;
                triangle_path[1][2] = y1;
                x1 = newX;
                canvasmap[canvasname]['drawopts'][legend]['x1'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y1'] = y1;
            }
            
            //controls[4].attr({x:newX+30, y:newY-20});
            controls[0].attr({path: triangle_path});
            var bb = Raphael.pathBBox(triangle_path);
            controls[11].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = triangle_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(triangle_path);
        };
        
        //controls[3] updates end_x and end_y co-ordinates
        controls[3].update = function (x, y,receive_control) {
            var newX, newY;
            newX = this.attr("cx") + x;
            newY = this.attr("cy") + y;
            if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                triangle_path[2][1] = newX;
                triangle_path[2][2] = newY;
                end_x = newX;
                end_y = newY;
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            }
            else{
                this.attr({cx: newX, cy: newY});
                triangle_path[2][1] = newX;
                triangle_path[2][2] = newY;
                end_x = newX;
                end_y = newY;
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;    
            }
            
            controls[4].attr({x:newX+30, y:newY-20});
            controls[0].attr({path:triangle_path});
            var bb = Raphael.pathBBox(triangle_path);
            controls[11].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = triangle_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(triangle_path);
        };
        
        //controls[5] will useful for drag the rectangle along the paper
        controls[11].update = function (x, y) {
            controls[1].update(x, y);
            var bb = Raphael.pathBBox(triangle_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };
        
        controls[1].drag(move, start, end);
        controls[3].drag(move, start, end);
        controls[2].drag(move, start, end);
        
        controls[11].drag(move, start, end);
        //controls[1].update(0, 0);
        elemap[canvasname].push(controls);    
        
    };
   
    var drawRect = function(canvasname, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x, end_y;
        var x1 = start_x;
        var y1 = start_y+80;
        var x2 = start_x+180;
        var y2 = start_y+80;
        end_x = start_x+180;
        end_y = start_y;
        var rect_path
        
        if (drawopts['custom_path'] === null){
            rect_path = [["M", start_x, start_y], ["L", x1, y1],["L", x2, y2],
                          ["L", end_x, end_y], "z"];
        }else{
            rect_path = drawopts['custom_path'];
            end_x = drawopts['end_x']
            end_y = drawopts['end_y']
            x1 = drawopts['x1']
            x2 = drawopts['x2']
            y1 = drawopts['y1']
            y2 = drawopts['y2']
        }
        
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'rectangle', color:colormap[canvasname],
            start_x:start_x, start_y:start_y,
            x1:x1, y1:y1,
            x2:x2, y2:y2,
            end_x:end_x, end_y:end_y,
            custom_path:rect_path, custom_handler_path:null,
            rcoordinate:getrcoordinate(rect_path, "rectangle")
        }
        
        //controls which make the rectangle scalable
        var controls = paper.set(
            paper.path().attr({path: rect_path, stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
            paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
            paper.circle(x1, y1, 5).attr(discattr).data("what", 'circle'),
            paper.circle(x2, y2, 5).attr(discattr).data("what", 'circle'),
            paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
            paper.text(rect_path[3][1]+30, rect_path[3][2]-20, legend).attr({'font-size': '10px'}).data("what", 'text'),
            paper.rect(Raphael.pathBBox(rect_path).x, Raphael.pathBBox(rect_path).y, Raphael.pathBBox(rect_path).width, Raphael.pathBBox(rect_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
           
        );
        
        //Controls[0] will updates the path
        controls[0].update = function (x, y) {
            controls[1].update(x, y);
        };
        
        //controls[1] update the start_x and start_y co-ordinates
        controls[1].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            rect_path[0][1] = newX;
            rect_path[0][2] = newY;
            controls[2].update(x, y,"controls[1]");
            controls[3].update(x, y,"controls[1]");
            controls[4].update(x, y,"controls[1]");
            start_x = newX;
            start_y = newY;
            var bb = Raphael.pathBBox(rect_path);
            controls[6].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
           // controls[5].attr({x:newX+50, y:newY-10});
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = rect_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(rect_path);
        };
        
        //controls[2] updates x1 and y1 co-ordinates
        controls[2].update = function (x, y,receive_control) {
            var newX, newY;
            newX = this.attr("cx") + x;
            newY = this.attr("cy") + y;
            if (receive_control=="controls[3]") {
                this.attr({cx: start_x, cy: newY});
                rect_path[1][1] = start_x;
                rect_path[1][2] = newY;
                y1 = newY;
                canvasmap[canvasname]['drawopts'][legend]['x1'] = start_x;
                canvasmap[canvasname]['drawopts'][legend]['y1'] = newY;
            }
            else if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                rect_path[1][1] = newX;
                rect_path[1][2] = newY;
                x1 = newX;
                y1 = newY;
                canvasmap[canvasname]['drawopts'][legend]['x1'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y1'] = newY;
            }
            
            else {
                this.attr({cx: start_x, cy: newY});
                rect_path[1][1] = start_x;
                rect_path[1][2] = newY;
                y1 = newY;
                controls[3].update(x,y,"controls[2]")
                canvasmap[canvasname]['drawopts'][legend]['x1'] = start_x;
                canvasmap[canvasname]['drawopts'][legend]['y1'] = newY;
            }
            //controls[5].attr({x:newX+30, y:newY-20});
            controls[0].attr({path: rect_path});
            var bb = Raphael.pathBBox(rect_path);
            controls[6].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = rect_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(rect_path);
        };
        
        //controls[3] updates x2 and y2 co-ordinates
        controls[3].update = function (x, y,receive_control) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            if (receive_control=="controls[4]") {
                this.attr({cx: newX, cy: y2});
                rect_path[2][1] = newX;
                rect_path[2][2] = y2;
                x2 = newX;
                canvasmap[canvasname]['drawopts'][legend]['x2'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y2'] = y2;
            }
            else if(receive_control=="controls[2]"){
                this.attr({cx: x2, cy: newY});
                rect_path[2][1] = x2;
                rect_path[2][2] = newY;
                y2 = newY;
                canvasmap[canvasname]['drawopts'][legend]['x2'] = x2;
                canvasmap[canvasname]['drawopts'][legend]['y2'] = newY;
            }
            else if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                rect_path[2][1] = newX;
                rect_path[2][2] = newY;
                x2 = newX;
                y2 = newY;
                canvasmap[canvasname]['drawopts'][legend]['x2'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y2'] = newY;
            }
            
            else{
                this.attr({cx: newX, cy: newY});
                rect_path[2][1] = newX;
                rect_path[2][2] = newY;
                x2 = newX;
                y2 = newY;
                controls[2].update(x,y,"controls[3]")
                controls[4].update(x,y,"controls[3]")
                canvasmap[canvasname]['drawopts'][legend]['x2'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['y2'] = newY;
            }
            //controls[5].attr({x:newX+30, y:newY-10});
            controls[0].attr({path: rect_path});
            var bb = Raphael.pathBBox(rect_path);
            controls[6].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = rect_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(rect_path);
        };
        
        //controls[4] updates end_x and end_y co-ordinates
        controls[4].update = function (x, y,receive_control) {
            var newX, newY;
            newX = this.attr("cx") + x;
            newY = this.attr("cy") + y;
            if (receive_control=="controls[3]") {
                this.attr({cx: newX, cy: start_y});
                rect_path[3][1] = newX;
                rect_path[3][2] = start_y;
                end_x = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = start_y;
            }
            else if(receive_control=="controls[1]"){
                this.attr({cx: newX, cy: newY});
                rect_path[3][1] = newX;
                rect_path[3][2] = newY;
                end_x = newX;
                end_y = newY;
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            }
            
            else{
                this.attr({cx: newX, cy: start_y});
                rect_path[3][1] = newX;
                rect_path[3][2] = start_y;
                end_x = newX;
                controls[3].update(x, y,"controls[4]");
                canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
                canvasmap[canvasname]['drawopts'][legend]['end_y'] = start_y;
            }
            controls[5].attr({x:newX+30, y:newY-20});
            controls[0].attr({path: rect_path});
            var bb = Raphael.pathBBox(rect_path);
            controls[6].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = rect_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(rect_path);
        };
        
        //controls[6] will useful for drag the rectangle along the paper
        controls[6].update = function (x, y) {
            controls[1].update(x, y);
            var bb = Raphael.pathBBox(rect_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };
        
        controls[1].drag(move, start, end);
        controls[3].drag(move, start, end);
        controls[4].drag(move, start, end);
        controls[2].drag(move, start, end);
        
        controls[6].drag(move, start, end);
        //controls[1].update(0, 0);
        elemap[canvasname].push(controls);
       
    };
    
    var drawCircle = function (canvasname, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var radius = 80
        var end_x = start_x+radius;
        var end_y = start_y;
        var circle_path
        if (drawopts['custom_path'] === null){
            circle_path = [["M" , (start_x), (start_y-radius)],[ "A", radius, radius,0,1,1,(start_x-0.1),(start_y-radius)], "z"];
        }else{
            circle_path = drawopts['custom_path'];
            start_x = drawopts['start_x'];
            start_y = drawopts['start_y'];
            radius = drawopts['radius']
            end_x = drawopts['end_x']
            end_y = drawopts['end_y']
        }
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'circle', color:colormap[canvasname],
            start_x:start_x, start_y:start_y,
            radius : radius,
            end_x:end_x, end_y:end_y,
            custom_path:circle_path, custom_handler_path:null,
            'rcoordinate':getrcoordinate([[start_x, start_y],[end_x, end_y]])
        }
        var controls = paper.set(
                                paper.path().attr({path: circle_path, stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
                                paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
                                paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
                                paper.text(start_x, start_y-15, legend).attr({'font-size': '10px'}).data("what", 'text'),
                                paper.rect(Raphael.pathBBox(circle_path).x, Raphael.pathBBox(circle_path).y, Raphael.pathBBox(circle_path).width, Raphael.pathBBox(circle_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
                                                );
        controls.push(paper.text(circle_path[0][1], circle_path[0][2]+radius+10, "circle").hide());
        controls[0].update = function (x, y) {
            controls[1].update(x, y);
        };
        controls[1].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            start_x = newX;
            start_y = newY;
            circle_path[0][1] = newX;
            circle_path[0][2] = (newY-radius);
            circle_path[1][6] = (newX-0.1);
            circle_path[1][7] = (newY-radius);
            controls[2].update(x, y);
            var bb = Raphael.pathBBox(circle_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            controls[3].attr({x : start_x, y:start_y-15});
            controls[5].attr({x : circle_path[0][1],y:circle_path[0][2]+radius+10});
            controls[0].attr({path: circle_path});
            canvasmap[canvasname]['drawopts'][legend]['radius'] = radius;
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = circle_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate([[start_x, start_y],[end_x, end_y]]);
        };
        controls[2].update = function (x,y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            radius = (newX - start_x) > 0 ? (newX-start_x) : (start_x-newX)
            this.attr({cx: newX, cy: start_y});
            
            end_x = newX
            end_y = start_y
            circle_path[0][2] = (start_y-radius);
            circle_path[1][1] = radius;
            circle_path[1][2] = radius;
            circle_path[1][7] = (start_y-radius);
            
            var bb = Raphael.pathBBox(circle_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            controls[3].attr({x : start_x, y:start_y-15});
            //controls[3].attr({x : start_x+50, y:start_y-radius-10});
            controls[0].attr({path: circle_path})
            
            canvasmap[canvasname]['drawopts'][legend]['radius'] = radius;
            canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['end_y'] = start_y;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = circle_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate([[start_x, start_y],[end_x, end_y]]);
        }
        
        
        controls[4].update = function (x, y) {
            controls[1].update(x, y);
            var bb = Raphael.pathBBox(circle_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };
        
        
        controls[1].drag(move, start, end);
        controls[2].drag(move, start, end);
        controls[3].drag(move, start, end);
        controls[4].drag(move, start, end);
        
        //controls[1].update(0, 0);
        elemap[canvasname].push(controls);
        
    };
    var drawEllipse = function (canvasname, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var custom_path = drawopts['custom_path'];
        var custom_handler_path = drawopts['custom_handler_path'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var r_x = 80
        var r_y = 50
        var end_x = start_x+r_x;
        var end_y = Math.abs(start_y-r_y);
        if (drawopts['custom_path'] === null){
            ellipse_path = [["M", (start_x - r_x), (start_y)], ["a", r_x, r_y ,0,1,1,0,0.1 ],"z"];
        }else{
            ellipse_path = drawopts['custom_path'];
            r_x = drawopts['r_x']
            r_y = drawopts['r_y']
            end_x = start_x + r_x;
            end_y = Math.abs(start_y - r_y);
        }
        var rcoordinate_val = [[start_x, start_y],[start_x, end_y],[end_x, start_y]]
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'ellipse', color:colormap[canvasname],
            start_x:start_x, start_y:start_y,
            r_x:r_x, r_y:r_y,
            end_x:end_x, end_y:end_y,
            custom_path:ellipse_path, custom_handler_path:null,
            rcoordinate:getrcoordinate(rcoordinate_val,"ellipse")
        }
        var controls = paper.set(
                                paper.path().attr({path: ellipse_path, stroke: color.hex || color || Raphael.getColor(),"stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path'),
                                
                                paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
                                
                                paper.circle(start_x, end_y, 5).attr(discattr).data("what", 'circle'),
                                
                                paper.circle(end_x, start_y, 5).attr(discattr).data("what", 'circle'),
                                                                
                                paper.rect(Raphael.pathBBox(ellipse_path).x, Raphael.pathBBox(ellipse_path).y, Raphael.pathBBox(ellipse_path).width, Raphael.pathBBox(ellipse_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
                                                );
        controls.push(
            paper.text(start_x, start_y-15, legend).attr({'font-size': '10px'}).data("what", 'text'),
            paper.text(0, 0, " ").attr({'font-size': '10px'}).data("what", 'add_text').hide(),
            paper.text(0, 0, " ").attr({'font-size': '10px'}).data("what", 'add_text').hide(),
            paper.text(0, 0, " ").attr({'font-size': '10px'}).data("what", 'add_text').hide(),
            paper.text(0, 0, " ").attr({'font-size': '10px'}).data("what", 'add_text').hide()
        );
        
        controls[1].update = function(x,y){
            start_x = this.attr("cx") + x;
            start_y = this.attr("cy") + y;
            this.attr({cx:start_x , cy: start_y});
            ellipse_path[0][1] = (start_x - r_x);
            ellipse_path[0][2] = start_y;
            controls[2].update(x,y);
            controls[3].update(x,y);
            controls[0].attr({path:ellipse_path});
            var bb = Raphael.pathBBox(ellipse_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            controls[5].attr({x: start_x, y:start_y-15});
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = ellipse_path;
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = start_x;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = start_y;
            rcoordinate_val = [[start_x, start_y],[start_x, end_y],[end_x, start_y]]
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(rcoordinate_val,"ellipse");
        };
        controls[2].update = function(x,y){
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            end_y = newY;
            r_y = Math.abs(start_y - end_y);
            ellipse_path[1][2] = r_y;
            this.attr({cx:start_x , cy: end_y});
            controls[0].attr({path:ellipse_path});
            var bb = Raphael.pathBBox(ellipse_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['r_y'] = r_y;
            canvasmap[canvasname]['drawopts'][legend]['end_y'] = end_y;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = ellipse_path;
            rcoordinate_val = [[start_x, start_y],[start_x, end_y],[end_x, start_y]]
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(rcoordinate_val,"ellipse");
        };
        controls[3].update = function(x,y){
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            end_x = newX;
            r_x = Math.abs(end_x - start_x);
            ellipse_path[0][1] = (start_x - r_x);
            ellipse_path[1][1] = r_x;
            this.attr({cx:end_x , cy: start_y});
            controls[0].attr({path:ellipse_path});
            var bb = Raphael.pathBBox(ellipse_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['end_x'] = end_x;
            canvasmap[canvasname]['drawopts'][legend]['r_x'] = r_x;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = ellipse_path;
            rcoordinate_val = [[start_x, start_y],[start_x, end_y],[end_x, start_y]]
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(rcoordinate_val,"ellipse");
        };
        controls[4].update = function(x,y){
            controls[1].update(x,y)
        };
        
        controls[1].drag(move, start, end);
        controls[2].drag(move, start, end);
        controls[3].drag(move, start, end);
        controls[4].drag(move, start, end);
        //controls[1].update(0, 0);
        elemap[canvasname].push(controls);
        
    };
    
    var drawArrow = function(canvasname, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr = {fill: "#00CC00", stroke: "none"};
        var discattr_drag = {fill: "#000", stroke: "none"};
        var discattr_intersect = {fill: "#993300", stroke: "none"};
        var color = drawopts['color'];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x, end_y, arrow_path;
        
        end_x = drawopts['end_x'];
        end_y = drawopts['end_y'];

        if (drawopts['custom_path'] === null){
            arrow_path = [["M", start_x, start_y], ["L", end_x, end_y]];
        }else{
            arrow_path = drawopts['custom_path'];
        }
        
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'arrow', color:colormap[canvasname],
            vertical:drawopts['vertical'], horizontal:drawopts['horizontal'],
            start_x:start_x, start_y:start_y,
            end_x:end_x, end_y:end_y,
            custom_path:arrow_path, custom_handler_path:null,
            'rcoordinate':getrcoordinate(arrow_path)
        }
        
        var controls = paper.set();
        controls.push(
            paper.path().attr({path: arrow_path, stroke: '#D8D8D8' || color || color.hex ||  Raphael.getColor(), "stroke-width": 4,'arrow-end': 'classic-wide-long'}).data("what", 'path')
        );
        console.log(controls[0])
               
        controls.push(
            paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
            paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
            paper.text(arrow_path[1][1]+20, arrow_path[1][2]-10, legend).attr({'font-size': '10px'}).data("what", 'text')
        );
        
        controls.push(
            paper.rect(Raphael.pathBBox(arrow_path).x, Raphael.pathBBox(arrow_path).y, Raphael.pathBBox(arrow_path).width, Raphael.pathBBox(arrow_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );

        //console.log(controls[0]);
        controls[0].update = function (x, y) {
            controls[1].update(x, y);
        };
        controls[1].update = function (x, y) {
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            arrow_path[0][1] = newX;
            arrow_path[0][2] = newY;
            controls[2].update(x, y);
            var bb = Raphael.pathBBox(arrow_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = arrow_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(arrow_path);
            
        };
        controls[2].update = function (x, y) {
            var newX, newY;
            
            newX = this.attr("cx") + x;
            newY = this.attr("cy") + y;
      
            this.attr({cx: newX, cy: newY});
            arrow_path[1][1] = newX;
            arrow_path[1][2] = newY;
            controls[0].attr({path: arrow_path});
            controls[3].attr({x:newX+50, y:newY-10});
            
            var bb = Raphael.pathBBox(arrow_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            canvasmap[canvasname]['drawopts'][legend]['custom_path'] = arrow_path;
            canvasmap[canvasname]['drawopts'][legend]['rcoordinate'] = getrcoordinate(arrow_path);
          
        };

        controls[4].update = function (x, y) {
            controls[1].update(x, y);
            var bb = Raphael.pathBBox(arrow_path);
            this.attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
        };

        controls[1].drag(move, start, end);
        controls[2].drag(move, start, end);
        controls[4].drag(move, start, end);
        controls[1].update(0, 0);
        elemap[canvasname].push(controls);
        
    };
    
    var drawLine = function(canvasname, drawopts){
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
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
        
        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'line', color:colormap[canvasname], dashline:drawopts['dashline'],
            vertical:drawopts['vertical'], horizontal:drawopts['horizontal'],
            start_x:start_x, start_y:start_y,
            end_x:end_x, end_y:end_y,
            custom_path:null, custom_handler_path:null,
            'rcoordinate':getrcoordinate(line_path)
        }
        
        var controls = paper.set();
        
        if (drawopts['dashline']){
            controls.push(
                paper.path().attr({path: line_path, stroke: color.hex || color || Raphael.getColor(), fill: "#00CCCC", "fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'path')
            );
        }else{
            controls.push(
                paper.path().attr({path: line_path, stroke: color.hex || color || Raphael.getColor(), "stroke-width": 4, "stroke-linecap": "round"}).data("what", 'path')
            );
        }

        if(drawopts['horizontal']){
            canvasmap[canvasname]['drawopts'][legend].type = 'axis-dashline';
            controls.push(
                paper.circle(start_x, start_y, 5).attr(discattr_intersect).data("what", 'dot'),
                paper.circle(end_x, end_y, 5).attr(discattr_intersect).data("what", 'horizontal'),
                paper.text(line_path[1][1]+50, line_path[1][2]-10, legend).attr({'font-size': '10px'}).data("what", 'text'));
        }else if (drawopts['vertical']){
            canvasmap[canvasname]['drawopts'][legend].type = 'axis-dashline';
            controls.push(
                paper.circle(start_x, start_y, 5).attr(discattr_intersect).data("what", 'dot'),
                paper.circle(end_x, end_y, 5).attr(discattr_intersect).data("what", 'vertical'),
                paper.text(line_path[1][1]+50, line_path[1][2]-10, legend).attr({'font-size': '10px'}).data("what", 'text'));
        }else{
            controls.push(
                paper.circle(start_x, start_y, 5).attr(discattr_drag).data("what", 'circle'),
                paper.circle(end_x, end_y, 5).attr(discattr).data("what", 'circle'),
                paper.text(line_path[1][1]+50, line_path[1][2]-10, legend).attr({'font-size': '10px'}).data("what", 'text'));
        }
        
        controls.push(
            paper.rect(Raphael.pathBBox(line_path).x, Raphael.pathBBox(line_path).y, Raphael.pathBBox(line_path).width, Raphael.pathBBox(line_path).height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );

        
        //console.log(controls[0]);
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
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
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
            //console.log("line_path");
            //console.log(line_path[0]);
            //console.log(line_path[1]);
            
            var bb = Raphael.pathBBox(line_path);
            controls[4].attr({x: bb.x, y:bb.y, width:bb.width, height:bb.height});
            canvasmap[canvasname]['drawopts'][legend]['end_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['end_y'] = newY;
            //console.log('pppppppp   '+line_path);
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
        elemap[canvasname].push(controls);
    };

    var drawDot = function(canvasname, drawopts) {
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var discattr_drag = {fill: "#993300", stroke: "none"};
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x = drawopts['end_x'];
        var end_y = drawopts['end_y'];

        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'dot',
            start_x:start_x, start_y:start_y,
            end_x:null, end_y:null, color:colormap[canvasname],
            custom_path:null, custom_handler_path:null,
            rcoordinate:null
        }

        var controls = paper.set(
                paper.circle(start_x, start_y, 6).attr(discattr_drag).data("what", 'dot'),
                paper.text(start_x+50, start_y+15, legend).attr({'font-size': '10px'}).data("what", 'dottext')
        );

        controls[0].update = function (x, y){
            var newX = this.attr("cx") + x;
            var newY = this.attr("cy") + y;
            this.attr({cx: newX, cy: newY});
            controls[1].attr({x: newX+50, y: newY+15});
            this.toFront();
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
            controls[1].toFront();
        };
        controls[0].drag(move, start, end);
        elemap[canvasname].push(controls);
    };

    var drawTips = function(canvasname, drawopts) {
        var legend = drawopts['legend'];
        var paper = instmap[canvasname];
        var start_x = drawopts['start_x'];
        var start_y = drawopts['start_y'];
        var end_x = drawopts['end_x'];
        var end_y = drawopts['end_y'];

        canvasmap[canvasname]['drawopts'][legend] = {
            type: 'tips',
            start_x:start_x, start_y:start_y,
            end_x:null, end_y:null, color:colormap[canvasname],
            custom_path:null, custom_handler_path:null,
            rcoordinate:null
        }

        var controls = paper.set();

        controls.push(
                paper.text(start_x, start_y, legend).attr({'font-size': '10px'}).data("what", 'tipstext')
        );

        var text_bbox = controls[0].getBBox();

        controls.push(
                paper.rect(text_bbox.x, text_bbox.y, text_bbox.width, text_bbox.height).attr({fill: "#00CCCC" ,"fill-opacity": 0, stroke: "#996699", "stroke-dasharray": ". "}).data("what", 'area').hide()
        );

        controls[0].update = function (x, y){
            var newX = this.attr("x") + x;
            var newY = this.attr("y") + y;
            this.attr({x: newX, y: newY});
            canvasmap[canvasname]['drawopts'][legend]['start_x'] = newX;
            canvasmap[canvasname]['drawopts'][legend]['start_y'] = newY;
        };

        controls[1].update = function (x, y){
            var newX = this.attr("x") + x;
            var newY = this.attr("y") + y;
            this.attr({x: newX, y: newY});
            controls[0].update(x, y);
        };

        controls[1].drag(move, start, end);
        elemap[canvasname].push(controls);
    };


    var move = function(dx, dy) {
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
    };

    var start = function() {
        var animObject = null;
        if (this.data('what') === 'dot' || this.data('what') === 'circle' || this.data('what') === 'handler_circle'){
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
    };

    var end = function(){
        var animObject = null;
        if (this.data('what') === 'dot' || this.data('what') === 'circle' || this.data('what') === 'handler_circle'){
            var dot_list = [];
            var path_list = [];
            var paper = this.paper;
            paper.forEach(function(el){
                if(el.data("what") === 'path'){
                  path_list.push(el);
                }
                if(el.data("what") === 'circle' || el.data("what") === 'dot'){
                  dot_list.push(el);
                }
            });

            //eliminate self in dotlist
            for(var i = 0; i < dot_list.length; i += 1){
                if(dot_list[i] === this){
                    dot_list.splice(i, 1);
                }
            }

            if (this.data('what') === 'dot'){
                animObject = Raphael.animation({ r:6, fill: "#993300" }, 1000, 'bounce',function(){});
                attractdot(this, path_list, dot_list);
            }else{
                 for(var i = 0; i < dot_list.length; i += 1){
                    var close_dot_x = dot_list[i].attr('cx');
                    var close_dot_y = dot_list[i].attr('cy');
                    if(Math.abs(close_dot_x - this.attr('cx')) <= 23 && Math.abs(close_dot_y - this.attr('cy')) <= 23){
                        this.attr({cx: close_dot_x, cy: close_dot_y});
                        break;
                    }
                 }
                 animObject = Raphael.animation({r: 5}, 1000, 'bounce',function(){});
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
            moveend_x = -bb.x + 3;
        if (bb.y <= 0)
            moveend_y = -bb.y + 3;
        if (bb.x2 >= width)
            moveend_x = width - bb.x2 - 3;
        if (bb.y2 >= height)
            moveend_y = height - bb.y2 - 3;
        this.update(moveend_x, moveend_y);
        //this.dx = this.dy = 0;
    };


    var findattractor = function(dot, path_list){
        var moveend_x = null;
        var moveend_y = null;
        var min_dist_x = 25;
        var min_dist_y = 25;

        for(var i = 0; i < path_list.length; i += 1){
            for(var j = i + 1; j < path_list.length; j += 1){
                var intersect_dot = Raphael.pathIntersection(path_list[i].attr('path'), path_list[j].attr('path'));
                for(var k = 0; k < intersect_dot.length; k += 1){
                    var inter_x = intersect_dot[k].x;
                    var inter_y = intersect_dot[k].y;
                    var dist_x = Math.abs(inter_x - dot.attr('cx'));
                    var dist_y = Math.abs(inter_y - dot.attr('cy'));
                    if(dist_x <= 25 && dist_y <= 25){
                        if(dist_x <= min_dist_x && dist_y <= min_dist_y){
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
        return {'x': moveend_x, 'y': moveend_y};
    };


    var attractdot = function(dot, path_list, dot_list){
        moveend = findattractor(dot, path_list);
        if(moveend['x'] !== null && moveend['y'] !== null){
            dot.attr({cx: moveend['x'], cy: moveend['y']});

            if (dot.next.data("what") === 'horizontal'){
                dot.next.attr({cy: moveend['y']});
            }else if(dot.next.data("what") === 'vertical'){
                dot.next.attr({cx: moveend['x']});
            }
        }else{
            for(var i = 0; i < dot_list.length; i += 1){
                var close_dot_x = dot_list[i].attr('cx');
                var close_dot_y = dot_list[i].attr('cy');
                if(Math.abs(close_dot_x - dot.attr('cx')) <= 25 && Math.abs(close_dot_y - dot.attr('cy')) <= 25){
                    dot.attr({cx: close_dot_x, cy: close_dot_y});
                    if (dot.next.data("what") === 'horizontal'){
                            dot.next.attr({cy:close_dot_y});
                    }else if(dot.next.data("what") === 'vertical'){
                            dot.next.attr({cx:close_dot_x});
                    }
                    break;
                }
            }
        }
    }


    var drawAxis = function(canvasname, axis){
        clearDeprecatedAxis(canvasname, axis);
        var paper = instmap[canvasname];
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
            
            canvasmap[canvasname]['axis'][0] = 'axis';
            canvasmap[canvasname]['axis']['x'] = axis;
            var end_x = attributes.width - 60;
            step =  Math.round((end_x - start_x - axis['splits'] - arrow_length)/ axis['splits']);
            axis_path = [["M", start_x, start_y]];
            
            axisset.push(paper.text(start_x, start_y + 10, axis['start']));
            for (idx = 0; idx < axis['splits']; idx += 1){
                axis_path = axis_path.concat([["l", step, 0]], [["v", -mini_height]], [["h", mini_width]], [["v", mini_height]]);
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
            axismap[canvasname][0] = axisset;
        }else if (axis['direction'] === '1'){
            // vertical axis
            canvasmap[canvasname]['axis'][0] = 'axis';
            canvasmap[canvasname]['axis']['y'] = axis;
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
            axismap[canvasname][1] = axisset;
        }
    };
    
    //XY axis generation in canvas
    var drawXYAxis = function(canvasname, XYaxis){
       
        clearDeprecatedXYAxis(canvasname, XYaxis);
       
        var axis ="1";
        var paper = instmap[canvasname];
        var axis_path = undefined;
        var discattr = {fill: "#00CC00", stroke: "none"};
        var Xaxislegend = XYaxis['Xname'] ;
        var Yaxislegend = XYaxis['Yname'] ;
        
        var startX_y = attributes.height/2
        var startY_x = XYaxisorigin['startY_x'];
        var startY_y = XYaxisorigin['startY_y'];
        var startX_x = XYaxisorigin['startX_x'];
        
        var O_x = XYaxisorigin['O_x'];
        var O_y = XYaxisorigin['O_y'];
        var endY_x = XYaxisorigin['endY_x'];
        var endY_y = XYaxisorigin['endY_y'];
        var endX_x = XYaxisorigin['endX_x'];
        var endX_y = XYaxisorigin['endX_y'];
        var arrow_length = 8;
        var mini_height = 3;
        var mini_width = 1;
        var idx = 0;
        var controls = paper.set();
        var axistext;
        var step;
        var x_no = XYaxis['Xsplits']
        var x_no = parseInt(x_no)
        var y_no = XYaxis['Ysplits']
        var y_no = parseInt(y_no)
           
        if (XYaxis['X_negetive_axis_path']) {
            
            O_x = XYaxis['O_x']
            O_y = XYaxis['O_y']
            startX_x = XYaxis['startX_x']
            startX_y = XYaxis['startX_y']
            endY_x = XYaxis['endY_x']
            endY_y = XYaxis['endY_y']
            xstep = XYaxis['xstep']
            ystep = XYaxis['ystep']
            
            x_neg_dist = Math.round(O_x - startX_x)
            x_pos_dist = Math.round(endX_x - O_x)
            y_neg_dist = Math.round(endY_y - O_y)
            y_pos_dist = Math.round(O_y - startY_y)
                                    
            canvasmap[canvasname]['axis'][0] = 'xyaxis'
            canvasmap[canvasname]['axis']['x'] = XYaxis;
         
            X_negetive_axis_path = XYaxis['X_negetive_axis_path']    
           
            for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                controls.push(paper.text(O_x - (idx+1) * xstep, O_y + 10, -axistext.toFixed(2)));
            }
            controls.push(paper.path(X_negetive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
            controls.push(paper.text(O_x + 10, O_y + 10, XYaxis['Xstart']));
            
            X_positive_axis_path = XYaxis['X_positive_axis_path']      
          
            for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                controls.push(paper.text(O_x + (idx+1) * xstep, O_y + 10, axistext.toFixed(2)));
            }
            
            controls.push(paper.text(endX_x, O_y + 25, Xaxislegend).attr({"font-size":16}));
            controls.push(paper.path(X_positive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
            axismap[canvasname][0] = controls;
            
            canvasmap[canvasname]['axis']['y'] = XYaxis;
            Y_negetive_axis_path = XYaxis['Y_negetive_axis_path']
           
            for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                controls.push(paper.text(O_x - 20, O_y + (idx+1) * ystep, -axistext.toFixed(2)));
            }
            
            controls.push(paper.path(Y_negetive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
            canvasmap[canvasname]['xyaxis'] = XYaxis
           
            Y_positive_axis_path = XYaxis['Y_positive_axis_path']
            
            for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                controls.push(paper.text(O_x - 20, O_y - (idx+1) * ystep, axistext.toFixed(2)));
            }
            
            controls.push(paper.text(O_x - 40, startY_y + 5, Yaxislegend).attr({"font-size":16}));
            controls.push(paper.path(Y_positive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
            controls.push(paper.circle(startX_x, startX_y, 5).attr(discattr).data("what", 'circle').data("class", 'controller'));
            controls.push(paper.circle(endY_x+2, endY_y, 5).attr(discattr).data("what", 'circle'));

            //console.log(controls)
            Xneg_step = Math.floor(x_neg_dist/xstep)
            hide_ctrls =  XYaxis['Xsplits'] - Xneg_step
            for (idx = 0; idx < hide_ctrls; idx +=1) {
                controls[Xneg_step+idx].hide()
            }
            
            Xpos_step = Math.floor(x_pos_dist/xstep)
            hide_ctrls =  XYaxis['Xsplits'] - Xpos_step
            for (idx = 0; idx < hide_ctrls; idx +=1) {
                controls[x_no+2+Xpos_step+idx].hide()
            }
           
            Ypos_step = Math.floor(y_pos_dist/ystep)
            hide_ctrls =  XYaxis['Xsplits'] - Ypos_step
            for (idx = 0; idx < hide_ctrls; idx +=1) {
                controls[(2*x_no)+4+y_no+1+Ypos_step+idx].hide()
            }
            
            Yneg_step = Math.floor(y_neg_dist/ystep)
            hide_ctrls = XYaxis['Xsplits'] - Yneg_step
            for (idx = 0; idx < hide_ctrls; idx +=1) {
                controls[(2*x_no)+4+Yneg_step+idx].hide()
            }
        }
        else{
                XYaxis['axis'] = 'xyaxis'
                canvasmap[canvasname]['axis'][0] = 'xyaxis'
                canvasmap[canvasname]['axis']['x'] = XYaxis;
                xstep =  Math.round((endX_x - O_x)/ XYaxis['Xsplits']);
               
                // X-axis (-ve) side
                X_negetive_axis_path = [["M", O_x, O_y]];
                for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                    X_negetive_axis_path = X_negetive_axis_path.concat([["l", -xstep, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                    axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                    controls.push(paper.text(O_x - (idx+1) * xstep, O_y + 10, -axistext.toFixed(2)));
                }
                X_negetive_axis_path = X_negetive_axis_path.concat(
                        [["l", -arrow_length, 0]],
                        [["v", -(2*mini_height)]],
                        [["l", -arrow_length/2, 2*mini_height]],
                        [["l", (arrow_length/2), 2*mini_height]],
                        [["v", -(2*mini_height)]]);
                controls.push(paper.path(X_negetive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
              
                // X-axis (+ve) side
                X_positive_axis_path = [["M", O_x, O_y]];
                controls.push(paper.text(O_x + 10, O_y + 10, XYaxis['Xstart']));
                xstep = xstep - 2
                for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                    X_positive_axis_path = X_positive_axis_path.concat([["l", xstep, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                    axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                    controls.push(paper.text(O_x + (idx+1) * xstep, O_y + 10, axistext.toFixed(2)));
                }
                X_positive_axis_path = X_positive_axis_path.concat(
                       
                        [["v", -(2*mini_height)]],
                        [["l", arrow_length/2, 2*mini_height]],
                        [["l", -(arrow_length/2), 2*mini_height]],
                        [["v", -(2*mini_height)]]);
                
                XYaxis['xstep'] = xstep
                controls.push(paper.text(endX_x, O_y + 25, Xaxislegend).attr({"font-size":16}));
                controls.push(paper.path(X_positive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
                axismap[canvasname][0] = controls;
                
                canvasmap[canvasname]['axis']['y'] = XYaxis;
                ystep =  Math.round((endY_y - O_y)/ XYaxis['Ysplits']);
                Y_negetive_axis_path = [["M", O_x, O_y]];
                ystep = ystep - 1
                for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                    Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,-ystep]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                    axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                    controls.push(paper.text(O_x - 20, O_y + (idx+1) * ystep, -axistext.toFixed(2)));
                }
                Y_negetive_axis_path = Y_negetive_axis_path.concat(
                        [["v", -(arrow_length)]],
                        [["h", 2*mini_height]],
                        [["l", -(2*mini_height), -(arrow_length/2)]],
                        [["l", -(2*mini_height), arrow_length/2]],
                        [["h", 2*mini_height]]);
                
                controls.push(paper.path(Y_negetive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
                canvasmap[canvasname]['xyaxis'] = XYaxis 
                // Y-axis (+ve) side
                Y_positive_axis_path = [["M", O_x, O_y]];
                for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                    Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,ystep]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                    axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                    controls.push(paper.text(O_x - 20, O_y - (idx+1) * ystep, axistext.toFixed(2)));
                }
                Y_positive_axis_path = Y_positive_axis_path.concat(

                        [["h", 2*mini_height]],
                        [["l", -(2*mini_height), (arrow_length/2)]],
                        [["l", -(2*mini_height), -arrow_length/2]],
                        [["h", 2*mini_height]]);
                
                XYaxis['ystep'] = ystep                       
                controls.push(paper.text(O_x - 40, startY_y + 5, Yaxislegend).attr({"font-size":16}));
                controls.push(paper.path(Y_positive_axis_path).data("what", 'path').attr({fill: "#000", stroke: "#000"}));
                controls.push(paper.circle(startX_x, startX_y, 5).attr(discattr).data("what", 'circle').data("class", 'controller'));
                controls.push(paper.circle(endY_x+2, endY_y, 5).attr(discattr).data("what", 'circle'));
                axismap[canvasname][1] = controls;
            }
            //XYaxis['controls'] = controls    
            //controls[0] will uodates the path
            controls[0].update = function (x, y) {
                controls[3].update(x, y);
            };
            
            // X-axis controller
            controls[(2*x_no)+(2*y_no)+7].update = function (x,y, receiver) {
                
                // if block is executed when x-axis controller is dragged alone
                if (receiver!="Y-control"){
                    
                    var newX = this.attr("cx") + x;
                    var newY = this.attr("cy") + y;
                    this.attr({cx: startX_x, cy: newY});
                    startX_y = newY
                    XYaxis['startX_y'] = startX_y
                    XYaxis['startX_x'] = startX_x
                    XYaxis['endY_x'] = endY_x
                    XYaxis['endY_y'] = endY_y
                    
                    XYaxisorigin['startX_y'] = newY;
                    O_x = O_x
                    O_y = newY
                    dist_neg = Math.round((O_x - startX_x))
                    dist_pos = Math.round((endX_x - O_x))
                    x_neg_dist = Math.round(O_x - startX_x)
                    x_pos_dist = Math.round(endX_x - O_x)
                    XYaxis['O_x'] = O_x
                    XYaxis['O_y'] = O_y
                    ctrl_dist = Math.round(endY_y - O_y)
                    if (ctrl_dist < 5) {
                        this.attr({cx: startX_x, cy: endY_y});
                        XYaxis['startX_x'] = startX_x
                        XYaxis['startX_y'] = endY_y
                        startX_y = endY_y
                        
                    }else{
                        this.attr({cx: startX_x, cy: newY});
                        XYaxis['startX_x'] = startX_x
                        XYaxis['startX_y'] = newY
                        startX_y = newY
                    }
                    
                    if (x_pos_dist > x_neg_dist) {
                        console.log(" gggg ") 
                        step = (dist_pos)/XYaxis['Xsplits']
                        X_negetive_axis_path = [["M", O_x, O_y]];
                        x_neg_dist = Math.round(O_x - startX_x)
                        new_step = Math.floor(x_neg_dist/step)
                        XYaxis['xstep'] = step
                        
                        for (idx = 0; idx < new_step; idx += 1){
                            X_negetive_axis_path = X_negetive_axis_path.concat([["l", -step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            controls[idx].attr({x:O_x - (idx+1) * step, y:O_y + 10})
                        }
                        hide_ctrls =  XYaxis['Xsplits'] - new_step
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[new_step+idx].hide()
                        }
                        
                        if (new_step > XYaxis['Xsplits']) {
                            
                            new_step = XYaxis['Xsplits']
                        }
                        
                        occupied_length = Math.round(step * new_step)
                        needed_length = O_x - startX_x - occupied_length - arrow_length
                        X_negetive_axis_path = X_negetive_axis_path.concat([["l",-needed_length,0]])
                        
                        X_negetive_axis_path = X_negetive_axis_path.concat(
                            [["l", -arrow_length, 0]],
                            [["v", -(2*mini_height)]],
                            [["l", -arrow_length/2, 2*mini_height]],
                            [["l", (arrow_length/2), 2*mini_height]],
                            [["v", -(2*mini_height)]]);
                        
                        if (x_neg_dist > step) {
                            for (idx =0;idx < new_step; idx += 1) {
                                controls[idx].show()
                            }
                            controls[x_no].attr({path:X_negetive_axis_path})
                            XYaxis['X_negetive_axis_path'] = X_negetive_axis_path
                        }else{
                            
                            delete X_negetive_axis_path;
                            X_negetive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                                X_negetive_axis_path = X_negetive_axis_path.concat([["l",0,0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = O_x - startX_x - occupied_length - arrow_length
                            X_negetive_axis_path = X_negetive_axis_path.concat([["l",-needed_length,0]])
                            
                            X_negetive_axis_path = X_negetive_axis_path.concat(
                                [["l", -arrow_length, 0]],
                                [["v", -(2*mini_height)]],
                                [["l", -arrow_length/2, 2*mini_height]],
                                [["l", (arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                            controls[x_no].attr({path:X_negetive_axis_path})
                            XYaxis['X_negetive_axis_path'] = X_negetive_axis_path
                        }
                        
                        X_positive_axis_path = [["M", O_x, O_y]];
                        for ( idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                            X_positive_axis_path = X_positive_axis_path.concat([["l", step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            ctrl_no = idx + x_no +2
                            controls[ctrl_no].attr({x:O_x + (idx+1) * step, y:O_y + 10, text:axistext.toFixed(2)});
                        }
                        X_positive_axis_path = X_positive_axis_path.concat(
                                [["l", arrow_length, 0]],
                                [["v", -(2*mini_height)]],
                                [["l", arrow_length/2, 2*mini_height]],
                                [["l", -(arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                         
                        controls[(2*x_no)+3].attr({path:X_positive_axis_path})
                        XYaxis['X_positive_axis_path'] = X_positive_axis_path
                        controls[x_no+1].attr({x:O_x+10, y:O_y+10})
                       
                        for (idx = 0;idx < XYaxis['Xsplits'];idx += 1) {
                            controls[x_no+2+idx].show()
                        }  
                        
                    }else{
                        console.log("DIDIDIDID") 
                        step = (dist_neg)/XYaxis['Xsplits']
                        XYaxis['xstep'] = step
                        X_negetive_axis_path = [["M", O_x, O_y]];
                        controls[x_no+1].attr({x: O_x + 10, y:O_y + 10})
                        new_step = Math.floor(x_pos_dist/step)
                        
                        for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                            X_negetive_axis_path = X_negetive_axis_path.concat([["l", -step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            controls[idx].attr({x:O_x - (idx+1) * step, y:O_y + 10})
                        }
                        X_negetive_axis_path = X_negetive_axis_path.concat(
                          
                           [["v", -(2*mini_height)]],
                           [["l", -arrow_length/2, 2*mini_height]],
                           [["l", (arrow_length/2), 2*mini_height]],
                           [["v", -(2*mini_height)]]);
                        controls[x_no].attr({path: X_negetive_axis_path})
                        XYaxis['X_negetive_axis_path'] = X_negetive_axis_path
                                                
                        if (new_step > XYaxis['Xsplits']) {
                            new_step = XYaxis['Xsplits']
                        }
                        
                        X_positive_axis_path = [["M", O_x, O_y]];
                        for ( idx = 0; idx < new_step; idx += 1){
                            X_positive_axis_path = X_positive_axis_path.concat([["l", step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            ctrl_no = idx + x_no +2
                            controls[ctrl_no].attr({x:O_x + (idx+1) * step, y:O_y + 10, text:axistext.toFixed(2)});
                        }
                        
                        hide_ctrls = XYaxis['Xsplits'] - new_step
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[x_no+2+new_step+idx].hide()
                        }
                        occupied_length = Math.round(step * new_step)
                        needed_length = endX_x - O_x - occupied_length - arrow_length
                        X_positive_axis_path = X_positive_axis_path.concat([["l",needed_length,0]])
                        
                        X_positive_axis_path = X_positive_axis_path.concat(
                                [["l", arrow_length, 0]],
                                [["v", -(2*mini_height)]],
                                [["l", arrow_length/2, 2*mini_height]],
                                [["l", -(arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                        
                        if (x_pos_dist > step) {
                            for (idx =0;idx < new_step; idx += 1) {
                                controls[x_no+2+idx].show()
                            }
                            controls[(2*x_no)+3].attr({path: X_positive_axis_path})
                            XYaxis['X_positive_axis_path'] = X_positive_axis_path
                           
                        }else{
                            delete X_positive_axis_path;
                            X_positive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                                X_positive_axis_path = X_positive_axis_path.concat([["l",0,0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = endX_x - O_x - occupied_length - arrow_length
                            X_positive_axis_path = X_positive_axis_path.concat([["l",needed_length,0]])
                            
                            X_positive_axis_path = X_positive_axis_path.concat(
                                [["l", arrow_length, 0]],
                                [["v", -(2*mini_height)]],
                                [["l", arrow_length/2, 2*mini_height]],
                                [["l", -(arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                                     
                            controls[(2*x_no)+3].attr({path:X_positive_axis_path});
                            XYaxis['X_positive_axis_path'] = X_positive_axis_path
                        }
                        
                        for (idx = 0;idx < XYaxis['Xsplits'];idx += 1) {
                            controls[idx].show()
                        }  
                        controls[x_no+1].attr({x:O_x+10, y:O_y+10})
                        
                    }
                    controls[(2*x_no)+2].attr({x:endX_x, y:O_y + 25})
                    controls[(2*x_no)+(2*y_no)+8].update(x,y,"X-control")
                }
                else{
                    console.log("DUDE")
                    x_neg_dist = Math.round(O_x - startX_x)
                    x_pos_dist = Math.round(endX_x - O_x)
                    dist_neg = Math.round((O_x - startX_x)/XYaxis['Xsplits'])
                    dist_pos = Math.round((endX_x - O_x)/XYaxis['Xsplits'])
                   
                    if (x_pos_dist>x_neg_dist) {
                        console.log("MOving Left")
                        step = dist_pos 
                        X_negetive_axis_path = [["M", O_x, O_y]];
                        x_neg_dist = Math.round(O_x - startX_x)
                        new_step = Math.floor(x_neg_dist/step)
                        XYaxis['xstep'] = step
                        for (idx = 0; idx < new_step; idx += 1){
                            X_negetive_axis_path = X_negetive_axis_path.concat([["l", -step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            controls[idx].attr({x:O_x - (idx+1) * step, y:O_y + 10})
                        }
                        hide_ctrls =  XYaxis['Xsplits'] - new_step
                        if (new_step > XYaxis['Xsplits']) {
                            new_step = XYaxis['Xsplits']
                        }
                        
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[new_step+idx].hide()
                        }
                        
                        occupied_length = Math.round(step * new_step)
                        needed_length = O_x - startX_x - occupied_length - arrow_length
                        X_negetive_axis_path = X_negetive_axis_path.concat([["l",-needed_length,0]])
                        
                        X_negetive_axis_path = X_negetive_axis_path.concat(
                           
                            [["v", -(2*mini_height)]],
                            [["l", -arrow_length/2, 2*mini_height]],
                            [["l", (arrow_length/2), 2*mini_height]],
                            [["v", -(2*mini_height)]]);
                        if (x_neg_dist > step) {
                            for (idx =0;idx < new_step; idx += 1) {
                                controls[idx].show()
                            }
                            controls[x_no].attr({path:X_negetive_axis_path})
                            XYaxis['X_negetive_axis_path'] = X_negetive_axis_path
                        }else{
                            delete X_negetive_axis_path;
                            X_negetive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                                X_negetive_axis_path = X_negetive_axis_path.concat([["l",0,0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = O_x - startX_x - occupied_length - arrow_length
                            X_negetive_axis_path = X_negetive_axis_path.concat([["l",-needed_length,0]])
                            
                            X_negetive_axis_path = X_negetive_axis_path.concat(
                                [["l", -arrow_length, 0]],
                                [["v", -(2*mini_height)]],
                                [["l", -arrow_length/2, 2*mini_height]],
                                [["l", (arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                            controls[x_no].attr({path:X_negetive_axis_path})
                            XYaxis['X_negetive_axis_path'] = X_negetive_axis_path
                        }
                        
                        X_positive_axis_path = [["M", O_x, O_y]];
                        for ( idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                            X_positive_axis_path = X_positive_axis_path.concat([["l", step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            ctrl_no = idx + x_no +2
                            controls[ctrl_no].attr({x:O_x + (idx+1) * step, y:O_y + 10, text:axistext.toFixed(2)});
                        }
                        X_positive_axis_path = X_positive_axis_path.concat(

                                [["v", -(2*mini_height)]],
                                [["l", arrow_length/2, 2*mini_height]],
                                [["l", -(arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                         
                        controls[(2*x_no)+3].attr({path:X_positive_axis_path})
                        XYaxis['X_positive_axis_path'] = X_positive_axis_path
                        controls[x_no+1].attr({x:O_x+10, y:O_y+10})
                        for (idx = 0;idx < XYaxis['Xsplits'];idx += 1) {
                            controls[x_no+2+idx].show()
                        }  
                       
                    }else{
                        console.log("MOving Right")
                        step = dist_neg 
                        XYaxis['xstep'] = step
                        X_negetive_axis_path = [["M", O_x, O_y]];
                        controls[x_no+1].attr({x: O_x + 10, y:O_y + 10})
                        new_step = Math.floor(x_pos_dist/step)
                        
                        for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                            X_negetive_axis_path = X_negetive_axis_path.concat([["l", -step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            controls[idx].attr({x:O_x - (idx+1) * step, y:O_y + 10})
                        }
                        X_negetive_axis_path = X_negetive_axis_path.concat(
                          
                           [["v", -(2*mini_height)]],
                           [["l", -arrow_length/2, 2*mini_height]],
                           [["l", (arrow_length/2), 2*mini_height]],
                           [["v", -(2*mini_height)]]);
                        controls[x_no].attr({path: X_negetive_axis_path})
                        XYaxis['X_negetive_axis_path'] = X_negetive_axis_path
                        if (new_step > XYaxis['Xsplits']) {
                           new_step = XYaxis['Xsplits']
                        }
                        
                        X_positive_axis_path = [["M", O_x, O_y]];
                        for ( idx = 0; idx < new_step; idx += 1){
                            X_positive_axis_path = X_positive_axis_path.concat([["l", step, 0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            axistext = Number(XYaxis['Xstart']) + ((XYaxis['Xend'] - XYaxis['Xstart'])/XYaxis['Xsplits']) * (idx + 1);
                            ctrl_no = idx + x_no +2
                            controls[ctrl_no].attr({x:O_x + (idx+1) * step, y:O_y + 10, text:axistext.toFixed(2)});
                        }
                        hide_ctrls = XYaxis['Xsplits'] - new_step
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[x_no+2+new_step+idx].hide()
                        }
                        
                        occupied_length = Math.round(step * new_step)
                        needed_length = endX_x - O_x - occupied_length - arrow_length
                        X_positive_axis_path = X_positive_axis_path.concat([["l",needed_length,0]])
                        
                        X_positive_axis_path = X_positive_axis_path.concat(
                                [["l", arrow_length, 0]],
                                [["v", -(2*mini_height)]],
                                [["l", arrow_length/2, 2*mini_height]],
                                [["l", -(arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                        
                        if (x_pos_dist > step) {
                            for (idx =0;idx < new_step; idx += 1) {
                                controls[x_no+2+idx].show()
                            }
                            controls[(2*x_no)+3].attr({path: X_positive_axis_path})
                            XYaxis['X_positive_axis_path'] = X_positive_axis_path
                        }else{
                            delete X_positive_axis_path;
                            X_positive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < XYaxis['Xsplits']; idx += 1){
                                X_positive_axis_path = X_positive_axis_path.concat([["l",0,0]], [["v", mini_height]], [["h", mini_width]], [["v", -mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = endX_x - O_x - occupied_length - arrow_length
                            X_positive_axis_path = X_positive_axis_path.concat([["l",needed_length,0]])
                            
                            X_positive_axis_path = X_positive_axis_path.concat(
                                [["l", arrow_length, 0]],
                                [["v", -(2*mini_height)]],
                                [["l", arrow_length/2, 2*mini_height]],
                                [["l", -(arrow_length/2), 2*mini_height]],
                                [["v", -(2*mini_height)]]);
                                     
                            controls[(2*x_no)+3].attr({path:X_positive_axis_path});
                            XYaxis['X_positive_axis_path'] = X_positive_axis_path
                            
                        }
                        for (idx = 0;idx < XYaxis['Xsplits'];idx += 1) {
                            controls[idx].show()
                        }
                        controls[x_no+1].attr({x:O_x+10, y:O_y+10})
                    }
                }
               
            };
            
            
            // Y-axis controller
            controls[(2*x_no)+(2*y_no)+8].update = function (x,y,receiver) {
               
                // This if block is executed when y-axis controller is dragged
                // And rest of else blocks are executed when x-axis controller is modified
                if (receiver!='X-control') {
                    var newX = this.attr("cx") + x;
                    var newY = this.attr("cy") + y;
                    O_x = newX
                    O_y = O_y
                    XYaxis['O_x'] = O_x
                    XYaxis['O_y'] = O_y
                    startY_x = newX
                    XYaxisorigin['startY_x'] = newX
                    XYaxis['endY_x'] = endY_x
                    XYaxis['endY_y'] = endY_y
                    XYaxis['startX_y'] = startX_y
                    XYaxis['startX_x'] = startX_x
                    
                    dist_neg = Math.round((endY_y-O_y))
                    dist_pos = Math.round((O_y-startY_y))
                    ctrl_dist = Math.round(O_x - startX_x)
                    if (ctrl_dist < 5) {
                        this.attr({cx: startX_x, cy: endY_y});
                            endY_x = startX_x
                            XYaxis['endY_x'] = startX_x
                            XYaxis['endY_y'] = endY_y
                    }else{
                        this.attr({cx: newX, cy: endY_y});
                            endY_x = newX
                            XYaxis['endY_x'] = newX
                            XYaxis['endY_y'] = endY_y
                    }
                    
                    if (dist_pos>dist_neg) {
                        console.log(" hhhh ") 
                        step = Math.round(((O_y-startY_y))/XYaxis['Ysplits'])
                        XYaxis['ystep'] = step
                        Y_negetive_axis_path = [["M", O_x, O_y]];
                        y_neg_dist = Math.round(endY_y - O_y)
                                              
                        new_step = Math.floor(y_neg_dist/step);
                                  
                        for (idx = 0; idx < new_step; idx += 1){
                            Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[((2*x_no)+idx)+4].attr({x:O_x - 20, y:O_y + (idx+1) * step, text:-axistext.toFixed(2)});
                        }
                        
                        hide_ctrls =  XYaxis['Ysplits'] - new_step
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[(2*x_no)+new_step+idx+4].hide()
                        }
                        
                        if (new_step > XYaxis['Ysplits']) {
                            new_step = XYaxis['Ysplits']
                        }
                        
                        occupied_length = Math.round(step * new_step)
                        needed_length = endY_y- O_y - occupied_length - arrow_length
                        Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,needed_length]])
                        
                        Y_negetive_axis_path = Y_negetive_axis_path.concat(
                                [["v", (arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), (arrow_length/2)]],
                                [["l", -(2*mini_height), -arrow_length/2]],
                                [["h", 2*mini_height]]);
                        if (y_neg_dist>step) {
                            for (idx = 0;idx< new_step;idx+=1) {
                                controls[(2*x_no)+4+idx].show()
                            }   
                            controls[(2*x_no)+4+y_no].attr({path:Y_negetive_axis_path})
                            XYaxis['Y_negetive_axis_path'] = Y_negetive_axis_path
                        }
                        else{
                            delete Y_negetive_axis_path;
                            for (idx = 0;idx< new_step;idx+=1) {
                               controls[(2*x_no)+4+idx].hide()
                            }
                           
                            Y_negetive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < new_step; idx += 1){
                                Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,0]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = endY_y- O_y - occupied_length - arrow_length
                            Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,needed_length]])
                                                        
                            Y_negetive_axis_path = Y_negetive_axis_path.concat(
                                [["v", (arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), (arrow_length/2)]],
                                [["l", -(2*mini_height), -arrow_length/2]],
                                [["h", 2*mini_height]]);
                            controls[(2*x_no)+4+y_no].attr({path:Y_negetive_axis_path})
                            XYaxis['Y_negetive_axis_path'] = Y_negetive_axis_path
                        }
                        
                        Y_positive_axis_path = [["M", O_x, O_y]];
                        for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                            Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[(2*x_no)+4+y_no+1+idx].attr({x:O_x - 20, y:O_y - (idx+1) * step, text:axistext.toFixed(2)});
                        }
                        Y_positive_axis_path = Y_positive_axis_path.concat(
                                [["v", -(arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), -(arrow_length/2)]],
                                [["l", -(2*mini_height), arrow_length/2]],
                                [["h", 2*mini_height]]);
                        
                        for (idx = 0;idx < XYaxis['Ysplits'];idx += 1) {
                            controls[(2*x_no)+4+y_no+1+idx].show()
                        }  
                        controls[(2*x_no)+4+(2*y_no)+2].attr({path:Y_positive_axis_path});
                        XYaxis['Y_positive_axis_path'] = Y_positive_axis_path
                    }
                    else{
                        console.log("MOVING UP")
                        step = (dist_neg)/XYaxis['Ysplits']
                        XYaxis['ystep'] = step
                        Y_negetive_axis_path = [["M", O_x, O_y]];
                        y_pos_dist = Math.round(O_y - startY_y)
                        for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                            Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[((2*x_no)+idx)+4].attr({x:O_x - 20, y:O_y + (idx+1) * step, text:-axistext.toFixed(2)});
                        }
                        
                        Y_negetive_axis_path = Y_negetive_axis_path.concat(
                            [["h", 2*mini_height]],
                            [["l", -(2*mini_height), (arrow_length/2)]],
                            [["l", -(2*mini_height), -arrow_length/2]],
                            [["h", 2*mini_height]]);
                        XYaxis['Y_negetive_axis_path'] = Y_negetive_axis_path
                        
                        controls[(2*x_no)+4+y_no].attr({path:Y_negetive_axis_path})
                        new_step = Math.floor(y_pos_dist/step);
                        
                        Y_positive_axis_path = [["M", O_x, O_y]];
                        for (idx = 0; idx < new_step; idx += 1){
                            Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[(2*x_no)+4+y_no+1+idx].attr({x:O_x - 20, y:O_y - (idx+1) * step, text:axistext.toFixed(2)});
                        }
                        
                        if (new_step > XYaxis['Ysplits']) {
                           new_step = XYaxis['Ysplits']
                        }
                        
                        hide_ctrls =  XYaxis['Ysplits'] - new_step
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[(2*x_no)+new_step+idx+4+y_no+1].hide()
                        }
                        
                        occupied_length = Math.round(step * new_step)
                        needed_length = O_y - startY_y - occupied_length - arrow_length
                        Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-needed_length]])
                        
                        Y_positive_axis_path = Y_positive_axis_path.concat(
                                [["v", -(arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), -(arrow_length/2)]],
                                [["l", -(2*mini_height), arrow_length/2]],
                                [["h", 2*mini_height]]);
                        
                        if (y_pos_dist>step) {
                            for (idx = 0;idx < new_step;idx += 1) {
                               controls[(2*x_no)+4+y_no+1+idx].show()
                            }
                            controls[(2*x_no)+4+(2*y_no)+2].attr({path:Y_positive_axis_path});
                            XYaxis['Y_positive_axis_path'] = Y_positive_axis_path
                        }
                        else{
                            delete Y_positive_axis_path;
                            for (idx = 0;idx < XYaxis['Ysplits'];idx+=1) {
                               controls[(2*x_no)+4+y_no+1+idx].hide()
                            }
                            Y_positive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                                Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,0]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = O_y - startY_y - occupied_length - arrow_length
                            Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-needed_length]])
                            Y_positive_axis_path = Y_positive_axis_path.concat(
                                [["v", -(arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), -(arrow_length/2)]],
                                [["l", -(2*mini_height), arrow_length/2]],
                                [["h", 2*mini_height]]);
                            
                            controls[(2*x_no)+4+(2*y_no)+2].attr({path:Y_positive_axis_path});
                            XYaxis['Y_positive_axis_path'] = Y_positive_axis_path
                        }
                        
                        for (idx = 0;idx < XYaxis['Ysplits'];idx += 1) {
                            controls[(2*x_no)+4+idx].show()
                        }
                        
                    }
                    controls[(2*x_no)+4+(2*y_no)+1].attr({x:newX - 40, y:startY_y + 5}); 
                    controls[(2*x_no)+(2*y_no)+7].update(x,y,"Y-control");
                }
                else{
                    console.log("ELSE 8")
                    y_neg_dist = Math.round(endY_y - O_y)
                    y_pos_dist = Math.round(O_y - startY_y)
                    dist_neg = Math.round((endY_y-O_y)/XYaxis['Ysplits'])
                    dist_pos = Math.round((O_y-startY_y)/XYaxis['Ysplits'])
                    if (y_pos_dist>y_neg_dist) {
                        console.log("MOVING DOWN")
                        step = dist_pos 
                        XYaxis['ystep'] = step
                        Y_negetive_axis_path = [["M", O_x, O_y]];
                        y_neg_dist = Math.round(endY_y - O_y)
                        new_step = Math.floor(y_neg_dist/step);
                        
                        if (new_step > XYaxis['Ysplits']) {
                            new_step = XYaxis['Ysplits']
                        }          
                        for (idx = 0; idx < new_step; idx += 1){
                            Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[((2*x_no)+idx)+4].attr({x:O_x - 20, y:O_y + (idx+1) * step, text:-axistext.toFixed(2)});
                        }
                        
                        // Making new step as 0 when it exceeding 0
                        if (new_step < 0) {
                            new_step = 0
                        }
                        // hiding the spliiting text when it is not needed 
                        hide_ctrls =  XYaxis['Ysplits'] - new_step
                       
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[(2*x_no)+new_step+idx+4].hide()
                        }
                       
                        occupied_length = Math.round(step * new_step)
                        needed_length = endY_y- O_y - occupied_length - arrow_length
                        Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,needed_length]])
                        
                        Y_negetive_axis_path = Y_negetive_axis_path.concat(
                               
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), (arrow_length/2)]],
                                [["l", -(2*mini_height), -arrow_length/2]],
                                [["h", 2*mini_height]]);
                       
                        if (y_neg_dist>step) {
                            for (idx = 0;idx< new_step;idx+=1) {
                                controls[(2*x_no)+4+idx].show()
                            }   
                            controls[(2*x_no)+4+y_no].attr({path:Y_negetive_axis_path})
                            XYaxis['Y_negetive_axis_path'] = Y_negetive_axis_path
                        }
                        else{
                            delete Y_negetive_axis_path;
                            for (idx = 0;idx< new_step;idx+=1) {
                               controls[(2*x_no)+4+idx].hide()
                            }
                           
                            Y_negetive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < new_step; idx += 1){
                                Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,0]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = endY_y- O_y - occupied_length - arrow_length
                            Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,needed_length]])
                                                        
                            Y_negetive_axis_path = Y_negetive_axis_path.concat(
                                [["v", (arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), (arrow_length/2)]],
                                [["l", -(2*mini_height), -arrow_length/2]],
                                [["h", 2*mini_height]]);
                            controls[(2*x_no)+4+y_no].attr({path:Y_negetive_axis_path})
                            XYaxis['Y_negetive_axis_path'] = Y_negetive_axis_path
                            
                        }
                        
                        Y_positive_axis_path = [["M", O_x, O_y]];
                        for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                            Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[(2*x_no)+4+y_no+1+idx].attr({x:O_x - 20, y:O_y - (idx+1) * step, text:axistext.toFixed(2)});
                        }
                        Y_positive_axis_path = Y_positive_axis_path.concat(
                                [["v", -(arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), -(arrow_length/2)]],
                                [["l", -(2*mini_height), arrow_length/2]],
                                [["h", 2*mini_height]]);
                        
                        for (idx = 0;idx < XYaxis['Ysplits'];idx += 1) {
                            controls[(2*x_no)+4+y_no+1+idx].show()
                        }  
                        controls[(2*x_no)+(2*y_no)+7].update(x,y,"Y-control");
                        controls[(2*x_no)+2].attr({x:endX_x, y:O_y + 25})
                        controls[(2*x_no)+4+(2*y_no)+2].attr({path:Y_positive_axis_path});
                        XYaxis['Y_positive_axis_path'] = Y_positive_axis_path
                    }
                    else{
                        console.log("MOVING UP")
                        step = dist_neg 
                        XYaxis['ystep'] = step
                        Y_negetive_axis_path = [["M", O_x, O_y]];
                        y_pos_dist = Math.round(O_y - startY_y)
                        for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                            Y_negetive_axis_path = Y_negetive_axis_path.concat([["l",0,step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[((2*x_no)+idx)+4].attr({x:O_x - 20, y:O_y + (idx+1) * step, text:-axistext.toFixed(2)});
                        }
                        
                        Y_negetive_axis_path = Y_negetive_axis_path.concat(
                            [["h", 2*mini_height]],
                            [["l", -(2*mini_height), (arrow_length/2)]],
                            [["l", -(2*mini_height), -arrow_length/2]],
                            [["h", 2*mini_height]]);
                        
                        controls[(2*x_no)+4+y_no].attr({path:Y_negetive_axis_path})
                        XYaxis['Y_negetive_axis_path'] = Y_negetive_axis_path
                        new_step = Math.floor(y_pos_dist/step);
                        if (new_step > XYaxis['Ysplits']) {
                            new_step = XYaxis['Ysplits']
                        }
                        
                        Y_positive_axis_path = [["M", O_x, O_y]];
                        for (idx = 0; idx < new_step; idx += 1){
                            Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-step]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            axistext = Number(XYaxis['Ystart']) + ((XYaxis['Yend'] - XYaxis['Ystart'])/XYaxis['Ysplits']) * (idx + 1);
                            controls[(2*x_no)+4+y_no+1+idx].attr({x:O_x - 20, y:O_y - (idx+1) * step, text:axistext.toFixed(2)});
                        }
                        
                        if (new_step < 0) {
                            new_step = 0
                        }
                        
                        hide_ctrls =  XYaxis['Ysplits'] - new_step
                        for (idx = 0; idx < hide_ctrls; idx +=1) {
                            controls[(2*x_no)+new_step+idx+4+y_no+1].hide()
                        }
                        
                        occupied_length = Math.round(step * new_step)
                        needed_length = O_y - startY_y - occupied_length - arrow_length
                        Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-needed_length]])
                        
                        Y_positive_axis_path = Y_positive_axis_path.concat(
                                [["v", -(arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), -(arrow_length/2)]],
                                [["l", -(2*mini_height), arrow_length/2]],
                                [["h", 2*mini_height]]);
                        
                        if (y_pos_dist>step) {
                            for (idx = 0;idx < new_step;idx += 1) {
                               controls[(2*x_no)+4+y_no+1+idx].show()
                            }
                            controls[(2*x_no)+4+(2*y_no)+2].attr({path:Y_positive_axis_path});
                            XYaxis['Y_positive_axis_path'] = Y_positive_axis_path
                        }
                        else{
                            delete Y_positive_axis_path;
                            for (idx = 0;idx < XYaxis['Ysplits'];idx+=1) {
                               controls[(2*x_no)+4+y_no+1+idx].hide()
                            }
                            Y_positive_axis_path = [["M", O_x, O_y]];
                            for (idx = 0; idx < XYaxis['Ysplits']; idx += 1){
                                Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,0]],[["h",-mini_height]],[["v",mini_width]],[["h",mini_height]]);
                            }
                            occupied_length = Math.round(step * new_step)
                            needed_length = O_y - startY_y - occupied_length - arrow_length
                            Y_positive_axis_path = Y_positive_axis_path.concat([["l",0,-needed_length]])
                            Y_positive_axis_path = Y_positive_axis_path.concat(
                                [["v", -(arrow_length)]],
                                [["h", 2*mini_height]],
                                [["l", -(2*mini_height), -(arrow_length/2)]],
                                [["l", -(2*mini_height), arrow_length/2]],
                                [["h", 2*mini_height]]);
                            
                            controls[(2*x_no)+4+(2*y_no)+2].attr({path:Y_positive_axis_path});
                            XYaxis['Y_positive_axis_path'] = Y_positive_axis_path
                        }
                        
                        for (idx = 0;idx < XYaxis['Ysplits'];idx += 1) {
                            controls[(2*x_no)+4+idx].show()
                        }   
                        controls[(2*x_no)+2].attr({x:endX_x, y:O_y + 25})
                        controls[(2*x_no)+(2*y_no)+7].update(x,y,"Y-control");
                        
                    }
                   
                }
                   
                };
            
            controls[(2*x_no)+(2*y_no)+7].drag(move, start, end);
            controls[(2*x_no)+(2*y_no)+8].drag(move, start, end);
    };

    var clearDeprecatedAxis = function(canvasname, axis){
        if (axis['direction'] === '0' && axismap[canvasname][0]){
           // console.log('horizontal axis already exist');
            delete canvasmap[canvasname]['axis']['x'];
            axismap[canvasname][0].remove();
            delete axismap[canvasname][0];
        }else if (axis['direction'] === '1' && axismap[canvasname][1]){
            //console.log('vertical axis already exist');
            delete canvasmap[canvasname]['axis']['y'];
            axismap[canvasname][1].remove();
            delete axismap[canvasname][1];
        }
    };
    
    var clearDeprecatedXYAxis = function(canvasname, XYaxis){
        if (canvasmap[canvasname]['axis'][0] === 'xyaxis' && axismap[canvasname][0]) {
            
            delete canvasmap[canvasname]['axis']['x'];
            delete canvasmap[canvasname]['axis']['y'];
            axismap[canvasname][0].remove();
            delete axismap[canvasname][0];
            
        }
        
    }
    
    var drawSelectionArea = function(parent,x1,y1,x2,y2){
        //console.log('draw selectionArea | x1:' +x1+',y1:' +y1+',x2:' +x2+',y2:' +y2);
        var canvasname = $(parent).attr('id');
        var paper = instmap[canvasname];
        var start_x, start_y, selection_width, selection_height;
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
            curSelectionArea.attr({x: start_x, y: start_y, width: selection_width, height: selection_height});
        }else{
            curSelectionArea = paper.rect(start_x, start_y, selection_width, selection_height).attr({fill: "#aaa", stroke: "#eee", opacity: 0.3});
        }
    };


    var calculateRules = function(thiscanvas,x1,y1,x2,y2){
        //calculate all points rules in this function
        // console.log("calculateRules | x1:"+x1+",y1:"+y1+",x2:"+x2+",y2:"+y2);
        var area = [x1, y1, x2, y2];
        var elist = elemap[thiscanvas];
        console.log('elist'+elist);
        var curveelemlist = [];
        var rulelist = [];

        //there should be two kinds of relationship of rule.
        //1, curve and curve(I don't think curve and point is useful)
        //2, circle and circle(start,middle,end point)
        elist.forEach(function(elset){
                console.log('elset     '+elset);
            var curveelem = getcurveelemlist(elset, area);
            //console.log('curveelem'+curveelem);
            if (curveelem){
                curveelemlist.push(curveelem);
            }
        });

        //generate intesectpoints to help fuzzy intesect check
        intesect_set = getintesect_set(thiscanvas, curveelemlist, area);

        //generate rules according to curveelemlist
        for (var i = 0 ; i < curveelemlist.length; i += 1){
            for( var j = 0; j < i; j += 1){
                var rules = [];
                console.log("curveelemlist[i]['complete'] = "+curveelemlist[i]['complete']+"    curveelemlist[j]['complete']  = "+curveelemlist[j]['complete'])
                if (curveelemlist[i]['complete'] === true && curveelemlist[j]['complete'] === true){
                    //console.log('curve analysis');
                    if(curveelemlist[i]['legend'] < curveelemlist[j]['legend'])
                        rules = getcurverules(thiscanvas, curveelemlist[i], curveelemlist[j]);
                    else{
                        rules = getcurverules(thiscanvas, curveelemlist[j], curveelemlist[i]);
                    }
                }else if (curveelemlist[i]['type'] !== 'dot' && curveelemlist[j]['type'] !== 'dot'){
                    //console.log('curve point analysis');
                    if(curveelemlist[i]['legend'] < curveelemlist[j]['legend'])
                        rules = getpointrules(thiscanvas, curveelemlist[i], curveelemlist[j]);
                    else{
                        rules = getpointrules(thiscanvas, curveelemlist[j], curveelemlist[i]);
                    }
                }else if (curveelemlist[i]['type'] === 'dot' || curveelemlist[j]['type'] === 'dot'){
                    //console.log('dot-curve analysis');
                    rules = getdotrules(thiscanvas, curveelemlist[i], curveelemlist[j], area);
                }
                
                for(var ri = 0; ri < rules.length; ri += 1){
                    rulelist.push(rules[ri]);
                }
            }
            
            if (canvasmap[thiscanvas]['axis'][0] === 'axis') {
               
                var axisrule = getaxisrules(curveelemlist[i]);
                if (axisrule.length > 0){
                    rulelist.push(axisrule);
                }
            }
           if (canvasmap[thiscanvas]['axis'][0] === 'xyaxis') {
               
                var XYaxisrule = getXYaxisrules(curveelemlist[i]);
                if (XYaxisrule.length > 0){
                    rulelist.push(XYaxisrule);
                }
           }
           
        }
        return rulelist;
    };


    var listRules = function(thiscanvas, rulelist){
        if (!isobjectnull(rulelist)){
            var ruletable = '#list' + thiscanvas;
            $(ruletable).css('display','table-cell');
            $(ruletable + ' thead tr').remove();
            $(ruletable + ' thead a').remove();
            $(ruletable + ' thead').append("<tr><th class='intemasscanvas-table'> Point No.</th><th class='intemasscanvas-table'> (Type)Legend[Point]  </th><th class='intemasscanvas-table'> Relation  </th><th class='intemasscanvas-table'> (Type)Legend[Point]</th></tr>");
            $(ruletable + ' tbody tr').remove();

            for (var i = 0; i < rulelist.length; i += 1){
                var ruletd = '';
                for(var j = 0; j < 4; j += 1){
                    rulelist[i][j] = rulelist[i][j].replace(' ', '');
                    ruletd += '<td>' + rulelist[i][j] + "</td>";
                }
                $(ruletable + ' tbody').append("<tr>" + ruletd + "</tr>");
            }
            canvasmap[thiscanvas]['rulelist'] = rulelist;
        }
    };

    var getpointlist = function(point, rule){
        var key = rule[1].charAt(0);
        var retpoint;
        switch (key){
            case 'L':
                if (!point.P1) point.P1 = 0;
                point.P1 += 1;
                retpoint = 'P1.' + point.P1;
                break;
            case 'R':
                if (!point.P1) point.P1 = 0;
                point.P1 += 1;
                retpoint = 'P1.' + point.P1;
                break;
            case 'A':
                if (!point.P2) point.P2 = 0;
                point.P2 += 1;
                retpoint = 'P2.' + point.P2;
                break;
            case 'B':
                if (!point.P2) point.P2 = 0;
                point.P2 += 1;
                retpoint = 'P2.' + point.P2;
                break;
            case 'O':
                if (!point.P3) point.P3 = 0;
                point.P3 += 1;
                retpoint = 'P2.' + point.P3;
                break;
            case 'I':
                if (!point.P4) point.P4 = 0;
                point.P4 += 1;
                retpoint = 'P4.' + point.P4;
                break;
            default:
                if (!point.P5) point.P5 = 0;
                point.P5 += 1;
                retpoint = 'P5.' + point.P5;
                break;
        }
        return retpoint;
    };


    // exchange start and end point to ensure little one on the left
    var normalizepoint = function(area){
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
    };
    
    var getrcoordinate = function(path,is_what){
        var box = Raphael.pathBBox(path);

        if (typeofpath(path,is_what) === 'complexcurve'){
            return [getrelativesize(path[0][1],path[0][2], box), getrelativesize(path[1][1], path[1][2], box),
                   getrelativesize(path[3][3],path[3][4], box), getrelativesize(path[3][5], path[3][6], box),
                   getrelativesize(path[2][1], path[2][2], box), getrelativesize(path[1][5], path[1][6], box),
                   getrelativesize(path[3][1], path[3][2], box)];
        }else if (typeofpath(path,is_what) === 'curve'){
            return [getrelativesize(path[1][1], path[1][2], box), getrelativesize(path[1][3], path[1][4], box),
                    getrelativesize(path[0][1], path[0][2], box), getrelativesize(path[1][5], path[1][6], box)];
        }else if (typeofpath(path,is_what)  === 'simplecurve'){
            return [getrelativesize(path[1][1], path[1][2], box), getrelativesize(path[1][3], path[1][4], box),
                    getrelativesize(path[0][1], path[0][2], box)];
        }else if (typeofpath(path,is_what) === 'line'){
            return [[0,0], [1,1]];
        }else if (typeofpath(path,is_what) === 'circle'){
         
            return [getrelativesize(path[0][0], path[0][1], box),getrelativesize(path[1][0], path[1][1], box)];
        }
        else if (typeofpath(path,is_what) === 'triangle'){
            
            return [getrelativesize(path[0][1],path[0][2], box), getrelativesize(path[1][1], path[1][2], box),
                   getrelativesize(path[2][1],path[2][2], box)];
        }
        else if (typeofpath(path,is_what) === 'rectangle'){
            
            return [getrelativesize(path[0][1],path[0][2], box), getrelativesize(path[1][1], path[1][2], box),
                   getrelativesize(path[2][1],path[2][2], box),getrelativesize(path[3][1],path[3][2], box)];
        }
        else if (typeofpath(path,is_what) === 'square'){
            return [getrelativesize(path[0][1],path[0][2], box), getrelativesize(path[1][1], path[1][2], box),
                   getrelativesize(path[2][1],path[2][2], box),getrelativesize(path[3][1],path[3][2], box)];
        }
        else if (is_what === 'ellipse'){
            return [getrelativesize(path[0][0],path[0][1], box), getrelativesize(path[1][0], path[1][1], box),getrelativesize(path[1][0], path[1][1], box)];
        }
        };


    var typeofpath = function(path, is_what){
        var curvetype;
        if(path.length === 4){
           curvetype = 'triangle'
        }
        else if (path.length === 3) {
            //curvetype = 'triangle'
            if (is_what === 'triangle') {
                curvetype = 'triangle'
            }
            else{
                curvetype = 'circle'
            }
        }
        
        else if (path.length === 5) {
            //curvetype = 'square'
            if (is_what === 'rectangle') {
                curvetype = 'rectangle'
            }
            else{
                curvetype = 'square'
            }
        }
        else{
            if(path[1][0] === 'L'){
                curvetype = 'line';
            }else if(path[1][0] === 'C'){
                curvetype = 'curve';
            }else if(path[1][0] === 'A'){
                curvetype = 'circle'
            }else if(path[1][0] === 'Q'){
                curvetype = 'simplecurve'
            }
        }
        return curvetype;
    };
   
    var getrelativesize = function(cx, cy, box){
        var x = box['x'];
        var y = box['y'];
        var x2 = box['x2'];
        var y2 = box['y2'];
        var width = box['width'], height = box['height'];
        return [(cx - x)/ width, (cy - y)/ height];
    };


    var getcurvepath = function(curve){
        var c_elem = curve['elem'];
        var c_path = c_elem[c_elem.length-1]['location'];
        return Raphael.pathBBox(c_path);
    };


    var curvecompare3p = function(canvasname, c1, c2){
        var rule;
        if (getcurveintesectpoint(canvasname, c1, c2, [])){
            rule = 'Intersect';
        }else{
            var c1_pathbox = getcurvepath(c1);
            var c2_pathbox = getcurvepath(c2);
            if ((c1_pathbox['y'] + c1_pathbox['height']/2) > (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) < (c2_pathbox['x'] + c2_pathbox['width']/2))){
                rule = 'Below';
            }else if ((c1_pathbox['y'] + c1_pathbox['height']/2) < (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) > (c2_pathbox['x'] + c2_pathbox['width']/2))){
                rule = 'Above';
            }else{
                rule = 'Undefined';
            }
        }
        return rule;
    };


    var curvecompare2p = function(canvasname, c1, c2){
        var relation;
        if (getcurveintesectpoint(canvasname, c1, c2, [])){
            relation = 'Intersect';
        }else{
            var c1_pathbox = getcurvepath(c1);
            var c2_pathbox = getcurvepath(c2);
            if ((c1_pathbox['y'] + c1_pathbox['height']/2) > (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) < (c2_pathbox['x'] + c2_pathbox['width']/2))){
                relation = 'Below';
            }else if ((c1_pathbox['y'] + c1_pathbox['height']/2) < (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) > (c2_pathbox['x'] + c2_pathbox['width']/2))){
                relation = 'Above';
            }else{
                relation = 'Undefined';
            }
        }
        return relation;
    };


    var curvecompare2_3p = function(canvasname, c1, c2){
        var relation;
        if (getcurveintesectpoint(canvasname, c1, c2, [])){
            relation = 'Intersect';
        }else{
            var c1_pathbox = getcurvepath(c1);
            var c2_pathbox = getcurvepath(c2);
            if ((c1_pathbox['y'] + c1_pathbox['height']/2) > (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) < (c2_pathbox['x'] + c2_pathbox['width']/2))){
                relation = 'Below';
            }else if ((c1_pathbox['y'] + c1_pathbox['height']/2) < (c2_pathbox['y'] + c2_pathbox['height']/2) &&
                    ((c1_pathbox['x'] + c1_pathbox['width']/2) > (c2_pathbox['x'] + c2_pathbox['width']/2))){
                relation = 'Above';
            }else{
                relation = 'Undefined';
            }
        }
        return relation;
    };


    var getcurverules = function(canvasname, c1, c2){
        var rules = [];
        
        if (c1['type'] === 'complexcurve' && c2['type'] === 'complexcurve'){
            relation = curvecompare3p(canvasname, c1, c2);
            rules = generatecurverule(relation, c1, c2);
        }else if (c1['type'] !== 'complexcurve' && c2['type'] !== 'complexcurve'){
            relation = curvecompare2p(canvasname, c1, c2);
            rules = generatecurverule(relation, c1, c2);
        }else{
            if (c1['type'] !== 'complexcurve' && c2['type'] === 'complexcurve'){
                relation = curvecompare2_3p(canvasname, c1, c2);
                rules = generatecurverule(relation, c1, c2);
            }else{
                relation = curvecompare2_3p(canvasname, c2, c1);
                rules = generatecurverule(relation, c2, c1);
            }
        }
        return rules;
    };


    var generatecurverule = function(relation, c1, c2){
        var rules = [];
        if (relation === 'Undefined'){
            rules.push(["(" + c1['type'] + ")" + c1['legend'] + ' ',
                    'Above ',
                    "(" + c2['type'] + ") " + c2['legend'] + ' ']);
            rules.push(["(" + c1['type'] + ")" +  c1['legend'] + ' ',
                    'Below ',
                    "(" + c2['type'] + ")" + c2['legend'] + ' ']);
        }else{
            rules.push(["(" + c1['type'] + ")" +  c1['legend'] + ' ',
                    relation + " ",
                    "(" + c2['type'] + ")" + c2['legend'] + ' ']);
        }
        return rules;
    };


    var getpointrules = function(canvasname, c1, c2){
        var rules = [];
        var rulelang;
        /*only compare points : last one (path) don't need compare*/
        for (var i = 0; i < c1['elem'].length - 1; i+=1){
            for (var j = 0; j < c2['elem'].length - 1; j+=1){
                rulelang = ["(" + c1['type'] + ")" + c1['legend'] + "[" + c1['elem'][i]['name'] + "] ",
                           dotcompare(c1['elem'][i], c2['elem'][j]) + " ",
                           "(" + c2['type'] + ")" + c2['legend'] + "[" + c1['elem'][i]['name'] + "] "];
                rules.push(rulelang);
            }
        }
        return rules;
    };


    var ispointinsidecurve = function(dot, curve){
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
    };

    var foundintesectpoint = function(curvelegend, dot_x, dot_y){
        for (var i = 0; i < intesect_set.length; i += 1){
            var row = intesect_set[i];
            for (var j = 0; j < row.length; j += 1){
                //legend name in intesect_set
                if(curvelegend === row[j][0] || curvelegend === row[j][1]){
                    var intesectpoints = row[j][2];
                    if (intesectpoints.length > 0){
                        for (var k = 0; k < intesectpoints.length; k += 1){
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
    };


    var getdotrules = function(canvasname, c1, c2, area){
        var rules = [];
        var dot;
        var curve;
        if (c1['type'] === 'dot' && c2['type'] === 'dot'){
            rules.push(["(" + c1['type'] + ")" + c1['legend'] + ' ',
                        dotcompare(c1['elem'][0], c2['elem'][0]) + " ",
                        "(" + c2['type'] + ")" + c2['legend'] + ' ']);
            return rules;
        }else if(c1['type'] === 'dot'){
           dot = c1;
           curve = c2;
        }else{
           dot = c2;
           curve = c1;
        }
        if(ispointinsidecurve(dot, curve)){
            rules.push(["(" + dot['type'] + ")" + dot['legend'] + ' ', "On ",
            "(" + curve['type'] + ") " + curve['legend'] + ' ']);
        }else{
            for (var i = 0, elemlength = curve['elem'].length - 1;  i < elemlength; i  +=  1){
                rules.push(["(" + dot['type'] + ")" + dot['legend'] + ' ',
                dotcompare(dot['elem'][0], curve['elem'][i]) + " ",
                "(" + curve['type'] + ")" + curve['legend'] + "[" + curve['elem'][i]['name'] + "] "]);
            }
        }
        return rules;
    };


    var dotcompare = function(p1, p2){
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
    };

    var getaxisrules = function(curve){
        var rules = [];
        var dot;
        if (curve['type'] === 'dot'){
            dot = curve['elem'][0];
            if(dotaxiscompare(dot)){
                rules.push('(' + curve['type'] + ')' + curve['legend'],
                    'On ', dotaxiscompare(dot) + ' ');
            }
        }else{
            for (var i = 0, dotcount = curve['elem'].length - 1; i < dotcount; i += 1){
                dot = curve['elem'][i];
                if(dotaxiscompare(dot)){
                    rules.push('(' + curve['type'] + ')' + curve['legend'] + '[' + dot['name'] + '] ',
                        'On ', dotaxiscompare(dot) + ' ');
                }
            }
        }
        return rules;
    };
    
    
    var dotaxiscompare = function(dot){
        var axisname;
        if (dot['location'][0] === axisorigin['start_x'] && dot['location'][1] === axisorigin['start_y']){
            axisname = 'coordinate origin';
        }else if(dot['location'][0] === axisorigin['start_x']){
            axisname = 'y-axis';
        }else if(dot['location'][1] === axisorigin['start_y']){
            axisname = 'x-axis';
        }else{
            axisname = '';
        }
        return axisname;
    };

    // This function get the rules for XY-axis
    var getXYaxisrules = function(curve){
        var rules = [];
        var dot;
        if (curve['type'] === 'dot'){
            dot = curve['elem'][0];
            if(dotXYaxiscompare(dot)){
                rules.push('(' + curve['type'] + ')' + curve['legend'],
                    'On ', dotXYaxiscompare(dot) + ' ');
            }
        }else{
            for (var i = 0, dotcount = curve['elem'].length - 1; i < dotcount; i += 1){
                dot = curve['elem'][i];
                
                if(dotXYaxiscompare(dot)){
                    rules.push('(' + curve['type'] + ')' + curve['legend'] + '[' + dot['name'] + '] ',
                        'On ', dotXYaxiscompare(dot) + ' ');
                }
            }
            
        }
        return rules;
    };
    
    var dotXYaxiscompare = function(dot){
       var axisname;
       
       if ((Math.abs(dot['location'][0] - XYaxisorigin['startY_x']) < 3) && (Math.abs(dot['location'][1] - XYaxisorigin['startX_y']) < 3)){
           axisname = 'coordinate origin';
           
       }else if(Math.abs(dot['location'][0] - XYaxisorigin['startY_x']) < 3){
           axisname = 'y-axis';
       }else if(Math.abs(dot['location'][1] - XYaxisorigin['startX_y']) < 5){
           axisname = 'x-axis';
       }else{
           axisname = '';
       }
       return axisname;
    };
    

    var getcomplexcurveelem = function(elset, area){
        var complexcurveelem = {'type': 'complexcurve', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[2], area)){
            complexcurveelem['elem'].push({'name': 'Start', 'location': [elset[2].attr('cx'), elset[2].attr('cy')]});
               // console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[5], area)){
            complexcurveelem['elem'].push({'name': 'End', 'location': [elset[5].attr('cx'), elset[5].attr('cy')]});
            //console.log('end in selectarea');
        }
        if (isdotinselectedarea(elset[6], area)){
            complexcurveelem['elem'].push({'name': 'Middle', 'location': [elset[6].attr('cx'), elset[6].attr('cy')]});
            //console.log('middle in selectarea');
        }
        complexcurveelem['elem'].push({'name': 'Path', 'location': elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            complexcurveelem['complete'] = true;
        }else{
            complexcurveelem['complete'] = false;
        }
        return complexcurveelem;
    };


    var getcurveintesectpoint = function(canvasname, c1, c2, area){
        var c1_elem = c1['elem'];
        var c2_elem = c2['elem'];
        var c1_path = c1_elem[c1_elem.length-1]['location'];
        var c2_path = c2_elem[c2_elem.length-1]['location'];
        var dot = Raphael.pathIntersection(c1_path, c2_path);
        if ( dot.length > 0){
            return dot;
        }
        return false;
    };

    var isdotinselectedarea = function(pointset, area){
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
    };

    var getcurveelem = function(elset, area){
        var curveelem = {'type': 'curve', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[2], area)){
            curveelem['elem'].push({'name':'Start', 'location':[elset[2].attr('cx'), elset[2].attr('cy')]});
            //console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[5], area)){
            curveelem['elem'].push({'name': 'End', 'location': [elset[5].attr('cx'), elset[5].attr('cy')]});
            //console.log('end in selectarea');
        }
        curveelem['elem'].push({'name': 'Path','location': elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            curveelem['complete'] = true;
        }else{
            curveelem['complete'] = false;
        }
        return curveelem;
    };
    
    var gettrianglelem = function(elset, area){
        
        var trianglelem = {'type': 'triangle', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[1], area)){
            trianglelem['elem'].push({'name':'Start', 'location':[elset[1].attr('cx'), elset[1].attr('cy')]});
            //console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[2], area)){
            trianglelem['elem'].push({'name':'Middle', 'location':[elset[2].attr('cx'), elset[1].attr('cy')]});
            //console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[3], area)){
            trianglelem['elem'].push({'name': 'End', 'location': [elset[3].attr('cx'), elset[3].attr('cy')]});
            //console.log('end in selectarea');
        }
        
        trianglelem['elem'].push({'name':'Path', 'location':elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            trianglelem['complete'] = true;
        }else{
            trianglelem['complete'] = false;
        }
        return trianglelem;
        
    };
    
    var getrectelem = function(elset, area){

        var getrectelem = {'type': 'rectangle', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[1], area)){
            getrectelem['elem'].push({'name':'Start', 'location':[elset[1].attr('cx'), elset[1].attr('cy')]});
            //console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[3], area)){
            getrectelem['elem'].push({'name': '2ndord', 'location': [elset[2].attr('cx'), elset[2].attr('cy')]});
            //console.log('end in selectarea');
        }
        if (isdotinselectedarea(elset[1], area)){
            getrectelem['elem'].push({'name':'3rdord', 'location':[elset[3].attr('cx'), elset[3].attr('cy')]});
            //console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[3], area)){
            getrectelem['elem'].push({'name': 'End', 'location': [elset[4].attr('cx'), elset[4].attr('cy')]});
            //console.log('end in selectarea');
        }
        
        getrectelem['elem'].push({'name':'Path', 'location':elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            getrectelem['complete'] = true;
        }else{
            getrectelem['complete'] = false;
        }
        return getrectelem;
        
    };
    
     var getsqrelem = function(elset, area){

        var getsqrelem = {'type': 'square', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[1], area)){
            getsqrelem['elem'].push({'name':'Start', 'location':[elset[1].attr('cx'), elset[1].attr('cy')]});
            //console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[3], area)){
            getsqrelem['elem'].push({'name': '2ndord', 'location': [elset[2].attr('cx'), elset[2].attr('cy')]});
            //console.log('end in selectarea');
        }
        if (isdotinselectedarea(elset[1], area)){
            getsqrelem['elem'].push({'name':'3rdord', 'location':[elset[3].attr('cx'), elset[3].attr('cy')]});
            //console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[3], area)){
            getsqrelem['elem'].push({'name': 'End', 'location': [elset[4].attr('cx'), elset[4].attr('cy')]});
            //console.log('end in selectarea');
        }
        
        getsqrelem['elem'].push({'name':'Path', 'location':elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            getsqrelem['complete'] = true;
        }else{
            getsqrelem['complete'] = false;
        }
        return getsqrelem;
        
    };
    
    var getlineelem = function(elset, area){
       
        var lineelem = {'type': 'line','legend': elset.getlegend(), 'elem':[]};
        if (isdotinselectedarea(elset[1], area)){
            //console.log('start in selectarea');
            lineelem['elem'].push({'name':'Start', 'location':[elset[1].attr('cx'),elset[1].attr('cy')]});
        }
        if (isdotinselectedarea(elset[2], area)){
            lineelem['elem'].push({'name':'End', 'location':[elset[2].attr('cx'),elset[2].attr('cy')]});
       //     console.log('end in selectarea');
        }
        lineelem['elem'].push({'name':'Path', 'location':elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            lineelem['complete'] = true;
        }else{
            lineelem['complete'] = false;
        }
        return lineelem;
    };

    var getdotelem = function(elset, area){
        var dotelem, elem = [];
        if(isdotinselectedarea(elset[0], area)){
         //   console.log('dot in selectarea');
            elem.push({'name':'Dot','location':[elset[0].attr('cx'),elset[0].attr('cy')]});
            dotelem = {'type':'dot', 'legend': elset.getlegend(), 'elem':elem, 'complete':false};
        }
        return dotelem;
    };


    var getsimplecurveelem = function(elset, area){
        var simplecurveelem = {'type': 'curve', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[1], area)){
            simplecurveelem['elem'].push({'name':'Start', 'location':[elset[1].attr('cx'), elset[1].attr('cy')]});
 //           console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[3], area)){
            simplecurveelem['elem'].push({'name': 'End', 'location': [elset[3].attr('cx'), elset[3].attr('cy')]});
   //         console.log('end in selectarea');
        }
        simplecurveelem['elem'].push({'name': 'Path','location': elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            simplecurveelem['complete'] = true;
        }else{
            simplecurveelem['complete'] = false;
        }
        return simplecurveelem;
    };
    
    var getcircleelem = function(elset, area){
        var circleelem = {'type': 'circle', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[1], area)){
            circleelem['elem'].push({'name':'Start', 'location':[elset[1].attr('cx'), elset[1].attr('cy')]});
            //           console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[2], area)){
            circleelem['elem'].push({'name': 'End', 'location': [elset[2].attr('cx'), elset[2].attr('cy')]});
            //         console.log('end in selectarea');
        }
        circleelem['elem'].push({'name': 'Path','location': elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            circleelem['complete'] = true;
        }else{
            circleelem['complete'] = false;
        }
        return circleelem;
    };
    var getellipseelem = function(elset, area){
        var ellipseelem = {'type': 'ellipse', 'legend': elset.getlegend(), 'elem': []};
        if (isdotinselectedarea(elset[1], area)){
            ellipseelem['elem'].push({'name':'Start', 'location':[elset[1].attr('cx'), elset[1].attr('cy')]});
            //           console.log('start in selectarea');
        }
        if (isdotinselectedarea(elset[2], area)){
            ellipseelem['elem'].push({'name': 'End', 'location': [elset[2].attr('cx'), elset[2].attr('cy')]});
            //         console.log('end in selectarea');
        }
        ellipseelem['elem'].push({'name': 'Path','location': elset[0].attr('path')});
        if (ispathinselectedarea(elset[0], area)){
            ellipseelem['complete'] = true;
        }else{
            ellipseelem['complete'] = false;
        }
        return ellipseelem;
    };
    var getcurveelemlist;
    getcurveelemlist = function (elset, area) {
        console.log(elset.getelemtype()+"ELEM TYPE")
        switch (elset.getelemtype()) {
            case 'complexcurve':
                return getcomplexcurveelem(elset, area);
                break;
            case 'curve':
                return getcurveelem(elset, area);
                break;
            case 'line':
                return getlineelem(elset, area);
                break;
            case 'dot':
                return getdotelem(elset, area);
                break;
            case 'triangle':
               return gettrianglelem(elset, area);
               break;
            case 'rectangle':
               return getrectelem(elset, area);
               break;
            case 'square':
               return getsqrelem(elset, area);
               break;           
            case 'simplecurve':
                return getsimplecurveelem(elset, area);
                break;
            case 'circle':
                return getcircleelem(elset, area);
                break;
            case 'ellipse':
                return getellipseelem(elset, area);
                break;
            default:
                return;
        }
    };

    var ispathinselectedarea = function(curveset, area){
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
    };


    var getintesect_set = function(canvasname, curveelemlist, area){
        for (var i = 0 ; i < curveelemlist.length; i++){
            var intesect_row = [];
            for( var j = 0; j < i; j++){
                var intesectpoint = getcurveintesectpoint(canvasname, curveelemlist[i], curveelemlist[j], area);
                if(intesectpoint){
                    intesect_row.push([curveelemlist[i]['legend'], curveelemlist[j]['legend'], intesectpoint]);
                }
            }
            if(intesect_row.length > 0){
                intesect_set.push(intesect_row);
            }
        }
        return intesect_set;
    };


    var enable_preview = function(elist) {
        elist.forEach(function(elset){
            elset.forEach(function(el){
                if (el.data("what") === 'circle' || el.data("what") === 'handler_path' || el.data("what") === 'handler_circle' || el.data("what") === 'controler'){
                    el.attr({"fill-opacity": 0, "stroke-opacity": 0});
                }
                if (el.data("what") === 'text'){
                    el.show();
                }
            })
            //elset.hide();
        });
    };
    

    var disable_preview = function(elist) {
        elist.forEach(function(elset){
            elset.forEach(function(el){
                //if (el.data("what") === 'text'){
                //    el.hide();
                //}else 
                if (el.data("what") !== 'area'){
                    el.attr({"fill-opacity": 1, "stroke-opacity": 1});
                }
            })
        });
    };


    var IntemassCanvasGet = function(thiscanvas, csrfvalue, id){
        var canvasid = $.toJSON(id);
        $.post('/canvas/get/',
            {'name': thiscanvas, 'id': canvasid, 'csrfmiddlewaretoken': csrfvalue},
            function(payload){
                if (payload['state'] === 'success'){
                    var elem, type, canvas;
                    canvasmap = payload['canvasmap'];
                    console.log("canvasmap   ==  "+canvasmap);
                    for(var canvasname in canvasmap){
                        console.log('canvasname = '+canvasname, "  thiscanvas  =  "+thiscanvas);
                        if (canvasname === thiscanvas){
                            canvas = canvasmap[canvasname];
                            recoverdraw(canvasname);
                            listRules(canvasname, canvas['rulelist']);
                        }
                        var $viewBtn = $("#" + thiscanvas + "-viewBtn");
                        $viewBtn.attr('checked', true);
                        var elist = elemap[canvasname];
                        enable_preview(elist);
                        $viewBtn.next().addClass('ui-state-active');
                    }
                }
            }, 'json');
        
    };

    var recoverdraw = function(canvasname){
        var canvas = canvasmap[canvasname];
        //for(var axisname in canvas['axis']){
        //    var axis = canvas['axis'][axisname];
        //    drawAxis(canvasname, axis);
        //}
        
        if (canvas['axis'][0] === 'axis') {
            $("#"+ canvasname +"-XYaxisBtn").attr("disabled", "");
            for(var axisname in canvas['axis']){
                var axis = canvas['axis'][axisname];
                axis['redraw'] = 'redraw'
                drawAxis(canvasname, axis);
            }
        }
        
        if (canvas['axis'][0] === 'xyaxis') {
           $("#"+ canvasname +"-axisBtn").attr("disabled", "");
           var XYaxis = canvas['axis']['x'];
           drawXYAxis(canvasname, XYaxis);
        }
       
        var canvas_list = [];
        for(var legend in canvas['drawopts']){
            
            global_legends.push(legend + ':' + canvasname);
            var drawopts = canvas['drawopts'][legend];
            drawopts['legend'] = legend;
            canvas_list.push(drawopts);
        }
        var sort_canvas = function(obj1,obj2) {
            if(obj1.type === 'dot')
                return true;
            if(obj1.type === 'axis-dashline')
                return true;
            //return  obj1.type - obj2.type;
        }
        canvas_list = canvas_list.sort(sort_canvas);

        for(var i in canvas_list){
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
                case 'triangle':
                    drawTriangle(canvasname, drawopts);
                    break;
                case 'rectangle':
                    drawRect(canvasname, drawopts);
                    break;
                case 'square':
                    drawSquare(canvasname, drawopts);
                    break;
                case 'circle':
                    drawCircle(canvasname, drawopts);
                    //addDraw(canvasname, drawCircle, drawopts);
                    break;
                case 'ellipse':
                    drawEllipse(canvasname, drawopts);
                    break;
                case 'simplecurve':
                    drawSimpleCurve(canvasname, drawopts);
                    break;
                case 'arrow':
                    drawArrow(canvasname, drawopts)
                default:
                    break;
            }
        }
    };

    var isobjectnull = function(Obj){
        for(var name in Obj){
            if (Obj.hasOwnProperty(name)){
                return false;
            }
        }
        return true;
    };

    var IntemassCanvasUpload = function(csrfvalue, id){
        autogenrulelist();
        var canvasjson = $.toJSON(canvasmap);
        var canvasid = $.toJSON(id);
        $.post('/canvas/upload/',
            {'id': canvasid, 'canvasmap': canvasjson, 'csrfmiddlewaretoken': csrfvalue},
            function(payload){
                if (payload['state'] === 'success')
                    alert('upload success');
        }, "json");
    };

    var autogenrulelist = function(){
        for (var canvasname in canvasmap){
            //console.log(canvasname+ "CANVASNAME");
            if (!isobjectnull(canvasmap[canvasname]['drawopts']) || isobjectnull(canvasmap[canvasname]['rulelist'])){
               var point = {};
               var concatedrulelist = [];
               rulelist = calculateRules(canvasname, 0, 0, attributes.width, attributes.height);
               console.log('rulelist    '+rulelist);
               for (var i = 0; i < rulelist.length; i += 1){
                   var rule = [getpointlist(point, rulelist[i]) + ' '].concat(rulelist[i]);
                   concatedrulelist.push(rule);
               }
               console.log('concatedrulelist    '+concatedrulelist);
               canvasmap[canvasname]['rulelist'] = concatedrulelist;
            }
        }
    };

})(jQuery);