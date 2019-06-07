

let $loading = $('#view-file-loading');

//let base_layer = new ol.layer.Tile({
//	source: new ol.source.BingMaps({
//		key: 'eLVu8tDRPeQqmBlKAjcw~82nOqZJe2EpKmqd-kQrSmg~AocUZ43djJ-hMBHQdYDyMbT-Enfsk0mtUIGws1WeDuOvjY4EXCH-9OK3edNLDgkc',
//		imagerySet: 'Road'
//	})
//});
//
//
//
//let nepal_rivers = new ol.layer.Image({
//	source: new ol.source.ImageWMS({
////		url: 'http://tethys.icimod.org:8181/geoserver/hydroviewer/wms',
////		params: { 'LAYERS': 'drainageline' },
//        url: 'https://tethys.byu.edu/geoserver/nepal_hiwat/wms',
//		params: { 'LAYERS': 'drainageline' },
//		serverType: 'geoserver',
//		crossOrigin: 'Anonymous'
//	})
//});
//
//
//let feature_layer = nepal_rivers;
//
//
//
//
//
//let map = new ol.Map({
//	target: 'showMapView',
//	layers: [base_layer, nepal_rivers],
//	view: new ol.View({
//		center: ol.proj.fromLonLat([85.22, 27.43]),
//		zoom: 7
//	})
//});

/************************************************************************
* MODULE LEVEL / GLOBAL VARIABLES
*************************************************************************/
var animationDelay,
$btnGetPlot,
det_options,
hourly_options,
int_type,
int_options,
map,
$modalChart,
opacity,
public_interface, // Object returned by the module
$slider,
$sliderContainer,
sliderInterval,
tdWmsLayer,
thredds_urls,
var_options,
gs_wms_url;


/************************************************************************
* PRIVATE FUNCTION DECLARATIONS
*************************************************************************/
var add_wms,
clear_coords,
get_ts,
init_dropdown,
init_events,
init_jquery_vars,
init_all,
init_map,
init_opacity_slider;

// inti the map//
var map_leaft = L.map('showMapView').setView([27,86.77],7);
map_leaft.createPane('HiwatRaster');
map_leaft.getPane('HiwatRaster').style.zIndex=650;
map_leaft.getPane('HiwatRaster').style.pointerEvents='none';
var OpenStreetMap_Mapnik = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
     opacity: 0.5, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
     }).addTo(map_leaft);

//var ecmwfAdmin = new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
var nepalBoundary = new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
    layers:'nepal:nationalBoundary',
    format:'image/png',
    transparent: true
}).addTo(map_leaft);

//var ecmwfDist = new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
var nepalDistritos = new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
    layers:'CRFMS:districtsNepal',
    format:'image/png',
    transparent: true
});

//var ecmwfProv = new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
var nepalProv = new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
    layers:'CRFMS:provinceNepal',
    format:'image/png',
    transparent: true
});

//**NORMAL INITILIZATION IN LEAFLET FOR THE GEOSERVER WMS SERVICE**//
//var hiwatRiverColor =new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
//    layers:'hydroviewer:rivernepal',
//    format:'image/png',
//    transparent:true,
//    styles:'nepalHiresColor'
//}).addTo(map_leaft);


//**INITIALIZING THE WMS LAYERS THAT HAS THE RIVERS WITH COLORS*\\
var url = 'http://tethys.icimod.org:8181/geoserver/ows';
var hiwatRiverColor= new L.tileLayer.betterWms(url, {
    layers: 'hydroviewer:rivernepal',
    transparent: true,
    format: 'image/png',
    styles:'nepalHiresColor'
}).addTo(map_leaft);




var hiwatRiver = new L.tileLayer.wms('http://tethys.icimod.org:8181/geoserver/ows',{
   layers:'hydroviewer:rivernepal',
   format:'image/png',
   transparent: true
});

//** initializing the wms layer to show teh HIWAT data. I am using this random file to just initialize it
//   you can see that it was not added to the map, so it is ok to use any to initialize//
var hiwatWmsUrl = "https://tethys.servirglobal.net/thredds/wms/tethys/HIWAT/hkhControl_20180329-1800_latlon.nc";
var wmsLayer = L.tileLayer.wms(hiwatWmsUrl, {
    layers: 'APCP_surface',
    format: 'image/png',
    transparent: true,
    style:'boxfill/apcp_surface',
    opacity:0.2
});

var timeDimension = new L.TimeDimension();
map_leaft.timeDimension = timeDimension;

var player = new L.TimeDimension.Player({
    loop: true,
    startOver:true
}, timeDimension);

var timeDimensionControlOptions = {
    player: player,
    timeDimension: timeDimension,
    position: 'bottomleft',
    autoPlay: false,
    minSpeed: 1,
    speedStep: 0.5,
    maxSpeed: 20,
    timeSliderDragUpdate: true,
    loopButton:true,
    limitSliders:true
};
var timeDimensionControl = new L.Control.TimeDimension(timeDimensionControlOptions);
  $('#chkRaster').change(function(){
    if($(this).is(':checked')){
        map_leaft.addControl(timeDimensionControl);
     }
     else
        map_leaft.removeControl(timeDimensionControl);

   });
tdWmsLayer = L.timeDimension.layer.wms(wmsLayer);

clear_coords = function(){
    $("#point-lat-lon").val('');
    $("#poly-lat-lon").val('');
    $("#shp-lat-lon").val('');
};

//init the coordinate tracker//
init_events = function(){
    map_leaft.on("mousemove", function (event) {
        document.getElementById('mouse-position').innerHTML = 'Latitude:'+event.latlng.lat.toFixed(5)+', Longitude:'+event.latlng.lng.toFixed(5);
    });
};



// init the jquery variables//
init_jquery_vars = function(){
    $slider = $("#slider");
    $sliderContainer = $("#slider-container");
    $modalChart = $("#chart-modal");
    $btnGetPlot = $("#btn-get-plot");
    var $meta_element = $("#metadata");
//    gs_wms_url = $meta_element.attr('data-wms-url');
    var_options = $meta_element.attr('data-var-options');
//    console.log('printing the var_option');
//    console.log(typeof(var_options));
//    console.log(var_options);
    var_options = JSON.parse(var_options);
//    hourly_options = $meta_element.attr('data-hourly-options');
//    hourly_options = JSON.parse(hourly_options);
//    det_options = $meta_element.attr('data-det-options');
//    det_options = JSON.parse(det_options);
    thredds_urls = $meta_element.attr('data-thredds-urls');
    thredds_urls = JSON.parse(thredds_urls);
    int_options = {'det':'Deterministic','hourly':'Ensemble Hourly'};
//    int_options = {'det':'Deterministic','hourly':'Ensemble Hourly','day1':'Ensemble Day 1','day2':'Ensemble Day 2'};

};

// init the dropdown for the hiwat model.
init_dropdown = function () {
    $(".interval_table").select2({minimumResultsForSearch: -1});
    $(".var_table").select2({minimumResultsForSearch: -1});

};

// init the opacity filter of the function
init_opacity_slider = function(){
    opacity = 0.2;
    $("#opacity").text(opacity);
    $( "#opacity-slider" ).slider({
        value:opacity,
        min: 0.2,
        max: 1,
        step: 0.1, //Assigning the slider step based on the depths that were retrieved in the controller
        animate:"fast",
        slide: function( event, ui ) {

        }
    });
};

//init all the functions at once.
init_all = function(){

    init_jquery_vars();
    init_events();
    init_dropdown();
    init_opacity_slider();

};

add_wms = function(var_type,interval){

    var wmsUrl = thredds_urls[interval];
    // console.log(wmsUrl);
    // map.removeLayer(wms_layer);
    map_leaft.removeLayer(tdWmsLayer);
    var index = find_var_index(var_type,var_options);
    var scale = var_options[index]["scale"];
    // gen_color_bar(var_options[index]["colors_list"],scale);
    var layer_id = var_options[index]["id"];
    var range = var_options[index]["min"]+','+var_options[index]["max"];

    var style = 'boxfill/'+layer_id.toLowerCase();
    opacity = $('#opacity-slider').slider("option", "value");

    var wmsLayer = L.tileLayer.wms(wmsUrl, {
        layers: layer_id,
        format: 'image/png',
        transparent: true,
        styles: style,
        colorscalerange: range,
        opacity:opacity,
        version:'1.3.0',
        pane:'HiwatRaster'
    });

    if(interval=='det'||interval=='hourly'){
        $('.leaflet-bar-timecontrol').removeClass('hidden');
    // Create and add a TimeDimension Layer to the map

            tdWmsLayer = L.timeDimension.layer.wms(wmsLayer,{
                updateTimeDimension:true,
                setDefaultTime:true,
                cache:48
            });
            console.log('gg');
            console.log(tdWmsLayer);
            tdWmsLayer.addTo(map_leaft);



    }else{
    $('.leaflet-bar-timecontrol').addClass('hidden');
        tdWmsLayer = wmsLayer;
        tdWmsLayer.addTo(map_leaft);
    }

    var imgsrc = wmsUrl + "?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER="+layer_id+"&colorscalerange="+range+"&PALETTE="+layer_id.toLowerCase()+"&transparent=TRUE";

    document.getElementById('legend').innerHTML = '<img src="' + imgsrc + '" alt="legend">';

};

function find_var_index(item,data){
    var index = -1;
    for (var i = 0; i < data.length; ++i) {
        if (item.includes(data[i]["id"])) {
            index = i;
            break;
        }
    }
    return index
}

$(function() {
    $('#chkRaster').change(function(){
    if($(this).is(':checked')){
        $('#rasterOptions').show();
        init_all();

        // thredds_urls.forEach(function(item,i){
        // console.log(item,i);
        // });
        $("#interval_table").html('');
        $.each(thredds_urls,function(n){
            var new_option = new Option(int_options[n],n);
            //*ONLY SHOWING THE HOURLY AND DETERMINATION DATA BECAUSE THEY ARE LINKED TO THE PRECIPITAION
            if(new_option.value!="day1" && new_option.value!="day2" ){
                $("#interval_table").append(new_option);
                //      DEBUGGING COMMENTS
                console.log('printing the new option');
                console.log(typeof(new_option.value));
                console.log(new_option.value);
            }
        });

        $("#interval_table").change(function(){
            var interval_type = ($("#interval_table option:selected").val());

            $("#var_table").html('');

            var_options.forEach(function(item,i){
                if(item["category"]==interval_type){
                    var new_option = new Option(item["display_name"]+' ('+item["units"]+')',item["id"]);

                    //THIS "IF STATEMENT" ALLOWS TO SEE ONLY TO SEE TWO OPTIONS THE HOUR AND TOTAL PRECIPITATION//
                    //THE OPTIONS ARE:
                    //1-HR ACCUMULATED PRECIPITATION(MM)
                    //TOTAL ACCUMULATED PRECIPITATION(MM)
                    //COMPOSITE REFLECTIVITY (dBz)
                    //PROB. OF LIGHTINING (%)
                    //PROB. OF FREQUENT LIGHTING
                    //PROB. OF REFLECTIVITY>50 dBz(%)
                    //PROB. OF WINDS>40KTS(%)
                    //PROB. OF WINDS>50KTS(%)
                    //PROB. OF MODERATE HAIL THREAT(%)
                    //PROB. OF HIGH HAIL THREAT (%)
                    //PROB. OF MODERATE SUPERCELL THREAT (%)
                    //PROB. OF HIGH SUPERCELL THREAT (%)

                    // ONLY THE FIRST TWO OPTIONS ARE SHOWED BECAUSE THE FOCUS IS ON THE PRECIPITATION.
                    if((new_option.value == 'enspmm-prec1h'||new_option.value == 'enspmm-prectot') || (new_option.value=='APCP_surface' || new_option.value=='PWAT_entireatmosphere')){
    //                    DEBUGGING COMMENTS
                        console.log('printing the new option');
                        console.log(typeof(new_option));
                        console.log(new_option);
                        $("#var_table").append(new_option);
                    }
                }
            });
            $("#var_table").trigger('change');

        }).change();

        $("#var_table").change(function(){

                $('#types').val('None').trigger('change');
                var var_type = ($("#var_table option:selected").val());
                var interval_type = ($("#interval_table option:selected").val());
                console.log(interval_type);
                console.log(typeof interval_type);
                add_wms(var_type,interval_type);


        }).change();


        $("#opacity-slider").on("slidechange", function(event, ui) {
            opacity = ui.value;
            $("#opacity").text(opacity);
            tdWmsLayer.setOpacity(opacity);

        });
    }
     else
        $('#rasterOptions').hide();
    }),
      $('#chkProvince').change(function(){
        if($(this).is(':checked')){
            map_leaft.addLayer(nepalProv);
        }
      })

});

//******************************************************************************************************************************************//////////////
function getRisk(risk){
    if(risk == 4){
        return 'red'
    }
    if(risk == 3){
        return 'orange'
    }
    if(risk == 2){
        return 'yellow'
    }
    else{
        return 'blue'
    }
}


function streams_style(feature){
    if (feature.properties.risk < 1){
        return{
        weight: 5,
        opacity: 1,
        color: getRisk(feature.properties.risk),
        fillOpacity:1
        }
    }
    else {
        return{
        weight: 10,
        opacity: 1,
        color: getRisk(feature.properties.risk),
        fillOpacity:1
        }
    }
    return{
        weight: 10,
        opacity: 1,
        color: getRisk(feature.properties.risk),
        fillOpacity:1
    }
}

//var not_trans_boundary=document.getElementById("preLoadNotTrans").value;
//console.log(not_trans_boundary);
//console.log(typeof(not_trans_boundary));
//not_trans_boundary = JSON.parse(not_trans_boundary);


//var ecmwfLayer = L.geoJson(ecmwf,
//var not_trans_layer = L.geoJSON(not_trans_boundary,
//    {style: streams_style,
//    onEachFeature: function(feature, layer) {
//        if (feature.properties && feature.properties.comid) {
//            layer.on('click', function (e) {
//                $.ajax({
//                    type:"GET",
//                    data: {
//                        "stID": feature.properties.comid,
//                    },
//                    url:"chart",
//                    dataType: 'json',
//                    "beforeSend": function(xhr, settings) {
//                        console.log("Before Send");
//                        $.ajaxSettings.beforeSend(xhr, settings);
//                    },
//                    "success": function () {
//                        alert("success");
//                    }
//                })
//            }); //Layer on click
//        }
//    }
//    }).addTo(map_leaft);

//map_leaft.fitBounds(not_trans_layer.getBounds());
//var legend = L.control({position: 'bottomleft'});
//legend.onAdd = function (map_leaft) {
//    var div = L.DomUtil.create('div','legend');
//    var labels =["Twenty Year Return Period ","Ten Year Return Period ","Two Year Return Period ","Normal Drainage"];
//    var grades = [4,3,2,1];
//    div.innerHTML='<div><b>Legend</b></div>';
//    for (var i=0; i < grades.length; i++){
//        div.innerHTML += '<i style="background:' + getRisk(grades[i]) + '">&nbsp;&nbsp;</i>&nbsp;&nbsp;' + labels[i] + '<br/>';
//    }
//    return div;
//}
//legend.addTo(map_leaft);


function get_hiwat (comid,startdate) {
	$('#hiwat-loading').removeClass('hidden');
	$.ajax({
        url: '/apps/nepal-hiwatviewer/get-hiwat/',
        type: 'GET',
        data: {
            'comid' : comid,
            'startdate': startdate
        },
        error: function () {
            $('#info').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the data</strong></p>');
            $('#info').removeClass('hidden');

            setTimeout(function () {
                $('#info').addClass('hidden')
            }, 5000);
        },
        success: function (data) {
            if (!data.error) {
                $('#hiwat-loading').addClass('hidden');
                $('#dates').removeClass('hidden');
//                $('#obsdates').removeClass('hidden');
                $loading.addClass('hidden');
                $('#hiwat-chart').removeClass('hidden');
                $('#hiwat-chart').html(data);

                //resize main graph
                Plotly.Plots.resize($("#hiwat-chart .js-plotly-plot")[0]);

                let params = {
                    comid: comid,
                    //adding this ...
                    startdate: startdate
                };

                $('#submit-download-hiwat').attr({
                    target: '_blank',
                    href: '/apps/nepal-hiwatviewer/download-hiwat?' + jQuery.param(params)
                });

                 $('#download-hiwat').removeClass('hidden');

            } else if (data.error) {
            	$('#info').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the Data</strong></p>');
            	$('#info').removeClass('hidden');

            	setTimeout(function() {
            		$('#info').addClass('hidden')
                }, 5000);

            } else {
            	$('#info').html('<p><strong>An unexplainable error occurred.</strong></p>').removeClass('hidden');
            }
        }
    });
}

function get_historic (comid) {

	$('#historic-loading').removeClass('hidden');
	$.ajax({
        url: '/apps/nepal-hiwatviewer/get-historic/',
        type: 'GET',
        data: {'comid' : comid},
        error: function () {
            $('#info').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the data</strong></p>');
            $('#info').removeClass('hidden');

            setTimeout(function () {
                $('#info').addClass('hidden')
            }, 5000);
        },
        success: function (data) {
            if (!data.error) {
                $('#historic-loading').addClass('hidden');
                $('#dates').removeClass('hidden');
//                $('#obsdates').removeClass('hidden');
                $loading.addClass('hidden');
                $('#historic-chart').removeClass('hidden');
                $('#historic-chart').html(data);

                //resize main graph
                Plotly.Plots.resize($("#historic-chart .js-plotly-plot")[0]);

                let params = {
                    comid: comid,
                };

                $('#submit-download-historic').attr({
                    target: '_blank',
                    href: '/apps/nepal-hiwatviewer/download-historic?' + jQuery.param(params)
                });

                 $('#download-historic').removeClass('hidden');

            } else if (data.error) {
            	$('#info').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the Data</strong></p>');
            	$('#info').removeClass('hidden');

            	setTimeout(function() {
            		$('#info').addClass('hidden')
                }, 5000);

            } else {
            	$('#info').html('<p><strong>An unexplainable error occurred.</strong></p>').removeClass('hidden');
            }
        }
    });
}
function get_available_dates(comid) {
      console.log("entering get_available_dates_javascript");
       $.ajax({
           type: 'GET',
           url: '/apps/nepal-hiwatviewer/get-available-dates/',
           dataType: 'json',
           data: {
               'comid': comid
           },
           error: function() {
               $('#dates').html(
                   '<p class="alert alert-danger" style="text-align: center"><strong>An error occurred while retrieving the available dates</strong></p>'
               );

               setTimeout(function() {
                   $('#dates').addClass('hidden')
               }, 5000);
           },
           success: function(dates) {
               console.log(dates);
               datesParsed = JSON.parse(dates.available_dates);
               $('#datesSelect').empty();

               $.each(datesParsed, function(i, p) {
                   //var val_str = p.slice(1).join();
                   var val_str = p;
                   console.log(val_str);
                   $('#datesSelect').append($('<option></option>').val(val_str).html(p));
               });

           }
       });

}



function get_return_periods(comid) {
    console.log('entering get_return_periods_function ..')
    $.ajax({
        type: 'GET',
        url: '/apps/nepal-hiwatviewer/get-return-periods/',
        dataType: 'json',
        data: {
            'comid': comid
        },
        error: function() {
            $('#info').html(
                '<p class="alert alert-warning" style="text-align: center"><strong>Return Periods are not available for this dataset.</strong></p>'
            );

            $('#info').removeClass('hidden');

            setTimeout(function() {
                $('#info').addClass('hidden')
            }, 5000);
        },
        success: function(data) {
            console.log(data);
            console.log(typeof(data))
            $("#hiwat-chart").highcharts().yAxis[0].addPlotBand({
                from: parseFloat(data.return_periods.twenty),
                to: parseFloat(data.return_periods.max),
                color: 'rgba(128,0,128,0.4)',
                id: '20-yr',
                label: {
                    text: '20-yr',
                    align: 'right'
                }
            });
            $("#hiwat-chart").highcharts().yAxis[0].addPlotBand({
                from: parseFloat(data.return_periods.ten),
                to: parseFloat(data.return_periods.twenty),
                color: 'rgba(255,0,0,0.3)',
                id: '10-yr',
                label: {
                    text: '10-yr',
                    align: 'right'
                }
            });
            $("#hiwat-chart").highcharts().yAxis[0].addPlotBand({
                from: parseFloat(data.return_periods.two),
                to: parseFloat(data.return_periods.ten),
                color: 'rgba(255,255,0,0.3)',
                id: '2-yr',
                label: {
                    text: '2-yr',
                    align: 'right'
                }
            });
        }
    });
}

//**OPEN LAYER CODE FOR THE CHANGE IN THE CURSOR WHEN ENTERING THE WMS LAYER**//
//map.on('pointermove', function(evt) {
//	if (evt.dragging) {
//		return;
//	}
//	let pixel = map.getEventPixel(evt.originalEvent);
//	let hit = map.forEachLayerAtPixel(pixel, function(layer) {
//		if (layer == feature_layer) {
//			current_layer = layer;
//			return true;
//		}
//	});
//	map.getTargetElement().style.cursor = hit ? 'pointer' : '';
//});
//


//**OPEN LAYERS CODE FOR THE CLICK EVENT ON THE WMS LAYER**//
//map.on("singleclick", function(evt) {
//
//	if (map.getTargetElement().style.cursor == "pointer") {
//
//		let view = map.getView();
//		let viewResolution = view.getResolution();
//		let wms_url = current_layer.getSource().getGetFeatureInfoUrl(evt.coordinate, viewResolution, view.getProjection(), { 'INFO_FORMAT': 'application/json' });
//
//		if (wms_url) {
//
//			$("#graph").modal('show');
//			$('#hiwat-chart').addClass('hidden');
//			$('#historical-chart').addClass('hidden');
//			$('#hiwat-loading').removeClass('hidden');
//			$('#historical-loading').removeClass('hidden');
//			$("#stream-info").empty()
//			//$('#download_hiwat').addClass('hidden');
//			//$('#download_historical').addClass('hidden');
//
//			$.ajax({
//				type: "GET",
//				url: wms_url,
//				dataType: 'json',
//				success: function (result) {
//					comid = result["features"][0]["properties"]["COMID"];
//					countryname = 'Nepal';
//					model = 'Hiwat';
//					$("#stream-info").append('<h3 id="Country-Tab">Country: '
//						+ countryname + '</h3><h5 id="Model">Model: '+ model
//						+ '</h5><h5 id="COMID">COMID: '+ comid + '</h5>');
//					get_hiwat (comid,'0')
//					get_historic (comid)
//					get_available_dates(comid)
////					get_return_periods(comid)
//
//					 $('#datesSelect').change(function() { //when date is changed
//                        var sel_val = ($('#datesSelect option:selected').val()).split(',');
//                        var index=$('#datesSelect').find(':selected').index();
//                        var indexString=index.toString();
//                        console.log("check");
//                        console.log(index);
//                        console.log(typeof index);
//                        console.log($('#datesSelect option:selected').val());
//                        console.log(sel_val);
//                        var startdate = indexString;
//                        $loading.removeClass('hidden');
//                        get_hiwat(comid, startdate);
//                        //get_return_periods(comid)
//
//                       // get_forecast_percent(comid, startdate);
//                     });
//
//				}
//			});
//
//
//		}
//	};
//});

function resize_graphs() {
    $("#hiwat_tab_link").click(function() {
        Plotly.Plots.resize($("#hiwat-chart .js-plotly-plot")[0]);
    });
    $("#historic_tab_link").click(function() {
        Plotly.Plots.resize($("#historic-chart .js-plotly-plot")[0]);
    });
};

