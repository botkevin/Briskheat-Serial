# @author Kevin Shi

import briskheat_serial_reader as bsr
from getpass import getpass

#runs the briskheat, also an example of usage
#gets password
print('Input your password:')
password = getpass()
print(password)

bh = bsr.Briskheat('/dev/ttyUSB0', 30, 20, 'status.CSV', 'devamdatadump', 'intern_K', password, 'heatandlogs', 'briskheat_hht01', 'status_briskheat_hht01')

bh.save_dump()
