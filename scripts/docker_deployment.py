import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import *
import os
import json


reservation_id = helpers.get_reservation_context_details().id
service_details = helpers.get_resource_context_details()
dict = helpers.get_resource_context_details_dict()
docker_host = service_details.attributes['Docker Host']
image = service_details.attributes['Docker Image']
environment = service_details.attributes['Container Env']
ports = service_details.attributes['Container Ports']


api = helpers.get_api_session()

api.WriteMessageToReservationOutput(reservation_id,"Deploying App..." )
result = api.ExecuteCommand(reservationId=reservation_id, targetName=docker_host, targetType="Resource",
                            commandName="deploy_image",
                            commandInputs=[InputNameValue("app_name",dict["appData"]["name"]),
                                           InputNameValue("image", image),InputNameValue("env", environment),
                                           InputNameValue("port_config", ports)])

api.WriteMessageToReservationOutput(reservation_id,"Deploy done:" + result.Output)

if hasattr(result, "Output"):
    print 'command_json_result=%s=command_json_result_end' % result.Output
else:
    print 'command_json_result=%s=command_json_result_end' % result

