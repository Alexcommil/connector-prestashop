## -*- coding: utf-8 -*-
###############################################################################
#
#   PrestashopERPconnect for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   Copyright (C) 2013 Camptocamp (http://www.camptocamp.com)
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Guewen Baconnier <guewen.baconnier@camptocamp.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.connector import Binder
from ..backend import prestashop


class PrestashopBinder(Binder):
    """ Generic Binder for Prestshop """


@prestashop
class PrestashopModelBinder(PrestashopBinder):
    """
    Bindings are done directly on the model
    """
    _model_name = [
        'prestashop.shop.group',
        'prestashop.shop',
        'prestashop.res.partner',
        'prestashop.address',
        'prestashop.res.partner.category',
        'prestashop.res.lang',
        'prestashop.res.country',
        'prestashop.res.currency',
        'prestashop.account.tax',
        'prestashop.account.tax.group',
        'prestashop.product.category',
        'prestashop.product.image',
        'prestashop.product.product',
        'prestashop.product.combination',
        'prestashop.product.combination.option',
        'prestashop.product.combination.option.value',
        'prestashop.sale.order',
        'prestashop.sale.order.state',
        'prestashop.delivery.carrier',
        'prestashop.refund',
        'prestashop.supplier',
        'prestashop.product.supplierinfo',
        'prestashop.mail.message',
        'prestashop.mrp.bom',
        'prestashop.combination.mrp.bom',
        'prestashop.groups.pricelist',
    ]

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: if True, returns the openerp_id of the prestashop_xxxx
                       record, else return the id of that record
        :return: a record ID, depending on the value of unwrap,
                 or None if the external_id is not mapped
        :rtype: int
        """
        openerp_ids = self.environment.model.search(
            self.session.cr,
            self.session.uid,
            [
                ('prestashop_id', '=', external_id),
                ('backend_id', '=', self.backend_record.id)
            ],
            limit=1,
            context=self.session.context
        )
        if not openerp_ids:
            return None
        openerp_id = openerp_ids[0]
        if unwrap:
            return self.session.read(self.environment.model._name,
                                     openerp_id,
                                     ['openerp_id'])['openerp_id'][0]
        else:
            return openerp_id

    def to_backend(self, local_id, unwrap=False):
        """ Give the external ID for an OpenERP ID

        :param local_id: Local ID for which we want the external id
                         can be an erp_id or a erp_ps_id
        :param unwrap: if True, the erp_id is the id of native openerp
                       object and not a prestashop_xxxx. In this case
                       we have first to found the prestashop_xxx object id
                       (erp_ps_id) and then the external id for this record
        :return: backend identifier of the record
        """
        if unwrap:
            erp_ps_id = self.session.search(self.model._name, [
                ['openerp_id', '=', local_id],
                ['backend_id', '=', self.backend_record.id]
            ])
            if erp_ps_id:
                erp_ps_id = erp_ps_id[0]
            else:
                return None
        else:
            erp_ps_id = local_id

        prestashop_id = self.session.read(
            self.model._name,
            erp_ps_id, ['prestashop_id'])['prestashop_id']
        return prestashop_id

    def bind(self, external_id, openerp_id):
        """ Create the link between an external ID and an OpenERP ID

        :param external_id: External ID to bind
        :param openerp_id: OpenERP ID to bind
        :type openerp_id: int
        """
        # avoid to trigger the export when we modify the `prestashop_id`
        context = dict(self.session.context, connector_no_export=True)
        now_fmt = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.environment.model.write(
            self.session.cr,
            self.session.uid,
            openerp_id,
            {'prestashop_id': str(external_id),
             'sync_date': now_fmt},
            #{'prestashop_id': external_id},
            context=context
        )
