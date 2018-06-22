from importes import Fichier
from outils import Outils


class User(Fichier):
    """
    Classe pour l'importation des données de Users
    """

    cles = ['annee', 'mois', 'id_user', 'nom', 'prenom']
    nom_fichier = "user.csv"
    libelle = "Users"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contient_id(self, id_user):
        """
        vérifie si un user contient l'id donné
        :param id_user: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        ligne = 1
        if self.verifie_coherence == 1:
            for cle, user in self.donnees.items():
                if user['id_user'] == id_user:
                    return ligne
                ligne += 1
        else:
            for user in self.donnees:
                if user['id_user'] == id_user:
                    return ligne
                ligne += 1
        return 0

    def est_coherent(self):
        """
        vérifie que les données du fichier importé sont cohérentes (si id user est unique),
        et efface les colonnes mois et année
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
        donnees_dict = {}
        ids = []

        for donnee in self.donnees:

            if donnee['id_user'] == "":
                msg += "l'id user de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_user'] not in ids:
                ids.append(donnee['id_user'])
            else:
                msg += "l'id user '" + donnee['id_user'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['id_user']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
