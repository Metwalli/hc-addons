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

class HCLabTestOrderLineReport(models.Model):
    _name = "hc.lab.test.order.line.report"
    _description = "Test Lines Statistics"
    _auto = False

    patient_id = fields.Many2one('hc.patient', 'Patient', readonly=True)
    order_date = fields.Datetime('Date Order', readonly=True)
    test_id = fields.Many2one('hc.lab.test', 'Test', readonly=True)
    component_id = fields.Many2one('hc.lab.test.component', 'Component', readonly=True)
    value = fields.Float('Value', readonly=True)
    avg_value = fields.Float('Average', readonly=True)

    def _select(self):
        select_str = """
            min(lr.id) as id,
            so.patient_id AS patient_id,
            t_order.order_date AS order_date,
            t_line.test_id AS test_id,
            lr.component_id AS component_id,
            lr.num_value AS value,
            avg(num_value) AS avg_value
        """
        return select_str

    def _from(self):
        from_str = """
            hc_service_order as so,
            hc_lab_test_order as t_order,
            hc_lab_test_order_line as t_line,
            hc_patient as patient,
            hc_lab_test as test,
            hc_lab_test_order_line_results as lr,
            hc_lab_test_component as component
        """
        return from_str

    def _where(self):
        where_str = """
            so.patient_id = patient.id AND
            t_order.service_order_id = so.id AND
            t_line.test_order_id = t_order.id AND
            t_line.test_id = test.id AND
            lr.test_line_id = t_line.id AND
            lr.component_id = component.id AND
            component.type = 'num' AND
            t_line.state in ('result_entered', 'result_verified', 'dispatch', 'done')
        """
        return where_str

    def _group_by(self):
        group_by_str = """
            so.patient_id,
            t_order.order_date,
            t_line.test_id,
            lr.component_id,
            lr.num_value
        """
        return group_by_str
    def _order_by(self):
        order_by_str = """
            so.patient_id,
            t_order.order_date
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
