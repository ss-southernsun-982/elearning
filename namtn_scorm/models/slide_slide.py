from odoo import models, fields, api, _
from markupsafe import Markup

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    slide_category = fields.Selection(
        selection_add=[('scorm', 'Scorm'),('embedded', 'Embedded')], ondelete={'scorm': 'set default', 'embedded': 'set default'})
    slide_type = fields.Selection(
        selection_add=[('scorm', 'Scorm'), ('embedded', 'Embedded')], ondelete={'scorm': 'set null', 'embedded': 'set null'}, compute="_compute_slide_type", store=True)
    scorm_sco_identifier = fields.Char("SCORM SCO ID")
    scorm_launch_url = fields.Char("Launch URL")
    embed_url = fields.Char("Embed URL")
    nbr_scorm = fields.Integer("Number of Scorms", compute="_compute_slides_statistics", store=True)
    nbr_embedded = fields.Integer("Number of Embedded", compute="_compute_slides_statistics", store=True)
    embed_code = fields.Html('Embed Code', readonly=True, compute='_compute_embed_code')
    embed_code_external = fields.Html('External Embed Code', readonly=True, compute='_compute_embed_code')

    @api.constrains('channel_id', 'slide_category', 'scorm_sco_identifier')
    def _check_scorm_sco_identifier(self):
        for slide in self:
            if slide.slide_category == 'scorm':
                if not slide.scorm_sco_identifier:
                    raise ValueError("Missing scorm_sco_identifier")
                if not slide.scorm_launch_url:
                    raise ValueError("Missing scorm_launch_url")
                if slide.channel_id.slide_ids.filtered(lambda s: s.scorm_sco_identifier == slide.scorm_sco_identifier and s.id != slide.id):
                    raise ValueError("Duplicate scorm_sco_identifier")

    @api.depends('slide_category', 'source_type', 'video_source_type')
    def _compute_slide_type(self):
        res = super(SlideSlide, self)._compute_slide_type()
        for slide in self:
            if slide.slide_category == 'scorm':
                slide.slide_type = 'scorm'
            elif slide.slide_category == 'embedded':
                slide.slide_type = 'embedded'
        return res

    @api.depends('slide_ids.sequence', 'slide_ids.slide_category', 'slide_ids.is_published', 'slide_ids.is_category')
    def _compute_slides_statistics(self):
        super(SlideSlide, self)._compute_slides_statistics()

    @api.depends('slide_category', 'question_ids', 'channel_id.is_member')
    @api.depends_context('uid')
    def _compute_mark_complete_actions(self):
        super(SlideSlide, self)._compute_mark_complete_actions()

    @api.depends('slide_type')
    def _compute_slide_icon_class(self):
        slide = self.filtered(lambda slide: slide.slide_type == 'scorm')
        slide.slide_icon_class = 'fa-file-archive-o'
        super(SlideSlide, self - slide)._compute_slide_icon_class()

    @api.depends('slide_category', 'google_drive_id', 'video_source_type', 'youtube_id')
    def _compute_embed_code(self):
        for rec in self:
            super(SlideSlide, rec)._compute_embed_code()
            try:
                if rec.slide_category == 'scorm':
                    rec.embed_code = Markup('<div class="player ratio ratio-16x9 embed-responsive-item h-100"><iframe src="%s" frameborder="0"  aria-label="%s"  allowFullScreen="true" frameborder="0"></iframe></div>') % (rec.scorm_launch_url, _('Scorm'))
                    rec.embed_code_external = Markup('<iframe src="%s" frameborder="0"  aria-label="%s"></iframe>') % (rec.scorm_launch_url, _('Scorm'))
            except Exception as e:
                if rec.slide_category  == 'scorm':
                    rec.embed_code = Markup(' <div class="player ratio ratio-16x9 embed-responsive-item h-100"><iframe src="%s" frameborder="0"  allowFullScreen="true" frameborder="0"></iframe></div>') % (rec.scorm_launch_url)
                    rec.embed_code_external = Markup('<iframe src="%s" aria-label="%s"></iframe>') % (rec.scorm_launch_url, _('Scorm'))

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('slide_category') == 'scorm':
                if not val.get('scorm_sco_identifier'):
                    raise ValueError("Missing scorm_sco_identifier")
                if not val.get('scorm_launch_url'):
                    raise ValueError("Missing scorm_launch_url")
        return super().create(vals)

