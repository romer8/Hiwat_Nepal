#################CONTROLER FUNCTIONS FOR THE APP!!!!!!!!!!!!


from __future__ import division

import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import *
from django.http import HttpResponse, JsonResponse
import os
import netCDF4 as nc
import datetime as dt
import numpy as np
import plotly.graph_objs as go
import datetime
from csv import writer as csv_writer
from .app import NepalHiwatviewer as app
from .config import *
from .utils import generate_variables_meta,get_thredds_info,get_hiwat_file
base_name = __package__.split('.')[-1]

@login_required()
def home(request):
    """
Controller for the app home page.
"""
    variable_options = [('Total Precipitation(mm)', 'APCP_surface'),
                        ('Convective Available Potential Energy(J/kg)', 'CAPE_surface'),
                        ('Dew Point Temperature(C)', 'DPT_2maboveground'),
                        ('Geopotential Height(m)','HGT_500mb'),
                        ('0-3 km Storm Relative Helicity(m^2/s^2)','HLCY_0M3000maboveground'),
                        ('Temparature 2m above ground(C)','TMP_2maboveground'),
                        ('Hourly Precipitation(mm)', 'PCP'),
                        ('Pressure Reduced To MSL(hPa)', 'PRMSL_meansealevel'),
                        ('Wind Direction 10m above ground(m)','WDIR_10maboveground'),
                        ('Wind Direction 250 mb(degress)', 'WDIR_250mb'),
                        ('Wind Speed 10m(m/s)', 'WIND_10maboveground'),
                        ('Wind Speed(m/s)', 'WIND_250mb')]

    # Select Variable Dropdown
    select_variable = SelectInput(display_text='Select HIWAT Variable',
                                  name='select_variable',
                                  multiple=False,
                                  options=variable_options,
                                  initial=['Total Accumulated Precipitation(mm)'])


    thredds_wms_obj = get_thredds_info()

    var_options = generate_variables_meta()

    context = {
        'select_variable':select_variable,
        'thredds_urls':json.dumps(thredds_wms_obj),
        'var_options':json.dumps(var_options),
    }

    return render(request, 'nepal_hiwatviewer/home.html',context)

# FUNCTION TO GIVE THE FORECAST DATA FOR THE GIVEN RIVER
def get_hiwat(request):
    print("enter get hiwat function ..")
    """
        Get hiwat data
    """

    get_data = request.GET

    try:
        comid = get_data['comid']
        startdate=get_data['startdate']
        country = 'Nepal'
        model = 'Hiwat'

        print(comid, country, model,startdate)
        path = os.path.join(app.get_custom_setting('forescast_data'))
        print('printing the path in the get hiwat function')
        print(path)
        filename = [f for f in os.listdir(path) if 'Qout_hiwat' in f]
        filename.reverse()
        print("printing filename")
        print (filename)
        print("starting reverse. ..")

        for file in filename:
            print(file)



        selectedDate=int(startdate)
        filename = filename[selectedDate]


        file = path + '/' + filename

        print(file)
        res = nc.Dataset(file, 'r')

        dates_raw = res.variables['time'][:]
        dates = []
        for d in dates_raw:
            dates.append(dt.datetime.fromtimestamp(d))

        print('after append')
        comid_list = res.variables['rivid'][:]
        print('after commid list')
        commid = int(comid)
        index_string = np.where(comid_list == commid)[0]
        print(np.shape(index_string))
        print('error is happening here')
        print('type of index_string')
        print(type(index_string))
        print('after index_string')
        print(index_string)
        print('new')
        comid_index = index_string.item(0)
        print('after comid_index')

        values = []
        for l in list(res.variables['Qout'][:]):
            values.append(float(l[comid_index]))

        # --------------------------------------
        # Chart Section
        # --------------------------------------
        series = go.Scatter(
            name='HIWAT',
            x=dates,
            y=values,
        )

        print("thi is the max date ..")
        print(max(dates))
        max_date=max(dates)
        min_date=min(dates)
        max_value=max(values)
        print('THIS IS THE VALUES')
        print(values)

        return_shapes, return_annotations= get_return_period_ploty_info(request,min_date,max_date)

        if return_shapes[2]["y0"]>max_value:
            return_shapes.pop(2)
            return_annotations.pop(2)

        if return_shapes[1]["y0"]>max_value:
            return_shapes.pop(1)
            return_annotations.pop(1)

        if return_shapes[0]["y0"]>max_value:
            return_shapes.pop(0)
            return_annotations.pop(0)


        if len(return_shapes)>0:
            layout = go.Layout(
                title="HIWAT Streamflow<br><sub>{0}: {1}</sub>".format(country, comid),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Streamflow (m<sup>3</sup>/s)'),
                shapes=return_shapes,
                annotations=return_annotations
            )
        else:
            layout = go.Layout(
                title="HIWAT Streamflow<br><sub>{0}: {1}</sub>".format(country, comid),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Streamflow (m<sup>3</sup>/s)'),

            )

        chart_obj = PlotlyView(go.Figure(data=[series], layout=layout))

        context = {
            'gizmo_object': chart_obj,
        }

        print('this is the chart_obj')
        print(chart_obj)
        return render(request, '{0}/gizmo_ajax.html'.format(base_name), context)

    except Exception as e:
        print (e)
        return JsonResponse({'error': 'No HIWAT data found for the selected reach.'})

# FUNCTION TO GIVE THE HISTORICAL DATA FROM THE GIVEN RIVER
def get_historic(request):
    """
        Get historic data
    """

    get_data = request.GET

    try:
        comid = get_data['comid']
        country = 'Nepal'
        model = 'Historic ECMWF'

        path = os.path.join(app.get_custom_setting('historical_data'))

        filename = [f for f in os.listdir(path) if 'Qout_erai' in f]


        filename = filename[0]

        file = path + '/' + filename

        res = nc.Dataset(file, 'r')

        dates_raw = res.variables['time'][:]
        dates = []
        for d in dates_raw:
            dates.append(dt.datetime.fromtimestamp(d))

        comid_list = res.variables['rivid'][:]
        comid_index = int(np.where(comid_list == int(comid))[0])

        values = []
        for l in list(res.variables['Qout'][:]):
            values.append(float(l[comid_index]))


        return_shapes, return_annotations= get_return_period_ploty_info(request,dates[0],dates[-1])

        # --------------------------------------
        # Chart Section
        # --------------------------------------
        series = go.Scatter(
            name='Historic Simulation ECMWF',
            x=dates,
            y=values,
        )


        layout = go.Layout(
            title="Historic Streamflow<br><sub>{0}: {1}</sub>".format(country, comid),
            xaxis=dict(title='Date'),
            yaxis=dict(title='Streamflow (m<sup>3</sup>/s)'),
            shapes=return_shapes,
            annotations=return_annotations
        )

        chart_obj = PlotlyView(go.Figure(data=[series], layout=layout))

        context = {
            'gizmo_object': chart_obj,
        }

        return render(request, '{0}/gizmo_ajax.html'.format(base_name), context)

    except Exception as e:
        print (e)
        return JsonResponse({'error': 'No Historic ECMWF data found for the selected reach.'})


#DOWNLOAD TEH FORECAST DATA FOR THE GIVEN RIVER
def download_hiwat(request):
    """
        Get hiwat data
    """

    print(request)
    get_data = request.GET

    try:
        comid = get_data['comid']
        startdate=get_data['startdate']
        country = 'Nepal'
        model = 'Hiwat'


        path = os.path.join(app.get_custom_setting('forescast_data'))

        filename = [f for f in os.listdir(path) if 'Qout_hiwat' in f]
        filename.reverse()
        selectedDate = int(startdate)
        filename = filename[selectedDate]

        #filename = filename[0]

        file = path + '/' + filename

        res = nc.Dataset(file, 'r')

        dates_raw = res.variables['time'][:]
        dates = []
        for d in dates_raw:
            dates.append(dt.datetime.fromtimestamp(d))

        comid_list = res.variables['rivid'][:]
        comid_index = int(np.where(comid_list == int(comid))[0])

        values = []
        for l in list(res.variables['Qout'][:]):
            values.append(float(l[comid_index]))

        pairs = [list(a) for a in zip(dates, values)]

        response = HttpResponse(content_type='text/csv')

        response['Content-Disposition'] = 'attachment; filename={0}-{1}-{2}.csv'.format(country, model, comid)

        writer = csv_writer(response)

        writer.writerow(['datetime', 'streamflow (m3/s)'])

        for row_data in pairs:
            writer.writerow(row_data)

        return response

    except Exception as e:
        print (e)
        return JsonResponse({'error': 'No HIWAT data found for the selected reach.'})

#DOWNLOAD THE HISTORIC DATA FOR THE GIVEN RIVER.

def download_historic(request):
    """
        Get historic data
    """

    get_data = request.GET

    try:
        comid = get_data['comid']
        country = 'Nepal'
        model = 'Historic ECMWF'


        path = os.path.join(app.get_custom_setting('historical_data'))

        filename = [f for f in os.listdir(path) if 'Qout_erai' in f]
        filename = filename[0]

        file = path + '/' + filename

        res = nc.Dataset(file, 'r')

        dates_raw = res.variables['time'][:]
        dates = []
        for d in dates_raw:
            dates.append(dt.datetime.fromtimestamp(d))

        comid_list = res.variables['rivid'][:]
        comid_index = int(np.where(comid_list == int(comid))[0])

        values = []
        for l in list(res.variables['Qout'][:]):
            values.append(float(l[comid_index]))

        pairs = [list(a) for a in zip(dates, values)]

        response = HttpResponse(content_type='text/csv')

        response['Content-Disposition'] = 'attachment; filename={0}-{1}-{2}.csv'.format(country, model, comid)

        writer = csv_writer(response)

        writer.writerow(['datetime', 'streamflow (m3/s)'])

        for row_data in pairs:
            writer.writerow(row_data)

        return response

    except Exception as e:
        print (e)
        return JsonResponse({'error': 'No Historic ECMWF data found for the selected reach.'})

# GET THE DATES ASSOCIATED WITH THE NAME OFTHE FORECAST FILES SAVED ON THE FORECAST LOCAL PATH
def get_avaialable_dates_raw(request):
    get_data = request.GET
    comid = get_data['comid']
    path = os.path.join(app.get_custom_setting('forescast_data'))
    print('printing path in get available dates raw')
    print(path)
    filenames = [f for f in os.listdir(path) if 'Qout' in f]
    print(type (filenames[0]))
    sorted(filenames)
    print("get_available_dates_raw ..")
    for filename in filenames:
        print(filename)


    availableDates = []
    files_count = 0
    for filename in filenames:
        ##filename = path + '/' + filename
        filecut=filename.split("_")[5]
        filecut2=filecut.split(".")[0]
        filecut2=filecut2[:8]
        date = datetime.datetime.strptime(filecut2, "%Y%m%d")
        print(date)
        hour=0
        actualTimeDate=str(date + datetime.timedelta(hours=int(hour)))
        actualTimeDate=str(date)

        availableDates.append(actualTimeDate)
        files_count += 1
        # limit number of directories
        if files_count > 64:
            break
    print("printing availbale dates...")
    sorted(availableDates)
    for dates in availableDates:
        print(dates)

    availableDates.reverse()

    return JsonResponse({
        "success": "Data analysis complete!",
        "available_dates": json.dumps(availableDates)
    })

#FINAL DATES AVAILABLE FOR TEH FORECAST DATA FOR TEH RIVER. THIS USES THE GET_AVAILABLE_DATES_RAW FUNCTION.
def get_availableDatesFinal(request):
    print("get_available_dates")
    print(request)
    get_data = request.GET
    comid = get_data['comid']
    print("this is my "+ comid)
    res=get_avaialable_dates_raw()
    dates = []
    for date in eval(res.content):
        if len(date) == 10:
            date_mod = date + '000'
            date_f = dt.datetime.strptime(date_mod, '%Y%m%d.%H%M').strftime('%Y-%m-%d %H:%M')
        else:
            date_f = dt.datetime.strptime(date, '%Y%m%d.%H%M').strftime('%Y-%m-%d %H:%M')
        dates.append([date_f, date, comid])

    dates.reverse()

    return JsonResponse({
        "success": "Data analysis complete!",
        "available_dates": json.dumps(dates)
    })




##Get the return periods associated with the selected forecast
def get_return_periods_final(request):

    # Check if its an ajax post request
    if request.is_ajax() and request.method == 'GET':
        reach = request.GET.get('comid')
        ##date = request.GET.get('startdate')

        request_params1 = dict(reach_id=reach)

        rpall=get_return_periods(request_params1)

    return rpall

#GET THE RETURN PERIODS FROM THE GET_RETURN_PERIOD_DICT FUNCTION AS A DICTIONARY OBJECT, THIS IS
# BASICALLY A WRAPPER FUNCTION FOR THE GET RETURN PERIOD DICT
def get_return_periods(request):
# def get_return_periods(commid):
    print("entring get_return_periods")
    """
    Controller that will show the return period data in json format
    """
    return JsonResponse(get_return_period_dict(request), safe=False)


#GET THE RETURN PERIOD AS A DICTIONARY OBJECT
def get_return_period_dict(request):

    print("entering the return period_dict function ..")
    return_period_file, river_id = validate_historical_data(request)[:2]

    print("printing return_period_file and river id ..")
    print(return_period_file)
    print(river_id)

    # get information from dataset
    return_period_data = {}


    res = nc.Dataset(return_period_file, 'r')
    print(res)
    max_flows=res.variables['max_flow'][:]
    return_20=res.variables['return_period_20']
    return_10=res.variables['return_period_10']
    return_2=res.variables['return_period_2']
    comids=res.variables['rivid'][:]
    print('this is the max value of flowSS')
    print('maxflows size is ' + str(len(max_flows)))
    print(max_flows)
    print ('commids size is '+str(len(comids)))
    print(comids)
    commid_index=0
    for comid in comids:
        if comid!=river_id:
            commid_index=commid_index+1
        else:
            break
    selected_commid=comids[commid_index]
    selected_max_flow=max_flows[commid_index]
    selected_return_20=return_20[commid_index]
    selected_return_10=return_10[commid_index]
    selected_return_2=return_2[commid_index]
    return_period_data["twenty"] = str(selected_return_20)
    return_period_data["max"] = str(selected_max_flow)
    return_period_data["ten"] = str(selected_return_10)
    return_period_data["two"] = str(selected_return_2)
    print("this is my selected comid..")
    print(selected_commid)
    # print("printing the return periods")
    # print(return_period_data["max"])
    # print(return_period_data["twenty"])
    # print(return_period_data["ten"])
    # print(return_period_data["two"])



    return return_period_data


#VALIDATE THE RETUNR PERIODS FROM THE ESPECIFIED PATH IN THE LOCAL FILE
def validate_historical_data(request_info):

    print("entering the validate_historical_data function ...")
    path_to_era_interim_data = app.get_custom_setting('return_periods')
    filename = [f for f in os.listdir(path_to_era_interim_data) if 'return_periods_' in f]
    filename=filename[0]
    file = path_to_era_interim_data + '/' + filename

    if not os.path.exists(path_to_era_interim_data):
            raise Exception('Location of historical files faulty. '
                                'Please check settings.')




    river_id = validate_rivid_info(request_info)

    print("exiting the validate_historical_data function ..")

    return file, river_id

#VALIDATE THE RIVER ID
def validate_rivid_info(request_info):
    """
    This function validates the input rivid data for a request

    Returns
    -------
    rivid
    """
    print("enetering the validate_rivid_info fucntion")

    reach_id = request_info.get('reach_id')
    if reach_id is None:
        raise Exception('Missing reach_id parameter ....')

    # make sure reach id is integet
    try:
        reach_id = int(reach_id)
    except (TypeError, ValueError):
        raise Exception('Invalid value for reach_id {}.'.format(reach_id))

    print("exiting the validate_rivid_function ..")
    print("result of this is .. ")
    print(reach_id)
    return reach_id


#EXCEPTION HANDLER FOR THE RIVER ID
def rivid_exception_handler(file_type, river_id):
    """
    Raises proper exceptions for rivids queries
    """
    try:
        yield
    except (IndexError, KeyError):
        raise Exception('{file_type} river with ID {river_id}.'
                            .format(file_type=file_type, river_id=river_id))
    except Exception:
        raise Exception("Invalid {file_type} file ..."
                          .format(file_type=file_type))



#GET THE RETURN PERIOD COLORS FOR THE FORECAST AND HISTORICAL DATA
def get_return_period_ploty_info(request, datetime_start, datetime_end,
                                  band_alt_max=-9999):
    """
    Get shapes and annotations for plotly plot
    """
    # Return Period Section

    print("entering the plotly return periods function")
    # print("request")
    # print(request)
    print("commid")
    # print(commid)
    return_period_data = get_return_periods_final(request)
    #return_period_data = get_return_period_dict(request)

    ##return_period_data = get_return_periods(commid)
    print("printing the return_period data in the get_return_period_ploty_info function ...")
    print(return_period_data)
    return_period_data_dictionary=eval(return_period_data.content)
    print(type(return_period_data_dictionary))
    # print("printing return periods converted as a dictionary ...")

    # return_period_data_dictionary=json.loads(return_period_data)
    # print(return_period_data_dictionary)
    # print(return_period_data['max'])
    return_max = float(return_period_data_dictionary["max"])
    return_20 = float(return_period_data_dictionary["twenty"])
    return_10 = float(return_period_data_dictionary["ten"])
    return_2 = float(return_period_data_dictionary["two"])
    print("printing the retun periods from the plotly Function converted as floats..")
    print(return_2)
    print(return_10)
    print(return_20)
    print(return_max)

    # plotly info section
    shapes = [
         # return 20 band
         dict(
             type='rect',
             xref='x',
             yref='y',
             x0=datetime_start,
             y0=return_20,
             x1=datetime_end,
             y1=max(return_max, band_alt_max),
             line=dict(width=0),
             fillcolor='rgba(128, 0, 128, 0.4)',
         ),
         # return 10 band
         dict(
             type='rect',
             xref='x',
             yref='y',
             x0=datetime_start,
             y0=return_10,
             x1=datetime_end,
             y1=return_20,
             line=dict(width=0),
             fillcolor='rgba(255, 0, 0, 0.4)',
         ),
         # return 2 band
         dict(
             type='rect',
             xref='x',
             yref='y',
             x0=datetime_start,
             y0=return_2,
             x1=datetime_end,
             y1=return_10,
             line=dict(width=0),
             fillcolor='rgba(255, 255, 0, 0.4)',
         ),
    ]
    annotations = [
        # return max
        dict(
            x=datetime_end,
            y=return_max,
            xref='x',
            yref='y',
            text='Max. ({:.1f})'.format(return_max),
            showarrow=False,
            xanchor='left',
        ),
        # return 20 band
        dict(
            x=datetime_end,
            y=return_20,
            xref='x',
            yref='y',
            text='20-yr ({:.1f})'.format(return_20),
            showarrow=False,
            xanchor='left',
            yanchor='bottom',
        ),
        # return 10 band
        dict(
            x=datetime_end,
            y=return_10,
            xref='x',
            yref='y',
            text='10-yr ({:.1f})'.format(return_10),
            showarrow=False,
            xanchor='left',
            yanchor='bottom',

        ),
        # return 2 band
        dict(
            x=datetime_end,
            y=return_2,
            xref='x',
            yref='y',
            text='2-yr ({:.1f})'.format(return_2),
            showarrow=False,
            xanchor='left',
            yanchor='bottom',

        ),
    ]
    print("exiting the plotly function for return periods..")
    return shapes, annotations
