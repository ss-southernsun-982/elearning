# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_profile.controllers.main import WebsiteProfile
import werkzeug
from odoo.exceptions import AccessError

def handle_wslide_error(exception):
    if isinstance(exception, AccessError):
        return request.redirect("/slides?invite_error=no_rights", 302)

class WebsiteSlidesScorm(WebsiteProfile):

    @http.route('/slide/slide/set_session_info', type='json', auth="user", website=True)
    def _set_session_info(self, slide_id, element, value):
        slide_partner_sudo = request.env['slide.slide.partner'].sudo()
        slide_id = request.env['slide.slide'].browse(slide_id)
        slide_partner_id = slide_partner_sudo.search([
            ('slide_id', '=', slide_id.id),
            ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        if not slide_partner_id:
            slide_partner_id = slide_partner_sudo.create({
                'slide_id': slide_id.id,
                'channel_id': slide_id.channel_id.id,
                'partner_id': request.env.user.partner_id.id
            })
        session_element_id = slide_partner_id.slide_session_info_ids.filtered(lambda l: l.name == element)
        if session_element_id:
            session_element_id.value = value
        else:
            request.env['slide.session.info'].create({
                'name': element,
                'value': value,
                'slide_partner_id': slide_partner_id.id
            })

    @http.route('/slide/slide/get_session_info', type='json', auth="user", website=True)
    def _get_session_info(self, slide_id):
        slide_partner_sudo = request.env['slide.slide.partner'].sudo()
        slide_id = request.env['slide.slide'].browse(slide_id)
        slide_partner_id = slide_partner_sudo.search([
            ('slide_id', '=', slide_id.id),
            ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        session_info_ids = request.env['slide.session.info'].search([
            ('slide_partner_id', '=', slide_partner_id.id)
        ])
        values = {}
        for session_info in session_info_ids:
            values[session_info.name] = session_info.value
        return values

    def _fetch_slide(self, slide_id):
        slide = request.env['slide.slide'].browse(int(slide_id)).exists()
        if not slide:
            return {'error': 'slide_wrong'}
        if not slide.has_access('read'):
            return {'error': 'slide_access'}
        return {'slide': slide}

    @http.route('/slides/slide/set_completed', website=True, type="json", auth="public")
    def slide_set_completed(self, slide_id):
        if request.website.is_public_user():
            return {'error': 'public_user'}
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            return fetch_res
        self._slide_mark_completed(fetch_res['slide'])
        next_category = fetch_res['slide']._get_next_category()
        return {
            'channel_completion': fetch_res['slide'].channel_id.completion,
            'next_category_id': next_category.id if next_category else False,
        }

    @http.route('/slides/slide/<model("slide.slide"):slide>', type='http', auth="public",
                website=True, sitemap=True, handle_params_access_error=handle_wslide_error)
    def slide_view(self, slide, **kwargs):
        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()
        # redirection to channel's homepage for category slides
        if slide.is_category:
            return request.redirect(slide.channel_id.website_url)

        if slide.can_self_mark_completed and not slide.user_has_completed \
           and slide.channel_id.channel_type == 'training' and slide.slide_category != 'video' \
           and slide.slide_category != 'scorm':
            self._slide_mark_completed(slide)
            next_category_to_open = slide._get_next_category()
        else:
            self._set_viewed_slide(slide)
            next_category_to_open = False

        values = self._get_slide_detail(slide)
        # quiz-specific: update with karma and quiz information
        if slide.question_ids:
            values.update(self._get_slide_quiz_data(slide))
        # sidebar: update with user channel progress
        values['channel_progress'] = self._get_channel_progress(slide.channel_id, include_quiz=True)
        # sidebar: auto-collapsed the categories depending on conditions
        values['category_data'] = self._prepare_collapsed_categories(values['category_data'], slide, next_category_to_open)

        # Allows to have breadcrumb for the previously used filter
        values.update({
            'search_category': slide.category_id if kwargs.get('search_category') else None,
            'search_tag': request.env['slide.tag'].browse(int(kwargs.get('search_tag'))) if kwargs.get('search_tag') else None,
            'slide_categories': dict(request.env['slide.slide']._fields['slide_category']._description_selection(request.env)) if kwargs.get('search_slide_category') else None,
            'search_slide_category': kwargs.get('search_slide_category'),
            'search_uncategorized': kwargs.get('search_uncategorized'),
        })

        values['channel'] = slide.channel_id
        values = self._prepare_additional_channel_values(values, **kwargs)
        values['signup_allowed'] = request.env['res.users'].sudo()._get_signup_invitation_scope() == 'b2c'

        if kwargs.get('fullscreen') == '1':
            values.update(self._slide_channel_prepare_review_values(slide.channel_id))
            return request.render("website_slides.slide_fullscreen", values)

        values.pop('channel', None)
        return request.render("website_slides.slide_main", values)