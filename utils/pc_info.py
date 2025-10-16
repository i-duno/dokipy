import typing
import os
import getpass

def guess_pc_user() -> typing.Union[str, None]:
    '''
    Checks common sources for the name of the user
    '''
    def check_if_passable(name: typing.Union[str, None]) -> bool:
        if name is None:
            return False
        name = name.strip().lower()
        common = ['user', 'default user', 'admin', 'administrator', 'guest', 'default', 'username']

        #reject if in common list or looks like path
        if name in common:
            return False
        elif '/' in name or '\\' in name:
            return False
        return True
    
    NAME = None
    
    NAME = os.getlogin()
    if check_if_passable(NAME):
        return NAME
    
    NAME = os.environ.get('USERNAME')
    if check_if_passable(NAME):
        return NAME
    
    try:
        NAME = getpass.getuser()
        if check_if_passable(NAME):
            return NAME
    finally:
        pass