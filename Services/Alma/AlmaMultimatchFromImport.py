# -*- coding: utf-8 -*-
import math

import json
import logging
from math import *
from . import Alma_api_fonctions, AlmaRecord



class AlmaMultimatchFromImport(object):
    """Retourne les identifiants des notices chargées pour lesquelles une ou pluisieurs correspondance ont été trouvées dan sAlma  """

    def __init__(
        self, job_id="", instance="", population="", apikey="", service="AlmaPy", nombre_de_membres=0
    ):
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.est_erreur = False
        self.message_erreur = ""
        self.mes_logs = logging.getLogger(service)
        self.job_id = job_id
        self.instance_id = instance
        self.population = population
        self.nombre_de_membres = nombre_de_membres
        self.liste_membres_set = {}
        self.accept = "json"
        self.appel_api = Alma_api_fonctions.Alma_API(
            apikey=self.apikey, service=self.service
        )
        

        self.liste_des_membres()





    def get_match_members(self, offset):
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/jobs/{}/instances/{}/matches?population={}&limit=100&&offset={}".format(
                self.job_id, self.instance_id, self.population,offset
            ),
            accept=self.accept,
        )
        if status == "Error":
            return True, response
        else:
            return False, self.appel_api.extract_content(response)


    def liste_des_membres(self):
        """Récupère la liste des documents dans
        - pour chaque document récupère des informations détaillées
        """
        # On évalue le nombre d'appels nécessaires pour obtenir la liste
        nb_appels = math.ceil(self.nombre_de_membres / 100)
        all_documents = []

        for i in range(0, nb_appels):
            offset = i * 100
            status, result = self.get_match_members(
             offset=offset
            )
            # self.mes_logs.debug(result)
            if status == "Error":
                self.est_erreur = True
                self.message_erreur = result
            else:
                self.mes_logs.debug(json.dumps(result,indent=4))
                all_documents.extend(result["match"])
        # On récupère les infos des notices
        for groupe in all_documents :
            ppn = groupe['incoming_record_id']
            infos_groupe = {
                ppn : {
                    "doc" : [],
                    "population": self.population,
                }
            }
            for mmsid in groupe["mms_ids"].split(",") :
                self.mes_logs.info("{} : Récupération des infos pour le mmsid {}".format(self.population,mmsid))
                Notice_Alma = AlmaRecord.AlmaRecord(
                mms_id=mmsid.strip(),
                view="full",
                expand="p_avail",
                accept="xml",
                apikey=self.apikey,
                service=self.service,
            )
                if Notice_Alma.est_erreur:
                    continue
                infos_titres = {
                    "mmsid": mmsid.strip(),
                    "isbn": Notice_Alma.isbn(),
                    "titre": Notice_Alma.titre(),
                    "auteur": Notice_Alma.auteur(),
                    "editeur": Notice_Alma.editeur(),
                    "date_pub": Notice_Alma.date_pub(),
                    "localisations": Notice_Alma.localisations(),
                    "population": self.population,
                    "mmsid_institutions" : Notice_Alma.mmsid_institutions(),
                    "est_elec" : Notice_Alma.est_elec()
                }
                infos_groupe[ppn]["doc"].append(infos_titres)
            self.liste_membres_set.update(infos_groupe)


