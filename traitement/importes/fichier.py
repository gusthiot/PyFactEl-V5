import sys
from outils import Outils


class Fichier(object):
    """
    Classe de base des classes d'importation de données

    Attributs de classe (à définir dans les sous-classes) :
         nom_fichier    Le nom relatif du fichier à charger
         libelle        Un intitulé pour les messages d'erreur
         cles           La liste des colonnes à charger
    """

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        try:
            fichier_reader = dossier_source.reader(self.nom_fichier)
            donnees_csv = []
            for ligne in fichier_reader:
                donnees_ligne = self.extraction_ligne(ligne)
                if donnees_ligne == -1:
                    continue
                donnees_csv.append(donnees_ligne)
            self.donnees = donnees_csv
            self.verifie_date = 0
            self.verifie_coherence = 0
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+self.nom_fichier)

    def extraction_ligne(self, ligne):
        """
        extracte une ligne de données du csv
        :param ligne: ligne lue du fichier
        :return: tableau représentant la ligne, indexé par les clés
        """
        num = len(self.cles)
        if len(ligne) != num:
            info = self.libelle + ": nombre de colonnes incorrect : " + str(len(ligne)) + ", attendu : " + str(num)
            Outils.affiche_message(info)
            sys.exit("Erreur de consistance")
        donnees_ligne = {}
        for xx in range(0, num):
            donnees_ligne[self.cles[xx]] = ligne[xx]
        return donnees_ligne

    def verification_date(self, annee, mois):
        """
        vérifie que le mois et l'année présents sur la ligne sont bien ceux espérés
        :param annee: année selon paramètres d'édition
        :param mois: mois selon paramètres d'édition
        :return: 0 si ok, 1 sinon
        """
        if self.verifie_date == 1:
            print(self.libelle + ": date déjà vérifiée")
            return 0

        msg = ""
        position = 1
        for donnee in self.donnees:
            try:
                if (int(donnee['mois']) != mois) or (int(donnee['annee']) != annee):
                    msg += "date incorrect ligne " + str(position) + "\n"
            except ValueError:
                msg += "année ou mois n'est pas valable" + str(position) + "\n"
            position += 1

        del self.donnees[0]
        self.verifie_date = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
