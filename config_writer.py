# @author Kevin Shi
print('Welcome to the config writer')
print('Enter the following parameters and a config.py file will be outputted, which can then be run to start the program')
print('Port:')
port = "'" + input() + "', "
print('Poll Interval (x10 sec): ')
p_interval = input() + ", "
print('Send Interval (xPoll Interval): ')
s_interval = input() + ", "
print('Status Directory: ')
status_dir = "'" + input() + "', "
print('SQL Hostname: ')
host = "'" + input() + "', "
print('User: ')
user = "'" + input() + "', "
print('Database: ')
db = "'" + input() + "', "
print('Temperature Table: ')
t = "'" + input() + "', "
print('Logging Table: ')
lt = "'" + input() + "'"

with open('config.py', 'w') as f:
    print("""# @author Kevin Shi

import briskheat_serial_reader as bsr
from getpass import getpass
import mysql.connector

#runs the briskheat, also an example of usage

bh = None
password = ''

#change this for Briskheat params
def config_briskheat():
    global bh
    bh = bsr.Briskheat("""+port+p_interval+s_interval+status_dir+host+user+db+t+lt+""")

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
bh.save_dump()""", file = f)

