from enum import Enum


class UserType(Enum):
    '''Defines the usertypes allowed in the system'''
    CHURCH_USER = 'CHURCH_USER'
    DIVISION_USER = 'DIVISION_USER'
    FINANCE_OFFICER = 'FINANCE_OFFICER'
    ADMIN = 'ADMIN'
    

class SupportType(Enum):
    '''Defines the support types allowed in the system'''
    AID = 'AID'
    REVOLVING_FUND = 'REVOLVING_FUND'


class ApplicationStatus(Enum):
    '''Defines the application statuses allowed in the system'''
    DRAFT = 'DRAFT'
    PENDING = 'PENDING REVIEW'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    DELETED = 'DELETED'

class ConstLists:
    '''Defines the constant lists for the system'''
    user_types = [
        (UserType.CHURCH_USER.name, UserType.CHURCH_USER.value),
        (UserType.DIVISION_USER.name, UserType.DIVISION_USER.value),
        (UserType.FINANCE_OFFICER.name, UserType.FINANCE_OFFICER.value),
        (UserType.ADMIN.name, UserType.ADMIN.value),
    ]
    
    support_types = [
        (SupportType.AID.name, SupportType.AID.value), 
        (SupportType.REVOLVING_FUND.name, SupportType.REVOLVING_FUND.value)
    ]
    
    church_project_types = [
        ('REGIONAL HEADQUARTERS CHURCH', 'REGIONAL HEADQUARTERS CHURCH'),
        ('DIVISIONAL HEADQUARTERS CHURCH', 'DIVISIONAL HEADQUARTERS CHURCH'),
        ('GROUP OF DISTRICTS HEADQUARTERS CHURCH', 'GROUP OF DISTRICTS HEADQUARTERS CHURCH'),
        ('DISTRICT CHURCH', 'DISTRICT CHURCH'),
        ('LOCATION CHURCH', 'LOCATION CHURCH'),
    ]

