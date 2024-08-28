# -*- coding: utf-8 -*-
import logging
from math import *
from . import Alma_api_fonctions


class AlmaJob_Instance_Id(object):
    """Return l'id de l'instance pour un jour donnée d'un job identifié via son job_id "
    """

    def __init__(self,job_id, date_start,date_end,accept='json', apikey="", service='AlmaPy') :
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.error_status = False
        self.accept =accept
        self.job_id=job_id
        self.mes_logs = logging.getLogger(service)
        self.appel_api = Alma_api_fonctions.Alma_API(apikey=self.apikey,service=self.service)
        status,response = self.appel_api.request('GET', 
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/jobs/{}/instances?limit=10&offset=0&submit_date_from={}&submit_date_to={}&status=COMPLETED_SUCCESS'.format(job_id,date_start,date_end),
                                        accept=self.accept)
        if status == 'Error':
            self.error_status = True
            self.error_message = response
        else:
            self.result = self.appel_api.extract_content(response)
            self.mes_logs.debug(self.result)
            self.job_instance_id = self.get_job_instance_id()
        


    def get_nb_de_jobs(self):
        return self.result['total_record_count']

    def get_job_instance_id(self):
        if 'job_instance' in self.result.keys():
            return self.result['job_instance'][0]['id']
        else :
            return 0
        
    def get_job_infos(self):
        job_infos = {
            "est_erreur" : False,
            "msg_erreur" : "",
            "job_id" : self.job_instance_id,
        }
        status,response = self.appel_api.request('GET', 
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/jobs/{}/instances/{}'.format(self.job_id,self.job_instance_id),
                                        accept=self.accept)
        if status == 'Error':
            job_infos['est_erreur'] = True
            job_infos['msg_erreur'] = response
            return job_infos
        result = self.appel_api.extract_content(response)
        for counter in result['counter'] :
            job_infos[counter["type"]["value"]] = counter["value"]
        for action in result['action'] :
            job_infos[action["population"]["value"]] = action["members"]
        return job_infos
    
