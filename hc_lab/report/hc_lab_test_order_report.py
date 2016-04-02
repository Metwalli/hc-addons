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

from openerp import fields, models, api, tools

class HCLabTestOrderReport(models.Model):
    _name = "hc.lab.test.order.report"
    _description = "Test Statistics"
    _auto = False
    _rec_name = 'order_date'

    patient_id = fields.Many2one('hc.patient', 'Patient', readonly=True)
    doctor_id = fields.Many2one('resource.resource', 'Doctor', readonly=True)
    order_date = fields.Datetime('Date Order', readonly=True)
    test_id = fields.Many2one('hc.lab.test', 'Test', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('new', 'New Order'),
        ('sample_collected', 'Sample Collected'),
        ('sample_recollect', 'Sample Recollect'),
        ('result_entered', 'Results Entered'),
        ('result_verified', 'Results Verified'),
        ('dispatch', 'Dispatch'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
        ], 'Order State', readonly=True)
    order_count = fields.Integer('Orders', readonly=True)

    _order = 'order_date desc'

    def _select(self):
        select_str = """
            min(t_line.id) As id,
            so.patient_id AS patient_id,
            so.doctor_id AS doctor_id,
            t_order.order_date AS order_date,
            t_line.test_id AS test_id,
            t_line.state AS state,
            count(*) AS order_count
        """
        return select_str

    def _from(self):
        from_str = """
            hc_service_order as so,
            hc_patient as patient,
            resource_resource as resource,
            hc_lab_test_order as t_order,
            hc_lab_test_order_line as t_line,
            hc_lab_test as test
        """
        return from_str

    def _where(self):
        where_str = """
            so.patient_id = patient.id AND
            so.doctor_id = resource.id AND
            t_order.service_order_id = so.id AND
            t_line.test_order_id = t_order.id AND
            t_line.test_id = test.id
        """
        return where_str

    def _group_by(self):
        group_by_str = """
            so.patient_id,
            so.doctor_id,
            t_order.order_date,
            t_line.test_id,
            t_line.state
        """
        return group_by_str
    def _order_by(self):
        order_by_str = """
            ORDER BY
                t_order.order_date DESC,
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
            )""" % (self._table, self._select(), self._from(), self._where(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
