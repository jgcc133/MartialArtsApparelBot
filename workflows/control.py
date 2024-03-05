import yaml

from workflows import utils as ut

# from dataclasses import dataclass

'''Control object to store the keys (from os.environ) and control logic (from user/config.yml)'''


# @dataclass

class Control():
    def __init__(self, control_file_path:str ):
        self.logic = self._load(control_file_path)
    
    def _load(self, control_file: str) -> dict:
        '''Loads control flow from control file (yml file) into the global const CONTROL'''    
        
        ut.pLog(f"Loading Control from {control_file}...")
        try:
            with open(control_file, 'r') as file:
                control = yaml.safe_load(file)            
            ut.pLog(f"Control has been loaded from {control_file}", p1=True)
            ut.logObj(control, "Control")
            return control
        except:
            ut.pLog(f"Unable to load control flow from {control_file}", p1=True)