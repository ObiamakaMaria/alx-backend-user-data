#!/usr/bin/env python3
"""Operations related to data filtering"""

from typing import List
import logging
import re
from os import getenv
import mysql.connector

SENSITIVE_FIELDS = ('email', 'name', 'ssn', 'password', 'phone')


def obfuscate_data(fields: List[str], redaction: str,
                   message: str, separator: str) -> str:
    '''
    A function named obfuscate_data that
    returns the obfuscated log message
    '''
    for field in fields:
        message = re.sub(field+'=.*?'+separator,
                         field+'='+redaction+separator, message)
    return message


class RedactingFormatter(logging.Formatter):
    """Custom Formatter class for redacting sensitive data"""

    REDACTION = "***"
    FORMAT = "[COMPANY] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        '''
        A format method to filter values in
        incoming log records using obfuscate_data
        '''
        log_message = super(RedactingFormatter, self).format(record)
        redacted_message = obfuscate_data(self.fields, self.REDACTION,
                                          log_message, self.SEPARATOR)
        return redacted_message


def get_logger() -> logging.Logger:
    '''Obtain a logging instance'''
    logger = logging.getLogger("user_data")
    logger.propagate = False
    logger.setLevel(logging.INFO)
    handler = logger.StreamHandler()
    formatter = RedactingFormatter(SENSITIVE_FIELDS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_database_connection() -> mysql.connector.connection.MySQLConnection:
    '''Obtain a database connection securely'''
    user = getenv('PERSONAL_DATA_DB_USERNAME')
    password = getenv('PERSONAL_DATA_DB_PASSWORD')
    host = getenv('PERSONAL_DATA_DB_HOST')
    db = getenv('PERSONAL_DATA_DB_NAME')
    connection = mysql.connector.connect(user=user, password=password,
                                         host=host, database=db)
    return connection


def main():
    '''
    Entry point of the program
    '''
    database = get_database_connection()
    logger = get_logger()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM users;")
    field_names = cursor.column_names
    for row in cursor:
        message = "".join("{}={}; ".format(key, value) for key, value in zip(field_names, row))
    cursor.close()
    database.close()


if __name__ == "__main__":
    main()
