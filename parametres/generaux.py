from outils import Outils
from erreurs import ErreurConsistance
from collections import namedtuple

_champs_article = ["code_d", "code_sap", "quantite", "unite", "type_prix", "type_rabais", "texte_sap", "intitule_long",
                   "intitule_court", "eligible_U1", "eligible_U2", "eligible_U3"]
Article = namedtuple("Article", _champs_article)


class Generaux(object):
    """
    Classe pour l'importation des paramètres généraux
    """

    nom_fichier = "paramgen.csv"
    libelle = "Paramètres Généraux"
    cles_obligatoires = ['centre', 'code_cfact_centre', 'origine', 'code_int', 'code_ext', 'commerciale', 'canal',
                         'secteur', 'devise', 'financier', 'fonds', 'entete', 'poste_emolument', 'poste_reservation',
                         'lien', 'chemin', 'chemin_propre', 'chemin_filigrane', 'code_t', 'code_n', 'code_ref_fact',
                         'avantage_HC', 'annexe_cout', 'filtrer_article_nul', 'code_d', 'code_sap', 'quantite', 'unite',
                         'type_prix', 'type_rabais', 'texte_sap', 'intitule_long', 'intitule_court', 'eligible_U1',
                         'eligible_U2', 'eligible_U3', 'modes', 'min_fact_rese']
    cles_autorisees = cles_obligatoires + ['code_sap_qas']

    def __init__(self, dossier_source, prod2qual=None):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param prod2qual: Une instance de la classe Prod2Qual si on souhaite éditer
                          des factures et annexes avec les codes d'articles de
                          qualification
        """
        self._donnees = {}
        try:
            for ligne in dossier_source.reader(self.nom_fichier):
                cle = ligne.pop(0)
                if cle not in self.cles_autorisees:
                    Outils.fatal(ErreurConsistance(),
                                 "Clé inconnue dans %s: %s" % (self.nom_fichier, cle))
                if cle != "texte_sap":
                    while ligne[-1] == "":
                        del ligne[-1]
                self._donnees[cle] = ligne
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+Generaux.nom_fichier)
        if prod2qual and 'code_sap_qas' in self._donnees:
            self._donnees['code_sap'] = self._donnees['code_sap_qas']

        erreurs = ""
        for cle in self.cles_obligatoires:
            if cle not in self._donnees:
                erreurs += "\nClé manquante dans %s: %s" % (self.nom_fichier, cle)

        try:
            for quantite in self._donnees['quantite'][1:]:
                int(quantite)
        except ValueError:
            erreurs += "les quantités doivent être des nombres entiers\n"

        try:
            self._donnees['min_fact_rese'][1] = int(self._donnees['min_fact_rese'][1])
        except ValueError:
            erreurs += "le montant minimum pour des frais de facturation doit être un nombre\n"

        codes_n = []
        for nn in self._donnees['code_n'][1:]:
            if nn not in codes_n:
                codes_n.append(nn)
            else:
                erreurs += "le code N '" + nn + "' n'est pas unique\n"
        codes_d = []
        for dd in self._donnees['code_d'][1:]:
            if dd not in codes_d:
                codes_d.append(dd)
            else:
                erreurs += "le code D '" + dd + "' n'est pas unique\n"

        if len(self._donnees['code_n']) != len(self._donnees['code_ref_fact']):
            erreurs += "le nombre de colonees doit être le même pour le code N et pour le code référence du client\n"

        if (len(self._donnees['code_d']) != len(self._donnees['code_sap'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['quantite'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['unite'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['type_prix'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['intitule_long'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['intitule_court'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['eligible_U1'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['eligible_U2'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['eligible_U3'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['type_rabais'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['texte_sap'])):
            erreurs += "le nombre de colonnes doit être le même pour le code D, le code SAP, la quantité, l'unité, " \
                       "le type de prix, le type de rabais, le texte SAP, l'intitulé long, l'intitulé court, " \
                       "l'éligible U1, l'éligible U2 et l'éligible U3\n"

        if len(self._donnees['centre'][1]) > 70:
            erreurs += "le string du paramètre centre est trop long"

        if erreurs != "":
            Outils.fatal(ErreurConsistance(), self.libelle + "\n" + erreurs)

    def obtenir_code_n(self):
        """
        retourne les codes N
        :return: codes N
        """
        return self._donnees['code_n'][1:]

    def obtenir_modes_envoi(self):
        """
        retourne les modes d'envoi
        :return: modes d'envoi
        """
        return self._donnees['modes'][1:]

    @property
    def articles(self):
        """renvoie la liste des articles de facturation.

        Les deux premiers (émolument / frais de réservation) s'appelle "D1"; le second (coûts procédés machines)
        s'appellent "D2"; les suivants (en nombre variable) s'appellent "D3".

        :return: une liste ordonnée d'objets Article
        """
        if not hasattr(self, "_articles"):
            self._articles = []
            for i in range(1, len(self._donnees['code_d'])):
                kw = dict((k, self._donnees[k][i]) for k in _champs_article)
                self._articles.append(Article(**kw))
        return self._articles

    @property
    def articles_d3(self):
        """
        retourne uniquement les articles D3

        :return: une liste ordonnée d'objets Article
        """
        return self.articles[3:]

    def codes_d3(self):
        return [a.code_d for a in self.articles_d3]

    def code_ref_par_code_n(self, code_ref):
        return self._donnees['code_ref_fact'][
            self._donnees['code_n'].index(code_ref)]

    def avantage_hc_par_code_n(self, avantage_hc):
        return self._donnees['avantage_HC'][
            self._donnees['code_n'].index(avantage_hc)]

    def annexe_cout_par_code_n(self, annexe_cout):
        return self._donnees['annexe_cout'][
            self._donnees['code_n'].index(annexe_cout)]

    def filtrer_article_nul_par_code_n(self, filtrer_article_nul):
        return self._donnees['filtrer_article_nul'][
            self._donnees['code_n'].index(filtrer_article_nul)]


def ajoute_accesseur_pour_valeur_unique(cls, nom, cle_csv=None):
    if cle_csv is None:
        cle_csv = nom

    def accesseur(self):
        return self._donnees[cle_csv][1]
    setattr(cls, nom, property(accesseur))


ajoute_accesseur_pour_valeur_unique(Generaux, "centre_financier", "financier")

for champ_valeur_unique in ('fonds', 'entete', 'chemin', 'lien', 'min_fact_rese', 'poste_emolument', 'devise', 'canal',
                            'secteur', 'origine', 'commerciale', 'poste_reservation', 'code_int', 'code_ext', 'code_t',
                            'centre', 'code_cfact_centre', 'chemin_propre', 'chemin_filigrane'):
    ajoute_accesseur_pour_valeur_unique(Generaux, champ_valeur_unique)
