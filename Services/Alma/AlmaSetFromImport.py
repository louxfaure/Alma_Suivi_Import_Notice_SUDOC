# -*- coding: utf-8 -*-
import time
import math

import json
import logging
from math import *
from . import Alma_api_fonctions, AlmaRecord
from concurrent.futures import ThreadPoolExecutor, as_completed



class AlmaSetFromImport(object):
    """Créé un set de notice bib et et l'alimente" """

    def __init__(
        self, instance="", population="", nom_du_set="", apikey="", service="AlmaPy"
    ):
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.est_erreur = False
        self.mes_logs = logging.getLogger(service)
        self.instance_id = instance
        self.population = population
        self.nom_du_set = nom_du_set
        self.nombre_de_membres = ""
        self.liste_membres_set = {}
        self.accept = "json"
        self.est_erreur = False
        self.message_erreur = ""
        self.create_set()
        if not self.est_erreur:
            self.liste_des_membres()

    def create_set(self):
        data = {
            "link": "",
            "name": self.nom_du_set,
            "description": "Créé par API par le programme {}".format(self.service),
            "type": {"value": "ITEMIZED"},
            "content": {"value": "BIB_MMS"},
            "private": {"value": "true"},
            "status": {"value": "ACTIVE"},
            "note": "",
            "query": {"value": ""},
            "origin": {"value": "UI"},
        }
        self.appel_api = Alma_api_fonctions.Alma_API(
            apikey=self.apikey, service=self.service
        )
        status, response = self.appel_api.request(
            "POST",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets?population={}&job_instance_id={}".format(
                self.population, self.instance_id
            ),
            accept=self.accept,
            content_type=self.accept,
            data=json.dumps(data),
        )
        if status == "Error":
            self.est_erreur = True
            self.message_erreur = response
        else:
            self.set_data = self.appel_api.extract_content(response)
            self.set_id = self.set_data["id"]
            # self.mes_logs.debug(self.set_data)

    def get_set(self):
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{}".format(
                self.set_id
            ),
            accept=self.accept,
        )
        if status == "Error":
            self.est_erreur = True
            self.message_erreur = response
        else:
            set_data = self.appel_api.extract_content(response)
            return set_data

    def get_nombre_de_membres(self):
        set_info = self.get_set()
        return set_info["number_of_members"]["value"]

    def get_set_members(self, set_id, limit, offset):
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{}/members?limit={}&offset={}".format(
                set_id, limit, offset
            ),
            accept=self.accept,
        )
        if status == "Error":
            return True, response
        else:
            return False, self.appel_api.extract_content(response)

    def get_job_status(self):
        job_is_completed_status = {
            "COMPLETED_FAILED": True,
            "COMPLETED_NO_BULKS": True,
            "COMPLETED_SUCCESS": True,
            "COMPLETED_WARNING": True,
            "FAILED": True,
            "FINALIZING": False,
            "INITIALIZING": False,
            "MANUAL_HANDLING_REQUIRED": True,
            "PENDING": False,
            "QUEUED": False,
            "RUNNING": False,
            "SKIPPED": True,
            "SYSTEM_ABORTED": True,
            "USER_ABORTED": True,
        }
        status, response = self.appel_api.request(
            "GET", self.set_data["additional_info"]["link"], accept="json"
        )
        if status == "Error":
            return False, "FAILED", response
        else:
            result = self.appel_api.extract_content(response)
            return (
                job_is_completed_status[result["status"]["value"]],
                result["status"]["value"],
                result["status"]["desc"],
            )

    def job_is_comleted(self):
        """Regarde si le job de création du set est terminé

        Returns:
            _type_: _description_
        """
        while True:
            is_completed, code, response = self.get_job_status()
            if is_completed:
                self.mes_logs.info(
                    "Le traitement {} est terminé".format(
                        self.set_data["additional_info"]["value"]
                    )
                )
                return code, response
            self.mes_logs.info("{} : on rappelle le taitement".format(response))
            time.sleep(30)

    def liste_des_membres(self):
        """Récupère la liste des documents dans un set
        - s'assure que le job d'alimentation du SET est bien terminé
        - récupère la liste des membres
        - pour chaque document récupère des informations détaillées
        """
        # On temporise on vient de lancer la création du SET il ne doit pas être encore créé
        time.sleep(15)
        # On regarde si le job est terminé
        statut_du_job, reponse_du_job = self.job_is_comleted()
        if statut_du_job in ["FAILED", "SKIPPED", "SYSTEM_ABORTED", "USER_ABORTED"]:
            self.est_erreur = True
            self.message_erreur = reponse_du_job
        else:
            # On évalue le nombre d'appels nécessaires pour obtenir la liste
            nb_appels = math.ceil(self.get_nombre_de_membres() / 100)
            all_documents = []

            for i in range(0, nb_appels):
                offset = i * 100
                status, result = self.get_set_members(
                    set_id=self.set_id, limit=100, offset=offset
                )
                self.mes_logs.debug(result)
                if status == "Error":
                    self.est_erreur = True
                    self.message_erreur = result
                else:
                    all_documents.extend(result["member"])

            def fetch_details(doc):
                self.mes_logs.info("{} : Récupération des infos pour le mmsid {}".format(self.population,doc["id"]))
                Notice_Alma = AlmaRecord.AlmaRecord(
                    mms_id=doc["id"],
                    view="full",
                    expand="p_avail",
                    accept="xml",
                    apikey=self.apikey,
                    service=self.service,
                )
                if Notice_Alma.est_erreur:
                    return None
                infos_titre = {
                    Notice_Alma.ppn(): {
                        "mmsid": doc["id"],
                        "isbn": Notice_Alma.isbn(),
                        "titre": Notice_Alma.titre(),
                        "auteur": Notice_Alma.auteur(),
                        "editeur": Notice_Alma.editeur(),
                        "date_pub": Notice_Alma.date_pub(),
                        "localisations": Notice_Alma.localisations(),
                        "population": "ELECTRONIQUE" if Notice_Alma.est_elec() else self.population,
                        "mmsid_institutions" : Notice_Alma.mmsid_institutions()
                    }
                }
                return infos_titre

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(fetch_details, doc): doc for doc in all_documents}

                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        self.liste_membres_set.update(result)
