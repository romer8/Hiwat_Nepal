L.TileLayer.BetterWMS = L.TileLayer.WMS.extend({
  
  onAdd: function (map) {
    // Triggered when the layer is added to a map.
    //   Register a click listener, then do all the upstream WMS things
    L.TileLayer.WMS.prototype.onAdd.call(this, map);
    map.on('click', this.getFeatureInfo, this);
    map.on('mousemove',this.getFeatureInfoMove, this);
  },

  getFeatureInfoMove: function (evt){

    if (evt.drag) {
     return;
    }
    var coordinatesMap=evt.latlng;
//    console.log(coordinatesMap.lat);
    var changeCursor=false;
    var url = this.getFeatureInfoUrl(evt.latlng),
        showResults = L.Util.bind(this.showGetFeatureInfo, this);

    if (url) {
        $.ajax({
          type:"GET",
          url: url,
          dataType:'json',
          success: function (data, status, xhr) {
              var err = typeof data === 'object' ? null : data;
              features=data["features"][0];
//              riverName=features["properties"]["riv_name"];
//                  $("#stream-info").append('<h3 id="riverName">River Name: '
//                  + riverName
//                  + '</h5><h5 id="COMID">COMID: '+ comid + '</h5>');
////              showResults(err, evt.latlng, riverName);

              if(typeof features !='undefined'){
                 changeCursor=true;
                 document.getElementById('showMapView').style.cursor='pointer';
              }
              else{
//                console.log('the mouse is outside the map :(');
                changeCursor=false;
                document.getElementById('showMapView').style.cursor='';
              }

          },
          error: function (xhr, status, error) {
            showResults(error);
          }
        });


    }
    else{
        console.log('the url for the wms layer request is not correct for the mousemove map event');
    }

  },
  
  onRemove: function (map) {
    // Triggered when the layer is removed from a map.
    //   Unregister a click listener, then do all the upstream WMS things

    L.TileLayer.WMS.prototype.onRemove.call(this, map);
    map.off('click', this.getFeatureInfo, this);
    map.off('mousemove', this.getFeatureInfoMove, this);
  },
  
  getFeatureInfo: function (evt) {
    if(document.getElementById('showMapView').style.cursor=='pointer'){
        // Make an AJAX request to the server and hope for the best
        var url = this.getFeatureInfoUrl(evt.latlng),
            showResults = L.Util.bind(this.showGetFeatureInfo, this);

        if (url) {
            $("#graph").modal('show');
            $('#hiwat-chart').addClass('hidden');
            $('#historical-chart').addClass('hidden');
            $('#hiwat-loading').removeClass('hidden');
            $('#historical-loading').removeClass('hidden');
            $("#stream-info").empty()
            $('#download_hiwat').addClass('hidden');
            $('#download_historical').addClass('hidden');
            console.log('the url is correct');
    //    if(url){
            $.ajax({
              type:"GET",
              url: url,
              dataType:'json',
              success: function (data, status, xhr) {
                  var err = typeof data === 'object' ? null : data;
//                  showResults(err,data);


                  comid = data["features"][0]["properties"]["comid"];
                  riverName=data["features"][0]["properties"]["riv_name"];
                  if(riverName.match(/[a-z]/i)){
                      $("#stream-info").append('<h3 id="riverName">River Name: '
                      + riverName
                      + '</h5><h5 id="COMID">COMID: '+ comid + '</h5>');
                  }
                  else{
                  riverName="No river name available";
                    $("#stream-info").append('<h3 id="riverName">River Name: '
                      + riverName
                      + '</h5><h5 id="COMID">COMID: '+ comid + '</h5>');
                  }
                  showResults(err, evt.latlng, riverName);

                  get_hiwat (comid,'0');
                  get_historic (comid);
                  get_available_dates(comid);


                  $('#datesSelect').change(function() { //when date is changed
                      var sel_val = ($('#datesSelect option:selected').val()).split(',');
                      var index=$('#datesSelect').find(':selected').index();
                      var indexString=index.toString();
                      console.log("check");
                      console.log(index);
                      console.log(typeof index);
                      console.log($('#datesSelect option:selected').val());
                      console.log(sel_val);
                      var startdate = indexString;
                      $loading.removeClass('hidden');
                      get_hiwat(comid, startdate);
                  });


              },
              error: function (xhr, status, error) {
                showResults(error);
              }

            });
        }
        else{
            console.log('the url for the wms layer request is not correct');

        }
    }
  },
  
  getFeatureInfoUrl: function (latlng) {
    // Construct a GetFeatureInfo request URL given a point
    var point = this._map.latLngToContainerPoint(latlng, this._map.getZoom()),
        size = this._map.getSize(),
        
        params = {
          request: 'GetFeatureInfo',
          service: 'WMS',
          srs: 'EPSG:4326',
          styles: this.wmsParams.styles,
          transparent: this.wmsParams.transparent,
          version: this.wmsParams.version,      
          format: this.wmsParams.format,
          bbox: this._map.getBounds().toBBoxString(),
          height: size.y,
          width: size.x,
          layers: this.wmsParams.layers,
          query_layers: this.wmsParams.layers,
          info_format: 'application/json'
//          info_format: 'text/html'
        };
    
    params[params.version === '1.3.0' ? 'i' : 'x'] = point.x;
    params[params.version === '1.3.0' ? 'j' : 'y'] = point.y;

    return this._url + L.Util.getParamString(params, this._url, true);
  },
  
  showGetFeatureInfo: function (err, latlng, content) {
//  showGetFeatureInfo: function (err, content) {
    if (err) { console.log(err);

    return; } // do nothing if there's an error
    console.log('popup');
    // Otherwise show the content in a popup, or something.
//    if(content.match(/[a-z]/i)){
        console.log(content);
        L.popup({ maxWidth:2000 })
          .setLatLng(latlng)
          .setContent(content)
          .openOn(this._map);
//    }
//    else {
//        L.popup({ maxWidth:2000 })
//          .setLatLng(latlng)
//          .setContent("No river name available")
//          .openOn(this._map);
//    }
  }
});

L.tileLayer.betterWms = function (url, options) {
  return new L.TileLayer.BetterWMS(url, options);  
};