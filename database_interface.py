# @author Kevin Shi

import mysql.connector as mariadb

class database_interface:

    # params host, user, password, database, table
    def __init__(self, h, u, pswd, db, t):
        self.mariadb_connection = mariadb.connect(host = h, user = u, password = pswd, database = db)
        self.cursor = self.mariadb_connection.cursor()
        self.table = t

    #takes specifically what data briskheat_serial_reader.py will give it and formats the data so that it can be sent to a database
    #self, time is a array of times, data is a dictionary of arrays
    def write(self, time, data):
        # print(data)
        data_str = ''
        # print(time)
        # format the command to feed into database
        for i in range(len(time)):
            data_str += ' ("' + time[i] + '"'
            for key in data.values():
                data_str += ', ' + str(key[i])
            data_str += '), '
        data_str = data_str[:-2]
        # print(data_str)
        command = 'INSERT INTO ' + self.table + ' VALUES' + data_str
        # print(command)
        self.cursor.execute(command)
        self.mariadb_connection.commit()

    # status message writer writing errors, timestamps, and all the info surrounding an error into the sql log table
    # params time : time of error,
    #        Zone: the zone that the error happened
    #        ErrorID : ID number representing error. See table in README for details
    #        msg: the message corresponding to the ErrorID
    #        info: an info dump of all the information surrounding the error. Not in a human readable format.
    def write_log(self, time, zone, ErrorID, msg, info):
        self.cursor.execute('INSERT INTO ' + self.table + '(ts, zone, ErrorID, msg, info) VALUES ("' + time + '", ' + ', ' + str(zone) + ',' + str(ErrorID) + ', ' + msg + ', ' + info + ')')
        self.mariadb_connection.commit()

    # status message writer writing start or stop times into the sql log table
    # params time: time of start or stop
    #        start_stop_bit: bit representing whether this time is representing a start, stop, or error. 0=start, 1=stop, NULL=error
    def write_start_stop(self, time, start_stop_bit):
        self.cursor.execute('INSERT INTO ' + self.table + '(ts, StartStop) VALUES ("' + time + '", ' + str(start_stop_bit) + ')')
        self.mariadb_connection.commit()
