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
# Modules import
from pprint import pprint

import requests
import json
from requests.auth import HTTPBasicAuth
import time
import configparser
import sys

# Disable SSL warnings. Not needed in production environments with valid certificates
import urllib3

urllib3.disable_warnings()


AUTH_URL = '/dna/system/api/v1/auth/token'
# URLs
DEVICES_BY_SERIAL_URL = '/dna/intent/api/v1/network-device/serial-number/{serial_number}'
NETWORK_URL = '/dna/intent/api/v1/network/{site_id}'
SITE_DEVICE_URL = '/dna/intent/api/v1/site/{site_id}/device'
SITE_URL = '/dna/intent/api/v1/site'
TASK_BY_ID_URL = '/dna/intent/api/v1/task/{task_id}'
TEMPLATE_DEPLOY_URL = '/dna/intent/api/v1/template-programmer/template/deploy'
TEMPLATE_PROJECT_URL = '/dna/intent/api/v1/template-programmer/project'
TEMPLATE_URL = '/dna/intent/api/v1/template-programmer/project/{project_id}/template'
TEMPLATE_VERSION_URL = '/dna/intent/api/v1/template-programmer/template/version'
SITE_PROFILE_ADD_SITE_URL = '/api/v1/siteprofile/{site_profile_id}/site/{site_id}'
SITE_PROFILE_URL = '/api/v1/siteprofile'
ONBOARDING_PNP_IMPORT_URL = '/dna/intent/api/v1/onboarding/pnp-device/'
ONBOARDING_CLAIM_DEVICE_URL = '/dna/intent/api/v1/onboarding/pnp-device/site-claim'
PNP_DEVICE_LIST = '/dna/intent/api/v1/onboarding/pnp-device'
TEMPLATE_ID_LIST = '/dna/intent/api/v2/template-programmer/template'
SOFTWARE_IMAGE_LIST = '/dna/intent/api/v1/image/importation'
SOFTWARE_IMAGE_DEPLOY = '/dna/intent/api/v1/image/distribution'
SOFTWARE_IMAGE_ACTIVATE = '/dna/intent/api/v1/image/activation/device'
CLIENT_ENRICHMENT_DETAILS = '/dna/intent/api/v1/client-enrichment-details'
DEVICE_LIST = '/dna/intent/api/v1/network-device'
CLIENT_HEALTH = '/dna/intent/api/v1/client-health'
ALLOWED_MACS = '/dna/intent/api/v1/security/threats/rogue/allowed-list'
SITE_HEALTH = '/dna/intent/api/v1/site-health'
SITE_TOPO = '/dna/intent/api/v1/topology/site-topology'


def load_config_file():
    config = configparser.ConfigParser()
    config.read('../resources/config.ini')
    print(config.sections())
    global USERNAME
    USERNAME = config['DNAC']['USERNAME']
    global PASSWORD
    PASSWORD = config['DNAC']['PASSWORD']
    global BASE_URL
    BASE_URL = config['DNAC']['URL']

# Get Authentication token
def get_dnac_jwt_token():


    response = requests.post(BASE_URL + AUTH_URL,
                             auth=HTTPBasicAuth(USERNAME, PASSWORD),
                             verify=False)
    token = response.json()['Token']
    return token


# Get list of sites
def get_sites(headers):
    response = requests.get(BASE_URL + SITE_URL,
                            headers=headers, verify=False)
    return response.json()['response']


# Get device by serial
def get_device_by_serial(headers, serial_number):
    response = requests.get(BASE_URL + DEVICES_BY_SERIAL_URL.format(serial_number=serial_number),
                            headers=headers,
                            verify=False)
    return response.json()['response']


# Add devices to site
def add_devices_site(headers, site_id, devices):
    headers['__runsync'] = 'true'
    headers['__runsynctimeout'] = '30'
    response = requests.post(BASE_URL + SITE_DEVICE_URL.format(site_id=site_id),
                             headers=headers, json=devices,
                             verify=False)
    return response.json()


# Create template configuration project
def create_network(headers, site_id, network):
    response = requests.post(BASE_URL + NETWORK_URL.format(site_id=site_id),
                             headers=headers, json=network,
                             verify=False)
    return response.json()


# Get template configuration project
def get_configuration_template_project(headers):
    response = requests.get(BASE_URL + TEMPLATE_PROJECT_URL,
                            headers=headers,
                            verify=False)
    return response.json()


# Create template configuration project
def create_configuration_template_project(headers, name):
    response = requests.post(BASE_URL + TEMPLATE_PROJECT_URL,
                             headers=headers,
                             verify=False,
                             data=json.dumps({"name": name}))
    task = response.json()
    # Checks if the project already exists, if it does, it returns True
    if 'errorCode' in task['response']:
        if task['response']['errorCode'] == "NCTP10001":
            print(task['response']['message'])
            return True

    task_complete = measure_task(headers, task['response'])
    return task_complete


# Create template
def create_configuration_template(headers, project_id, template):
    response = requests.post(BASE_URL + TEMPLATE_URL.format(project_id=project_id),
                             headers=headers, json=template,
                             verify=False)
    return response.json()['response']


# Create configuration template version
def create_configuration_template_version(headers, template_version):
    response = requests.post(BASE_URL + TEMPLATE_VERSION_URL,
                             headers=headers, json=template_version,
                             verify=False)
    return response.json()['response']


# Deploy template
def deploy_configuration_template(headers, deployment_info):
    response = requests.post(BASE_URL + TEMPLATE_DEPLOY_URL,
                             headers=headers, json=deployment_info,
                             verify=False)
    return response.json()


# Get Task result
def get_task(headers, task_id):
    response = requests.get(BASE_URL + TASK_BY_ID_URL.format(task_id=task_id),
                            headers=headers, verify=False)
    return response.json()['response']


# Import device to PnP process
def import_device_to_pnp(headers, pnp_import_info):
    response = requests.post(BASE_URL + ONBOARDING_PNP_IMPORT_URL,
                             headers=headers, json=pnp_import_info,
                             verify=False)
    return response.json()


# Create site profile
def create_site_profile(headers, site_profile_info):
    response = requests.post(BASE_URL + SITE_PROFILE_URL,
                             headers=headers, json=site_profile_info,
                             verify=False)
    return response.json()['response']


# Assign Site to Site Profile
def assign_site_to_site_profile(headers, site_profile_id, site_id):
    response = requests.post(BASE_URL +
                             SITE_PROFILE_ADD_SITE_URL.format(site_profile_id=site_profile_id,
                                                              site_id=site_id),
                             headers=headers, verify=False)
    return response.json()


# Import device to PnP process
def claim_device_to_site(headers, claim_info):
    response = requests.post(BASE_URL + ONBOARDING_CLAIM_DEVICE_URL,
                             headers=headers, json=claim_info,
                             verify=False)
    return response.json()


def get_pnp_device_list(headers):
    response = requests.get(BASE_URL + ONBOARDING_PNP_IMPORT_URL,
                            headers=headers, verify=False)
    return response.json()


def get_templates_list(headers, project_id):
    response = requests.get(BASE_URL + TEMPLATE_ID_LIST + f"?projectId={project_id}",
                            headers=headers, verify=False)
    return response.json()


def get_images_list(headers):
    response = requests.get(BASE_URL + SOFTWARE_IMAGE_LIST,
                            headers=headers, verify=False)
    return response.json()


def deploy_software_image(headers, claim_info):
    response = requests.post(BASE_URL + SOFTWARE_IMAGE_DEPLOY,
                             headers=headers, json=claim_info,
                             verify=False)
    return response.json()


def activate_software_image(headers, claim_info):
    response = requests.post(BASE_URL + SOFTWARE_IMAGE_DEPLOY,
                             headers=headers, json=claim_info,
                             verify=False)
    return response.json()


def get_client_enrichment_details(headers):
    response = requests.get(BASE_URL + CLIENT_ENRICHMENT_DETAILS,
                            headers=headers,
                            verify=False)
    return response.json()


def get_device_list(headers):
    response = requests.get(BASE_URL + DEVICE_LIST,
                            headers=headers,
                            verify=False)
    return response.json()


def get_client_health(headers):
    response = requests.get(BASE_URL + CLIENT_HEALTH,
                            headers=headers,
                            verify=False)
    return response.json()


def get_allowed_macs(headers):
    response = requests.get(BASE_URL + ALLOWED_MACS,
                            headers=headers,
                            verify=False)
    return response.json()


def get_site_health(headers):
    response = requests.get(BASE_URL + SITE_HEALTH,
                            headers=headers,
                            verify=False)
    return response.json()


def get_site_topo(headers):
    response = requests.get(BASE_URL + SITE_TOPO,
                            headers=headers,
                            verify=False)
    return response.json()


def create_project_and_get_id(headers, name):
    """
    Searches Template Editor projects and returns the Project ID of the project with the given 'name' parameter.
    If the project is not found, it will create the project and then return the Project ID of the newly created project.
    :param headers: dictionary
    :param name: string
    :return project_id: string
    """
    project_is_created = create_configuration_template_project(headers=headers, name=name)
    if project_is_created:
        projects = get_configuration_template_project(headers=headers)
        for project in projects:
            if project['name'] == name:
                return project['id']


def create_e911_configuration_template(headers, project_id, name="default"):
    # Change <civic-location> to elin-location if needed
    template_content = """location {{ civicType }}-location identifier {{ identifier }} 
  building "{{ building }}"
  city "{{ city }}"
  country "{{ country }}"
  county "{{ county }}"
  primary-road-name "{{ road }}"
  room "{{ room }}"
  state "{{ state }}"
  number "{{ number }}"
interface {{ interface }} 
  location {{ civicType }}-location-id {{ identifier }}""" #Change <civicType> to Elin if needed for Elin.
    with open("../resources/configuration_template.txt") as f:
        template = json.loads(f.read())

    template['name'] = name
    template['templateContent'] = template_content
    task = create_configuration_template(headers=headers, project_id=project_id, template=template)
    if 'errorCode' in task:
        if task['errorCode'] == "NCTP10003":
            print(task['message'])
            return True

    task_complete = measure_task(headers, task)

    return task_complete


def create_template_and_get_id(headers, name, project_id):
    """
    Attempt to create template with given name, if template exists, it returns the template_id. If the template is not found,
    it will create the template and version it. It then returns the template ID of the newly created template.
    :param headers: dictionary
    :param name: string
    :return template_id: string
    """
    template_is_created = create_e911_configuration_template(headers=headers, name=name, project_id=project_id)

    if template_is_created:
        for template in get_templates_list(headers, project_id)['response']:
            pprint(template)
            if template['name'] == name:
                pprint(template['id'])
                return template['id']

        projects = get_configuration_template_project(headers=headers)
        for project in projects:
            if project['id'] == project_id:
                templates = project['templates']
                for template in templates:
                    if template['name'] == name:
                        template_id = template['id']


    # Commit the default template
    task = create_configuration_template_version(headers=headers, template_version={"templateId": template_id})
    task_complete = measure_task(headers, task)
    if task_complete:
        return template_id
    else:
        raise AssertionError('Template was not committed')


def measure_task(headers, task):
    """
    Continuously checks task until it has completed successfully, or an error occurs.

    :param headers: dictionary
    :param task: dictionary
    :return task_complete: bool
    """
    # Continuously checks task until it has completed successfully
    while True:
        response = requests.get(url=BASE_URL + task['url'],
                                headers=headers,
                                verify=False)
        pprint(response)
        if "Success" in response.json()['response']['progress']:
            task_complete = True
            return task_complete
        elif 'isError' in response.json():
            pprint(response)
            raise Exception("An error occured!")
        else:
            time.sleep(1)


def deploy_e911_template(headers, template_id, ip_address, identifier, building, city, country, county, road, room, state, interface, civic_type="civic-location", number="", ):
    #TODO add interface application to the deployment script somehow.
    """
    Deploys e911 template
    :param headers: dictionary
    :param template_id: string
    :param ip_address: string
    :param identifier: string
    :param building: string
    :param city: string
    :param country: string
    :param county: string
    :param road: string
    :param room: string
    :param state: string
    :param number: string
    :param interface string
    :return task: dictionary
    """
    payload = {
        "forcePushTemplate": "true",
        "targetInfo": [
            {
                "id": ip_address,
                "params": {
                    "civic_type": civic_type,
                    "identifier": identifier,
                    "building": building,
                    "city": city,
                    "country": country,
                    "county": county,
                    "road": road,
                    "room": room,
                    "state": state,
                    "number": number,
                    "interface": interface
                },
                "type": "MANAGED_DEVICE_IP"
            }
        ],
        "templateId": template_id
    }

    task = deploy_configuration_template(headers=headers, deployment_info=payload)

    print(task)
    return task

if __name__ == "__main__":
    load_config_file()