from enum import Enum


class UserType(Enum):
    '''Defines the usertypes allowed in the system'''
    CHURCH_USER = 'CHURCH_USER'
    DIVISION_USER = 'DIVISION_USER'
    FINANCE_OFFICER = 'FINANCE_OFFICER'
    ADMIN = 'ADMIN'
    
