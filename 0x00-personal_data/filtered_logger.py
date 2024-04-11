#!/usr/bin/env python3
""" Operations related to data filtering """


import logging
from typing import List
import re
from os import getenv
import mysql.connector


PII_FIELDS = ('email', 'name', 'ssn', 'password', 'phone')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    '''
    A function named obfuscate_data that
    returns the obfuscated log message
    '''
    for field in fields:
        mes = re.sub(field+'=.*?'+separator,
                     field+'='+redaction+separator, message)
    return mes


class RedactingFormatter(logging.Formatter):
    """Custom Formatter class for redacting sensitive data
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        '''
        A format method to filter values in
        incoming log records using obfuscate_data
        '''
        message = super(RedactingFormatter, self).format(record)
        redact = filter_datum(self.fields, self.REDACTION,
                              message, self.SEPARATOR)
        return redact


def get_logger() -> logging.Logger:
    ''' Obtain a logging instance'''
    logger = logging.getLogger("user_data")
    logger.propagate = False
    logger.setLevel(logging.INFO)
    handler = logger.StreamHandler()
    fmt = RedactingFormatter(PII_FIELDS)
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    ''' Obtain a database connection securely '''
    user = getenv('PERSONAL_DATA_DB_USERNAME')
    password = getenv('PERSONAL_DATA_DB_PASSWORD')
    host = getenv('PERSONAL_DATA_DB_HOST')
    db = getenv('PERSONAL_DATA_DB_NAME')
    connect = mysql.connector.connect(user=user, password=password,
                                      host=host, database=db)
    return connect


def main():
    '''
    entry point of the program
    '''
    db = get_db()
    logger = get_logger()
    cs = db.cursor()
    cs.execute("SELECT * FROM users;")
    fd = cs.column_names
    for r in cs:
        msg = "".join("{}={}; ".format(k, v) for k, v in zip(fd, r))
    cs.close()
    db.close()


if __name__ == "__main__":
    main()
