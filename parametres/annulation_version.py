from outils import Outils
from erreurs import ErreurConsistance


class AnnulationVersion(object):
    """
    Classe pour la annuler la modification d'une facture
    """

    nom_fichier = "annulversion.csv"
    libelle = "Paramètres d'Annulation"

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
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+AnnulationVersion.nom_fichier)

        num = 4
        if len(donnees_csv) != num:
            Outils.fatal(ErreurConsistance(),
                         AnnulationVersion.libelle + ": nombre de lignes incorrect : " +
                         str(len(donnees_csv)) + ", attendu : " + str(num))
        try:
            self.annee = int(donnees_csv[0][1])
            self.mois = int(donnees_csv[1][1])
        except ValueError as e:
            Outils.fatal(e, AnnulationVersion.libelle +
                         "\nle mois et l'année doivent être des nombres entiers")

        try:
            self.annule_version = int(donnees_csv[2][1])
        except ValueError as e:
            Outils.fatal(e, AnnulationVersion.libelle +
                         "\nla version doit être un nombre entier")
        if self.annule_version < 0:
            Outils.fatal(ErreurConsistance(),
                         AnnulationVersion.libelle + ": la version doit être positive")

        self.client_unique = donnees_csv[3][1]
        self.recharge_version = self.annule_version - 1
