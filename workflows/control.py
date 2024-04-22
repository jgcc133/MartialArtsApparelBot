import yaml

from workflows import utils as ut

# from dataclasses import dataclass

'''Control object to store the keys (from os.environ) and control logic (from user/config.yml)'''


class Control():
    def __init__(self, control_file_path:str ):
        self.logic = self._load(control_file_path)
    
    def _load(self, control_file: str):
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

    def update(self, trawler):
        ut.pLog(f"Updating control with {list(trawler.trawlers.keys())}")
        try:
            tree = trawler.trawlers['GoogleDrive'].pointers
            bc = trawler.trawlers['GoogleDrive']._Trawler__breadcrumbs

            # the branch of control that we're interested in updating is:
            # self.logic['B2DFlow']['data']['callbacks']['Product Enquiry'] and
            # creating a list of callbacks based on the products, categories, etc

            current_flow = self.logic['B2DFlow']['data']['callbacks']
            new_flow = current_flow.copy()
            new_media = {}

            # update 'Product Enquiry' buttons
            new_flow['Product Enquiry']['btn'] = sorted(list(tree.keys()))
            categories = sorted(list(tree.keys()))
            products = sorted(list(bc['products'].keys()))
            variations = sorted(list(bc['variations'].keys()))

            # iterate over the rest of 'callbacks', if category, or product, generate buttons for up to variations
            # if variations, generate buttons for media, purchase, or try on
            
            # Loop 1: Iterate over current_flow, if it is a category/ product/ variation and it is not in tree.keys(), remove it
            for key, callback in current_flow.items():
                if callback['tag'] == 'category':
                    if key not in categories:
                        del new_flow[key]
                    pass
                elif callback['tag'] == 'product':
                    if key not in products:
                        del new_flow[key]
                    pass
                elif callback['tag'] == 'variation':
                    if key not in variations:
                        del new_flow[key]
                    pass
                else:

                    pass

            # Loop 2: Iterate over tree.keys(), add new category key
            for cat in categories:
                if cat not in new_flow.keys():
                    # add new callback
                    new_flow[cat] = {'tag': 'category',
                                     'msg': 'Which product would you like to explore?',
                                     'btn': sorted(list(tree[cat]['products'].keys()))}
            for prod in products:
                if prod not in new_flow.keys():
                    # add new callback
                    cate = bc['products'][prod]['category']
                    new_flow[prod] = {'tag': 'product',
                                     'msg': 'Which variation would you like to explore?',
                                     'btn': sorted(list(tree[cate]['products'][prod]['variations'].keys()))}
            
            for vari in variations:
                if vari not in new_flow.keys():
                    # add new callback, that sends media, with 1 add to cart and 1 back button
                    cate, prod = bc['variations'][vari]['category'], bc['variations'][vari]['product']
                    new_flow[vari] = {'tag': 'variation',
                                      'msg': cate + "\n" + vari,
                                      'media': list(tree[cate]['products'][prod]['media'].keys())
                                                     + list(tree[cate]['products'][prod]['variations'][vari]['media'].keys()),
                                      'btn': ['Add to Cart', 'Back']}
                    
            # Loop 3: Iterate over media, and consolidate into new_meda
            # await tele._Tele__uploadMedia(self.logic)
            for name, media in trawler.trawlers['GoogleDrive'].mediaList.items():
                new_media[name] = media['storage']
        except:
            raise ValueError(f"Unable to update control")
        self.logic['B2DFlow']['data']['callbacks'] = new_flow
        self.logic['MediaList']['data'] = new_media

        return self.logic