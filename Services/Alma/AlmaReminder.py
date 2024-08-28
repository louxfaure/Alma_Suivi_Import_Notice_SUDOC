# -*- coding: utf-8 -*-
import os

# external imports
import json
import logging
import xml.etree.ElementTree as ET
from math import *
from . import Alma_api_fonctions
from datetime import date


class Reminder(object):
    """Créé un reminder sous une notice bib" """

    def __init__(
        self,
        mms_id,
        reminder_type,
        reminder_status,
        msg,
        accept="json",
        apikey="",
        service="AlmaPy",
    ):
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.est_erreur = False
        self.mes_logs = logging.getLogger(service)
        self.appel_api = Alma_api_fonctions.Alma_API(
            apikey=self.apikey, service=self.service
        )
        self.mms_id = mms_id
        self.msg = msg
        self.type = reminder_type
        self.status = reminder_status
        self.accept = accept
        


        # On regarde si un rappel existe
        self.reminder_exist = self.check_reminder()
        if not self.reminder_exist :
            self.mes_logs.debug('truc')
            self.create_reminder()


    def check_reminder(self):
        """Retourne True si un reminder du même type existe déjà sur la notice

        Args:
            mms_id ([type]): [description]
            accept (str, optional): [description]. Defaults to 'xml'.

        Returns:
            [type]: [description]
        """
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/reminders?type={}&satus={}".format(self.mms_id,self.type,self.status),
            accept=self.accept,
        )
        # self.response = self.appel_api.extract_content(response)
        if status == "Error":
            self.est_erreur = True
            self.message_erreur = response
        else:
            reminders_list = self.appel_api.extract_content(response)
            if reminders_list['total_record_count'] > 0 :
                self.mes_logs.info("une alerte du même type existe déjà pour la notice {}, le type {} et le rcr {}".format(self.mms_id,self.type,self.status))
                return True
            else :
                return False     

    def create_reminder(self):
            """Attache une alerte à une notice bibliographique

            Args:
                bib_id (string): mmsid
                type (string) : type de l'alerte


            Returns:
                staus: Sucess ou ERROR
                response: Upadtaed Record or Error message
            """
            
            today = date.today()
            reminder = {
                        "link": "string",
                        "entity": {
                            "link": "string",
                            "entity_type": {
                            "value": "BIB_MMS"
                            },
                            "entity_id": self.mms_id
                        },
                        "type": {
                            "value": self.type
                        },
                        "status": {
                            "value": self.status
                        },
                        "text": self.msg,
                        "reminder_date": today.strftime("%Y-%m-%d")
            }
            data = json.dumps(reminder)
            status, response = self.appel_api.request(
                    "POST",
                    "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/reminders?type={}&satus={}".format(self.mms_id,self.type,self.status),
                    data=data, content_type=self.accept, accept=self.accept
                    )
            
            if status == 'Error':
                self.est_erreur = True
                self.message_erreur = response


               
