#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Modules externes
import os
import logging
import json
from datetime import datetime

#Modules maison
 
from Services import logs,mail,fonctions
from Services.Alma import AlmaSetFromImport, AlmaMatchFromImport, AlmaMultimatchFromImport, Alma_api_imports, AlmaReminder, AlmaSet,AlmaNettoieSets
from Services.SUDOC import Sudoc_test_localisation
import bib, autres_parametres


SERVICE = "Alma_Suivi_Import_Notice_SUDOC"

LOGS_LEVEL = 'INFO'
LOGS_DIR = os.getenv('LOGS_PATH')
JOB_ID = 'S10555924020004671' #Identifiant du profil d'import
API_KEY = os.getenv('PROD_NETWORK_BIB_API') 
PREFIXE_SETS_ZONE_RESEAU = "[Ensemble depuis Import]"
PREFIXE_SETS_INSTITUTION = "[Chargements SUDOC]"  
DELAI_CONSERVATION_SETS_INSTITUTION = 15
info_mails = autres_parametres.recupere_parametres()
MAIL_ADMINISTRATEUR = info_mails['mail_admin']
MAIL_DESTINATAIRES = info_mails['mails_destinataires']
MAIL_FROM = info_mails['mail_from']

# Calcul des dates
# Pour débogage
# today = '2024-07-09'
# now = datetime.now()
# ## Conversion en objet datetime
# date_fixe = datetime.strptime(today, '%Y-%m-%d')
# ## Ajout des heurs minutes secondes
# date_du_jour = date_fixe.replace(hour=now.hour, minute=now.minute,second=now.second)
# En production
date_heure_du_jour = datetime.now()
date_du_jour = date_heure_du_jour.replace(hour=0, minute=0, second=1)
date_du_jour_formatee = date_du_jour.strftime('%Y-%m-%d')
date_du_jour_formatee_fr = date_du_jour.strftime('%d/%m/%Y')
# Calcule la date de modification des notices dans le SUDOC par rapport à la date de leur chargement
date_modif_notice_sudoc = fonctions.calcul_date_modif_notice_sudoc(date_du_jour)

mon_message = mail.Mail()

#On initialise le logger
logs.setup_logging(name=SERVICE, level=LOGS_LEVEL,log_dir=LOGS_DIR)
mes_logs = logging.getLogger(SERVICE)
mes_logs.info("DEBUT TRAITEMENT IMPORT DU {}".format(date_du_jour_formatee))

##################################
# Nettoyage des jeux de résulats #
##################################
# Le programme s'appuie sur deux types de jeux de résultats :
# 1. En zone réseau (PREFIXE_SETS_ZONE_RESEAU) les jeux permettent de récupérer les anomalies de type IMPORTED_RECORDS_NO_MATCH','NOT_ADDED_LOCKED','NOT_ADDED_DUPLICATED'
# 2. Dans les institutions (PREFIXE_SETS_INSTITUTION) pour partager aux bibliothèques la liste des notices chargées pour lesquelles la bibliothèque est responsable de la descente

mes_logs.info("Nettoyage des jeux de résultats Zone Réseau")
set_a_supprimer = AlmaNettoieSets.AlmaNettoieSet(prefixe=PREFIXE_SETS_ZONE_RESEAU,delais_conservation=DELAI_CONSERVATION_SETS_INSTITUTION,apikey=API_KEY,service=SERVICE)
if set_a_supprimer.est_erreur :
    mes_logs.warnings("Impossible de récupérer la liste des sets pour la zone réseau. Voici le message d'erreur : {}".format(set_a_supprimer.message_erreur))
else :
    set_a_supprimer.supprime_sets()

# Nettoyage des jeux des institutions
for institution in ['UB','INP','UBM','IEP'] :
    mes_logs.info("Nettoyage des jeux de résultats Zone {}".format(institution))
    # On récupère la clef d'API
    clef_api_institution = os.getenv('PROD_{}_BIB_API'.format(institution))
    set_a_supprimer = AlmaNettoieSets.AlmaNettoieSet(prefixe=PREFIXE_SETS_INSTITUTION,delais_conservation=DELAI_CONSERVATION_SETS_INSTITUTION,apikey=clef_api_institution,service=SERVICE)
    if set_a_supprimer.est_erreur :
        mes_logs.warnings("Impossible de récupérer la liste des sets pour l'institution {}. Voici le message d'erreur : {}".format(institution, set_a_supprimer.message_erreur))
    else :
        set_a_supprimer.supprime_sets()


#########################################
# Récupération du rapport de traitement #
#########################################
mes_logs.info("Récupération du rapport de traitement")
# Récupération de la liste des instance du job d'import JOB_ID exécutée ce jour
job_import = Alma_api_imports.AlmaJob_Instance_Id(JOB_ID,date_du_jour_formatee,date_du_jour_formatee,apikey=API_KEY,service=SERVICE)
# mes_logs.debug(job_import)
if job_import.error_status :
    mes_logs.error("Impossible de récupérer la listes des traitements d'import Unimarc du jour : {}".format(job_import.error_message))
    mes_logs.info("FIN DU TRAITEMENT")
    exit()
if job_import.get_nb_de_jobs()== 0 :
    mes_logs.warning("Il n'y a pas eu de chargements de notices SUDOC Unimarc ce jour.\r\nLe traitement a rrété son exécution.")
    mes_logs.info("FIN DU TRAITEMENT : Pas de traitement d'import ce jour")
    exit()
# Récupération de l'ID du job exécuté ce jour
job_instance_id = job_import.job_instance_id 
mes_logs.debug("Identifiant du job d'importation : {}".format(job_instance_id))
# Récupération des informations du rapport de traitement
job_infos =job_import.get_job_infos()

if job_infos['est_erreur'] :
    mes_logs.error("Impossible de récupérer le rapport du traitement d'import des notices ABES. Fin du traitement\n. {}".format(job_infos['msg_erreur']))
    mes_logs.info("FIN DU TRAITEMENT : impossible de récupérer le rapport du traitement d'import des notices ABES")
    exit()
mes_logs.debug(json.dumps(job_infos,indent=4))

##############################################
#  Récupération de la liste notices chargées #
##############################################
mes_logs.info("Récupération de la liste notices chargées")
liste_notices_chargees = {}
for population in ['SINGLE_MATCHES','MULTI_MATCHES','IMPORTED_RECORDS_NO_MATCH','NOT_ADDED_LOCKED','NOT_ADDED_DUPLICATED']:
    if job_infos[population] == 0 :
        mes_logs.info("Pas de cas pour {}".format(population))
        continue 
    mes_logs.info("Récupération de la liste notices chargées pour {}".format(population))   
    # Pour les recouvrement simple et les multimatches on utilise un webservice dédié
    if population == 'SINGLE_MATCHES' :
        # Via le webservice Match
        mon_set = AlmaMatchFromImport.AlmaMatchFromImport(job_id=JOB_ID,instance=job_instance_id,population=population,apikey=API_KEY,service=SERVICE,nombre_de_membres=job_infos[population])
    elif population == 'MULTI_MATCHES' :
        # Via le webservice Match
        mon_set = AlmaMultimatchFromImport.AlmaMultimatchFromImport(job_id=JOB_ID,instance=job_instance_id,population=population,apikey=API_KEY,service=SERVICE,nombre_de_membres=job_infos[population])
    else :
        # Pour les autres cas on créé un set pour les cas et on récupère les résultats 
        mon_set = AlmaSetFromImport.AlmaSetFromImport(instance=job_instance_id, population=population, nom_du_set= "{} Import du {} : {}".format(PREFIXE_SETS_ZONE_RESEAU,date_du_jour,population),apikey=API_KEY,service=SERVICE)
    if mon_set.est_erreur :
        mes_logs.error("Erreur lors de la récupération de la liste des noticeschargées pour {}.\nFIN DU TRAITEMENT\n{}".format(population,mon_set.message_erreur))
        mes_logs.info("FIN DU TRAITEMENT")
        exit()
    liste_notices_chargees.update(mon_set.liste_membres_set)
mes_logs.debug(json.dumps(liste_notices_chargees,indent=4))

mes_logs.info("Il y a {} notices chargées".format(len(liste_notices_chargees)))


################################################################
#  Récupération des informations de localisation dans le SUDOC #
################################################################

# Appel du web service where (https://www.sudoc.fr/services/where/) pour récupérer les informations de localisations sous chaque notice SUDOC
# Interrogation du service par lot de 100 notices

mes_logs.info(" Récupération des informations de localisation dans le SUDOC")
# Récupération de la liste des PPNS des notices importées
liste_ppn = list(liste_notices_chargees.keys())
mes_logs.info("Il y a {} PPN à traiter".format(len(liste_ppn)))
mes_logs.debug(liste_ppn)

# On splite la liste des ppns en liste de 100 ppn
n = 100
liste_de_listes_ppn = [liste_ppn[i * n:(i + 1) * n] for i in range((len(liste_ppn) + n - 1) // n )] 

# Récupérations des informations de localisations dans le SUDOC
liste_infos_loc_sudoc = []
for liste_ppn in liste_de_listes_ppn :
    # appel du web service Where/iln de l'ABES
    infos_loc_sudoc = Sudoc_test_localisation.Sudoc_Qui_Est_Loc(liste_ppn, service=SERVICE)
    if infos_loc_sudoc.est_erreur :
        mes_logs.error("Erreur lors de l'appel au service WHERE.\nFIN DU TRAITEMENT\n{}".format(infos_loc_sudoc.message_erreur))
        mes_logs.info("FIN DU TRAITEMENT")
        exit()
    # mes_logs.debug(infos_loc_sudoc.get_liste_notice())
    liste_infos_loc_sudoc.extend(infos_loc_sudoc.get_liste_notice())    

mes_logs.debug(liste_infos_loc_sudoc)

###########################################################################
#  Rattachement des notices à une bibliothèque responsable de sa descente #
###########################################################################

mes_logs.info("Rattachement des notices à une bibliothèque responsable de sa descente")

# Récupération de la liste des RCR
liste_rcr = bib.liste_bib()
# mes_logs.debug(liste_rcr)

for doc in liste_infos_loc_sudoc :
    ppn = doc['ppn']
    mes_logs.debug(json.dumps(doc,indent=4))
    date_modif_notice = datetime.strptime(doc['bib0touched'], '%Y-%m-%dT%H:%M:%S.%f000')


    # un de nos rcr a-t-il modifié la notice ? La date de modification correspond-t-elle à la date de la veille ?
    if doc['byrcr'] in liste_rcr and date_modif_notice >= date_modif_notice_sudoc:
        mes_logs.debug("{} -- {} -- {}".format(ppn,liste_rcr[doc['byrcr']]['nom'],date_modif_notice))
        liste_rcr[doc['byrcr']]['notices_a_controler'].append({ 'ppn' : ppn, 'date_modif' : date_modif_notice.strftime('%d/%m/%Y'),'type_modif' : 'modif_notice'})

    # cas ou la bibliothèque s'est délocalisée dans le SUDOC avant le passage de l'analyse
    if "library" not in doc :
        mes_logs.error("Plus de localisations dans le SUDOC sous la notice {}".format(ppn))
        continue

    # Un de nos rcr a-t-il créé ou modifié un exemplaire la veille ?
    # Si qu'une seule loc la loc est présentée sous forme d'un dictionnaire
    if isinstance(doc['library'],dict) :
        type_modif, rcr, date_modif_ex = fonctions.exemplaire_sudoc_modifie_par_membre_reseau(doc['library'],date_modif_notice_sudoc)
        # On s'assure que la notice n'a pas été déjà signalée pour la modification de la notice
        if not any(d['ppn'] == ppn and d['type_modif'] == 'modif_notice' for d in liste_rcr[rcr]['notices_a_controler']) :
            liste_rcr[rcr]['notices_a_controler'].append({ 'ppn' : ppn, 'date_modif' : date_modif_ex.strftime('%d/%m/%Y'),'type_modif' : type_modif})
            mes_logs.debug("{} -- {} -- {}".format(ppn,rcr,date_modif_ex.strftime('%d/%m/%Y')))
    else :
        # Sinon on parcour la liste des localisations
        for loc_sudoc in doc['library'] :
            type_modif, rcr, date_modif_ex = fonctions.exemplaire_sudoc_modifie_par_membre_reseau(loc_sudoc,date_modif_notice_sudoc)
            # On s'assure que la notice n'a pas été déjà signalée pour la modification de la notice
            if not any(d['ppn'] == ppn and d['type_modif'] == 'modif_notice' for d in liste_rcr[rcr]['notices_a_controler']) :
                liste_rcr[rcr]['notices_a_controler'].append({ 'ppn' : ppn, 'date_modif' : date_modif_ex.strftime('%d/%m/%Y'),'type_modif' : type_modif})
                mes_logs.debug("{} -- {} -- {}".format(ppn,rcr,date_modif_ex.strftime('%d/%m/%Y')))
mes_logs.debug(json.dumps(liste_rcr,indent=4))

##########################################
#  Construction du rapport de traitement #
##########################################
# on analyse les notices, on créé les rappels et les sets et on renseigne les compteurs 
liste_pour_redaction_rapport = fonctions.liste_pour_redaction_rapport()
for rcr, rcr_infos in liste_rcr.items() :             

    if len(rcr_infos['notices_a_controler']) == 0 :
        mes_logs.info("Pas de notices pour la bibliothèque {}".format(rcr))
        continue
    institution_rcr = rcr_infos['institution']
    nom_bib = rcr_infos['nom']
    id_bib_alma = rcr_infos['id_alma']
    liste_pour_creation_set = []
    message = fonctions.retourne_objet_message(nom_bib)
    # Parcour de la liste des notices
    for notice in rcr_infos['notices_a_controler'] :
        message['compteurs']['nb_notices_chargees']['valeur'] += 1
        ppn = notice['ppn']
        population,mmsid,loc_alma,liste_mmsid_institutions = fonctions.retourne_variable_notices_dans_Alma(liste_notices_chargees[ppn])
        # On ne conserve que les notices Modifiées la veille par l'établissement pour ajout dans un jeu de résultat on exclu les multi match
        if notice['type_modif'] in ['modif_exemplaire','modif_notice'] and population != "MULTI_MATCHES":
            message['compteurs'][notice['type_modif']]['valeur'] += 1
            if institution_rcr in liste_mmsid_institutions :
                liste_pour_creation_set.append(liste_mmsid_institutions[institution_rcr])        


        # Repérage des anomales (Multimatchs, notices verouillées et notices dupliquées) 
        if population in ['MULTI_MATCHES','NOT_ADDED_LOCKED','NOT_ADDED_DUPLICATED','ELECTRONIQUE'] :
            if population == 'MULTI_MATCHES' :
                msg = "Doublon sur PPN {} pour les notices {}".format(ppn," et ".join(mmsid))
                for mms_id in mmsid :

                    rappel = AlmaReminder.Reminder(mms_id,population,rcr,msg,apikey=API_KEY,service=SERVICE)
                    if rappel.est_erreur :
                        message['est_erreur'] = True
                        message['message_erreur'].append("Impossible de créer de rappel pour la notice {} et le blocage erreur_synchro".format(mms_id))
                        mes_logs.error("Impossible de créer de rappel pour la notice {} et le blocage {}".format(mms_id,population))
            else :
                rappel = AlmaReminder.Reminder(mmsid,population,rcr,ppn,apikey=API_KEY,service=SERVICE)
                if rappel.est_erreur :
                    message['est_erreur'] = True
                    message['message_erreur'].append("Impossible de créer de rappel pour la notice {} et le blocage erreur_synchro".format(mmsid))
                    mes_logs.error("Impossible de créer de rappel pour la notice {} et le blocage {}".format(mmsid,population))
            message['compteurs'][population]['valeur'] += 1
           
                
        # Est ce qu'une localisation existe dans Alma ? (Analyse de synchronisation)
        
        # On ne fait pas d'analyse de synchronisation pour les notices redescendus car modifiées par l'établissement car ce dernier n'est pas nécessairement localisé sous la notice  
        if notice['type_modif'] != 'modif_notice':
            if len(loc_alma) == 0 :
                rappel = AlmaReminder.Reminder(mmsid,'LOC_ABSENTE',rcr,ppn,apikey=API_KEY,service=SERVICE)
                message['compteurs']['nb_erreurs_synchro']['valeur'] += 1
                if rappel.est_erreur :
                    message['est_erreur'] = True
                    message['message_erreur'].append("Impossible de créer de rappel pour la notice {} et le blocage erreur_synchro".format(mmsid))
                    mes_logs.error("Impossible de créer de rappel pour la notice {} et le blocage erreur_synchro".format(mmsid))
            else : 
                if fonctions.localisation_absente(id_bib_alma,loc_alma) :
                    rappel = AlmaReminder.Reminder(mmsid,'LOC_ABSENTE',rcr,ppn,apikey=API_KEY,service=SERVICE)
                    message['compteurs']['nb_erreurs_synchro']['valeur'] += 1
                    if rappel.est_erreur :
                        message['est_erreur'] = True
                        message['message_erreur'].append("Impossible de créer de rappel pour la notice {} et le blocage erreur_synchro".format(mmsid))
                        mes_logs.error("Impossible de créer de rappel pour la notice {} et le blocage erreur_synchro".format(mmsid))
        

 
    # Si la liste des notices à controler est pleine on va créer le jeux de résultat pour signalement dans Alma
    if len(liste_pour_creation_set) > 0 :
        mes_logs.debug(liste_pour_creation_set)
        mes_logs.info("Set des notices chargées pour le rcr {}".format(rcr))
        nom_set = "{} - {} : Notices chargées du {}".format(PREFIXE_SETS_INSTITUTION,nom_bib,date_du_jour_formatee_fr)
        clef_api_institution = os.getenv('PROD_{}_BIB_API'.format(institution_rcr))
        mon_set = AlmaSet.AlmaSet(create=True,nom=nom_set,apikey=clef_api_institution,service=SERVICE)
        if mon_set.est_erreur :
            message['est_erreur'] = True
            message['message_erreur'].append("Impossible de créeer l'ensemble pour la bibliothèque {}".format(nom_bib))
            mes_logs.error("Impossible de créeer l'ensemble pour la bibliothèque {}".format(nom_bib))
        else : 
            mon_set.add_members(liste_pour_creation_set)
            if mon_set.est_erreur :
                message['est_erreur'] = True
                message['message_erreur'].append("Impossible de créeer l'ensemble pour la bibliothèque {}".format(nom_bib))
                mes_logs.error("Impossible de créeer l'ensemble pour la bibliothèque {}".format(nom_bib))
    if institution_rcr == 'UB' :
        périmètre = rcr_infos['périmètre']
        mes_logs.debug(périmètre)
        mes_logs.debug(liste_pour_redaction_rapport[institution_rcr]["périmètres"])
        liste_pour_redaction_rapport[institution_rcr]["périmètres"][périmètre].append(message)
    else :         
        liste_pour_redaction_rapport[institution_rcr]['liste'].append(message)


mes_logs.debug(json.dumps(liste_pour_redaction_rapport,indent=4))
text_messsage = fonctions.rediger_message_mail_tableau(liste_pour_redaction_rapport, date_du_jour_formatee_fr)

mon_message.envoie(mailfrom=MAIL_FROM,mailto=MAIL_DESTINATAIRES,subject="Rapport de chargement des notices du SUDOC du {} [SUCCES]".format(date_du_jour_formatee_fr),text=text_messsage)

mes_logs.info("FIN DU TRAITEMENT")