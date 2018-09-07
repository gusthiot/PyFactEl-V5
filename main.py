# This Python file uses the following encoding: utf-8

"""
Fichier principal à lancer pour faire tourner le logiciel

Usage:
  main.py [options]

Options:

  -h   --help              Affiche le présent message
  --entrees <chemin>       Chemin des fichiers d'entrée
  --sansgraphiques         Pas d'interface graphique
"""
import datetime
import sys
from docopt import docopt

from importes import (Client,
                      Acces,
                      Emolument,
                      CoefPrest,
                      CategPrix,
                      Compte,
                      Livraison,
                      Machine,
                      Prestation,
                      Reservation,
                      Couts,
                      User,
                      DossierSource,
                      DossierDestination)
from outils import Outils
from parametres import (Edition,
                        DocPdf,
                        Paramannexe,
                        SuppressionFacture,
                        AnnulationVersion,
                        AnnulationSuppression,
                        Generaux)
from traitement import (Annexes,
                        BilanMensuel,
                        BilanComptes,
                        Facture,
                        Sommes,
                        Verification,
                        Detail,
                        Resumes,
                        Recapitulatifs)
from prod2qual import Prod2Qual
from latex import Latex

arguments = docopt(__doc__)

if arguments["--sansgraphiques"]:
    Outils.interface_graphique(False)

if arguments["--entrees"]:
    dossier_data = arguments["--entrees"]
else:
    dossier_data = Outils.choisir_dossier()
dossier_source = DossierSource(dossier_data)

pe_present = Outils.existe(Outils.chemin([dossier_data, Edition.nom_fichier]))
sup_present = Outils.existe(Outils.chemin([dossier_data, SuppressionFacture.nom_fichier]))
ann_present = Outils.existe(Outils.chemin([dossier_data, AnnulationVersion.nom_fichier]))
ann_sup_present = Outils.existe(Outils.chemin([dossier_data, AnnulationSuppression.nom_fichier]))

if pe_present and sup_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : supprfact.csv et paramedit.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

if pe_present and ann_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : paramedit.csv et annulversion.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

if ann_present and sup_present:
    msg = "Deux fichiers bruts incompatibles dans le répertoire : supprfact.csv et annulversion.csv"
    Outils.affiche_message(msg)
    sys.exit("Erreur sur les fichiers")

if pe_present and ann_sup_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : annulsuppr.csv et paramedit.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

if ann_sup_present and ann_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : annulsuppr.csv et annulversion.csv"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

if ann_sup_present and sup_present:
    msg = "Deux fichiers bruts incompatibles dans le répertoire : annulsuppr.csv et annulversion.csv"
    Outils.affiche_message(msg)
    sys.exit("Erreur sur les fichiers")

if not ann_present and not sup_present and not pe_present and not ann_sup_present:
    msg = "Ni supprfact.csv, ni paramedit.csv, ni annulversion.csv , ni annulsuppr.csv " \
          "dans le répértoire, rien ne sera fait !"
    Outils.affiche_message(msg)
    sys.exit("Erreur sur les fichiers")

generaux = Generaux(dossier_source)

if pe_present:
    edition = Edition(dossier_source)
    paramannexe = Paramannexe(dossier_source)

    if edition.version > 0 and edition.client_unique == generaux.code_cfact_centre:
        chemin = generaux.chemin_propre
    elif edition.filigrane != "":
        chemin = generaux.chemin_filigrane
    else:
        chemin = generaux.chemin
    dossier_enregistrement = Outils.chemin([chemin, edition.annee, Outils.mois_string(edition.mois)], generaux)
    existe = Outils.existe(dossier_enregistrement, True)
    dossier_lien = Outils.lien_dossier([generaux.lien, edition.annee, Outils.mois_string(edition.mois)], generaux)

    if edition.version == 0:
        if existe:
            msg = "Le répertoire " + dossier_enregistrement + " existe déjà !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur le répértoire")
        dossier_csv = Outils.chemin([dossier_enregistrement, "csv_0"], generaux)
        Outils.existe(dossier_csv, True)
    else:
        dossier_csv = Outils.chemin([dossier_enregistrement, "csv_" + str(edition.version) + "_" +
                                     edition.client_unique])

        w = edition.version - 1
        dossier_w = Outils.chemin([dossier_enregistrement, "suppr_" + str(w) + "_" + edition.client_unique])
        if Outils.existe(dossier_w) and not Outils.existe(Outils.chemin([dossier_w, "copernic.csv"])):
            msg = "La suppression de la version " + str(w) + " du client " + edition.client_unique + \
                  " n'a pas été confirmée !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur le répértoire")

        if Outils.existe(dossier_csv, True):
            msg = "La version " + str(edition.version) + " du client " + edition.client_unique + " existe déjà !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur le répértoire")


    dossier_destination = DossierDestination(dossier_csv)

    if Outils.existe(Outils.chemin([dossier_data, DocPdf.nom_fichier])):
        docpdf = DocPdf(dossier_source)
    else:
        docpdf = None

    acces = Acces(dossier_source)
    clients = Client(dossier_source)
    emoluments = Emolument(dossier_source)
    categprix = CategPrix(dossier_source)
    coefprests = CoefPrest(dossier_source)
    comptes = Compte(dossier_source)
    livraisons = Livraison(dossier_source)
    machines = Machine(dossier_source)
    prestations = Prestation(dossier_source)
    reservations = Reservation(dossier_source)
    couts = Couts(dossier_source)
    users = User(dossier_source)

    verification = Verification()

    if verification.verification_date(edition, acces, clients, comptes, users, livraisons, machines, prestations,
                                      reservations) > 0:
        sys.exit("Erreur dans les dates")

    if verification.verification_coherence(generaux, edition, acces, clients, emoluments, coefprests, comptes, users,
                                           livraisons, machines, prestations, reservations, couts, categprix,
                                           docpdf) > 0:
        sys.exit("Erreur dans la cohérence")

    livraisons.calcul_montants(prestations, coefprests, clients, verification, comptes)
    reservations.calcul_montants(machines, categprix, clients, comptes, verification)
    acces.calcul_montants(machines, categprix, clients, verification, couts, comptes)

    sommes = Sommes(verification, generaux)
    sommes.calculer_toutes(livraisons, reservations, acces, clients, machines)

    for donnee in paramannexe.donnees:
        donnee['chemin'] = Outils.chemin([dossier_enregistrement, donnee['dossier']], generaux)
        Outils.existe(donnee['chemin'], True)
        donnee['lien'] = Outils.lien_dossier([dossier_lien, donnee['dossier']], generaux)

    # faire les annexes avant la facture, que le ticket puisse vérifier leur existence
    if Latex.possibles():
        Annexes.annexes(sommes, clients, edition, livraisons, acces, machines, reservations, comptes, paramannexe,
                        generaux, users, couts, docpdf)

    Outils.copier_dossier("./reveal.js/", "js", dossier_enregistrement)
    Outils.copier_dossier("./reveal.js/", "css", dossier_enregistrement)
    facture_prod = Facture()
    f_html_sections = facture_prod.factures(sommes, dossier_destination, edition, generaux, clients, comptes,
                                            paramannexe)

    prod2qual = Prod2Qual(dossier_source)
    if prod2qual.actif:
        facture_qual = Facture(prod2qual)
        generaux_qual = Generaux(dossier_source, prod2qual)
        facture_qual.factures(sommes, dossier_destination, edition, generaux_qual, clients, comptes, paramannexe)

    bm_lignes = BilanMensuel.creation_lignes(edition, sommes, clients, generaux, acces, livraisons, comptes,
                                             reservations)
    BilanMensuel.bilan(dossier_destination, edition, generaux, bm_lignes)
    bc_lignes = BilanComptes.creation_lignes(edition, sommes, clients, generaux, comptes)
    BilanComptes.bilan(dossier_destination, edition, generaux, bc_lignes)
    det_lignes = Detail.creation_lignes(edition, sommes, clients, generaux, acces, livraisons, comptes, couts,
                                        prestations)
    Detail.detail(dossier_destination, edition, det_lignes)

    cae_lignes = Recapitulatifs.cae_lignes(edition, acces, comptes, clients, users, machines, couts)
    Recapitulatifs.cae(dossier_destination, edition, cae_lignes)
    lvr_lignes = Recapitulatifs.lvr_lignes(edition, livraisons, comptes, clients, users, prestations)
    Recapitulatifs.lvr(dossier_destination, edition, lvr_lignes)
    res_lignes = Recapitulatifs.res_lignes(edition, reservations, comptes, clients, users, machines)
    Recapitulatifs.res(dossier_destination, edition, res_lignes)

    for fichier in [acces.nom_fichier, clients.nom_fichier, emoluments.nom_fichier, coefprests.nom_fichier,
                    comptes.nom_fichier, livraisons.nom_fichier, machines.nom_fichier, prestations.nom_fichier,
                    reservations.nom_fichier, couts.nom_fichier, users.nom_fichier, generaux.nom_fichier,
                    edition.nom_fichier, categprix.nom_fichier, paramannexe.nom_fichier]:
        dossier_destination.ecrire(fichier, dossier_source.lire(fichier))
    if docpdf is not None:
        dossier_destination.ecrire(docpdf.nom_fichier, dossier_source.lire(docpdf.nom_fichier))

    if edition.filigrane == "":
        if edition.version == 0:
            Resumes.base(edition, DossierSource(dossier_csv), DossierDestination(dossier_enregistrement))
            Resumes.supprimmer(generaux.code_cfact_centre, edition.mois, edition.annee,
                               DossierSource(dossier_enregistrement), DossierDestination(dossier_enregistrement))
        elif Outils.existe(Outils.chemin([dossier_enregistrement, "csv_0"])):
            maj = [bm_lignes, bc_lignes, det_lignes, cae_lignes, lvr_lignes, res_lignes]
            Resumes.mise_a_jour(edition, clients, DossierSource(dossier_enregistrement),
                                DossierDestination(dossier_enregistrement), maj, f_html_sections)

if sup_present:
    suppression = SuppressionFacture(dossier_source)
    dossier_enregistrement = Outils.chemin([generaux.chemin, suppression.annee,
                                            Outils.mois_string(suppression.mois)])
    suffixe = str(suppression.version) + "_" + suppression.client_unique

    if suppression.version == 0:
        if not Outils.existe(Outils.chemin([dossier_enregistrement, "csv_0"])):
            msg = "La version 0 n'existe pas dans " + dossier_enregistrement + ", impossible de supprimer une facture !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        dossier_copernic = "csv_0"
    else:
        if not Outils.existe(Outils.chemin([dossier_enregistrement, "csv_" + suffixe])):
            msg = "La version " + str(suppression.version) + " du client " + suppression.client_unique + \
                  " n'existe pas dans " + dossier_enregistrement + ", impossible de supprimer une facture !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")
        dossier_copernic = "csv_" + suffixe

    if not Outils.existe(Outils.chemin([dossier_enregistrement, dossier_copernic, "copernic.csv"])):
            msg = "La version " + str(suppression.version) + \
                  " n’a pas été émise dans SAP, impossible de supprimer une facture !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

    dossier_suppr = Outils.chemin([dossier_enregistrement, "suppr_" + suffixe])
    if Outils.existe(dossier_suppr):
        msg = "La suppression de la version " + str(suppression.version) + " du client " + suppression.client_unique + \
              " existe déjà !"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur la version")

    Outils.existe(dossier_suppr, True)

    DossierDestination(dossier_suppr).ecrire(suppression.nom_fichier, dossier_source.lire(suppression.nom_fichier))

    Resumes.suppression(
        suppression, DossierSource(dossier_enregistrement), DossierDestination(dossier_enregistrement))

if ann_sup_present:
    annsupp = AnnulationSuppression(dossier_source)
    dossier_enregistrement = Outils.chemin([generaux.chemin, annsupp.annee,
                                            Outils.mois_string(annsupp.mois)])
    suffixe = str(annsupp.version) + "_" + annsupp.client_unique
    dossier_suppr = Outils.chemin([dossier_enregistrement, "suppr_" + suffixe])

    if not Outils.existe(dossier_suppr):
        msg = "Annulation de suppression impossible !"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur la version")

    if Outils.existe(Outils.chemin([dossier_suppr, "copernic.csv"])):
        msg = "Impossible d’annuler l’opération de suppression de la version " + str(annsupp.version) + \
              " car l’opération a été confirmée !"
        Outils.affiche_message(msg)
        sys.exit("Erreur sur la version")

    if annsupp.version == 0:
        dossier_csv = Outils.chemin([dossier_enregistrement, "csv_0"])
        if not Outils.existe(dossier_csv):
            msg = "La version 0 à recharger pour le client " + annsupp.client_unique + " n’existe pas !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")
    else:
        dossier_csv = Outils.chemin([dossier_enregistrement, "csv_" + suffixe])
        if not Outils.existe(dossier_csv):
            msg = "La version " + str(annsupp.version) + " du client " + annsupp.client_unique + \
                  " à recharger n'existe pas !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

    DossierDestination(dossier_suppr).ecrire(annsupp.nom_fichier, dossier_source.lire(annsupp.nom_fichier))
    now = datetime.datetime.now()
    Outils.renommer_dossier([dossier_enregistrement, "suppr_" + suffixe],
                            [dossier_enregistrement, "old_" + suffixe + "_" + now.strftime("%Y%m%d_%H%M")])
    Resumes.annulation_suppression(annsupp, DossierSource(dossier_enregistrement),
                                   DossierDestination(dossier_enregistrement), DossierSource(dossier_csv))

if ann_present:
    annulation = AnnulationVersion(dossier_source)
    if annulation.client_unique == generaux.code_cfact_centre:
        chemin = generaux.chemin_propre
    else:
        chemin = generaux.chemin
    dossier_enregistrement = Outils.chemin([chemin, annulation.annee, Outils.mois_string(annulation.mois)])
    if annulation.annule_version == 0:
        chemin_copernic = Outils.chemin([dossier_enregistrement, "csv_0", "copernic.csv"])
        if Outils.existe(chemin_copernic):
            msg = "La version 0 a déjà été émise et ne peut plus être annulée !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")
        else:
            Outils.effacer_dossier(Outils.chemin([chemin, annulation.annee, Outils.mois_string(annulation.mois)]))
    else:
        chemin = Outils.chemin([dossier_enregistrement, "csv_" + str(annulation.annule_version) + "_" +
                                annulation.client_unique])
        if not Outils.existe(chemin):
            msg = "La version " + str(annulation.annule_version) + " à annuler pour le client " +\
                  annulation.client_unique + " n’existe pas !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        chemin_copernic = Outils.chemin([dossier_enregistrement, "csv_" + str(annulation.annule_version) + "_" +
                                         annulation.client_unique, "copernic.csv"])
        if Outils.existe(chemin_copernic):
            msg = "La version " + str(annulation.annule_version) + " à annuler pour le client " + \
                  annulation.client_unique + " a déjà été émise et ne peut plus être annulée !"
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        if annulation.recharge_version == 0:
            dossier_csv = Outils.chemin([dossier_enregistrement, "csv_0"])
            if not Outils.existe(dossier_csv):
                msg = "La version 0 à recharger n'existe pas !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")
        else:
            dossier_csv = Outils.chemin([dossier_enregistrement, "csv_" + str(annulation.recharge_version) + "_" +
                                         annulation.client_unique])
            if not Outils.existe(dossier_csv):
                msg = "La version " + str(annulation.recharge_version) + " à recharger pour le client " + \
                      annulation.client_unique + " n'existe pas !"
                Outils.affiche_message(msg)
                sys.exit("Erreur sur la version")

        DossierDestination(chemin).ecrire(annulation.nom_fichier, dossier_source.lire(annulation.nom_fichier))
        now = datetime.datetime.now()
        Outils.renommer_dossier([dossier_enregistrement, "csv_" + str(annulation.annule_version) + "_" +
                                annulation.client_unique],
                                [dossier_enregistrement, "old_" + str(annulation.annule_version) + "_" +
                                 annulation.client_unique + "_" + now.strftime("%Y%m%d_%H%M")])

        Resumes.annulation(annulation, DossierSource(dossier_enregistrement),
                           DossierDestination(dossier_enregistrement), DossierSource(dossier_csv))

Outils.affiche_message("OK !!!")
