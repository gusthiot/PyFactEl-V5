from importes import Fichier
from outils import Outils


class CategPrix(Fichier):
    """
    Classe pour l'importation des données de Catégories Prix
    """

    nom_fichier = "categprix.csv"
    cles = ['nature', 'id_cat_cout', 'prix_h_mach_p', 'prix_h_mo_o']
    libelle = "Catégories Prix"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, generaux, couts):
        """
        vérifie que les données du fichier importé sont cohérentes,
        et efface les colonnes mois et année
        :param generaux: paramètres généraux
        :param couts: catégories coûts importés
        :return: 1 s'il y a une erreur, 0 sinon
        """

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        natures = []
        couples = []
        ids = []

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

            if donnee['id_cat_cout'] == "":
                msg += "l'id cout " + str(ligne) + " ne peut être vide\n"
            elif couts.contient_id(donnee['id_cat_cout']) == 0:
                msg += "l'id cout de la ligne " + str(ligne) + " n'existe pas dans les catégories coûts\n"
            elif donnee['id_cat_cout'] not in ids:
                ids.append(donnee['id_cat_cout'])

            if (donnee['id_cat_cout'] != "") and (donnee['nature'] != ""):
                couple = [donnee['id_cat_cout'], donnee['nature']]
                if couple not in couples:
                    couples.append(couple)
                else:
                    msg += "Couple id cout '" + donnee['id_cat_cout'] + "' et nature '" + \
                           donnee['nature'] + "' de la ligne " + str(ligne) + " pas unique\n"

            donnee['prix_h_mach_p'], info = Outils.est_un_nombre(donnee['prix_h_mach_p'], "le prix horaire machine ",
                                                                 ligne)
            msg += info

            donnee['prix_h_mo_o'], info = Outils.est_un_nombre(donnee['prix_h_mo_o'], "le prix horaire main d'oeuvre",
                                                               ligne)
            msg += info

            donnees_dict[donnee['nature'] + donnee['id_cat_cout']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        for code_n in generaux.obtenir_code_n():
            if code_n not in natures:
                msg += "La nature '" + code_n + "' dans les paramètres généraux n'est pas présente dans " \
                                                         "les catégories prix\n"

        for id_cout in ids:
            for nature in natures:
                couple = [id_cout, nature]
                if couple not in couples:
                    msg += "Couple id cout '" + id_cout + "' et nature client '" + \
                           nature + "' n'existe pas\n"

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
