import csv
import os

class Prod2Qual(object):
    nom_fichier = "QAS_vs_PRD.csv"

    def __init__(self, dossier_source):
        self.actif = dossier_source.existe(self.nom_fichier)
        if not self.actif:
            return
        self._client_conv = dict((kv["PRD"], kv["QAS"])
                                 for kv in list(dossier_source.dict_reader(self.nom_fichier)))
                         
    def traduire_code_client(self, code_client_prod):
        assert self.actif

        if self.code_client_existe(code_client_prod):
            return self._client_conv[code_client_prod]
        else:
            return "XXX" + str(code_client_prod)

    def code_client_existe(self, code_client_prod):
        return code_client_prod in self._client_conv

