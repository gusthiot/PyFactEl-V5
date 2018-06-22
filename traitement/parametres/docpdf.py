import sys
from outils import Outils


class DocPdf(object):
    """
    Classe pour l'ajout de documents pdf aux annexes
    """

    nom_fichier = "docpdf.csv"
    cles = ['nom', 'position', 'Annexe-pièces', 'Annexe-interne', 'nature', 'code']
    libelle = "Documents PDF"

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        self._chemin = dossier_source.chemin
        try:
            fichier_reader = dossier_source.reader(self.nom_fichier)
            donnees_csv = []
            for ligne in fichier_reader:
                donnees_ligne = self.extraction_ligne(ligne)
                if donnees_ligne == -1:
                    continue
                donnees_csv.append(donnees_ligne)
            self.donnees = donnees_csv
            self.verifie_coherence = 0
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+self.nom_fichier)
        del self.donnees[0]

    def extraction_ligne(self, ligne):
        """
        extracte une ligne de données du csv
        :param ligne: ligne lue du fichier
        :return: tableau représentant la ligne, indexé par les clés
        """
        num = len(self.cles)
        if len(ligne) != num:
            info = self.libelle + ": nombre de colonnes incorrect : " + str(len(ligne)) + ", attendu : " + str(
                num)
            Outils.affiche_message(info)
            sys.exit("Erreur de consistance")
        donnees_ligne = {}
        for xx in range(0, num):
            donnees_ligne[self.cles[xx]] = ligne[xx]
        return donnees_ligne

    def pdfs_pour_client(self, client, type_annexe):
        """
        retourne les pdfs à ajouter en fin d'annexe pour le client
        :return: pdfs selon position
        """
        if self.verifie_coherence == 0:
            info = self.libelle + ". vous devez vérifier la cohérence avant de pouvoir obtenir les codes"
            Outils.affiche_message(info)
            return []
        pdfs = {}
        for donnee in self.donnees:
            if donnee['code'] != "" and donnee['code'] != client['code']:
                continue
            if donnee['nature'] != "" and donnee['nature'] != client['nature']:
                continue
            if donnee[type_annexe] == 'NON':
                continue
            if not donnee['position'] in pdfs:
                pdfs[donnee['position']] = [{'chemin': donnee['chemin'], 'nom': donnee['nom']}]
            else:
                pdfs[donnee['position']].append({'chemin': donnee['chemin'], 'nom': donnee['nom']})
        return pdfs

    def est_coherent(self, generaux, clients):
        """
        vérifie que les données du fichier importé sont cohérentes
        :param generaux: paramètres généraux
        :param clients: clients importés
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_list = []

        for donnee in self.donnees:
            if donnee['position'] == "":
                msg += "la position de la ligne " + str(ligne) + " ne peut être vide\n"

            donnee['position'], info = Outils.est_un_nombre(donnee['position'], "la position", ligne)
            msg += info
            donnee['position'] = int(donnee['position'])
            if donnee['position'] < 1:
                msg += " la position de la ligne " + str(ligne) + " doit être un entier > 0\n"

            if donnee['Annexe-pièces'] == "":
                msg += "le annexe P.J. de la ligne " + str(ligne) + " ne peut être vide\n"
            if not (donnee['Annexe-pièces'] == "OUI" or donnee['Annexe-pièces'] == "NON"):
                msg += "le annexe P.J. de la ligne " + str(ligne) + " doit être 'OUI' ou 'NON'\n"

            if donnee['Annexe-interne'] == "":
                msg += "le annexe Int de la ligne " + str(ligne) + " ne peut être vide\n"
            if not (donnee['Annexe-interne'] == "OUI" or donnee['Annexe-interne'] == "NON"):
                msg += "le annexe Int de la ligne " + str(ligne) + " doit être 'OUI' ou 'NON'\n"

            if donnee['nature'] != "" and donnee['nature'] not in generaux.obtenir_code_n():
                msg += "la nature '" + donnee['nature'] + "' de la ligne " + str(ligne) +\
                    " n'existe pas dans les types N\n"

            if donnee['code'] != "" and donnee['code'] not in clients.obtenir_codes():
                msg += "le code client '" + donnee['code'] + "' de la ligne " + str(ligne) + " n'est pas référencé\n"

            donnee['chemin'] = Outils.chemin([self._chemin, donnee['nom']+".pdf"])
            if not Outils.existe(donnee['chemin']):
                msg += "le fichier PDF '" + donnee['nom'] + "' de la ligne " + str(ligne) + " n'existe pas\n"

            donnees_list.append(donnee)

            ligne += 1

        self.donnees = donnees_list
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
