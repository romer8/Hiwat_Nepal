import datetime
import os
import requests

from config import *
import numpy as np

import xml.etree.ElementTree as ET

# GENERATE THE DATA VARIABLS ASSOCIATED WITH THE RASTER MAP
def generate_variables_meta():
    print('entering generate_variables')
    db_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'public/data/var_info.txt')
    print('printing the db_file path')
    print(db_file)
    variable_list = []
    var_issues = []
    with open(db_file, mode='r') as f:
        f.readline()  # Skip first line

        lines = f.readlines()

    for line in lines:
        if line != '':
            line = line.strip()
            linevals = line.split('|')
            variable_id = linevals[0]
            category = linevals[1]
            display_name = linevals[2]
            units = linevals[3]
            vmin = linevals[4]
            vmax = linevals[5]
            start = linevals[6]
            end = linevals[7]

            try:
                # print variable_id.lower()
                colors_list = retrieve_colors(str(variable_id).lower())
                scale = calc_color_range(float(vmin), float(vmax),len(colors_list))
                variable_list.append({
                    'id': variable_id,
                    'category': category,
                    'display_name': display_name,
                    'units': units,
                    'min': vmin,
                    'max': vmax,
                    'start': start,
                    'end': end,
                    'scale': scale,
                    'colors_list':colors_list
                })
            except Exception as e:
                # print variable_id,e
                var_issues.append(variable_id)
                scale = calc_color_range(float(vmin), float(vmax), 20)
                variable_list.append({
                    'id': variable_id,
                    'category': category,
                    'display_name': display_name,
                    'units': units,
                    'min': vmin,
                    'max': vmax,
                    'start': start,
                    'end': end,
                    'scale': scale
                })
                continue


    # print var_issues
    # print('printing the variable list')
    #print(variable_list)
    return variable_list

#GENERATE THE COLORS ASSOCIATED WITH THE RASTER ANIMATION FOR THE GIVEN VARIABLE
def retrieve_colors(field):
    fillcols = None

    if ('tmp_2m' in field):
        clevs = [-27, -24, -21, -18, -15, -12, -9, -6, -3, 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42]
        fillcols = [c['57'], c['55'], c['53'], c['51'], c['49'], c['47'], c['45'], c['43'], c['41'], c['39'],
                    c['37'], c['35'], c['33'], c['31'], c['22'], c['23'], c['25'], c['27'], c['29'], c['62'],
                    c['63'], c['65'], c['67'], c['69'], c['75'], c['77'], c['79']]
        below = c['59']
        above = c['79']
    elif ('dpt_2m' in field):
        clevs = [-27, -24, -21, -18, -15, -12, -9, -6, -3, 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        fillcols = [c['57'], c['55'], c['53'], c['51'], c['49'], c['47'], c['45'], c['43'], c['41'], c['39'],
                    c['37'], c['35'], c['33'], c['31'], c['22'], c['23'], c['25'], c['27'], c['29'], c['62']]
        below = c['59']
        above = c['62']
    elif ('sbcape' in field):
        clevs = [100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000]
        fillcols = [c['52'], c['55'], c['49'], c['46'], c['43'], c['38'], c['36'], c['34'], c['22'], c['23'],
                    c['24'], c['25'], c['26'], c['27'], c['29']]
        below = 'white'
        above = c['29']
    elif ('spd10m' in field):
        clevs = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
        fillcols = [c['2'], c['3'], c['4'], c['5'], c['6'], c['7'], c['8'], c['9'], c['10'], c['11'], c['12'], c['13']]
        below = 'white'
        above = 'magenta'
    elif ('refc' in field):
        clevs = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
        fillcols = [c['1'], c['2'], c['3'], c['4'], c['5'], c['6'], c['7'], c['8'], c['9'], c['10'], c['11'], c['12'], c['13'], c['14']]
        below = 'white'
        above = 'purple'
        # Use colors/contour intervals consistent with grads plots for deterministic runs.
    elif ('prec1h' in field or 'prec3h' in field or 'prec6h' in field ):
        clevs = [1, 2, 5, 10, 15, 20, 25, 50, 75, 100, 125, 150]
        fillcols = [c['33'], c['35'], c['37'], c['39'], c['43'], c['45'], c['47'], c['49'], c['53'], c['55'],
                    c['57'], c['59']]
        below = 'white'
        above = 'purple'
    elif ('prec12h' in field or 'prec24h' in field or 'prectot' in field):
        clevs = [1, 2, 5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200, 250, 300]
        fillcols = [c['33'], c['35'], c['37'], c['39'], c['43'], c['45'], c['47'], c['49'], c['53'], c['55'],
                    c['57'], c['59'], c['65'], c['67'], c['69']]
        below = 'white'
        above = 'purple'
    elif ('tcolg' in field):
        clevs = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
        fillcols = [c['1'], c['2'], c['3'], c['4'], c['5'], c['6'], c['7'], c['8'], c['9'], c['10'], c['11'], c['12'], c['13'], c['14']]
        below = 'white'
        above = 'purple'
    elif ('lfa' in field):
        #      clevs = [0.07,0.5,1,2,3,4,5,6,7,8,9,10,12,14]
        clevs = [0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14]
        fillcols = [c['1'], c['2'], c['3'], c['4'], c['5'], c['6'], c['7'], c['8'], c['9'], c['10'], c['11'], c['12'], c['13'], c['14']]
        below = 'white'
        above = 'purple'
    elif (('uphlcy16' in field) or ('uphlcy25' in field) or ('uphlcy' in field)):
        clevs = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700]
        fillcols = [c['1'], c['2'], c['3'], c['4'], c['5'], c['6'], c['7'], c['8'], c['9'], c['10'], c['11'], c['12'], c['13'], c['14']]
        below = 'white'
        above = 'purple'
    elif('apcp' in field):
        fillcols = [c['33'],c['35'],c['37'],c['39'], c['43'],c['45'], c['47'], c['49'],c['53'],c['55'],c['57'],c['59'],c['65'],c['67'],c['69']]
    elif('cape' in field):
        fillcols = [c['52'], c['55'], c['49'], c['46'], c['43'], c['38'], c['36'], c['34'], c['22'], c['23'], c['24'],
                    c['25'], c['26'], c['27'], c['29']]
    # print webcolors.rgb_to_hex((int(c['57'][0]*255),int(c['57'][1]*255),int(c['57'][2]*255)))

    # color_str = ','.join(map(str, fillcols))
    # print color_str
    return fillcols

#CALCULATE THE MAX RANGE FOR THE COLORS OF THE ANIMATION
def calc_color_range(min,max,classes):
    # breaks = None

    if classes is not None:
        breaks = int(classes)
    else:
        breaks = int(20)

    interval = float(abs((max - min) / breaks))

    if interval == 0:
        scale = [0] * breaks
    else:
        scale = np.arange(min, max, interval).tolist()

    return scale

# GET THE INFORMATION FROM THE TREDDS SERVER ASSOCIATED WITH ALL THE VARIABLES
def get_thredds_info():
    catalog_url = THREDDS_catalog

    catalog_wms = THREDDS_wms

    urls_obj = {}
    if catalog_url[-1] != "/":
        catalog_url = catalog_url + '/'

    if catalog_wms[-1] != "/":
        catalog_wms = catalog_wms + '/'

    catalog_xml_url = catalog_url+'catalog.xml'

    possible_dates = []
    valid_dates = []

    cat_response = requests.get(catalog_xml_url,verify=False)

    cat_tree = ET.fromstring(cat_response.content)

    for elem in cat_tree.iter():
        for k, v in elem.attrib.items():
            if 'title' in k:
            # if 'title' in k and '2018' in v:
                possible_dates.append(v)

    for date in possible_dates:
        try:

            valid_date = datetime.datetime.strptime(date, "%Y%m%d18")
            valid_dates.append(valid_date)

        except Exception as e:
            continue


    latest_date = max(valid_dates).strftime("%Y%m%d18")

    date_xml_url = catalog_url + latest_date + '/catalog.xml'

    date_xml = requests.get(date_xml_url, verify=False)

    date_response = ET.fromstring(date_xml.content)

    for el in date_response.iter():
        for k, v in el.items():
            if 'urlPath' in k:
                if 'Control' in v:
                    urls_obj['det'] = catalog_wms+v
                if 'hourly' in v:
                    urls_obj['hourly'] = catalog_wms+v
                if 'day1' in v:
                    urls_obj['day1'] = catalog_wms+v
                if 'day2' in v:
                    urls_obj['day2'] = catalog_wms+v
    print('printing the urls_obj')
    print(urls_obj)
    print('*********************')
    return urls_obj

##GET THE HIWAT DATA SAVED ON THE HIWAT FILE PATH
def get_hiwat_file():

    hiwat_files = {}
    latest_dir = max([os.path.join(HIWAT_storage, d) for d in os.listdir(HIWAT_storage) if os.path.isdir(os.path.join(HIWAT_storage, d)) if 'allhourly' not in d if 'RAPID_OUTPUT' not in d])

    print(latest_dir)
    # print(latest_dir)
    for file in os.listdir(latest_dir):
        if 'hourly' in file:
            hiwat_files['hourly'] = os.path.join(latest_dir, file)
        if 'Control' in file:
            hiwat_files['det'] = os.path.join(latest_dir, file)
        if 'day1' in file:
            hiwat_files['day1'] = os.path.join(latest_dir, file)
        if 'day2' in file:
            hiwat_files['day2'] = os.path.join(latest_dir, file)

    return hiwat_files








