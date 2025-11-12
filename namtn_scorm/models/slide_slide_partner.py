# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SlideSlidePartner(models.Model):
    _inherit = 'slide.slide.partner'

    slide_session_info_ids = fields.One2many('slide.session.info', 'slide_partner_id', 'LMS Session Info')

