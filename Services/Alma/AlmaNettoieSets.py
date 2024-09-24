# -*- coding: utf-8 -*-
import logging
import xml.etree.ElementTree as ET
from math import ceil
from datetime import datetime,timedelta
import urllib.parse
from . import Alma_api_fonctions

class AlmaNettoieSet(object):
    """Créé un set de notice bib et et l'alimente"
    """

    def __init__(self, prefixe="", delais_conservation=0, apikey="", service='AlmaPy') :
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.est_erreur = False
        self.mes_logs = logging.getLogger(service)
        self.prefixe = prefixe
        # On calcule la date jusqu'à laquelle on souhaite supprimer les jeux de résultats en fonction du nombre de jours de conservations
        self.date_limite = datetime.now() - timedelta(days=delais_conservation)
        # On initialise les fonctions de requêtage des API
        self.appel_api = Alma_api_fonctions.Alma_API(
            apikey=self.apikey, service=self.service
        )
        # Identifie la liste des sets à supprimer
        self.liste_set_a_supprimer = self.identifie_set()

        
    def recherche_set(self,offset) :
        """Appel l'API get sets pour rechercher les sets dont le nom commence par self.prefixe. Filtre les résultats en fonction de self.date

        Args:
            offset (int): décalage de la plage des résultats 

        Returns:
            est-erreur(bool): true si l'appel plante
            response(string): si erreur, message d'erreur
            nb_resultats: nb de jeux de résultats retournés par l'API
            liste_set_a_supprimer: liste des id des jeux de résultats

        """
        ''' '''
        # Fonction pour convertir la date du JSON en objet datetime
        def parse_date(date_string):
            try:
                return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        # Appel de l'API
        status,response = self.appel_api.request('GET', 
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets?content_type=BIB_MMS&set_type=ITEMIZED&q=name~{}&limit=100&offset={}&set_origin=UI'.format(urllib.parse.quote_plus(self.prefixe),offset),
                                        accept='json')
        # Gestion des erreurs
        if status == 'Error':
            return True, response, 0 , []
        else:
            set_data = self.appel_api.extract_content(response)
            liste_set_a_supprimer = []
            nb_resultats = set_data['total_record_count']
            if nb_resultats > 0 :
                # Filtre les résultats en fonction de la date de création du jeu de résultats
                liste_set_a_supprimer = [
                        set_item["id"]
                        for set_item in set_data["set"]
                        if parse_date(set_item["created_date"]) < self.date_limite
                ]
            return False, "", nb_resultats,liste_set_a_supprimer
        

    def identifie_set(self) :
        """Récupère la liste des des sets (jeux de résultats) créés depuis une date donnée (self.date_limite) et dont le nom est préfixé par self.prefixe retourne une liste d'identifiant de set

        Returns:
            array: liste des identifiants des jeux de résultats à supprimer
        """
        ''''''
        liste_set_a_supprimer = []
        # Recherche des set à supprimer
        est_erreur, message_erreur, nb_resultats, liste_set_id = self.recherche_set(0)        
        if est_erreur:
            self.est_erreur = True
            self.message_erreur = message_erreur
            return liste_set_a_supprimer
        else:
            liste_set_a_supprimer.extend(liste_set_id)
            # L'API ne remonte pas plus de 100 résulats. S'il y a plus de 100 résultats
            if nb_resultats > 100 :
                # On calcule le nb. d'appels nécessaires 
                nb_appels = ceil(nb_resultats / 100)
                # On relance l'appel autant de fois que nécessaire
                for i in range(1, nb_appels):
                    #  En décalant la plage des résultats 
                    offset = i * 100
                    est_erreur, message_erreur, nb_resultats, liste_set_id = self.recherche_set(offset)
                    if est_erreur:
                        self.est_erreur = True
                        self.message_erreur = message_erreur
                    else:
                        liste_set_a_supprimer.extend(liste_set_id)
        self.mes_logs.info("{} jeux de résultats à supprimer".format(len(liste_set_a_supprimer)))
        return liste_set_a_supprimer



    def supprime_sets(self):
        nb_sets_a_supprimer = len(self.liste_set_a_supprimer)
        nb_sets_supprimes = 0
        for set_id in self.liste_set_a_supprimer :
            self.appel_api.request('DELETE', 
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{}'.format(set_id),
                                        accept='json')
            nb_sets_supprimes += 1
        if nb_sets_a_supprimer == nb_sets_supprimes :
            self.mes_logs.info("{} jeux de résultats supprimés sur {}".format(nb_sets_supprimes,nb_sets_a_supprimer))
        else :
            self.warning("Tous les sets n'ont pas pu être supprimés")
