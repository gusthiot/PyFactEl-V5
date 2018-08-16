from importes import Fichier
from outils import Outils


class Couts(Fichier):
    """
    Classe pour l'importation des données de Catégories de Coûts
    """

    cles = ['id_cat_cout', 'intitule', 'U1', 'U2', 'U3', 'MO']
    nom_fichier = "categcout.csv"
    libelle = "Catégories Coûts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_id(self, id_cat):
        """
        vérifie si une catégorie contient l'id donné
        :param id_cat: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_cat in self.donnees.keys():
                    return 1
        else:
            for cat in self.donnees:
                if cat['id_cat_cout'] == id_cat:
                    return 1
        return 0

    def est_coherent(self):
        """
        vérifie que les données du fichier importé sont cohérentes (si id catégorie est unique),
        et efface les colonnes mois et année
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        ids = []

        del self.donnees[0]
        for donnee in self.donnees:

            if donnee['id_cat_cout'] == "":
                msg += "l'id catégorie de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_cat_cout'] not in ids:
                ids.append(donnee['id_cat_cout'])
            else:
                msg += "l'id catégorie '" + donnee['id_cat_cout'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            donnee['U1'], info = Outils.est_un_nombre(donnee['U1'], "le coût U1 ", ligne)
            msg += info

            donnee['U2'], info = Outils.est_un_nombre(donnee['U2'], "le coût U2 ", ligne)
            msg += info

            donnee['U3'], info = Outils.est_un_nombre(donnee['U3'], "le coût U3 ", ligne)
            msg += info

            donnee['MO'], info = Outils.est_un_nombre(donnee['MO'], "le coût MO ", ligne)
            msg += info

            donnees_dict[donnee['id_cat_cout']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
