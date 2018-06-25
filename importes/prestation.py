from importes import Fichier
from outils import Outils


class Prestation(Fichier):
    """
    Classe pour l'importation des données de Prestations du catalogue
    """

    cles = ['annee', 'mois', 'id_prestation', 'no_prestation', 'designation', 'categorie', 'unite_prest', 'prix_unit',
            'categ_stock', 'affiliation', 'prix_rev_unit']
    nom_fichier = "prestation.csv"
    libelle = "Prestations"

    def contient_id(self, id_prestation):
        """
        vérifie si une prestation contient l'id donné
        :param id_prestation: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_prestation in self.donnees.keys():
                    return 1
        else:
            for prestation in self.donnees:
                if prestation['id_prestation'] == id_prestation:
                    return 1
        return 0

    def prestation_de_num(self, num):
        """
        récupère la prestation d'un numéro
        :param num: numéro de prestation
        :return: données de la prestation ou None
        """
        if self.verifie_coherence == 1:
            for cle, prestation in self.donnees.items():
                if prestation['no_prestation'] == num:
                    return prestation
        else:
            for prestation in self.donnees:
                if prestation['no_prestation'] == num:
                    return prestation
        return None

    def est_coherent(self, generaux, coefprests):
        """
        vérifie que les données du fichier importé sont cohérentes (id prestation unique,
        catégorie prestation présente dans les paramètres D3), et efface les colonnes mois et année
        :param generaux: paramètres généraux
        :param coefprests: coefficients prestations importés
        :return: 1 s'il y a une erreur, 0 sinon
        """
        if self.verifie_date == 0:
            info = self.libelle + ". vous devez vérifier la date avant de vérifier la cohérence"
            Outils.affiche_message(info)
            return 1

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        ids = []
        donnees_dict = {}

        for donnee in self.donnees:
            if donnee['id_prestation'] == "":
                msg += "le prestation id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_prestation'] not in ids:
                ids.append(donnee['id_prestation'])
            else:
                msg += "l'id prestation '" + donnee['id_prestation'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            if donnee['no_prestation'] == "":
                msg += "le numéro de prestation de la ligne " + str(ligne) + " ne peut être vide\n"

            if donnee['categorie'] == "":
                msg += "la catégorie  de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['categorie'] not in generaux.codes_d3():
                msg += "la catégorie '" + donnee['categorie'] + "' de la ligne " + str(ligne) +\
                       " n'existe pas dans les paramètres D3\n"
            elif coefprests.contient_categorie(donnee['categorie']) == 0:
                msg += "la catégorie prestation '" + donnee['categorie'] + "' de la ligne " + str(ligne) +\
                       " n'est pas référencée dans les coefficients\n"

            donnee['prix_unit'], info = Outils.est_un_nombre(donnee['prix_unit'], "le prix unitaire", ligne)
            msg += info
            num, info = Outils.est_un_nombre(donnee['no_prestation'], "le numéro prestation", ligne)
            donnee['no_prestation'] = int(num)
            msg += info
            donnee['prix_rev_unit'], info = Outils.est_un_nombre(donnee['prix_rev_unit'], "le prix de revient unitaire",
                                                                 ligne)

            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['id_prestation']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
