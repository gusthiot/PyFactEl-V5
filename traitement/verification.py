import sys
from outils import Outils


class Verification(object):
    """
    Classe servant à vérifier les dates et la cohérence de toutes les données importées
    """

    def __init__(self):
        """
        initialisation à 2 séries de vérification (date et cohérence)
        """
        self.a_verifier = 2

    def verification_date(self, edition, acces, clients, comptes, users, livraisons, machines, prestations,
                          reservations):
        """
        vérifie les dates de toutes les données importées
        :param edition: paramètres d'édition
        :param acces: accès importés
        :param clients: clients importés
        :param comptes: comptes importés
        :param users: users importés
        :param livraisons: livraisons importées
        :param machines: machines importées
        :param prestations: prestations importées
        :param reservations: réservations importées
        :return: 0 si ok, sinon le nombre d'échecs à la vérification
        """
        verif = 0
        verif += acces.verification_date(edition.annee, edition.mois)
        verif += clients.verification_date(edition.annee, edition.mois)
        verif += comptes.verification_date(edition.annee, edition.mois)
        verif += livraisons.verification_date(edition.annee, edition.mois)
        verif += machines.verification_date(edition.annee, edition.mois)
        verif += prestations.verification_date(edition.annee, edition.mois)
        verif += reservations.verification_date(edition.annee, edition.mois)
        verif += users.verification_date(edition.annee, edition.mois)
        self.a_verifier = 1
        return verif

    def verification_coherence(self, generaux, edition, acces, clients, emoluments, coefprests, comptes, users,
                               livraisons, machines, prestations, reservations, couts, categprix, docpdf):
        """
        vérifie la cohérence des données importées
        :param generaux: paramètres généraux
        :param edition: paramètres d'édition
        :param acces: accès importés
        :param clients: clients importés
        :param emoluments: émoluments importés
        :param coefprests: coefficients prestations importés
        :param comptes: comptes importés
        :param users: users importés
        :param livraisons: livraisons importées
        :param machines: machines importées
        :param prestations: prestations importées
        :param reservations: réservations importées
        :param couts: catégories couts importées
        :param categprix: catégories prix importées
        :param docpdf: paramètres d'ajout de document pdf
        :return: 0 si ok, sinon le nombre d'échecs à la vérification
        """
        verif = 0
        verif += acces.est_coherent(comptes, machines, users)
        verif += livraisons.est_coherent(comptes, prestations, users)
        verif += couts.est_coherent()
        verif += users.est_coherent()
        verif += machines.est_coherent(couts)
        verif += prestations.est_coherent(generaux, coefprests)
        verif += emoluments.est_coherent(generaux)
        verif += categprix.est_coherent(generaux, couts)
        verif += coefprests.est_coherent(generaux)
        verif += clients.est_coherent(emoluments, generaux)
        verif += reservations.est_coherent(comptes, machines, users)
        verif += docpdf.est_coherent(generaux, clients)
        verif += comptes.est_coherent(clients, generaux)

        if verif > 0:
            return verif

        comptes_actifs = Verification.obtenir_comptes_actifs(acces, livraisons)
        clients_actifs = Verification.obtenir_clients_actifs(comptes_actifs, comptes)

        if (edition.version > 0) and (len(clients_actifs) > 1):
            Outils.affiche_message("Si version différente de 0, un seul client autorisé")
            sys.exit("Trop de clients pour version > 0")
        if (edition.version > 0) and (edition.client_unique != clients_actifs[0]):
            Outils.affiche_message("Le client unique des paramètres d'édition n'est pas le même que celui présent dans "
                                   "les transactions")
            sys.exit("clients non-correspondants pour version > 0")
        self.a_verifier = 0
        return verif

    @staticmethod
    def obtenir_comptes_actifs(acces, livraisons):
        """
        retourne la liste des comptes utilisés, pour les accès et les livraisons
        :param acces: accès importés
        :param livraisons: livraisons importées
        :return: comptes utilisés mappés par clients
        """
        comptes_actifs = []
        for id_compte in livraisons.obtenir_comptes():
            if id_compte not in comptes_actifs:
                comptes_actifs.append(id_compte)
        for id_compte in acces.obtenir_comptes():
            if id_compte not in comptes_actifs:
                comptes_actifs.append(id_compte)

        return comptes_actifs

    @staticmethod
    def obtenir_clients_actifs(comptes_actifs, comptes):
        """
        retourne la liste des clients des comptes actifs
        :param comptes_actifs: comptes actifs
        :param comptes: comptes importés
        :return: comptes utilisés mappés par clients
        """
        clients_actifs = []
        for id_compte in comptes_actifs:
            code_client = comptes.donnees[id_compte]['code_client']
            if code_client not in clients_actifs:
                clients_actifs.append(code_client)
        return clients_actifs
