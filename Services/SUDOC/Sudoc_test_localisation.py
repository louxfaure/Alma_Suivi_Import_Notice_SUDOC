# -*- coding: utf-8 -*-
import os
# external imports
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
import xml.etree.ElementTree as ET
from math import *


__version__ = '0.1.0'
__apikey__ = os.getenv('ALMA_API_KEY')
__region__ = os.getenv('ALMA_API_REGION')

FORMATS = {
    'json': 'application/json',
    'xml': 'application/xml'
}


class Sudoc_Qui_Est_Loc(object):
    """
    """

    def __init__(self,liste_ppn, iln ='15', accept='json', service='AlmaPy') :
        self.service = service
        self.est_erreur = False
        self.logger = logging.getLogger(service)
        status,response = self.request('GET', 
                                       'https://www.sudoc.fr/services/where/{}/{}'.format(iln,','.join(liste_ppn)),
                                        accept=accept)
        if status == 'Error':
            self.est_erreur = True
            self.message_erreur = response
        else:
            self.result = self.extract_content(response)



    @property
    #Construit la requête et met en forme les réponses

    def headers(self, accept='json', content_type=None):
        headers = {
            "User-Agent": "pyalma/{}".format(__version__),
            "Authorization": "apikey {}".format(self.apikey),
            "Accept": FORMATS[accept]
        }
        if content_type is not None:
            headers['Content-Type'] = FORMATS[content_type]
        return headers
    def get_error_message(self, response, accept):
        """Extract error code & error message of an API response
        
        Arguments:
            response {object} -- API REsponse
        
        Returns:
            int -- error code
            str -- error message
        """
        error_code, error_message = '',''
        if accept == 'xml':
            root = ET.fromstring(response.text)
            error_message = root.find(".//xmlb:errorMessage",NS).text if root.find(".//xmlb:errorMessage",NS).text else response.text 
            error_code = root.find(".//xmlb:errorCode",NS).text if root.find(".//xmlb:errorCode",NS).text else '???'
        else :
            try :
             content = response.json()
            except : 
                # Parfois l'Api répond avec du xml même si l'en tête demande du Json cas des erreurs de clefs d'API 
                root = ET.fromstring(response.text)
                error_message = root.find(".//xmlb:errorMessage",NS).text if root.find(".//xmlb:errorMessage",NS).text else response.text 
                error_code = root.find(".//xmlb:errorCode",NS).text if root.find(".//xmlb:errorCode",NS).text else '???'
                return error_code, error_message 
            error_message = content['errorList']['error'][0]['errorMessage']
            error_code = content['errorList']['error'][0]['errorCode']
        return error_code, error_message
    
    def request(self, httpmethod, url, params={}, data=None,
                accept='json', content_type=None, nb_tries=0, in_url=None):
        #20190905 retry request 3 time s in case of requests.exceptions.ConnectionError
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.request(
            method=httpmethod,
            headers={
            "User-Agent": "pyalma/{}".format(__version__),
            "Accept": FORMATS[accept]
        },
            url= url,
            params=params,
            data=data)
        try:
            response.raise_for_status()  
        except requests.exceptions.HTTPError:
            if response.status_code == 400 :
                error_code, error_message= self.get_error_message(response,accept)
                self.logger.error("Alma_Apis :: Connection Error: {} || Method: {} || URL: {} || Response: {}".format(response.status_code,response.request.method, response.url, response.text))
                return 'Error', "{} -- {}".format(error_code, error_message)
            else :
                error_code, error_message= self.get_error_message(response,accept)
            if error_code == "401873" :
                return 'Error', "{} -- {}".format(error_code, "Notice innconnue")
            self.logger.error("Alma_Apis :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(response.status_code,response.request.method, response.url, response.text))
            return 'Error', "{} -- {}".format(error_code, error_message)
        except requests.exceptions.ConnectionError:
            error_code, error_message= self.get_error_message(response,accept)
            self.logger.error("Alma_Apis :: Connection Error: {} || Method: {} || URL: {} || Response: {}".format(response.status_code,response.request.method, response.url, response.text))
            return 'Error', "{} -- {}".format(error_code, error_message)
        except requests.exceptions.RequestException:
            error_code, error_message= self.get_error_message(response,accept)
            self.logger.error("Alma_Apis :: Connection Error: {} || Method: {} || URL: {} || Response: {}".format(response.status_code,response.request.method, response.url, response.text))
            return 'Error', "{} -- {}".format(error_code, error_message)
        return "Success", response
    
    def extract_content(self, response):
        ctype = response.headers['Content-Type']
        if 'json' in ctype:
            return response.json()
        else:
            return response.content.decode('utf-8')
        
    def get_list_bib(self) :
        list_bib = {}
        for bib in self.result['sudoc']['query']['result'] :
            list_bib[bib['library']['rcr']] = bib['library']['shortname']
        return list_bib
    
    def get_liste_notice(self):
        if isinstance(self.result['sudoc']['result'],dict):
           return [self.result['sudoc']['result']]
        else :
           return self.result['sudoc']['result']

    
    