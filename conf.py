#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Liste des RCR de l'ILN 15 avec pour chacun d'eux l'identifiant de l abibliothèque correspondante Alma
mes_bibs = {
    "333182205": {
        "id_alma": "1102700000",
        "nom": "Bib. Droit privé",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "333182210": {
        "id_alma": "1102800000",
        "nom": "Bib. droit public",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "330632213": {
        "id_alma": "1103600000",
        "nom": "Bib. du PJJ (CERCCLE-ISCJ)",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "335222111": {
        "id_alma": "2000200000",
        "nom": "Bib. Ecole Nationale Supérieure de Cognitique",
        "institution": "INP",
        "notices_a_controler": []
    },
    "335229907": {
        "id_alma": "4000200000",
        "nom": "Bib. Electronique (IEP)",
        "institution": "IEP",
        "notices_a_controler": []
    },
    "335229901": {
        "id_alma": "1000300000",
        "nom": "Bib. Electronique (UB)",
        "institution": "UB",
        "périmètre" : "Périmètres multiples",
        "notices_a_controler": []
    },
    "335229906": {
        "id_alma": "3000100000",
        "nom": "Bib. Electronique (UBM)",
        "institution": "UBM",
        "notices_a_controler": []
    },
    "333182208": {
        "id_alma": "1102600000",
        "nom": "Bib. Histoire du droit",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "335222103": {
        "id_alma": "3300800000",
        "nom": "BU Lettres et Sciences Humaines",
        "institution": "UBM",
        "notices_a_controler": []
    },
    "335222209": {
        "id_alma": "1201000000",
        "nom": "BMI",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "335222102": {
        "id_alma": "1103300000",
        "nom": "BU Droit sc. politique économie",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "330632101": {
        "id_alma": "1302100000",
        "nom": "BU Sc. du vivant et de la santé",
        "institution": "UB",
        "périmètre": "Périmètre SVS",
        "notices_a_controler": []
    },
    "335222101": {
        "id_alma": "1201300000",
        "nom": "BU Sc. et techniques",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "330632102": {
        "id_alma": "1402300000",
        "nom": "BU Sciences de l'homme",
        "institution": "UB",
        "périmètre": "Périmètre SH",
        "notices_a_controler": []
    },
    "335222105": {
        "id_alma": "1402400000",
        "nom": "BU STAPS",
        "institution": "UB",
        "périmètre": "Périmètre SH",
        "notices_a_controler": []
    },
    "330632209": {
        "id_alma": "1103400000",
        "nom": "Centres de recherche en droit",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "333182201": {
        "id_alma": "1103500000",
        "nom": "Centres de recherche en économie",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "333182101": {
        "id_alma": "1103200000",
        "nom": "CRDEI",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "333182213": {
        "id_alma": "1201100000",
        "nom": "CRPP",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "470012101": {
        "id_alma": "1103000000",
        "nom": "Bib Droit-langues Agen",
        "institution": "UB",
        "périmètre": "Périmètres multiples",
        "notices_a_controler": []
    },
    "335222221": {
        "id_alma": "2000300000",
        "nom": "ENSEGID",
        "institution": "INP",
        "notices_a_controler": []
    },
    "335222306": {
        "id_alma": "2000100000",
        "nom": "ENSEIRB-MATHMECA",
        "institution": "INP",
        "notices_a_controler": []
    },
    "335222201": {
        "id_alma": "1201800000",
        "nom": "EPOC Talence",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "330632212": {
        "id_alma": "1500300000",
        "nom": "INSPE Bordeaux Caudéran",
        "institution": "UB",
        "périmètre": "Périmètre SH",
        "notices_a_controler": []
    },
    "332812201": {
        "id_alma": "1500400000",
        "nom": "INSPE Mérignac",
        "institution": "UB",
        "périmètre": "Périmètre SH",
        "notices_a_controler": []
    },
    "401922201": {
        "id_alma": "1500600000",
        "nom": "INSPE Mont-de-Marsan",
        "institution": "UB",
        "périmètre": "Périmètre SH",
        "notices_a_controler": []
    },
    "644452201": {
        "id_alma": "1500500000",
        "nom": "INSPE Pau",
        "institution": "UB",
        "périmètre": "Périmètre SH",
        "notices_a_controler": []
    },
    "243222203": {
        "id_alma": "1500700000",
        "nom": "Campus Périgord",
        "institution": "UB",
        "périmètre": "Périmètres multiples",
        "notices_a_controler": []
    },
    "333182204": {
        "id_alma": "1201200000",
        "nom": "ICMCB",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "330632201": {
        "id_alma": "1601900000",
        "nom": "Infothèque PUSG",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "333182211": {
        "id_alma": "1102900000",
        "nom": "Institut du travail",
        "institution": "UB",
        "périmètre": "Périmètre DSPEG",
        "notices_a_controler": []
    },
    "400882201": {
        "id_alma": "1302000000",
        "nom": "Institut thermalisme Dax",
        "institution": "UB",
        "périmètre": "Périmètre SVS",
        "notices_a_controler": []
    },
    "330632207": {
        "id_alma": "1500900000",
        "nom": "ISPED",
        "institution": "UB",
        "périmètre": "Périmètre SVS",
        "notices_a_controler": []
    },
    "335502201": {
        "id_alma": "1201500000",
        "nom": "ISVV",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "331922101": {
        "id_alma": "1200900000",
        "nom": "IUT Bordeaux-Gradignan",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "335222216": {
        "id_alma": "3400900000",
        "nom": "IUT/IJBA",
        "institution": "UBM",
        "notices_a_controler": []
    },
    "331672201": {
        "id_alma": "1201700000",
        "nom": "LAB",
        "institution": "UB",
        "périmètre": "Périmètre ST",
        "notices_a_controler": []
    },
    "331922302": {
        "id_alma": "1000200000",
        "nom": "Médiaquitaine",
        "institution": "UB",
        "périmètre": "Périmètre SVS",
        "notices_a_controler": []
    },
    "470012102": {
        "id_alma": "1500800000",
        "nom": "Michel Serres Agen",
        "institution": "UB",
        "périmètre": "Périmètres multiples",
        "notices_a_controler": []
    },
    "335222302": {
        "id_alma": "3200000000",
        "nom": "Regards",
        "institution": "UBM",
        "notices_a_controler": []
    },
    "335222219": {
        "id_alma": "3500100000",
        "nom": "Rigoberta Menchu",
        "institution": "UBM",
        "notices_a_controler": []
    },
    "335222205": {
        "id_alma": "3101000000",
        "nom": "Robert Etienne",
        "institution": "UBM",
        "notices_a_controler": []
    },
    "335222203": {
        "id_alma": "4000100000",
        "nom": "IEP",
        "institution": "IEP",
        "notices_a_controler": []
    }
}
def liste_bib():
    return mes_bibs