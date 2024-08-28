# -*- coding: utf-8 -*-

# external imports
import logging
import xml.etree.ElementTree as ET
from math import *
from . import Alma_api_fonctions


class AlmaRecord(object):
    """A set of function for interact with Alma Apis in area "Records & Inventory" """

    def __init__(
        self,
        mms_id,
        id_type="mms_id",
        view="full",
        expand="None",
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
        status, response = self.appel_api.request(
            "GET",
            "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs?{}={}&view={}&expand={}".format(
                id_type, mms_id, view, expand
            ),
            accept=accept,
        )
        # self.response = self.appel_api.extract_content(response)
        if status == "Error":
            self.est_erreur = True
            self.message_erreur = response
        else:
            self.record = ET.fromstring(self.appel_api.extract_content(response))
            if self.nb_of_records() != 1:
                self.est_erreur = True
                self.message_erreur = "l'API retourne 0 ou plusieurs résultats"


    def nb_of_records(self):
        return int(self.record.find(".").attrib["total_record_count"])

    def titre(self):
        return self.record.find(".//title").text

    def auteur(self):
        return (
            "None"
            if self.record.find(".//author") is None
            else self.record.find(".//author").text
        )

    def isbn(self):
        return (
            "None"
            if self.record.find(".//isbn") is None
            else self.record.find(".//isbn").text
        )

    def editeur(self):
        return (
            "None"
            if self.record.find(".//place_of_publication") is None
            else self.record.find(".//place_of_publication").text
        )

    def date_pub(self):
        return (
            "None"
            if self.record.find(".//date_of_publication") is None
            else self.record.find(".//date_of_publication").text
        )

    def localisations(self):
        liste_loc = []
        for loc in self.record.findall('.//datafield[@tag="AVA"]'):
            loc_infos = {
                "code_institution": loc.find('subfield[@code="a"]').text,
                "mmsid": loc.find('subfield[@code="0"]').text,
                "code_bib": loc.find('subfield[@code="b"]').text,
                "nom_bib": loc.find('subfield[@code="q"]').text,
                "nom_loc": loc.find('subfield[@code="c"]').text,
                "cote": (
                    "None"
                    if loc.find('subfield[@code="d"]') is None
                    else loc.find('subfield[@code="d"]').text
                ),
            }
            liste_loc.append(loc_infos)
        return liste_loc
    
    def mmsid_institutions(self):
        liste_mmsid = {}
        for loc in self.record.findall('.//datafield[@tag="AVA"]'):
            code_institution = loc.find('subfield[@code="a"]').text
            mmsid = loc.find('subfield[@code="0"]').text
            liste_mmsid[code_institution[7:]] = mmsid
        return liste_mmsid


    def ppn(self):
        for network_numbers in self.record.findall(
            './/datafield[@tag="035"]/subfield[@code="a"]'
        ):
            if network_numbers.text.startswith("(PPN)"):
                return network_numbers.text[5:]
