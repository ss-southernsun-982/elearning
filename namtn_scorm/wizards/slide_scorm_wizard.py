# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
from odoo.exceptions import UserError, ValidationError
from ..utils.scorm_parser import parse_scorm_manifest
import base64
import zipfile
import tempfile
import os
import logging
import glob
import re

_logger = logging.getLogger(__name__)


class SlideScormWizard(models.TransientModel):
    _name = 'slide.scorm.wizard'
    _description = _('SlideScormWizard')

    name = fields.Char(_('Name'))
    slide_channel_id = fields.Many2one('slide.channel', string='Slide Channel', required=True)
    scorm_file = fields.Many2many(
        'ir.attachment',
        string="SCORM Package (.zip)",
        help="Upload a SCORM 1.2 or 2004 package (ZIP file)",
        required=True
    )
    override_channel = fields.Boolean('Override channel', default=False, help='If checked, the existing channel will be overridden')

    @api.model
    def default_get(self, fields_list):
        res = super(SlideScormWizard, self).default_get(fields_list)
        return res

    def action_import_scorm(self):
        self.ensure_one()
        if not self.scorm_file:
            raise UserError(_("Please upload a SCORM package."))

        # Get first attachment (if multiple)
        attachment = self.scorm_file[0]

        if not attachment.datas or not attachment.name.endswith('.zip'):
            raise UserError(_("Please upload a valid .zip file."))

        # Physic path to file in filestore
        # zip_path = attachment._full_path(attachment.store_fname)

        # Parse manifest
        # optional if you don't want to extract scorm file
        # try:
        #     title, chapters = parse_scorm_manifest(zip_path)
        # except Exception as e:
        #     raise UserError(_("Invalid SCORM package: %s") % str(e))

        # if not title or not chapters:
        #     raise UserError(_("No valid SCO found in the SCORM package."))
        lastest_sequence = self.slide_channel_id.slide_ids[-1].sequence if self.slide_channel_id.slide_ids else 0
        index_path, index_file = self._extract_scorm_package(attachment)
        if not index_file:
            raise UserError(_("No index file found in the SCORM package."))
        chapters = []
        title = ''
        with open(index_file, 'r') as f:
            index_html = f.read()
            match_content = re.search(r'deserialize\("([^"]+)"\)', index_html)
            if match_content:
                base64_data = match_content.group(1)
                decoded = base64.b64decode(base64_data).decode('utf-8')
                data = json.loads(decoded)
                for d in data['course']['lessons']:
                    chapters.append({
                        'identifier': d['id'],
                        'title': d['title'],
                        'href': '#/lessons/%s' % d['id'],
                        'type': d['type']
                    })
            match_title = re.search(r'<title>([^<]+)</title>', index_html)
            if match_title:
                title = match_title.group(1)
        self.name = title
        result = []
        current_section = None

        for idx, sco in enumerate(chapters, 1):
            lastest_sequence += idx
            if sco['type'] == 'section':
                # when encounter a new section, create a new group
                current_section = {
                    'name': sco['title'],
                    'scorm_sco_identifier': sco['identifier'],
                    'channel_id': self.slide_channel_id.id,
                    'slide_type': 'pdf',
                    'slide_category': 'document',
                    'sequence': lastest_sequence,
                    'slide_ids': [],
                    'is_category': True,
                    'scorm_launch_url': f'{index_path}{sco['href']}',
                }
                result.append(current_section)
            elif sco['type'] == 'blocks' and current_section:
                current_section['slide_ids'].append((0,0, {
                    'name': sco['title'],
                    'scorm_sco_identifier': sco['identifier'],
                    'channel_id': self.slide_channel_id.id,
                    'slide_type': 'scorm',
                    'slide_category': 'scorm',
                    'sequence': lastest_sequence,
                    'scorm_launch_url': f'{index_path}{sco['href']}',
                }))
            elif sco['type'] == 'blocks' and not current_section:
                # if no section, add to root
                current_section = {
                    'name': title,
                    'scorm_sco_identifier': 'root',
                    'channel_id': self.slide_channel_id.id,
                    'slide_type': 'pdf',
                    'slide_category': 'document',
                    'sequence': lastest_sequence,
                    'slide_ids': [],
                    'is_category': True,
                }
                current_section['slide_ids'].append((0,0, {
                    'name': sco['title'],
                    'scorm_sco_identifier': sco['identifier'],
                    'channel_id': self.slide_channel_id.id,
                    'slide_type': 'scorm',
                    'slide_category': 'scorm',
                    'sequence': lastest_sequence,
                    'scorm_launch_url': f'{index_path}{sco['href']}',
                }))
                result.append(current_section)
        self.slide_channel_id.slide_ids = [(0, 0, slide) for slide in result]
        if self.override_channel:
            self.slide_channel_id.write({
                'name': self.name
            })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'SCORM package imported successfully.',
                'type': 'rainbow_man',
            }
        }

    def _extract_scorm_package(self, attachment):
        """Extract SCORM package and find index file"""
        self.ensure_one()

        file_name = attachment.name.replace('.zip', '')

        # Create destination folder
        base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "static", "media", "scorm", str(self.slide_channel_id.id), file_name
        )
        os.makedirs(base_path, exist_ok=True)

        # Save zip file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            tmp_zip.write(base64.b64decode(attachment.datas))
            tmp_zip.flush()
            tmp_path = tmp_zip.name

        try:
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                zip_ref.extractall(base_path)

            _logger.info("✅ SCORM package extracted successfully to %s", base_path)

            # --- Use glob to find index.*
            index_file = self._find_index_file(base_path)
            if not index_file:
                raise ValidationError(_("No index.xml or index.html found in SCORM package."))
            css_file = self._find_css_file(base_path)
            if not css_file:
                raise ValidationError(_("No css file found in SCORM package."))
            with open(css_file, 'a') as f:
                f.write("\nnav { display: none !important; }\n.continue-btn { display: none !important; }\n.lesson-nav-link { display: none !important; }\n.lesson-header__counter { display: none !important; } \n.course-navigation__sidebar--nav-open .page-wrap,.course-navigation__sidebar--search-open .page-wrap {\nbox-shadow: 0 0 4rem #0000001f;\nmargin-inline-start:0 !important;}")
            # Save relative path
            relative_index_path = os.path.relpath(index_file, base_path)
            return f"/namtn_scorm/static/media/scorm/{self.slide_channel_id.id}/{file_name}/{relative_index_path}", index_file
        except zipfile.BadZipFile:
            raise ValidationError(_("Invalid zip file. Please upload a valid SCORM package."))
        except Exception as e:
            _logger.exception("Error extracting SCORM zip: %s", e)
            raise ValidationError(_("Failed to extract SCORM package: %s") % str(e))
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def _find_index_file(self, folder_path):
        """
        use glob to find index file in SCORM folder.
        priority: index_lms.html > index.html > index.xhtml > index.xml
        """
        candidates = ["index_lms.html", "index.html", "index.xhtml", "index.xml"]

        # Create a list of patterns to search for all candidates
        all_patterns = [os.path.join(folder_path, "**", c) for c in candidates]

        for pattern in all_patterns:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]

        return None

    def _find_css_file(self, folder_path):
        """
       use glob to find css file in SCORM folder.
        """
        candidates = ["*.css"]

        # Create a list of patterns to search for all candidates
        all_patterns = [os.path.join(folder_path, "**", c) for c in candidates]

        for pattern in all_patterns:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]

        return None
