# @author Kevin Shi

import mysql.connector as mariadb

class database_interface:

    # params host, user, password, database, table
    def __init__(self, h, u, pswd, db, t, tool = '', port = ''):
        try:
            self.mariadb_connection = mariadb.connect(host = h, user = u, password = pswd, database = db)
            self.cursor = self.mariadb_connection.cursor()
            self.table = t
            self.tool = tool
            self.port = port
        except Exception as e:
            raise NotImplementedError

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

    # status message writer writing errors and start stop times to sql table
    # params time : time of error,
    #        Status : ID number representing error. See table in README for details | value representing start or stop
    #        Zone: the zone that the error happened
    #        msg: the message corresponding to the StatusID
    def write_log(self, time, StatusID, zone = 'NULL', msg = 'NULL'):
        self.cursor.execute('INSERT INTO ' + self.table + ' (ts, identifier, StatusID, zone, msg) VALUES ("'
                            + time + '", "' + self.tool+self.port + '", "'+ str(StatusID) + '", ' + str(zone) + ', "' + msg + '")')
        self.mariadb_connection.commit()
