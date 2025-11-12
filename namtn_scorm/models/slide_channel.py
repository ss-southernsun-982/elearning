from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    nbr_scorm = fields.Integer("Number of Scorms", compute="_compute_slides_statistics", store=True)
    nbr_embedded = fields.Integer("Number of Embedded", compute="_compute_slides_statistics", store=True)

    @api.depends('slide_ids.slide_category', 'slide_ids.is_published', 'slide_ids.completion_time',
                 'slide_ids.likes', 'slide_ids.dislikes', 'slide_ids.total_views', 'slide_ids.is_category', 'slide_ids.active')
    def _compute_slides_statistics(self):
        super(SlideChannel, self)._compute_slides_statistics()

    def action_import_scorm(self):
        action = self.env.ref('namtn_scorm.action_slide_scorm_wizard').read()[0]
        action['context'] = {'default_slide_channel_id': self.id}
        return action
