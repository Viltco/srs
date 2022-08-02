# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PropertyMainInh(models.Model):
    _inherit = 'property.maintanance'

    tenant_id = fields.Many2one('res.partner', string="Tenant", related='property_id.tenant_id')
    email = fields.Char(string="Email", related='property_id.tenant_id.email')
    phone = fields.Char(string="Phone", related='property_id.tenant_id.phone')
    job_pos = fields.Char(string="Job Position", related='property_id.tenant_id.function')

    state = fields.Selection([('new', 'New'),
                              ('active', 'Active'),
                              ('assigned', 'Assigned'),
                              ('in_progress', 'In Progress'),
                              ('hold', 'Hold'),
                              ('to_approve', 'To Approve'),
                              ('rejected', 'Rejected'),
                              ('done', 'Done'),
                              ('invoice', 'Invoiced'),
                              ('cancel', 'Cancelled'),
                              ], default='new')

    def button_active(self):
        self.write({
            'state': 'active'
        })

    def button_assigned(self):
        self.write({
            'state': 'assigned'
        })

    def button_in_progress(self):
        self.write({
            'state': 'in_progress'
        })

    def button_hold(self):
        self.write({
            'state': 'hold'
        })

    def button_to_approve(self):
        self.write({
            'state': 'to_approve'
        })

    def button_rejected(self):
        self.write({
            'state': 'rejected'
        })

    def button_done(self):
        self.write({
            'state': 'done'
        })

    timer_start = fields.Datetime("Timer Start")
    timer_pause = fields.Datetime("Timer Last Pause")
    is_timer_running = fields.Boolean(compute="_compute_is_timer_running")
    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    user_id = fields.Many2one('res.users')

    mainte_time = fields.Float(string='Duration')

    is_hide_start = fields.Boolean(string="Hide Start")
    is_hide_pause = fields.Boolean(string="Hide Pause", default=True)
    is_hide_stop = fields.Boolean(string="Hide Stop", default=True)
    is_hide_resume = fields.Boolean(string="Hide Resume", default=True)

    _sql_constraints = [(
        'unique_timer', 'UNIQUE(res_model, res_id, user_id)',
        'Only one timer occurrence by model, record and user')]

    @api.depends('timer_start', 'timer_pause')
    def _compute_is_timer_running(self):
        for record in self:
            record.is_timer_running = record.timer_start and not record.timer_pause

    def action_timer_start(self):
        self.is_hide_start = True
        self.is_hide_stop = False
        self.is_hide_pause = False
        if not self.timer_start:
            self.write({'timer_start': fields.Datetime.now()})

    def action_timer_stop(self):
        self.is_hide_stop = True
        self.is_hide_pause = True
        self.is_hide_resume = True
        if not self.timer_start:
            return False
        minutes_spent = self._get_minutes_spent()
        self.write({'timer_start': False, 'timer_pause': False})
        self.mainte_time = minutes_spent
        return minutes_spent

    def _get_minutes_spent(self):
        start_time = self.timer_start
        stop_time = fields.Datetime.now()
        if self.timer_pause:
            start_time += (stop_time - self.timer_pause)
        return (stop_time - start_time).total_seconds() / 60

    def action_timer_pause(self):
        self.is_hide_pause = True
        self.is_hide_resume = False
        self.write({'timer_pause': fields.Datetime.now()})

    def action_timer_resume(self):
        self.is_hide_resume = True
        self.is_hide_pause= False
        if self.timer_start and self.timer_pause:
            new_start = self.timer_start + (fields.Datetime.now() - self.timer_pause)
            self.write({'timer_start': new_start, 'timer_pause': False})

    @api.model
    def get_server_time(self):
        return fields.Datetime.now()


