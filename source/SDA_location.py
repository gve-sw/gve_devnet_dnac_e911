""""
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
from pprint import pprint
import pandas as pd
import usaddress
import uszipcode
from uszipcode import SearchEngine
from collections import OrderedDict
import openpyxl

from python_api_helpers import *


def process_client_list(filepathDNAC, filepathRooms):
    filepathDNAC = filepathDNAC
    filepathRooms = filepathRooms
    load_config_file()
    configuration_project_name = "E911"
    masterFrame = pd.DataFrame()
    buildingFrame = pd.DataFrame()
    full_address = []
    addresses = []
    buildings = []
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = get_site_topo(headers)


    for x in response['response']['sites']:
        if x['locationAddress'] and x['groupNameHierarchy']:

            full_address = x['locationAddress']
            parseResult = usaddress.parse(full_address)
            parseResult = dict(parseResult)

            res = dict((v, k) for k, v in parseResult.items())
            try:
                zipC = res['ZipCode']
                zipC = zipC.split(',')[0]
                res['ZipCode'] = zipC
            except uszipcode.e:
                continue
            engine = SearchEngine()
            zipcode = engine.by_zipcode(int(res['ZipCode']))
            res['county'] = zipcode.county
            res['Full_Address'] = full_address

            buildingValue = x['groupNameHierarchy']
            buildingValue = buildingValue.replace('Global/', '')
            res['Building'] = buildingValue
            res['Floor'] = buildingValue.split('/')[-1]

            addresses.append(res)

    addressFrame = pd.DataFrame(addresses, columns=addresses[0].keys())

    pprint(addressFrame)

    frame = pd.read_csv(filepathDNAC)

    # Copy Building Addresses to the master frame
    masterFrame['Identifier'] = frame['Identifier']
    masterFrame['Building'] = frame['Location']
    masterFrame['Mac_Address'] = frame['MAC Address']
    masterFrame['IPv4'] = frame['IPv4 Address']
    masterFrame['Switch_IPv4'] = frame['Switch IP Address']
    masterFrame['Switch'] = frame['Switch']
    masterFrame['Interface'] = frame['Port']
    masterFrame = addressFrame.merge(masterFrame, how='inner', on='Building')
    print(masterFrame)

    # We now have a list of clients, macs, etc, with appropriate addresses, switches, interfaces, etc.
    # Now, we need to create the template to deploy the civic information.

    # Get Project ID
    project_id = create_project_and_get_id(headers=headers, name=configuration_project_name)

    # Get template ID
    template_id = create_template_and_get_id(headers=headers, name="test", project_id=project_id)

    # RENAME Columns to match civic:

    masterFrame = masterFrame.rename(
        columns={'AddressNumber': 'number', 'StreetNamePreDirectional': 'primary-road-name', 'PlaceName': 'city',
                 'StateName': 'state'})
    masterFrame['primary-road-name'] = masterFrame['primary-road-name'] + " " + masterFrame['StreetName'] + " " + \
                                       masterFrame['StreetNamePostType']

    masterFrame['primary-road-name'] = masterFrame['primary-road-name'].replace({',': ''}, regex=True)
    masterFrame['city'] = masterFrame['city'].replace({',': ''}, regex=True)
    masterFrame['Identifier'] = masterFrame.index

    #Load Customer provided file to merge on Room #.
    #Launch GUI to save files locally.
    #return Filepath

    customerFrame = pd.read_csv(filepathRooms)
    masterFrame = masterFrame.merge(customerFrame, how='inner', on='Mac_Address')
    masterFrame = masterFrame.drop(columns='Unnamed: 0')
    # Uncomment this line to see the output of the room mapping script. May help troubleshoot errors.
    #masterFrame.to_csv('../resources/masterFrame.csv')

    for index, rows in masterFrame.iterrows():

        task = deploy_e911_template(headers=headers,
                                    template_id=template_id,
                                    civic_type="civic", #TODO Change to elin if needed
                                    ip_address=rows['Switch_IPv4'],  # SWITCH IP ADDRESS NOT CLIENT IP
                                    identifier=rows['Identifier'],
                                    building=rows['Building'],
                                    city=rows['city'],
                                    country=rows['CountryName'],
                                    county=rows['county'],
                                    road=rows['primary-road-name'],
                                    room=rows['Room'],
                                    state=rows['state'],
                                    number=rows['number'],
                                    interface=rows['Interface'])
        try:
            measure_task(headers, task)
        except Exception as e:
            pprint(e.__str__())



def main(argv):
    if len(argv) < 2:
        print('Need two files')
    else:
        print("Loading files now for deployment and processing")
        process_client_list(argv[1], argv[2])


if __name__ == "__main__":
    pass
    # process_client_list(filepathDNAC=
    #                     filepathRooms=
    # )
