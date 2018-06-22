

class Rabais(object):
    """
    Classe contenant les règles de rabais
    """

    @staticmethod
    def rabais_reservation(drsf, supp, shp, shc):
        """
        calcule le rabais de réservation
        :param drsf: délai sans frais pour une machine donnée
        :param supp: durée ouvrée
        :param shp: durée du slot réservée en heures pleines
        :param shc: durée du slot réservée en heures creuses
        :return: durée facturée en heures pleines, durée facturée en heures creuses
        """
        if drsf == 0:
            return 0, 0
        else:
            k = max(0, min(1, (1-supp / drsf)))
            fhp = round(k * shp, 0)
            fhc = round(k * shc, 0)
            return fhp, fhc

    @staticmethod
    def rabais_emolument(mt, emb):
        """
        calcule le rabais sur émolument
        :param mt: mt
        :param emb: émolument de base mensuel
        :return: em, er
        """

        em = emb

        if mt > 0:
            er = 0
        else:
            er = emb
        return em, er

    @staticmethod
    def rabais_reservation_petit_montant(rm, rmin):
        """
        si le montant ne dépasse pas un seuil minimum, un rabais égal à ce montant est appliqué
        :param rm: montant
        :param rmin: seuil
        :return: rabais
        """
        if rm < int(rmin):
            return rm
        else:
            return 0
