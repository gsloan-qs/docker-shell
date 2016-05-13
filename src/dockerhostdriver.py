import json

import requests
from cloudshell.api.cloudshell_api import CloudShellAPISession, ResourceAttributesUpdateRequest, AttributeNameValue
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface


class DockerHostDriver (ResourceDriverInterface):
    def __init__(self):
        pass

    # Initialize the driver session, this function is called everytime a new instance of the driver is created
    # This is a good place to load and cache the driver configuration, initiate sessions etc.
    def initialize(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """
        return 'Finished initializing'

    # Destroy the driver session, this function is called everytime a driver instance is destroyed
    # This is a good place to close any open sessions, finish writing to log files
    def cleanup(self):
        pass

    def get_containers(self, context):
        """
        Retrieves the docker containers currently active on the host/swarm
        :param context: This is the execution context automatically injected by CloudShell when running this command
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return The JSON description of the running containers
        :rtype str
        """
        address = context.resource.address
        response = requests.get('{address}/containers/json'.format(address=address) )
        return response.json()

    def destroy_container(self, context, ports):
        """
        Destroys a running container, stopping and deleting it from CloudShell as well as from the Docker host/swarm
        :param context: This is the execution context automatically injected by CloudShell when running this command
        :type context: cloudshell.shell.core.driver_context.ResourceRemoteCommandContext
        :return The JSON response and HTTP status code
        :rtype str
        """
        vm_info_json =context.remote_endpoints[0].app_context.deployed_app_json
        vm_info_obj = json.loads(vm_info_json)
        uid = vm_info_obj['vmdetails']['uid']
        log = ""
        address = context.resource.address
        response = requests.post('{address}/containers/{uid}/stop'.format(address=address, uid=uid) )
        log+=str(response.status_code) + ": " + response.content
        response = requests.delete('{address}/containers/{uid}'.format(address=address, uid=uid) )
        log = log + '\n' + str(response.status_code) + ": " + response.content
        # session = CloudShellAPISession(host=context.connectivity.server_address,token_id=context.connectivity.admin_auth_token,domain='Global')
        self._get_api_session(context).DeleteResource(context.remote_endpoints[0].name)
        return log

    def deploy_image(self, context, source_docker_image, environment_variables_list, port_config):
        """
        Deploys a container from an image
        :param context: This is the execution context automatically injected by CloudShell when running this command
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :param source_docker_image: The docker image to create the container from
        :type source_docker_image: str
        :param environment_variables_list: Environment variables to use for the container, provided as comma separated list of name=value
        :type environment_variables_list: str
        :param port_config: Additional ports to expose on the host, should be provided as a comma separated list
        :type port_config: str
        :return The deployed app container name and identifier
        :rtype str
        """
        create_request_data = self._get__deploy_request(environment_variables_list,port_config,source_docker_image)

        self._get_api_session(context).WriteMessageToReservationOutput(context.reservation.reservation_id,"sending: " +
                                                                       create_request_data)

        address = context.resource.address
        response = None
        try:
            response = requests.post('{address}:4000/containers/create'.format(address=address),
                                     create_request_data)

        except Exception as e:
            self._get_api_session(context).WriteMessageToReservationOutput(context.reservation.reservation_id, "error"
                                                                           + e.message)

        self._get_api_session(context).WriteMessageToReservationOutput(context.reservation.reservation_id,
                                                                       "response" + response.content)

        container_id = response.json()["Id"]

        formatted_return_str = '{ "vm_name" : "%s", "vm_uuid" : "%s", "cloud_provider_resource_name" : "%s"}' % \
              (source_docker_image.replace('/','_').replace(':','_') ,container_id, context.resource.name)

        return json.loads(formatted_return_str)

    # the name is by the Qualisystems conventions
    def remote_refresh_ip(self, context, ports):
        """
        Deploys a container from an image
        :param context: This is the execution context automatically injected by CloudShell when running this command
        :type context: cloudshell.shell.core.driver_context.ResourceRemoteCommandContext
        :param ports: OBSOLETE - information on the remote ports
        :type ports: str

        """
        container_info_json = self.get_container_information(context,ports)
        ip = container_info_json["Node"]["IP"]
        matching_resources = \
            self._get_api_session(context).FindResources(attributeValues=[AttributeNameValue("Private IP", ip)])\
                .Resources

        if len(matching_resources) > 0:
            address = matching_resources[0].Address
        else:
            address = context.resource.address

        ports = container_info_json["NetworkSettings"]["Ports"]

        #Todo: make the list of ports extensible by variable
        attribute_value = ''
        attribute_name = ''
        if '22/tcp' in ports:
            attribute_value = ports['22/tcp'][0]['HostPort']
            attribute_name = 'SSH_Port'

        if '80/tcp' in ports:
            attribute_value = ports['80/tcp'][0]['HostPort']
            attribute_name = 'WWW_Port'

        if '8000/tcp' in ports:
            attribute_value = ports['8080/tcp'][0]['HostPOrt']
            attribute_name = 'WWW_Port'

        attribute_changes = self._get_attribute_update_request(context, attribute_name, attribute_value)
        self._get_api_session(context).SetAttributesValues(  resourcesAttributesUpdateRequests=attribute_changes)
        self._get_api_session(context).UpdateResourceAddress(resourceFullPath=context.remote_endpoints[0].name,
                                                             resourceAddress=address)


    def _get_api_session(self, context):
        return CloudShellAPISession(domain="Global", host=context.connectivity.server_address,
                                    token_id=context.connectivity.admin_auth_token,
                                    port=context.connectivity.cloudshell_api_port)



    def _get_attribute_update_request(self, context, attribute_name, attribute_value):

        return [ResourceAttributesUpdateRequest(context.remote_endpoints[0].name,
                                                [AttributeNameValue(Name=attribute_name,Value=attribute_value)])]


    def get_container_information(self, context, ports ):
        address = context.resource.address
        vm_info_json =context.remote_endpoints[0].app_context.deployed_app_json
        vm_info_obj = json.loads(vm_info_json)
        uid = vm_info_obj['vmdetails']['uid']
        response = requests.get('{address}/containers/{uid}/json'.format(address=address, uid=uid) )
        result = response.json()
        return result


    # the name is by the Qualisystems conventions
    def show_logs(self, context, ports):
        address = context.resource.address
        vm_info_json =context.remote_endpoints[0].app_context.deployed_app_json
        vm_info_obj = json.loads(vm_info_json)
        uid = vm_info_obj['vmdetails']['uid']
        response = requests.get('{address}/containers/{uid}/logs?stdout=1'.format(address=address, uid=uid) )
        return response.content

    def power_on(self, context, vm_uuid, resource_fullname):
        uid = vm_uuid
        log = ""
        address = context.resource.address

        response = requests.post('{address}/containers/{uid}/start'.format(address=address, uid=uid) )
        log+=str(response.status_code) + ": " + response.content
        return log

    def _wrap_in_parenthesis(self, value):
        value = value.strip()
        if not value.startswith('"'):
            value = '"' + value
        if not value.endswith('"'):
            value += '"'
        return value

    def _get__deploy_request(self, env, port_config, image):
        request_segments = []
        host_config_segments = []
        request_segments.append('"Cmd":[]')
        if len(env.strip()) > 0:
            env_variables = env
            env_variables_arr = env_variables.split(",")
            env_variables = ', '.join([self._wrap_in_parenthesis(x) for x in env_variables_arr])
            request_segments.append('"Env" : [{env_variables}]'.format(env_variables=env_variables))
        else:
            request_segments.append('"Env" : []')

        if len(port_config.strip()):
            ports = port_config.split(",")
            exposed_ports = '"ExposedPorts": {{ {exposed_ports} }}' \
                .format(exposed_ports=', '.join(['"{port}/tcp": {{}}'.format(port=port) for port in ports]))
            request_segments.append(exposed_ports)
            port_binding = '"PortBindings": {{ {port_binding} }}' \
                .format(
                port_binding=", ".join('"{port}/tcp": [{{ "HostPort": "" }}]'.format(port=port) for port in ports))
            host_config_segments.append(port_binding)

        request_segments.append('"Image":"{image}"'.format(image=image))
        host_config_segments.append('"PublishAllPorts": true')

        host_config_section = '"HostConfig": {{ {host_config} }}'.format(host_config=", ".join(host_config_segments))
        request_segments.append(host_config_section)
        request_section = ', '.join(request_segments)
        return '{{ {request_section} }}'.format(request_section=request_section)

