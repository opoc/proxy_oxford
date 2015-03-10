# proxy_oxford
Gather connections to Oxford Mercury iPS to simultaneously control the magnet and check the helium level


# Set-up
In the 'proxy_oxford.py', set the Mecury iPS address and port:
`OXFORD_IPS = ('iPS_address', port_number)`

If `DEBUG` is set to True, it will print out the communication data between the softwares and the Mecury iPS.

The `TEST` variable : the data will be directly returned to the sender software.
