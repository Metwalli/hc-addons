# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _name = "hc.service.order.report"
    _description = "Service Orders Statistics"
    _auto = False
    _rec_name = 'order_date'

    _columns = {
        'order_no': fields.char('Order No', size=20, readonly=True),
        'patient_id': fields.many2one('hc.patient', 'Patient', readonly=True),
        'doctor_id': fields.many2one('resource.resource', 'Doctor', readonly=True),
        'order_date': fields.datetime('Date Order', readonly=True),
        'user_id': fields.many2one('res.users', 'User ID', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', readonly=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('to_invoice', 'To Invoice'),
            ('progress', 'In Progress'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ], string='Status'),
        'service_type': fields.selection([
            ('consultation', 'Consultation'),
            ('lab_test', 'Laboratory Test'),
            ('rad_test', 'Radiology Test'),
            ('procedure', 'Procedure'),
            ('operation', 'Operation'),
            ('ward', 'Ward')
            ], string='Service Type'),
        'count_all': fields.integer('Count'),
    }
    _order = 'order_date desc'

    def _select(self):
        select_str = """
              min(order_line.id) AS id,
              service_order.order_no AS order_no,
              service_order.patient_id AS patient_id,
              service_order.doctor_id AS doctor_id,
              service_order.order_date AS order_date,
              service_order.user_id AS user_id,
              order_line.product_id AS product_id,
              order_line.product_uom AS product_uom,
              service_order.state AS state,
              product.service_type as service_type,
              count(*) AS count_all
        """
        return select_str

    def _from(self):
        from_str = """
              hc_service_order as service_order,
              hc_patient as patient,
              resource_resource as resource,
              hc_service_order_line as order_line,
              product_product as product,
              product_uom as units
        """
        return from_str

    def _where(self):
        where_str = """
              service_order.patient_id = patient.id AND
              service_order.doctor_id = resource.id AND
              order_line.order_id = service_order.id AND
              order_line.product_id = product.id AND
              order_line.product_uom = units.id
        """
        return where_str

    def _group_by(self):
        group_by_str = """
              service_order.order_no,
              service_order.patient_id,
              service_order.doctor_id,
              service_order.order_date,
              service_order.user_id,
              order_line.product_id,
              order_line.product_uom,
              service_order.state,
              product.service_type
        """
        return group_by_str
    def _order_by(self):
        order_by_str = """
                service_order.order_date DESC,
                service_order.order_no ASC
        """
        return order_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT
                %s
            FROM
                %s
            WHERE
                %s
            GROUP BY
                %s
            ORDER BY
                %s
            )""" % (self._table, self._select(), self._from(), self._where(), self._group_by(), self._order_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
