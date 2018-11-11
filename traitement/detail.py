from outils import Outils


class Detail(object):
    """
    Classe pour la création du détail des coûts
    """

    @staticmethod
    def detail(dossier_destination, edition, lignes):
        """
        création du détail des coûts
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param lignes: lignes de données du détail
        """

        nom = "detail_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = ["Année", "Mois", "Code Client Facture", "Code Client SAP", "Abrev. Labo", "type client",
                     "nature client", "Id-Compte", "Numéro de compte", "Intitulé compte", "Code Type Compte", "code_d",
                     "Id-categ-cout", "Intitulé catégorie coût", "Durée machines (min)", "Durée main d'oeuvre (min)",
                     "U1", "U2", "U3", "MO", "intitule_court", "N. prestation", "Intitulé", "Montant", "Rabais",
                     "Catégorie Stock", "Affiliation"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def creation_lignes(edition, sommes, clients, generaux, acces, livraisons, comptes, couts, prestations):
        """
        génération des lignes de données du détail
        :param edition: paramètres d'édition
        :param sommes: sommes calculées
        :param clients: clients importés
        :param generaux: paramètres généraux
        :param acces: accès importés
        :param livraisons: livraisons importées
        :param comptes: comptes importés
        :param couts: catégories coûts importées
        :param prestations: prestations importées
        :return: lignes de données du détail
        """
        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer le détail des coûts"
            Outils.affiche_message(info)
            return None

        lignes = []

        for code_client in sorted(sommes.sommes_clients.keys()):
            client = clients.donnees[code_client]

            if code_client in sommes.sommes_comptes:
                sclo = sommes.sommes_comptes[code_client]
                comptes_utilises = Outils.comptes_in_somme(sclo, comptes)
                base_client = [edition.annee, edition.mois, code_client, client['code_sap'], client['abrev_labo'],
                               'U', client['nature']]

                for num_compte, id_compte in sorted(comptes_utilises.items()):
                    compte = comptes.donnees[id_compte]
                    base_compte = base_client + [id_compte, num_compte, compte['intitule'], compte['type_subside']]

                    if code_client in acces.sommes and id_compte in acces.sommes[code_client]['categories']:
                        som_cats = acces.sommes[code_client]['categories'][id_compte]
                        for id_cout, som_cat in sorted(som_cats.items()):
                            duree = som_cat['duree_hp'] + som_cat['duree_hc']
                            ligne = base_compte + ['M', id_cout, couts.donnees[id_cout]['intitule'], duree,
                                                   som_cat['mo'], Outils.format_2_dec(som_cat['mu1']),
                                                   Outils.format_2_dec(som_cat['mu2']),
                                                   Outils.format_2_dec(som_cat['mu3']),
                                                   Outils.format_2_dec(som_cat['mmo']), "", "", "", "", "", "", ""]
                            lignes.append(ligne)

                        ligne = base_compte + ['M', 'Arrondi', "", "", "",
                                               Outils.format_2_dec(sclo[id_compte]['mu1_d']),
                                               Outils.format_2_dec(sclo[id_compte]['mu2_d']),
                                               Outils.format_2_dec(sclo[id_compte]['mu3_d']),
                                               Outils.format_2_dec(sclo[id_compte]['mmo_d']), "", "", "", "", "", "",
                                               ""]
                        lignes.append(ligne)

                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        somme = livraisons.sommes[code_client][id_compte]

                        for article in generaux.articles_d3:
                            if article.code_d in somme:
                                elu1 = article.eligible_U1
                                elu2 = article.eligible_U2
                                elu3 = article.eligible_U3
                                if elu1 == "NON" and elu2 == "NON" and elu3 == "NON":
                                    continue

                                for no_prestation, sip in sorted(somme[article.code_d].items()):
                                    prestation = prestations.prestation_de_num(no_prestation)
                                    ligne = base_compte + [article.code_d, "", "", "", "", "", "", "", "",
                                                           article.intitule_court, no_prestation, sip['nom'],
                                                           Outils.format_2_dec(sip['montantx']),
                                                           Outils.format_2_dec(sip['rabais']), prestation['categ_stock'], prestation['affiliation']]
                                    lignes.append(ligne)

                                ligne = base_compte + [article.code_d, "", "", "", "", "", "", "", "",
                                                       'Arrondi', "", "",
                                                       Outils.format_2_dec(
                                                           sclo[id_compte]['sommes_cat_m_x_d'][article.code_d]),
                                                       Outils.format_2_dec(
                                                           sclo[id_compte]['sommes_cat_r_d'][article.code_d]), "", ""]
                                lignes.append(ligne)

        return lignes
