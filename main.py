import re
import time
from telnetlib import Telnet

def telnet_connection(host, port, username, password):
    """Establish a Telnet connection."""
    conn = Telnet(host, port)
    conn.write(username.encode('ascii') + b"\n")
    conn.write(password.encode('ascii') + b"\n")
    conn.read_until(b"#", timeout=1).decode('ascii')
    return conn

def execute_command(conn, command):
    """Execute a command on the Telnet connection."""
    byteLimiter = b"#"
    conn.write(command.encode('ascii') + b"\n")
    if 'show gpon onu uncfg' in command:
        byteLimiter = b'OnuIndex'
    if 'onu type' in command:
        byteLimiter = b'.[Successful]'
    if 'show gpon onu by sn' in command:
        byteLimiter = b'Search result'
    if 'show gpon onu state gpon-olt' in command:
        byteLimiter = b'ONU Number:'
    if 'show onu running config' in command or 'show running-config interface' in command:
        byteLimiter = b'!'    

    return conn.read_until(byteLimiter, timeout=1).decode('ascii')

def sisir_uncfg(host, port, username, password):
    """Retrieve information about unconfigured ONUs."""
    conn = telnet_connection(host, port, username, password)
    
    command_olt_info = 'show gpon onu uncfg'
    data_onu = execute_command(conn, command_olt_info)
    
    if "OnuIndex" in data_onu:
        onu_info = execute_command(conn, "show gpon onu uncfg")
        extract_and_print_onu_info(onu_info)
    else:
        print(f"No unconfigured ONUs found on {host}")

    conn.close()

def extract_and_print_onu_info(data_onu):
    """Extract and print information about unconfigured ONUs."""
    hostnamenya = re.search(r'.*#', data_onu)

    cari_slot = re.findall('gpon-onu_1/(\d+)', data_onu)
    cari_port = re.findall('gpon-onu_1/\d+/(\d+)', data_onu)
    cari_sn = re.findall('ZTEG.{8}|RETG.{8}', data_onu)

    hasil_sisir = []
    
    for i, (slot, port, sn) in enumerate(zip(cari_slot, cari_port, cari_sn)):
        print(f"{i} {sn} {slot} {hostnamenya[0].strip('#')} {port}")
        data_uncfg = sn, slot, port, hostnamenya[0].strip('#')
        hasil_sisir.append(data_uncfg)

    print(hasil_sisir)

def autoconfig(host, port, username, password, SN, slot1, port1, NoInet, VLAN):
    """Automatically configure an ONU if not provisioned."""
    conn = telnet_connection(host, port, username, password)
    default_onu_id = 1
    script_interface_olt = f'show gpon onu state gpon-olt_1/{slot1}/{port1}\n'
    print(script_interface_olt)
    
    data = execute_command(conn, script_interface_olt)

    if 'No related information to show.' in data:
        print('No ONT provisioned yet')
        configure_new_onu(conn, slot1, port1, SN, NoInet, VLAN,default_onu_id)
    else:
        print('ONT is already provisioned')
        onu_id_ready = checking_onu_id_olt(conn,slot1,port1)
        default_onu_id = onu_id_ready[0]
        configure_new_onu(conn, slot1, port1, SN, NoInet, VLAN,default_onu_id)

    conn.close()

def configure_new_onu(conn, slot1, port1, SN, NoInet, VLAN,onuId):
    """Configure a new ONU."""
    conn.write(b'configure terminal\n')
    data = execute_command(conn, " ")
    print(data)
    
    script_int = f'interface gpon-olt_1/{slot1}/{port1}\n'
    conn.write(script_int.encode('ascii') + b"\n")

    data = execute_command(conn, " ")
    print(data)
    
    script_onu = f'onu {onuId} type ZTE-F609 sn {SN}\n'
    # conn.write(script_onu.encode('ascii') + b"\n")
    execute_command(conn,script_onu)
    
    time.sleep(1)
    conn.write(b'!\n')
    
    configure_service(conn, slot1, port1, SN, NoInet, VLAN)

def configure_service(conn, slot1, port1, SN, NoInet, VLAN,onuId):
    """Configure service parameters for a new ONU."""
    new_onu = f'1/{slot1}/{port1}:{onuId}'
    
    script_service = f'''interface gpon-onu_{new_onu}
name {NoInet}
description ODP_AutoProv
disable-first-online-alarm
tcont 1 profile 100M-UP
gemport 1 tcont 1
gemport 1 traffic-limit downstream 100M-DOWN
service-port 1 vport 1 user-vlan {VLAN} vlan {VLAN}
!
pon-onu-mng gpon-onu_{new_onu}
service 1 gemport 1 vlan {VLAN}
wan-ip 1 mode pppoe username {NoInet} password abece123zzz vlan-profile SVLAN{VLAN} host 1
!'''
    
    data = execute_command(conn, script_service)
    print(data)
    
    if '.[Successful]' in data:
        show_and_verify_configuration(conn, new_onu)
        print('Configuration successful')
    else:
        print('Configuration failed')

def show_and_verify_configuration(conn, new_onu):
    """Display and verify the configuration of a new ONU."""
    script_show_config = f'show running-config interface gpon-onu_{new_onu}\n'    
    data_interface = execute_command(conn,script_show_config)
    
    script_show_onu = f'show onu running config gpon-onu_{new_onu}\n'    
    data_onu = execute_command(conn,script_show_onu)

    print(data_interface + data_onu)
    print('Successful configuration')

def checking_onu_id_olt(conn,slot1,port1):
    """Checking configured onu in olt"""
    possible_onuid = []
    teksBaru = ''
    for _ in range(7):
        conn.write(b' ')
        dataStream = conn.read_until(b"ONU Number:", 1).decode('ascii')
        if 'ONU Number:' not in dataStream:
            teksBaru = teksBaru + dataStream
        else:
            teksBaru = teksBaru + dataStream
            break
    print(teksBaru)

    all_list_onu = re.findall('\d/\d+/\d+:\d+.*', teksBaru)
    list_onuid = []
    possible_onuid = []
    for ketemu in all_list_onu:
        data_mentah = re.split(r'\s+', ketemu)
        slotportonuid = data_mentah[0]
        hasil = slotportonuid.split('/')
        ambil_port_onuid = hasil[2].split(':')
        onu_id = ambil_port_onuid[1]
        list_onuid.append(int(onu_id))
    
    i = 0
    total = ''
    print('jumlah onu id : ', len(list_onuid))

    if len(list_onuid) < 128:
        for _ in range(128):
            i = i + 1
            while i not in list_onuid:
                if total != 128:
                    possible_onuid.append(i)
                    i = i + 1
                    total = len(possible_onuid) + len(list_onuid)
                else:
                    break

    if total == 128:
        print('onu id yang kosong : ', possible_onuid)
    elif len(list_onuid) >= 128:
        possible_onuid = 'slot port penuh'
        print('slot port penuh')
    
    return possible_onuid    

def main():
    host = "your_device_ip"
    port = 23
    username = "your_username"
    password = "your_password"

    # Example Usage
    sisir_uncfg(host, port, username, password)
    autoconfig(host, port, username, password, "example_SN", 1, 2, "example_NoInet", 10)

if __name__ == "__main__":
    main()
