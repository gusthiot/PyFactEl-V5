from outils import Outils
from .rabais import Rabais
import math


class Sommes(object):
    """
    Classe contenant les méthodes pour le calcul des sommes par compte, catégorie et client
    """

    cles_somme_compte = ['somme_j_mai', 'somme_j_mai_d', 'somme_j_moi', 'somme_j_moi_d', 'somme_j_dhi', 'somme_j_dhi_d',
                         'somme_j_mach_mai', 'somme_j_mach_mai_d', 'somme_j_mach_moi', 'somme_j_mach_moi_d',
                         'somme_j_mm', 'somme_j_mr','somme_j_mb', 'c1', 'c2', 'mu1', 'mu2', 'mu3', 'mmo', 'mu1_d',
                         'mu2_d', 'mu3_d', 'mmo_d']

    cles_somme_client = ['mat', 'mot', 'dht', 'somme_t_mm', 'somme_t_mr', 'somme_t_mb', 'mt', 'somme_t', 'em',
                         'er', 'e', 'res', 'rm', 'rm_d', 'rr', 'r']

    def __init__(self, verification, generaux):
        """
        initialisation des sommes, et vérification si données utilisées correctes
        :param verification: pour vérifier si les dates et les cohérences sont correctes
        :param generaux: paramètres généraux
        """

        self.verification = verification
        self.sommes_comptes = {}
        self.sco = 0
        self.sommes_clients = {}
        self.calculees = 0
        self.categories = generaux.codes_d3()
        self.min_fact_rese = generaux.min_fact_rese

    def calculer_toutes(self, livraisons, reservations, acces, clients, machines):
        """
        calculer toutes les sommes, par compte et par client
        :param livraisons: livraisons importées et vérifiées
        :param reservations: réservations importées et vérifiées
        :param acces: accès machines importés et vérifiés
        :param clients: clients importés et vérifiés
        :param machines: machines importées et vérifiées
        """
        self.somme_par_compte(livraisons, acces, clients)
        self.somme_par_client(clients, reservations, machines, acces)

    def nouveau_somme(self, cles, est_compte=False):
        """
        créé un nouveau dictionnaire avec les clés entrées
        :param cles: clés pour le dictionnaire
        :param est_compte: True s'il s'agit d'une somme par compte
        :return: dictionnaire indexé par les clés données, avec valeurs à zéro
        """
        somme = {}
        for cle in cles:
            somme[cle] = 0
        somme['sommes_cat_m'] = {}
        somme['sommes_cat_r'] = {}
        somme['tot_cat'] = {}
        if est_compte:
            somme['sommes_cat_m_d'] = {}
            somme['sommes_cat_r_d'] = {}
            somme['sommes_cat_m_x'] = {}
            somme['sommes_cat_m_x_d'] = {}
            somme['tot_cat_x'] = {}
        for categorie in self.categories:
            somme['sommes_cat_m'][categorie] = 0
            somme['sommes_cat_r'][categorie] = 0
            somme['tot_cat'][categorie] = 0
            if est_compte:
                somme['sommes_cat_m_d'][categorie] = 0
                somme['sommes_cat_r_d'][categorie] = 0
                somme['sommes_cat_m_x'][categorie] = 0
                somme['sommes_cat_m_x_d'][categorie] = 0
                somme['tot_cat_x'][categorie] = 0
        return somme

    def somme_par_compte(self, livraisons, acces, clients):
        """
        calcule les sommes par comptes sous forme de dictionnaire : client->compte->clés_sommes
        :param livraisons: livraisons importées et vérifiées
        :param acces: accès machines importés et vérifiés
        :param clients: clients importés et vérifiés
        """

        if self.verification.a_verifier != 0:
            info = "Sommes :  vous devez faire les vérifications avant de calculer les sommes"
            Outils.affiche_message(info)
            return

        spco = {}
        for code_client in acces.sommes:
            if code_client not in spco:
                spco[code_client] = {}
            spco_cl = spco[code_client]
            for id_compte in acces.sommes[code_client]['comptes']:
                if id_compte not in spco_cl:
                    spco_cl[id_compte] = self.nouveau_somme(Sommes.cles_somme_compte, True)
                somme = spco_cl[id_compte]
                ac_som = acces.sommes[code_client]['comptes']
                if id_compte in ac_som:
                    for id_machine, som in ac_som[id_compte].items():
                        somme['mu1'] += som['mu1']
                        somme['mu2'] += som['mu2']
                        somme['mu3'] += som['mu3']
                        somme['mmo'] += som['mmo']
                        somme['somme_j_mach_mai'] += som['mai_hp'] + som['mai_hc']
                        somme['somme_j_mach_moi'] += som['moi']
                        somme['somme_j_dhi'] += som['dhi']
                ac_cat_som = acces.sommes[code_client]['categories']
                if id_compte in ac_cat_som:
                    for id_cout, cat_som in ac_cat_som[id_compte].items():
                        somme['somme_j_mai'] += cat_som['mai']
                        somme['somme_j_moi'] += cat_som['moi']

        for code_client in livraisons.sommes:
            if code_client not in spco:
                spco[code_client] = {}
            spco_cl = spco[code_client]
            for id_compte in livraisons.sommes[code_client]:
                if id_compte not in spco_cl:
                    spco_cl[id_compte] = self.nouveau_somme(Sommes.cles_somme_compte, True)
                somme = spco_cl[id_compte]

                for categorie in livraisons.sommes[code_client][id_compte]:
                    scc = livraisons.sommes[code_client][id_compte][categorie]
                    for prestation in scc:
                        somme['sommes_cat_m'][categorie] += scc[prestation]['montant']
                        somme['sommes_cat_m_x'][categorie] += scc[prestation]['montantx']
                        somme['sommes_cat_r'][categorie] += scc[prestation]['rabais']

        for code_client in spco:
            for id_compte in spco[code_client]:
                somme = spco[code_client][id_compte]
                maij = round(2 * somme['somme_j_mai'], 1) / 2
                somme['somme_j_mai_d'] = maij - somme['somme_j_mai']
                somme['somme_j_mai'] = maij

                maij_mach = round(2 * somme['somme_j_mach_mai'], 1) / 2
                somme['somme_j_mach_mai_d'] = maij_mach - somme['somme_j_mach_mai']
                somme['somme_j_mach_mai'] = maij_mach

                moij = round(2 * somme['somme_j_moi'], 1) / 2
                somme['somme_j_moi_d'] = moij - somme['somme_j_moi']
                somme['somme_j_moi'] = moij

                moij_mach = round(2 * somme['somme_j_mach_moi'], 1) / 2
                somme['somme_j_mach_moi_d'] = moij_mach - somme['somme_j_mach_moi']
                somme['somme_j_mach_moi'] = moij_mach

                dhij = round(2 * somme['somme_j_dhi'], 1) / 2
                somme['somme_j_dhi_d'] = dhij - somme['somme_j_dhi']
                somme['somme_j_dhi'] = dhij

                client = clients.donnees[code_client]
                somme['somme_j_mm'] += somme['somme_j_mai'] + somme['somme_j_moi']
                somme['somme_j_mr'] = client['rh'] * somme['somme_j_dhi']
                somme['somme_j_mb'] = client['bh'] * somme['somme_j_dhi']
                somme['mj'] = somme['somme_j_mm'] - somme['somme_j_mr']

                for categorie in self.categories:
                    cat_m = round(2 * somme['sommes_cat_m'][categorie], 1) / 2
                    somme['sommes_cat_m_d'][categorie] = cat_m - somme['sommes_cat_m'][categorie]
                    somme['sommes_cat_m'][categorie] = cat_m

                    cat_r = round(2 * somme['sommes_cat_r'][categorie], 1) / 2
                    somme['sommes_cat_r_d'][categorie] = cat_r - somme['sommes_cat_r'][categorie]
                    somme['sommes_cat_r'][categorie] = cat_r

                    somme['tot_cat'][categorie] = somme['sommes_cat_m'][categorie] - somme['sommes_cat_r'][categorie]

                    cat_mx = round(2 * somme['sommes_cat_m_x'][categorie], 1) / 2
                    somme['sommes_cat_m_x_d'][categorie] = cat_mx - somme['sommes_cat_m_x'][categorie]
                    somme['sommes_cat_m_x'][categorie] = cat_mx

                    somme['tot_cat_x'][categorie] = somme['sommes_cat_m_x'][categorie]
                    somme['tot_cat_x'][categorie] -= somme['sommes_cat_r'][categorie]

                mu1 = round(2 * somme['mu1'], 1) / 2
                somme['mu1_d'] = mu1 - somme['mu1']
                somme['mu1'] = mu1

                mu2 = round(2 * somme['mu2'], 1) / 2
                somme['mu2_d'] = mu2 - somme['mu2']
                somme['mu2'] = mu2

                mu3 = round(2 * somme['mu3'], 1) / 2
                somme['mu3_d'] = mu3 - somme['mu3']
                somme['mu3'] = mu3

                mmo = round(2 * somme['mmo'], 1) / 2
                somme['mmo_d'] = mmo - somme['mmo']
                somme['mmo'] = mmo

                somme['c1'] = somme['somme_j_mm']
                somme['c2'] = somme['mj']
                for categorie in self.categories:
                    somme['c1'] += somme['sommes_cat_m'][categorie]
                    somme['c2'] += somme['tot_cat'][categorie]

        # print("")
        # print("spco")
        # for code in spco:
        #     if code != "220208":
        #         continue
        #     print(code)
        #     spco_cl = spco[code]
        #     for id in spco_cl:
        #         somme = spco_cl[id]
        #         print("   ", id, somme['somme_j_mai'])

        self.sco = 1
        self.sommes_comptes = spco

    def somme_par_client(self, clients, reservations, machines, acces):
        """
        calcule les sommes par clients sous forme de dictionnaire : client->clés_sommes
        :param clients: clients importés et vérifiés
        :param reservations: réservations importées et vérifiées
        :param machines: machines importées et vérifiées
        :param acces: accès machines importés et vérifiés
        """

        if self.verification.a_verifier != 0:
            info = "Sommes :  vous devez faire les vérifications avant de calculer les sommes"
            Outils.affiche_message(info)
            return

        if self.sco != 0:
            spcl = {}
            for code_client, spco_cl in self.sommes_comptes.items():
                spcl[code_client] = self.nouveau_somme(Sommes.cles_somme_client)
                somme = spcl[code_client]
                somme['res'] = {}
                somme['rm'] = 0
                somme['rr'] = 0
                somme['r'] = 0
                for id_compte, som_co in spco_cl.items():
                    somme['mat'] += som_co['somme_j_mai']
                    somme['mot'] += som_co['somme_j_moi']
                    somme['dht'] += som_co['somme_j_dhi']
                    somme['somme_t_mm'] += som_co['somme_j_mm']
                    somme['somme_t_mr'] += som_co['somme_j_mr']
                    somme['mt'] += som_co['mj']

                    for categorie in self.categories:
                        somme['sommes_cat_m'][categorie] += som_co['sommes_cat_m'][categorie]
                        somme['sommes_cat_r'][categorie] += som_co['sommes_cat_r'][categorie]
                        somme['tot_cat'][categorie] += som_co['tot_cat'][categorie]

            # réservations
            for code_client in reservations.sommes:
                if code_client not in spcl:
                    spcl[code_client] = self.nouveau_somme(Sommes.cles_somme_client)
                    spcl[code_client]['res'] = {}
                somme = spcl[code_client]
                somme_res = reservations.sommes[code_client]

                somme_cae = {}
                if code_client in acces.sommes:
                    somme_cae = acces.sommes[code_client]['machines']

                for id_machine in somme_res.keys():
                    re_hp = somme_res[id_machine]['res_hp']
                    re_hc = somme_res[id_machine]['res_hc']
                    pu_hp = somme_res[id_machine]['pu_hp']
                    pu_hc = somme_res[id_machine]['pu_hc']
                    tx_hp = machines.donnees[id_machine]['tx_occ_eff_hp']
                    tx_hc = machines.donnees[id_machine]['tx_occ_eff_hc']

                    if re_hp > 0 or re_hc > 0:
                        somme['res'][id_machine] = {'tot_hp': 0, 'tot_hc': 0, 'users': {}, 'mont_hp': 0, 'mont_hc': 0}

                        users = somme['res'][id_machine]['users']
                        for id_user, s_u in somme_res[id_machine]['users'].items():
                            if id_user not in users:
                                mini_hp = round(s_u['res_hp'] * tx_hp / 100)
                                mini_hc = round(s_u['res_hc'] * tx_hc / 100)
                                users[id_user] = {'ac_hp': 0, 'ac_hc': 0, 're_hp': s_u['res_hp'],
                                                  're_hc': s_u['res_hc'], 'mini_hp': mini_hp, 'mini_hc': mini_hc,
                                                  'tot_hp': 0, 'tot_hc': 0}

                        if id_machine in somme_cae:
                            for id_user, s_u in somme_cae[id_machine]['users'].items():
                                if id_user not in users:
                                    users[id_user] = {'ac_hp': s_u['duree_hp'], 'ac_hc': s_u['duree_hc'], 're_hp': 0,
                                                      're_hc': 0, 'mini_hp': 0, 'mini_hc': 0, 'tot_hp': 0, 'tot_hc': 0}
                                else:
                                    users[id_user]['ac_hp'] = s_u['duree_hp']
                                    users[id_user]['ac_hc'] = s_u['duree_hc']
                        for id_user, s_u in users.items():
                            s_u['tot_hp'] = s_u['mini_hp'] - s_u['ac_hp']
                            somme['res'][id_machine]['tot_hp'] += s_u['tot_hp']
                            s_u['tot_hc'] = s_u['mini_hc'] - s_u['ac_hc']
                            somme['res'][id_machine]['tot_hc'] += s_u['tot_hc']
                        somme['res'][id_machine]['tot_hp'] = max(0, somme['res'][id_machine]['tot_hp'])
                        somme['res'][id_machine]['tot_hc'] = max(0, somme['res'][id_machine]['tot_hc'])

                        somme['res'][id_machine]['mont_hp'] = round(somme['res'][id_machine]['tot_hp'] * pu_hp / 60, 2)
                        somme['res'][id_machine]['mont_hc'] = round(somme['res'][id_machine]['tot_hc'] * pu_hc / 60, 2)
                        somme['rm'] += somme['res'][id_machine]['mont_hp'] + somme['res'][id_machine]['mont_hc']

                rm = math.floor(somme['rm'])
                somme['rm_d'] = rm - somme['rm']
                somme['rm'] = rm
                somme['rr'] = Rabais.rabais_reservation_petit_montant(somme['rm'], self.min_fact_rese)
                somme['r'] = somme['rm'] - somme['rr']

            for code_client, somme in spcl.items():
                client = clients.donnees[code_client]

                if code_client in acces.sommes:
                    somme_acces = acces.sommes[code_client]
                    for id_machine, scm in somme_acces['machines'].items():
                        somme['somme_t_mb'] += scm['dhm']
                    somme['somme_t_mb'] *= client['bh']

                # somme['somme_t_mb'] += math.ceil(client['bh'] * somme['dht'])
                somme['em'], somme['er'] = Rabais.rabais_emolument(somme['mt'], client['emb'])
                somme['e'] = somme['em'] - somme['er']

                somme['somme_t'] = somme['r'] + somme['mt'] + somme['e']
                for cat, tt in somme['tot_cat'].items():
                    somme['somme_t'] += tt

            # print("")
            # print("spcl")
            # for code in spcl:
            #     if code != "220208":
            #         continue
            #     somme = spcl[code]
            #     print(code, somme['mat'])

            self.calculees = 1
            self.sommes_clients = spcl

        else:
            info = "Vous devez d'abord faire la somme par catégorie, avant la somme par client"
            Outils.affiche_message(info)
