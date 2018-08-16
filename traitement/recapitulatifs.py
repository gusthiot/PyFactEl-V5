from outils import Outils


class Recapitulatifs(object):
    """
    Classe pour la création des récapitulatifs
    """

    @staticmethod
    def cae(dossier_destination, edition, lignes):
        """
        création du récapitulatif des accès machines
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param lignes: lignes de données du récapitulatif
        """

        nom = "cae_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = [edition.annee, edition.mois, "Id-Compte", "Numéro de compte", "Intitulé compte",
                     "Code Type Compte", "Code Type Subsides", "Code Client Facture", "Abrev. Labo", "Id-User",
                     "Nom User", "Prénom User", "Id-Machine", "Nom Machine", "Id-Categ-cout", "Intitulé catégorie coût",
                     "Date et Heure login", "Durée machine HP", "Durée machine HC", "Durée opérateur", "Id-Opérateur",
                     "Prénom Nom opérateur", "Remarque opérateur", "Remarque staff"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def cae_lignes(edition, acces, comptes, clients, users, machines, couts):
        """
        génération des lignes de données du récapitulatif des accès machines
        :param edition: paramètres d'édition
        :param acces: accès importés
        :param comptes: comptes importés
        :param clients: clients importés
        :param users: users importés
        :param machines: machines importées
        :param couts: catégories coûts importées
        :return: lignes de données du récapitulatif
        """
        lignes = []
        for donnee in acces.donnees:
            compte = comptes.donnees[donnee['id_compte']]
            client = clients.donnees[compte['code_client']]
            user = users.donnees[donnee['id_user']]
            op = users.donnees[donnee['id_op']]
            machine = machines.donnees[donnee['id_machine']]
            id_cout = machine['id_cout']
            ligne = [edition.annee, edition.mois, donnee['id_compte'], compte['numero'], compte['intitule'],
                     compte['type_tarif'], compte['type_subside'], compte['code_client'], client['abrev_labo'],
                     donnee['id_user'], user['nom'], user['prenom'], donnee['id_machine'], machine['nom'],
                     machine['id_cout'], couts.donnees[id_cout]['intitule'], donnee['date_login'],
                     donnee['duree_machine_hp'], donnee['duree_machine_hc'], donnee['duree_operateur'], donnee['id_op'],
                     op['prenom'] + " " + op['nom'], donnee['remarque_op'], donnee['remarque_staff']]
            lignes.append(ligne)
        return lignes

    @staticmethod
    def lvr(dossier_destination, edition, lignes):
        """
        création du récapitulatif des livraisons
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param lignes: lignes de données du récapitulatif
        """
        nom = "lvr_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = [edition.annee, edition.mois, "Id-Compte", "Numéro de compte", "Intitulé compte",
                     "Code Type Compte", "Code Type Subsides", "Code Client Facture", "Abrev. Labo", "Id-User",
                     "Nom User", "Prénom User", "Id-Prestation", "Numéro de prestation", "Désignation prestation",
                     "Date de livraison", "Quantité livrée", "Unité de livraison", "Rabais [CHF]", "ID-Opérateur",
                     "Opérateur", "ID-Livraison", "Date et Heure de la commande", "Date et Heure de la prise en charge",
                     "Remarque"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def lvr_lignes(edition, livraisons, comptes, clients, users, prestations):
        """
        génération des lignes de données du récapitulatif des livraisons
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param comptes: comptes importés
        :param clients: clients importés
        :param users: users importés
        :param prestations: prestations importées
        :return: lignes de données du récapitulatif
        """
        lignes = []
        for donnee in livraisons.donnees:
            compte = comptes.donnees[donnee['id_compte']]
            client = clients.donnees[compte['code_client']]
            user = users.donnees[donnee['id_user']]
            op = users.donnees[donnee['id_operateur']]
            prestation = prestations.donnees[donnee['id_prestation']]
            ligne = [edition.annee, edition.mois, donnee['id_compte'], compte['numero'], compte['intitule'],
                     compte['type_tarif'], compte['type_subside'], compte['code_client'], client['abrev_labo'],
                     donnee['id_user'], user['nom'], user['prenom'], donnee['id_prestation'],
                     prestation['no_prestation'], prestation['designation'], donnee['date_livraison'],
                     donnee['quantite'], prestation['unite_prest'], donnee['rabais'], donnee['id_operateur'],
                     op['prenom'] + " " + op['nom'], donnee['id_livraison'], donnee['date_commande'],
                     donnee['date_prise'], donnee['remarque']]
            lignes.append(ligne)
        return lignes

    @staticmethod
    def res(dossier_destination, edition, lignes):
        """
        création du récapitulatif des réservations
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param lignes: lignes de données du récapitulatif
        """
        nom = "res_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = [edition.annee, edition.mois, "Id-Compte", "Numéro de compte", "Intitulé compte",
                     "Code Type Compte", "Code Type Subsides", "Code Client Facture", "Abrev. Labo", "Id-User",
                     "Nom User", "Prénom User", "Id-Machine", "Nom Machine", "Date et Heure début de slot",
                     "Durée du slot réservé HP", "Durée du slot réservé HC", "Durée ouvrée",
                     "Date et Heure de réservation", "Date et Heure de suppression"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def res_lignes(edition, reservations, comptes, clients, users, machines):
        """
        génération des lignes de données du récapitulatif des réservations
        :param edition: paramètres d'édition
        :param reservations: réservations importées
        :param comptes: comptes importés
        :param clients: clients importés
        :param users: users importés
        :param machines: machines importées
        :return: lignes de données du récapitulatif
        """
        lignes = []
        for donnee in reservations.donnees:
            compte = comptes.donnees[donnee['id_compte']]
            client = clients.donnees[compte['code_client']]
            user = users.donnees[donnee['id_user']]
            machine = machines.donnees[donnee['id_machine']]
            ligne = [edition.annee, edition.mois, donnee['id_compte'], compte['numero'], compte['intitule'],
                     compte['type_tarif'], compte['type_subside'], compte['code_client'], client['abrev_labo'],
                     donnee['id_user'], user['nom'], user['prenom'], donnee['id_machine'], machine['nom'],
                     donnee['date_debut'], donnee['duree_hp'], donnee['duree_hc'],
                     donnee['duree_ouvree'], donnee['date_reservation'], donnee['date_suppression']]
            lignes.append(ligne)
        return lignes
