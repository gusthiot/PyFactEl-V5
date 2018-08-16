from importes import Fichier
from outils import Outils


class CoefPrest(Fichier):
    """
    Classe pour l'importation des données de Coefficients Prestations
    """

    cles = ['nature', 'categorie', 'coefficient']
    nom_fichier = "coeffprestation.csv"
    libelle = "Coefficients Prestations"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_categorie(self, categorie):
        """
        vérifie si la catégorie est présente
        :param categorie: la catégorie à vérifier
        :return: 1 si présente, 0 sinon
        """
        if self.verifie_coherence == 1:
            for cle, coefprest in self.donnees.items():
                if coefprest['categorie'] == categorie:
                    return 1
        else:
            for coefprest in self.donnees:
                if coefprest['categorie'] == categorie:
                    return 1
        return 0

    def est_coherent(self, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes (si couple catégorie - classe de tarif est unique),
        et efface les colonnes mois et année
        :param generaux: paramètres généraux
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        categories = []
        couples = []
        donnees_dict = {}
        natures = []

        del self.donnees[0]
        for donnee in self.donnees:
            if donnee['nature'] == "":
                msg += "la nature client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['nature'] not in generaux.obtenir_code_n():
                msg += "la nature client de la ligne " + str(ligne) + " n'existe pas dans les codes N\n"
            elif donnee['nature'] not in natures:
                if donnee['nature'] not in natures:
                    natures.append(donnee['nature'])

            if donnee['categorie'] == "":
                msg += "la catégorie de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['categorie'] not in generaux.codes_d3():
                msg += "la catégorie '" + donnee['categorie'] + "' de la ligne " + str(ligne) +\
                       " n'existe pas dans les paramètres D3\n"
            elif donnee['categorie'] not in categories:
                categories.append(donnee['categorie'])

            if (donnee['categorie'] != "") and (donnee['nature'] != ""):
                couple = [donnee['categorie'], donnee['nature']]
                if couple not in couples:
                    couples.append(couple)
                else:
                    msg += "Couple categorie '" + donnee['categorie'] + "' et nature '" + \
                           donnee['nature'] + "' de la ligne " + str(ligne) + " pas unique\n"

            donnee['coefficient'], info = Outils.est_un_nombre(donnee['coefficient'], "le coefficient", ligne)
            msg += info

            donnees_dict[donnee['nature'] + donnee['categorie']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        for categorie in generaux.codes_d3():
            if categorie not in categories:
                msg += "La categorie D3 '" + categorie + "' dans les paramètres généraux n'est pas présente dans " \
                                                         "les coefficients de prestations\n"

        for categorie in categories:
            for nature in natures:
                couple = [categorie, nature]
                if couple not in couples:
                    msg += "Couple categorie '" + categorie + "' et nature client '" + \
                           nature + "' n'existe pas\n"

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
