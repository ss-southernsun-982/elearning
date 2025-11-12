# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SlideSessionInfo(models.Model):
    _name = 'slide.session.info'
    _description = 'SlideSessionInfo'

    name = fields.Char("Name")
    value = fields.Char("Value")
    slide_partner_id = fields.Many2one('slide.slide.partner')
