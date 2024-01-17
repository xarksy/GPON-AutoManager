# GPON Device Automation Script

## Overview

This script automates the management and configuration tasks related to GPON (Gigabit Passive Optical Network) devices. It provides functionalities to retrieve information about unconfigured ONUs, automatically configure ONUs if not provisioned, reset configuration, and save configurations.

## Features

- **sisir_uncfg**: Retrieve information about unconfigured ONUs.

- **autoconfig**: Automatically configure an ONU if not provisioned.

- **resetConfig**: Reset the configuration of a specified ONU.

- **saveConfig**: Save the configuration of a specified ONU.

- **cekOnuId**: Check for available ONU IDs.

- **cariOnunya**: Search and retrieve information about configured ONUs.

- **cekSN**: Check information about an ONU using its Serial Number (SN).

- **cekInterfaceOnu**: Retrieve and display the configuration of a specified ONU.

## Prerequisites

- Python 3.x
- Telnet enabled on the GPON device
- Proper network connectivity to the GPON device
