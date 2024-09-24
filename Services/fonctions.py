#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta


def calcul_date_modif_notice_sudoc(now):
    """Calcule la date de modification des notices dans le SUDOC par rapport à la date de leur chargement.
    Si le chargeur est lancé un lundi alors on remonte le vendredin précédent sinon date du jour précédent

    Args:
        now (date): date du jour

    Returns:
        date: date de la modification de la notice
    """
    # Obtenir la date d'hier
    hier = now - timedelta(days=1)
    # Si now est un lundi (jour de la semaine 0), on prend le vendredi précédent
    if now.weekday() == 0:  # Monday
        return now - timedelta(days=3)
    return hier


def exemplaire_sudoc_modifie_par_membre_reseau(loc_sudoc, date_modif_notice_sudoc):
    """Analyse une localisation renvoyée par le web service ABES Where et détermine si la modification de l'exemplaire a déclenché l'envoie de la notice dans les TR ('modif_exemplaire ou 'toute mise à jour')

    Args:
        loc_sudoc (dict ou liste): le ou les inventaires SUDOC pour un RCR du réseau
        date_modif_notice_sudoc (date): date de la veille du chargement analysé

    Returns:
        type modification (string) : modif_exemplaire ou toute_mise_a_jour détermine si la modification de l'exemplaire a déclenché l'envoie de la notice
        rcr (string) : rcr de la bibliothèque sous laquellle sont rattachés les exemplaires
        date de modification de l'exemplaire (date) :
    """
    rcr_bib = loc_sudoc["rcr"]
    # Si un seul exemplaire alors loc_sudoc est un dict
    if isinstance(loc_sudoc["epn"], dict):
        date_modif_ex = datetime.strptime(
            loc_sudoc["epn"]["content"], "%Y-%m-%dT%H:%M:%S.%f000"
        )
        if date_modif_ex >= date_modif_notice_sudoc:
            return "modif_exemplaire", rcr_bib, date_modif_ex
        else:
            return "toute_mise_a_jour", rcr_bib, date_modif_ex
    else:
        # Si plusieus exemplaires
        for epn in loc_sudoc["epn"]:
            date_modif_ex = datetime.strptime(epn["content"], "%Y-%m-%dT%H:%M:%S.%f000")
            if date_modif_ex >= date_modif_notice_sudoc:
                return "modif_exemplaire", rcr_bib, date_modif_ex
        return "toute_mise_a_jour", rcr_bib, date_modif_ex


def localisation_absente(id_bib_alma, liste_localisation):
    for loc in liste_localisation:
        if loc["code_bib"] == id_bib_alma:
            return False
    return True


def retourne_variable_notices_dans_Alma(dict_notice):
    population = dict_notice["population"]
    if population == "MULTI_MATCHES":
        liste_mmsid, loc_alma, liste_mmsid_institutions = [], [], []
        for doc in dict_notice["doc"]:
            liste_mmsid.append(doc["mmsid"])
            loc_alma.extend(doc["localisations"])
            liste_mmsid_institutions.extend(doc["mmsid_institutions"])
        return population, liste_mmsid, loc_alma, liste_mmsid_institutions
    else:
        return (
            population,
            dict_notice["mmsid"],
            dict_notice["localisations"],
            dict_notice["mmsid_institutions"],
        )


def retourne_objet_message(nom_bib):
    return {
        "est_erreur": False,
        "message_erreur": [],
        "nom_bib": nom_bib,
        "compteurs": {
            "nb_notices_chargees": {
                "valeur": 0,
                "descr": "Nombre de notices chargées (avec toutes màj)",
                "anomalie" : False
            },
            "modif_notice": {"valeur": 0, "descr": "Notices modifiées par le RCR", "anomalie" : False},
            "modif_exemplaire": {
                "valeur": 0,
                "descr": "Exemplaires créés ou modifiés par le RCR",
                "anomalie" : False
            },
            "nb_erreurs_synchro": {
                "valeur": 0,
                "descr": "Notices sans inventaires correspondants dans Alma",
                "anomalie" : True
            },
            "MULTI_MATCHES": {
                "valeur": 0,
                "descr": "Plusieurs notices dans Alma avec le même PPN",
                "anomalie" : True
            },
            "NOT_ADDED_LOCKED": {
                "valeur": 0,
                "descr": "Notices non importées car verouillées dans Alma",
                "anomalie" : True
            },
            "nb_notices_non_chargees_autres": {
                "valeur": 0,
                "descr": "Nombre de notices non chargées",
                "anomalie" : True
            },
            "NOT_ADDED_DUPLICATED": {
                "valeur": 0,
                "descr": "Notices non chargées car dupliquées dans les TR",
                "anomalie" : True
            },
        },
    }


def tab(nb_tab):
    tab = ""
    for nb in range(nb_tab):
        tab = tab + "\t"
    return tab


def th_col(text):
    return (
        '<th style="border: 1px solid rgb(160 160 160); padding: 8px 10px;">'
        + text
        + "</th>\n"
    )


def th_ligne(text):
    return (
        '<th style="border: 1px solid rgb(160 160 160); padding: 8px 10px; background-color: #d6ecd4;">'
        + text
        + "</th>\n"
    )
def td(text,est_anomalie, est_paire):
    ligne = '<td style="border: 1px solid rgb(160 160 160); padding: 8px 10px; text-align: center;'
    if est_paire :
        ligne = ligne + 'background-color: #eee;'
    if est_anomalie : 
        ligne = ligne + 'font-weight: bold; color: red;'
    ligne = ligne + '">' + text + "</td>\n"
    return ligne


def construire_en_tete_tableau():
    debut_tableau = (
        tab(4)
        + '<table style="border-collapse: collapse;border: 2px solid rgb(140 140 140);font-family: sans-serif; font-size: 0.8rem;letter-spacing: 1px;">\n'
    )
    debut_tableau = debut_tableau + tab(5) + "<tr>\n"

    debut_tableau = debut_tableau + tab(6) + th_col("Nom bibliothèque")
    for titre_col in [
        "Nombre de notices charg\u00e9es (avec toutes m\u00e0j)",
        "Notices modifi\u00e9es par le RCR",
        "Exemplaires cr\u00e9\u00e9s ou modifi\u00e9s par le RCR",
        "Notices sans inventaires correspondants dans Alma",
        "Plusieurs notices dans Alma avec le m\u00eame PPN",
        "Notices non import\u00e9es car verouill\u00e9es dans Alma",
        "Nombre de notices non charg\u00e9es",
        "Notices non charg\u00e9es car dupliqu\u00e9es dans les TR",
    ]:
        debut_tableau = debut_tableau + tab(6) + th_col(titre_col)
    debut_tableau = debut_tableau + tab(6) + th_col("Erreurs")
    debut_tableau = debut_tableau + tab(5) + "</tr>\n"
    return debut_tableau

def construire_cellules_tableau(liste_elements):
    message = ""
    for n, bib in enumerate(liste_elements):
        message = message + tab(6) + "<tr>" + th_ligne(bib["nom_bib"])
        est_paire = True if (n % 2) == 0 else False
        for compteur in bib["compteurs"].values():
            est_anomalie = True if (compteur["valeur"] > 0 and compteur['anomalie']) else False
            message = (
                message
                + tab(6)
                + td(str(compteur["valeur"]),est_anomalie=est_anomalie,est_paire=est_paire)
                + "\n"
            )
        message = (
            message
            + tab(6)
            + td(" ; ".join(bib["message_erreur"]),est_anomalie=True,est_paire=est_paire)
            + "\n"
        )
    return message

def rediger_message_mail_tableau(liste_pour_message, date):
    message = "<html>\n"
    message = (
        message
        + "<p>Bonjour,</p>\n<p>Voici le rapport de chargement des notices du SUDOC du "
        + date
        + ". Vous trouverez la liste des notices chargées pour votre RCR sous forme d'un ensemble et les anomalies sous la forme de rappels attachés aux notices.</p>\n"
    )
    for institution, institution_infos in liste_pour_message.items():
        if institution == "UB":
            message = message + tab(1) + "<h2>" + institution_infos["descr"] + "</h2>\n"
            for perimetre, perimetre_infos in institution_infos["périmètres"].items():
                message = message + tab(3) + "<h3>" + perimetre + "</h3>\n"
                message = message + construire_en_tete_tableau()
                message = message + construire_cellules_tableau(perimetre_infos)
                message = message + tab(4) + "</table>\n"
        elif len(institution_infos["liste"]) > 0:
            message = message + tab(1) + "<h2>" + institution_infos["descr"] + "</h2>\n"
            message = message + construire_en_tete_tableau()
            message = message + construire_cellules_tableau(institution_infos["liste"])
            message = message + tab(4) + "</table>\n"
    message = message + "</html>\n"
    return message


def liste_pour_redaction_rapport():
    ma_liste = {
        "UB": {
            "descr": "Université de Bordeaux",
            "périmètres": {
                "Périmètre DSPEG": [],
                "Périmètre SH": [],
                "Périmètre ST": [],
                "Périmètre SVS": [],
                "Périmètres multiples": [],
            },
        },
        "UBM": {"descr": "Université Bordeaux Montaigne", "liste": []},
        "IEP": {"descr": "Sciences Po Bordeaux", "liste": []},
        "INP": {"descr": "INP Bordeaux", "liste": []},
        "BXSA": {"descr": "Bordeaux Sciences Agro", "liste": []},
    }
    return ma_liste
