# GPON Device Automation Script

## Overview

This script automates the management and configuration tasks related to GPON (Gigabit Passive Optical Network) devices. It provides functionalities to retrieve information about unconfigured ONUs, automatically configure ONUs if not provisioned, reset configuration, and save configurations.

## Features

- **telnet_connection**: Establish a Telnet connection.

- **execute_command**: Execute a command on the Telnet connection.

- **sisir_uncfg**: Retrieve information about unconfigured ONUs.

- **extract_and_print_onu_info**: Extract and print information about unconfigured ONUs.

- **autoconfig**: Automatically configure an ONU if not provisioned.

- **configure_new_onu**: Configure a new ONU.

- **configure_service**: Configure service parameters for a new ONU.

- **show_and_verify_configuration**: Retrieve and display the configuration of a specified ONU.

- **checking_onu_id_olt**: Checking configured onu in OLT.

## Prerequisites

- Python 3.x
- Telnet enabled on the GPON device
- Proper network connectivity to the GPON device
