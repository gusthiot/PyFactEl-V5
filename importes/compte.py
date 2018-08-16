from importes import Fichier
from outils import Outils


class Compte(Fichier):
    """
    Classe pour l'importation des données de Comptes Cmi
    """

    cles = ['annee', 'mois', 'id_compte', 'numero', 'intitule', 'type_tarif', 'code_client', 'type_subside']
    nom_fichier = "compte.csv"
    libelle = "Comptes"
    
    def contient_id(self, id_compte):
        """
        vérifie si un compte contient l'id donné
        :param id_compte: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        if self.verifie_coherence == 1:
            if id_compte in self.donnees.keys():
                return 1
        else:
            for compte in self.donnees:
                if compte['id_compte'] == id_compte:
                    return 1
        return 0

    def est_coherent(self, clients, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes (code client dans clients,
        id compte unique), et efface les colonnes mois et année
        :param clients: clients importés
        :param generaux: paramètres généraux
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
            if donnee['code_client'] == "":
                msg += "le code client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['code_client'] not in clients.donnees:
                msg += "le code client " + donnee['code_client'] + " de la ligne " + str(ligne) + \
                       " n'est pas référencé\n"

            if donnee['id_compte'] == "":
                msg += "le compte id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_compte'] not in ids:
                ids.append(donnee['id_compte'])
            else:
                msg += "l'id compte '" + donnee['id_compte'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"
            if donnee['type_tarif'] != generaux.code_t:
                msg += "le type de tarif de la ligne " + str(ligne) + " n'est pas correct\n"

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['id_compte']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
