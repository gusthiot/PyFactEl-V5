from importes import Fichier
from outils import Outils
from traitement import Rabais


class Reservation(Fichier):
    """
    Classe pour l'importation des données de Réservations
    """

    cles = ['annee', 'mois', 'id_compte', 'id_user', 'id_machine', 'date_debut', 'duree_hp', 'duree_hc',
            'duree_ouvree', 'date_reservation', 'date_suppression']
    nom_fichier = "res.csv"
    libelle = "Réservation Equipement"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sommes = {}

    def est_coherent(self, comptes, machines, users):
        """
        vérifie que les données du fichier importé sont cohérentes (id compte parmi comptes,
        id machine parmi machines), et efface les colonnes mois et année
        :param comptes: comptes importés
        :param machines: machines importées
        :param users: users importés
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
        donnees_list = []

        for donnee in self.donnees:
            if donnee['id_compte'] == "":
                msg += "le id compte de la ligne " + str(ligne) + " ne peut être vide\n"
            elif comptes.contient_id(donnee['id_compte']) == 0:
                msg += "le id compte '" + donnee['id_compte'] + "' de la ligne " + str(ligne) + " n'est pas référencé\n"

            if donnee['id_machine'] == "":
                msg += "le machine id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif machines.contient_id(donnee['id_machine']) == 0:
                msg += "le machine id '" + donnee['id_machine'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            if donnee['id_user'] == "":
                msg += "le user id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif users.contient_id(donnee['id_user']) == 0:
                msg += "le user id '" + donnee['id_user'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnee['duree_hp'], info = Outils.est_un_nombre(donnee['duree_hp'], "la durée réservée HP", ligne)
            msg += info
            donnee['duree_hc'], info = Outils.est_un_nombre(donnee['duree_hc'], "la durée réservée HC", ligne)
            msg += info
            donnee['duree_ouvree'], info = Outils.est_un_nombre(donnee['duree_ouvree'], "la durée ouvrée", ligne)
            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_list.append(donnee)

            ligne += 1

        self.donnees = donnees_list
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0

    def calcul_montants(self, machines, categprix, clients, comptes, verification):
        """
        calcule les sous-totaux nécessaires
        :param machines: machines importées et vérifiées
        :param categprix: catégories prix importés et vérifiés
        :param clients: clients importés et vérifiés
        :param comptes: comptes importés
        :param verification: pour vérifier si les dates et les cohérences sont correctes
        """
        if verification.a_verifier != 0:
            info = self.libelle + ". vous devez faire les vérifications avant de calculer les montants"
            Outils.affiche_message(info)
            return

        donnees_list = []
        pos = 0
        for donnee in self.donnees:
            id_compte = donnee['id_compte']
            compte = comptes.donnees[id_compte]
            code_client = compte['code_client']
            id_machine = donnee['id_machine']
            id_user = donnee['id_user']
            machine = machines.donnees[id_machine]
            client = clients.donnees[code_client]
            prix = categprix.donnees[client['nature'] + machine['id_cout']]
            duree_fact_hp, duree_fact_hc = Rabais.rabais_reservation(machine['delai_sans_frais'],
                                                                     donnee['duree_ouvree'],
                                                                     donnee['duree_hp'],
                                                                     donnee['duree_hc'])

            donnee['duree_fact_hp'] = duree_fact_hp
            donnee['duree_fact_hc'] = duree_fact_hc

            tx_hp = machine['tx_occ_eff_hp']
            tx_hc = machine['tx_occ_eff_hc']
            pu_hp = round(prix['prix_h_mach_p'] * machine['tx_penalite_hp'] / 100, 2)
            pu_hc = round(prix['prix_h_mach_p'] * machine['tx_penalite_hc'] / 100 * (1 - machine['tx_rabais_hc'] / 100), 2)
            ok_hp = False
            ok_hc = False
            if duree_fact_hp > 0 and pu_hp > 0 and tx_hp > 0:
                ok_hp = True
            if duree_fact_hc > 0 and pu_hc > 0 and tx_hc > 0:
                ok_hc = True

            if ok_hp or ok_hc:
                if code_client not in self.sommes:
                    self.sommes[code_client] = {}
                scl = self.sommes[code_client]

                if id_machine not in scl:
                    scl[id_machine] = {'res_hp': 0, 'res_hc': 0, 'pu_hp': pu_hp, 'pu_hc': pu_hc, 'users': {}}

                scm = scl[id_machine]

                if ok_hp:
                    scm['res_hp'] += duree_fact_hp
                if ok_hc:
                    scm['res_hc'] += duree_fact_hc

                if id_user not in scm['users']:
                    scm['users'][id_user] = {'res_hp': 0, 'res_hc': 0, 'data': []}

                if ok_hp:
                    scm['users'][id_user]['res_hp'] += duree_fact_hp
                if ok_hc:
                    scm['users'][id_user]['res_hc'] += duree_fact_hc
                scm['users'][id_user]['data'].append(pos)

            donnees_list.append(donnee)
            pos += 1

        self.donnees = donnees_list

    def reservations_pour_compte(self, id_compte, code_client):
        """
        retourne toutes les données réservations pour un compte donné
        :param id_compte: l'id du compte
        :param code_client: le code du client
        :return: toutes les données réservations d'un compte donné
        """
        donnees_list = []
        for donnee in self.donnees:
            if (donnee['id_compte'] == id_compte) and (donnee['code_client'] == code_client):
                donnees_list.append(donnee)
        return donnees_list
