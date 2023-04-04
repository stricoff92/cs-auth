
""" Unified location to hold
    list indexes that correspond row columns in
    passwd, shadow, and group
"""

class PasswdLineIXs:
    """ Indexes of data held in the unix style passwd file
        index 1 data should always be 'x' indicating the password is
            hashed and stored in shadow
    """
    USER_NAME = 0
    PLAINTEXT_PASSWORD = 1
    USER_UID = 2
    USER_GROUP_GUID = 3
    USER_DETAILS = 4
    HOME_DIRECTORY = 5
    LOGIN_SHELL = 6

class ShadowLineIXs:
    """ Indexes of data held in the unix style shadow file
    """
    USER_NAME = 0
    HASHED_PASSWORD = 1
    LAST_CHANGE = 2
    MIN_PASSWORD_AGE = 3
    MAX_PASSWORD_AGE = 4
    PASSWORD_WARNING_PERIOD = 5

class GroupLineIXs:
    """ Indexes of data held in the unix style group file
    """
    GROUP_NAME = 0
    GROUP_GUID = 2
    GROUP_MEMBERS = 3
