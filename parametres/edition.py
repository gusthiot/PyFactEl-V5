from outils import Outils
from erreurs import ErreurConsistance


class Edition(object):
    """
    Classe pour l'importation des paramètres d'édition
    """

    nom_fichier = "paramedit.csv"
    libelle = "Paramètres d'Edition"

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        donnees_csv = []
        try:
            for ligne in dossier_source.reader(self.nom_fichier):
                donnees_csv.append(ligne)
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+Edition.nom_fichier)

        num = 4
        if len(donnees_csv) != num:
            Outils.fatal(ErreurConsistance(),
                         Edition.libelle + ": nombre de lignes incorrect : " +
                         str(len(donnees_csv)) + ", attendu : " + str(num))
        try:
            self.annee = int(donnees_csv[0][1])
            self.mois = int(donnees_csv[1][1])
        except ValueError as e:
            Outils.fatal(e, Edition.libelle +
                         "\nle mois et l'année doivent être des nombres entiers")
        try:
            self.version = int(donnees_csv[2][1])
        except ValueError as e:
            Outils.fatal(e, Edition.libelle +
                         "\nla version doit être un nombre entier")
        if self.version < 0:
            Outils.fatal(ErreurConsistance(),
                         Edition.libelle + ": la version doit être positive ")
        self.client_unique = ""
        self.filigrane = donnees_csv[3][1]

        jours = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if self.mois != 2:
            jour = jours[self.mois-1]
        else:
            if self.annee % 4 == 0:
                if self.annee % 100 == 0:
                    if self.annee % 400 == 0:
                        jour = 29
                    else:
                        jour = 28
                else:
                    jour = 29
            else:
                jour = 28
        self.dernier_jour = jour

        mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                   "novembre", "décembre"]
        self.mois_txt = mois_fr[self.mois-1]
