# -*- coding: utf-8 -*-
import os

import json
import logging
import xml.etree.ElementTree as ET
from math import *
from . import Alma_api_fonctions


class AlmaSet(object):
    """Créé un set de notice bib et et l'alimente"
    """

    def __init__(self,create=True,set_id="",nom="",accept='json', apikey="", service='AlmaPy') :
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.est_erreur = False
        self.logger = logging.getLogger(service)
        self.set_id = set_id
        if create :
            self.create_set(nom,accept)
        else :  
            self.get_set(set_id,accept)
        
    def create_set(self,name, accept='json') :
        data =  {
            "link":"",
            "name": name,
            "description":"Créé par API par le programme {}".format(self.service),
            "type":{"value":"ITEMIZED"},
            "content":{"value":"BIB_MMS"},
            "private":{"value":"false"},
            "status":{"value":"ACTIVE"},
            "note":"",
            "query":{"value":""},
            "origin":{"value":"UI"}
            }
        self.appel_api = Alma_api_fonctions.Alma_API(apikey=self.apikey,service=self.service)
        status,response = self.appel_api.request('POST', 
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets?combine=None&set1=None&set2=None',
                                        accept=accept, content_type=accept, data=json.dumps(data))
        if status == 'Error':
            self.est_erreur = True
            self.message_erreur = response
        else:
            self.set_data = self.appel_api.extract_content(response)
            self.set_id = self.set_data["id"]
            # self.logger.debug(self.set_data)


    def get_set(self,set_id, accept='json') :
        status,response = self.appel_api.request('GET', 
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{}'.format(set_id),
                                        accept=accept)
        if status == 'Error':
            self.est_erreur = True
            self.message_erreur = response
        else:
            self.set_data = self.appel_api.extract_content(response)
            # self.logger.debug(self.set_data)

    def add_members(self,mms_ids_list,accept='json'):
        # On splite la liste des mmsid en liste de 1000 identifiants
        n = 1000
        list_of_mms_ids_list = [mms_ids_list[i * n:(i + 1) * n] for i in range((len(mms_ids_list) + n - 1) // n )]
        for liste_menbres_jeu in list_of_mms_ids_list:
            members = [{'id': element} for element in liste_menbres_jeu]
            self.set_data["members"] = {
                "member" : members
            }
            self.logger.debug(self.set_data)
            status,response = self.appel_api.request('POST', 
                                    'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{}?op=add_members&fail_on_invalid_id=false'.format(self.set_id),
                                    accept=accept, content_type=accept, data=json.dumps(self.set_data))
            if status == 'Error':
                self.est_erreur = True
                self.message_erreur = response
            else:
                self.logger.debug(self.appel_api.extract_content(response))
