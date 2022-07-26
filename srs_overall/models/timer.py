# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PropertyMainInherit(models.Model):
    _inherit = 'property.maintanance'

    # display_timesheet_timer = fields.Boolean("Display Timesheet Time", compute='_compute_display_timesheet_timer')

    display_timer_start_secondary = fields.Boolean(compute='_compute_display_timer_buttons')

    timer_start = fields.Datetime("Timer Start")
    timer_pause = fields.Datetime("Timer Last Pause")
    is_timer_running = fields.Boolean(compute="_compute_is_timer_running")
    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    user_id = fields.Many2one('res.users')

    @api.depends('timer_start', 'timer_pause')
    # @api.depends('display_timesheet_timer', 'timer_start', 'timer_pause', 'total_hours_spent')
    def _compute_display_timer_buttons(self):
        for task in self:
            if not task.display_timesheet_timer:
                task.update({
                    'display_timer_start_primary': False,
                    'display_timer_start_secondary': False,
                    'display_timer_stop': False,
                    'display_timer_pause': False,
                    'display_timer_resume': False,
                })
            else:
                super(PropertyMainInherit, task)._compute_display_timer_buttons()
                task.display_timer_start_secondary = task.display_timer_start_primary
                if not task.timer_start:
                    task.update({
                        'display_timer_stop': False,
                        'display_timer_pause': False,
                        'display_timer_resume': False,
                    })
                    # if not task.total_hours_spent:
                    #     task.display_timer_start_secondary = False
                    # else:
                    #     task.display_timer_start_primary = False

    # @api.depends('allow_timesheets', 'project_id.allow_timesheet_timer', 'analytic_account_active')
    # def _compute_display_timesheet_timer(self):
    #     for task in self:
    #         task.display_timesheet_timer = task.allow_timesheets and task.project_id.allow_timesheet_timer and task.analytic_account_active

    def action_timer_start(self):
        if not self.user_timer_id.timer_start and self.display_timesheet_timer:
            super(PropertyMainInherit, self).action_timer_start()

    def action_timer_stop(self):
        # timer was either running or paused
        if self.user_timer_id.timer_start and self.display_timesheet_timer:
            minutes_spent = self.user_timer_id._get_minutes_spent()
            minimum_duration = int(self.env['ir.config_parameter'].sudo().get_param('hr_timesheet.timesheet_min_duration', 0))
            rounding = int(self.env['ir.config_parameter'].sudo().get_param('hr_timesheet.timesheet_rounding', 0))
            minutes_spent = self._timer_rounding(minutes_spent, minimum_duration, rounding)
            return self._action_open_new_timesheet(minutes_spent * 60 / 3600)
        return False
