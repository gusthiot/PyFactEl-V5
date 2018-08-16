from importes import Fichier
from outils import Outils


class Emolument(Fichier):
    """
    Classe pour l'importation des données de Emoluments
    """

    nom_fichier = "emolument.csv"
    cles = ['nature', 'emolument']
    libelle = "Emoluments"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes,
        et efface les colonnes mois et année
        :param generaux: paramètres généraux
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
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
                else:
                    msg += "la nature '" + donnee['nature'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            donnee['emolument'], info = Outils.est_un_nombre(donnee['emolument'], "l'émolument", ligne)
            msg += info

            donnees_dict[donnee['nature']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
