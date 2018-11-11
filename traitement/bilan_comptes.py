from outils import Outils


class BilanComptes(object):
    """
    Classe pour la création du bilan des comptes
    """

    @staticmethod
    def bilan(dossier_destination, edition, generaux, lignes):
        """
        création du bilan
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param generaux: paramètres généraux
        :param lignes: lignes de données du bilan
        """

        nom = "bilan-comptes_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
              str(edition.version)
        if edition.version > 0:
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = ["année", "mois", "référence", "code client", "code client sap", "abrév. labo", "nom labo",
                     "type client", "nature client", "id-compte", "numéro compte", "intitulé compte",
                     "code type compte", "maj", "moj", "rabais", "mj"]
            for categorie in generaux.codes_d3():
                ligne.append(categorie + "j")
            ligne += ["somme-j", "bonus"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def creation_lignes(edition, sommes, clients, generaux, comptes):
        """
        génération des lignes de données du bilan
        :param edition: paramètres d'édition
        :param sommes: sommes calculées
        :param clients: clients importés
        :param generaux: paramètres généraux
        :param comptes: comptes importés
        :return: lignes de données du bilan
        """
        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer le bilan des comptes"
            Outils.affiche_message(info)
            return None

        lignes = []
        for code_client in sorted(sommes.sommes_clients.keys()):
            if code_client in sommes.sommes_comptes:
                client = clients.donnees[code_client]
                nature = generaux.code_ref_par_code_n(client['nature'])
                reference = nature + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
                if edition.version > 0:
                    reference += "-" + str(edition.version)

                comptes_utilises = Outils.comptes_in_somme(sommes.sommes_comptes[code_client], comptes)
                for num_compte, id_compte in sorted(comptes_utilises.items()):
                    compte = comptes.donnees[id_compte]
                    sco = sommes.sommes_comptes[code_client][id_compte]
                    ligne = [edition.annee, edition.mois, reference, code_client, client['code_sap'],
                             client['abrev_labo'], client['nom_labo'], 'U', client['nature'], id_compte, num_compte,
                             compte['intitule'], compte['type_subside'], Outils.format_2_dec(sco['somme_j_mai']),
                             Outils.format_2_dec(sco['somme_j_moi']),
                             Outils.format_2_dec(client['rh'] * sco['somme_j_dhi']), Outils.format_2_dec(sco['mj'])]
                    total = sco['mj']
                    for categorie in generaux.codes_d3():
                        total += sco['tot_cat'][categorie]
                        ligne.append(Outils.format_2_dec(sco['tot_cat'][categorie]))
                    ligne += [Outils.format_2_dec(total), Outils.format_2_dec(client['bh'] * sco['somme_j_dhi'])]
                    lignes.append(ligne)
        return lignes
