"""Module Order."""

import json

from msa_sdk.device import Device


class Order(Device):
    """Class Order."""

    def __init__(self, device_id):
        """Initialize."""
        Device.__init__(self, device_id=device_id)
        self.api_path = '/ordercommand'
        self.read()

    def command_execute(self, command, params, timeout=300):
        """

        Command execute.

        Parameters
        -----------
        command: String
                Order command
                Available values : CREATE, UPDATE, IMPORT, LIST, READ, DELETE

        params: dict
                Parameters in a dict format:

                {
                    "simple_firewall": {
                        "12": {
                                "object_id": "12",
                                "src_ip": "3.4.5.6",
                                "dst_port": "44"
                        }
                }
                timeout:  int timeout in sec (300 secondes by default)

        Returns
        -------
        None

        """
        self.action = 'Command execute'
        self.path = '{}/execute/{}/{}'.format(self.api_path, self.device_id,
                                              command)

        self._call_post(params, timeout)

    def command_generate_configuration(self, command, params):
        """

        Command generate configuration.

        Parameters
        -----------
        command: String
                Order command

        params: dict
              Parameters


        Returns
        -------
        None

        """
        self.action = 'Command generate configuration'
        self.path = '{}/get/configuration/{}/{}'.format(self.api_path,
                                                        self.device_id,
                                                        command)

        self._call_post(params)

    def command_synchronize(self, timeout):
        """

        Command synchronize.

        Parameters
        -----------
        timeout: Integer
              Connection timeout


        Returns
        -------
        None

        """
        self.action = 'Command synchronize'
        self.path = '{}/synchronize/{}'.format(self.api_path,
                                               self.device_id)

        self._call_post(timeout=timeout)

    def command_synchronizeOneOrMoreObjectsFromDevice(self,
                                                      mservice_uris: list,
                                                      timeout: int) -> None:
        """

        Command synchronize objects from a Device.

        Parameters
        -----------
        mservice_uris: List
                List of microservices

        timeout: Integer
                Connection timeout

        Returns
        -------
        None

        """
        self.action = 'Command synchronize'
        self.path = '{}/microservice/synchronize/{}'.format(self.api_path,
                                                            self.device_id)

        params = {"microServiceUris": mservice_uris}

        self._call_post(params, timeout=timeout)

    def command_call(self, command, mode, params, timeout=300):
        """

        Command call.

        Parameters
        -----------
        command: String
                CRUID method in microservice to call
        mode: Integer
                0 - No application
                1 - Apply to base
                2 - Apply to device
        Returns
        --------
        None

        """
        self.action = 'Call command'
        self.path = '{}/call/{}/{}/{}'.format(self.api_path,
                                              self.device_id,
                                              command,
                                              mode)
        self._call_post(params, timeout)

    def command_objects_all(self):
        """

        Get all microservices attached to a device.

        Returns
        --------
        List:
                List of names of microservices attached

        """
        self.action = 'Get Microservices'
        self.path = '{}/objects/{}'.format(self.api_path, self.device_id)
        self._call_get()

    def command_objects_instances(self, object_name):
        """

        Get microservices instance by microservice name.

        Parameters
        -----------
        device_id: Integer
                Device ID of the device
        object_name: String
                Name of microservice
        Returns
        --------
        list of object:
                List of object IDs per microservice

        """
        self.action = 'Get Microservice Instances'
        self.path = '{}/objects/{}/{}'.format(self.api_path,
                                              self.device_id,
                                              object_name)
        self._call_get()

        return json.loads(self.content)

    def command_objects_instances_by_id(self, object_name, object_id):
        """

        Get microservices instance by microservice object ID.

        Parameters
        -----------
        device_id: Integer
                Device ID of the device
        object_name: String
                Name of microservice
        object_id: String
                Object ID of microservice instance
        Returns
        --------
        list of object:
                Object of microservice parameters per object ID

        """
        self.action = 'Get Microservice Object Details'
        self.path = '{}/objects/{}/{}/{}'.format(self.api_path,
                                                 self.device_id,
                                                 object_name,
                                                 object_id)
        self._call_get()

        return json.loads(self.content)

    def command_get_deployment_settings_id(self) -> int:
        """

        Get deployment settings ID for the device.

        Returns
        --------
        Integer:
                Deployment settings ID

        """
        self.action = 'Get deployment settings ID'
        self.path = '/conf-profile/v1/device/{}'.format(self.device_id)
        self._call_get()

        config_profile_device = \
            json.loads(self.content)['ConfigProfileByDevice']

        return int(config_profile_device)
