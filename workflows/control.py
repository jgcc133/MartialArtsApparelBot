import yaml

from workflows import utils as ut

# from dataclasses import dataclass

'''Control object to store the keys (from os.environ) and control logic (from user/config.yml)'''


class Control():
    def __init__(self, control_file_path:str ):
        self.__filepath = control_file_path
        self.logic = self._load()
    
    def _load(self):
        '''Loads control flow from control file (yml file) into the global const CONTROL'''    
        
        ut.pLog(f"Loading Control from {self.__filepath}...")
        try:
            with open(self.__filepath, 'r') as file:
                control = yaml.safe_load(file)            
            ut.pLog(f"Control has been loaded from {self.__filepath}", p1=True)
            ut.logObj(control, "Control")
            return control
        except:
            ut.pLog(f"Unable to load control flow from {self.__filepath}", p1=True)
    
    async def firstUpdate(self, trawler, tele):
        ut.pLog(f"Handling media from {list(trawler.trawlers.keys())} to telegram")
        trawler = trawler.trawlers['GoogleDrive']
        current_tree = trawler.pointers.copy()
        trawler.idPull(download_media=True)
        new_tree = trawler.pointers

        bc = trawler._Trawler__breadcrumbs
        current_flow = self.logic['B2DFlow']['data']['callbacks']
        new_flow = current_flow.copy()
        new_media = trawler.mediaList
        current_media = self.logic['MediaList']['data']

        new_flow['Product Enquiry']['btn'] = sorted(list(new_tree.keys())) + ['Back to Start']
        categories = sorted(list(new_tree.keys()))
        products = sorted(list(bc['products'].keys()))
        variations = sorted(list(bc['variations'].keys()))

        # Loop 1: Iterate over current_flow, if it is a category/ product/ variation and it is not in tree.keys(), remove it
        for key, callback in current_flow.items():
            if callback:
                if callback['tag'] == 'category':
                    if key not in categories: del new_flow[key]
                elif callback['tag'] == 'product':
                    if key not in products: del new_flow[key]
                elif callback['tag'] == 'variation':
                    if key not in variations: del new_flow[key]
                else:
                    pass
        # Loop 2: Iterate over tree.keys(), add new category key
        for cat in categories:
            # add new callback
            available_products = sorted(list(new_tree[cat]['products'].keys()))
            if len(available_products) == 0:
                new_flow[cat] = {'tag': 'category',
                                'msg': f"Stay tuned! More {cat} will be added to the store soon!",
                                'btn': available_products + ["Back to Categories"]}
            else:
                new_flow[cat] = {'tag': 'category',
                                'msg': 'Which product would you like to explore?',
                                'btn': available_products + ["Back to Categories"]}            
        new_flow["Back to Categories"] = new_flow["Product Enquiry"]

        for prod in products:
            # add new callback
            cate = bc['products'][prod]['category']
            available_variations = sorted(list(new_tree[cate]['products'][prod]['variations'].keys()))
            product_media = list(new_tree[cate]['products'][prod]['media'].keys())
            if len(available_variations) == 0 and len(product_media) == 0:
                new_flow[prod] = {'tag': 'product',
                                'msg':  f"Stay tuned! We will be adding more {prod} photos soon!",
                                'media': product_media,
                                'btn': available_variations + [f"Back to {cate}"]}
            elif len(available_variations) == 0 and len(product_media) != 0:
                new_flow[prod] = {'tag': 'product',
                                'msg':  prod,
                                'media': product_media,
                                'btn': available_variations + [f"Back to {cate}", "Back to Start"]}
            else:
                new_flow[prod] = {'tag': 'product',
                                'msg': 'Which variation would you like to explore?',
                                'media': product_media,
                                'btn': available_variations + [f"Back to {cate}", "Back to Start"]}
            new_flow[f"Back to {cate}"] = new_flow[cate]

        for vari in variations:
            # add new callback, that sends media, with 1 add to cart and 1 back button
            cate, prod = bc['variations'][vari]['category'], bc['variations'][vari]['product']
            variation_media = list(new_tree[cate]['products'][prod]['variations'][vari]['media'].keys())
            if len(variation_media) == 0:
                new_flow[vari] = {'tag': 'variation',
                                'msg': f"Stay tuned! We will be adding more {vari} photos soon!",
                                'media': variation_media,
                                'btn': ['Add to Cart', f"Back to {prod}", f"Back to {cate}", "Back to Start"]}
            else:
                new_flow[vari] = {'tag': 'variation',
                                'msg': prod + "\n" + vari,
                                'media': variation_media,
                                'btn': ['Add to Cart', f"Back to {prod}", f"Back to {cate}", "Back to Start"]}
            new_flow[f"Back to {prod}"] = new_flow[prod]

        # Loop 3: Iterate over media, and consolidate into new_meda
        ut.pLog(f"Uploading Media from Google Drive to Tele")
        for name, media in trawler.mediaList.items():
            new_media[name] = media['storage']
        
        self.logic['B2DFlow']['data']['callbacks'] = new_flow
        self.logic['MediaList']['data'] = new_media

        await tele.update(self.logic, upload_media=True)
        with open(self.__filepath, 'w') as file:
            yaml.dump(self.logic, file, sort_keys=False)


    async def update(self, trawler, tele, force_update: bool =False):
        trawler = trawler.trawlers['GoogleDrive']
        current_tree = trawler.pointers.copy()
        trawler.update()
        new_tree = trawler.pointers

        if new_tree != current_tree or force_update:
            ut.pLog("Update of Files Required.")
            try:
                # trawler.trawlers['GoogleDrive'].idPull(download_media = True)
                bc = trawler._Trawler__breadcrumbs

                # the branch of control that we're interested in updating is:
                # self.logic['B2DFlow']['data']['callbacks']['Product Enquiry'] and
                # creating a list of callbacks based on the products, categories, etc

                current_flow = self.logic['B2DFlow']['data']['callbacks']
                new_flow = current_flow.copy()
                new_media = {}

                # update 'Product Enquiry' buttons
                new_flow['Product Enquiry']['btn'] = sorted(list(new_tree.keys())) + ['Quick Search', 'Back to Start']
                
                categories = sorted(list(new_tree.keys()))
                products = sorted(list(bc['products'].keys()))
                variations = sorted(list(bc['variations'].keys()))

                # iterate over the rest of 'callbacks', if category, or product, generate buttons for up to variations
                # if variations, generate buttons for media, purchase, or try on
                
                # Loop 1: Iterate over current_flow, if it is a category/ product/ variation and it is not in tree.keys(), remove it
                for key, callback in current_flow.items():
                    if callback:
                        if callback['tag'] == 'category':
                            if key not in categories: del new_flow[key]
                        elif callback['tag'] == 'product':
                            if key not in products: del new_flow[key]
                        elif callback['tag'] == 'variation':
                            if key not in variations: del new_flow[key]
                        else:
                            pass

                # Loop 2: Iterate over tree.keys(), add new category key
                for cat in categories:
                    # add new callback
                    available_products = sorted(list(new_tree[cat]['products'].keys()))
                    if len(available_products) == 0:
                        new_flow[cat] = {'tag': 'category',
                                        'msg': f"Stay tuned! More {cat} will be added to the store soon!",
                                        'btn': available_products + ["Back to Categories"]}
                    else:
                        new_flow[cat] = {'tag': 'category',
                                        'msg': 'Which product would you like to explore?',
                                        'btn': available_products + ["Back to Categories"]}            
                new_flow["Back to Categories"] = new_flow["Product Enquiry"]

                for prod in products:
                    # add new callback
                    cate = bc['products'][prod]['category']
                    available_variations = sorted(list(new_tree[cate]['products'][prod]['variations'].keys()))
                    product_media = list(new_tree[cate]['products'][prod]['media'].keys())
                    if len(available_variations) == 0 and len(product_media) == 0:
                        new_flow[prod] = {'tag': 'product',
                                        'msg':  f"Stay tuned! We will be adding more {prod} photos soon!",
                                        'media': product_media,
                                        'btn': available_variations + [f"Back to {cate}"]}
                    elif len(available_variations) == 0 and len(product_media) != 0:
                        new_flow[prod] = {'tag': 'product',
                                        'msg':  prod,
                                        'media': product_media,
                                        'btn': available_variations + [f"Back to {cate}", "Back to Start"]}
                    else:
                        new_flow[prod] = {'tag': 'product',
                                        'msg': 'Which variation would you like to explore?',
                                        'media': product_media,
                                        'btn': available_variations + [f"Back to {cate}", "Back to Start"]}
                    new_flow[f"Back to {cate}"] = new_flow[cate]

                for vari in variations:
                    # add new callback, that sends media, with 1 add to cart and 1 back button
                    cate, prod = bc['variations'][vari]['category'], bc['variations'][vari]['product']
                    variation_media = list(new_tree[cate]['products'][prod]['variations'][vari]['media'].keys())
                    if len(variation_media) == 0:
                        new_flow[vari] = {'tag': 'variation',
                                        'msg': f"Stay tuned! We will be adding more {vari} photos soon!",
                                        'media': variation_media,
                                        'btn': ['Add to Cart', f"Back to {prod}", f"Back to {cate}", "Back to Start"]}
                    else:
                        new_flow[vari] = {'tag': 'variation',
                                        'msg': prod + "\n" + vari,
                                        'media': variation_media,
                                        'btn': ['Add to Cart', f"Back to {prod}", f"Back to {cate}", "Back to Start"]}
                    new_flow[f"Back to {prod}"] = new_flow[prod]
                            
                # Loop 3: Iterate over media, and consolidate into new_meda
                ut.pLog(f"Uploading Media from Google Drive to Tele")
                for name, media in trawler.mediaList.items():
                    new_media[name] = media['storage']
                
                self.logic['B2DFlow']['data']['callbacks'] = new_flow
                self.logic['MediaList']['data'] = new_media
                
                await tele.update(self.logic)
            except:
                raise ValueError(f"Unable to update control")
            with open(self.__filepath, 'w') as file:
                yaml.dump(self.logic, file, sort_keys=False)

        return self.logic