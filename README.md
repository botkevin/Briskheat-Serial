# Briskheat-Serial
Briskheat Serial Communication Analysis
A tool for connecting to the Centipede Briskheat tool for measuring temperatures through RS-232 port. 
Files in use in latest version are briskheat_serialreader.py and database_interface.py

## ```briskheat_serial_reader.py```
This is the bread and butter of the program. It connects to the Briskheat and handles the connection and parsing.
To run the serial_reader, first initialize class ```Briskheat``` and then run the command ```save_dump()``` on the new object.
To debug and have further communication/control of the Briskheat, run ```ez_terminal()``` on the object.

### Initializing Briskheat
#### Initialization requires several parameters
- path : port to open,
- poll_interval_x10 : interval to poll data: unit of time is ten seconds,
- sql_interval_xpoll : interval to send information to datase: unit of time is 1 poll interval
- status_dir : directory to write status and log messages to
- host : host of sql databse
- user : username for the sql server
- pswd : password for the sql server
- db : sql database name
- t : table name to store the data in
- lt: log table to store status and log messages
#### Example
Running: 
```
bh = bsr.Briskheat('/dev/ttyUSB0', 30, 20, 'status.CSV', 'sql_host', 'user1', 'hunter2', 'briskheat', 'Temp_HHT01', 'Status_HHT01')
```
will generate a Briskheat object called bh that 
- reads from the usb device mounted on '/dev/ttyUSB0'
- have a poll interval of 30 x 10 seconds(5 min)
- the interval of sending the stored up cache of data will be 20 x poll interval, so 20 x 5 min(1 hour)
- store status and log messages in a file called 'status.CSV'
- connect to a database using the
  - host with the name 'sql_host'
  - password 'hunter2'
  - database 'briskheat'
  - table for storing temperatures 'Temp_HHT01'
  - table for storing status and log messages 'Status_HHT01'
  
### Starting the Recording Process
#### Using the command
To start the process of recording temperatures, run the command ```save_dump()``` on the object
#### Example
Using the previous object created in the previous example, ```bh```, running the following command will start the recording process:
```bh.save_dump()```

### Debugging and Further Control
Run ```ez_terminal``` on the object and in terminal, a mini-terminal will start with ```BH > ```. From here, more commands can be run. By pressing '?' and enter, further help and commands will show.

<sub><sup>> Note with the current build, disabled zones will not send error messages as to not spam the status log with unimportant error messages and dilute the file. If needed to change, navigate to error check and delete ```code != '001'```</sup></sub>
