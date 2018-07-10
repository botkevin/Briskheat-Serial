# @author Kevin Shi

import mysql.connector as mariadb

class database_interface:

    # params host, user, password, database, table
    def __init__(self, h, u, pswd, db, t):
        self.mariadb_connection = mariadb.connect(host = h, user = u, password = pswd, database = db)
        self.cursor = self.mariadb_connection.cursor()
        self.table = t

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

    # params time : time of error,
    #        ErrorID : ID number representing error. See table in README for details
    def write_log(self, time, zone, ErrorID, msg, info):
        self.cursor.execute('INSERT INTO ' + self.table + '(ts, zone, ErrorID, msg, info) VALUES ("' + time + '", ' + ', ' + str(zone) + ',' + str(ErrorID) + ', ' + msg + ', ' + info + ')')
        self.mariadb_connection.commit()

    # params time: time of start or stop
    #        start_stop_bit: bit representing whether this time is representing a start, stop, or error. 0=start, 1=stop, NULL=error
    def write_start_stop(self, time, start_stop_bit):
        self.cursor.execute('INSERT INTO ' + self.table + '(ts, StartStop) VALUES ("' + time + '", ' + str(start_stop_bit) + ')')
        self.mariadb_connection.commit()
