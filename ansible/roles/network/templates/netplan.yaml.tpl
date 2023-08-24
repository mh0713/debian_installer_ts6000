network:
  version: 2
  renderer: NetworkManager
  ethernets:
    {{ LAN1 }}:
      dhcp4: no
    {{ LAN2 }}:
      dhcp4: no
    {{ LAN3 }}:
      dhcp4: no
  bridges:
    br-inline:
      interfaces:
        - {{ LAN1 }}
        - {{ LAN2 }}
      dhcp4: yes
      dhcp6: yes
      dhcp4-overrides:
        route-metric: 50
      parameters:
        forward-delay: 0
        stp: no
    br-reverse:
      interfaces:
        - {{{ LAN3 }}}
      dhcp4: no
      dhcp6: no
      parameters:
        forward-delay: 0
        stp: no
      addresses:
        - {{ LAN3_IP }}
      gateway4: {{ LAN3_GW }}
      nameservers:
        addresses:
          - {{ LAN3_DNS }}