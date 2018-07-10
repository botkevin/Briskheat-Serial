# @author Kevin Shi

import briskheat_serial_reader as bsr
from getpass import getpass
import mysql.connector

#runs the briskheat, also an example of usage

bh = None
password = ''

#change this for Briskheat params
def config_briskheat():
    global bh
    bh = bsr.Briskheat('/dev/ttyUSB0', 30, 20, 'status.CSV', 'devamdatadump', 'intern_K', password, 'heatandlogs', 'briskheat_hht01', 'status_briskheat_hht01')

#gets password
def password_input():
    global password
    try:
        print('Input your password')
        password = getpass()
        config_briskheat()
    except mysql.connector.errors.ProgrammingError:
        print('Wrong password')
        password_input()

password_input()
bh.save_dump()
