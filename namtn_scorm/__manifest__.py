# -*- coding: utf-8 -*-
{
    'name': 'NAMTN SCORM Integration for eLearning',
    'version': '18.0.1.0',
    'summary': "Integrate SCORM 1.2 & 2004 content into Odoo eLearning platform.",
    'description': """
NAMTN SCORM Integration for eLearning
=====================================

Enhance Odoo eLearning (Website Slides) with full SCORM 1.2 and 2004 support.

Key Features
-------------
* Upload and import SCORM packages (.zip)
* Seamless integration with Website Slides
* Track learner progress and scores
* Full-screen player mode for distraction-free learning
* Portal rating and feedback support
* Secure access rights and user management

How It Works
-------------
1. Go to eLearning → Courses.
2. Create or edit a course.
3. Use the “Upload SCORM” wizard to import SCORM content.
4. Learners can take the course directly on your website.
5. Progress and completion are automatically tracked.

Ideal For
----------
* Training organizations
* Universities and online schools
* Corporate learning systems
* Any team using SCORM materials for internal training

Technical Information
----------------------
* Dependencies: base, portal_rating, website_slides
* Odoo Version: 18.0
* License: LGPL-3
""",
    'author': 'NAMTN',
    'website': 'http://github.com/ss-southernsun-982',
    'category': 'eLearning',
    'depends': ['base', 'portal_rating', 'website_slides'],
    'data': [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/slide_channel_views.xml",
        "views/slide_slide_views.xml",
        "views/templates.xml",
        "wizards/slide_scorm_wizard.xml"
    ],
    'assets': {
        'web.assets_frontend': [
            'namtn_scorm/static/src/js/scorm_api.js',
            'namtn_scorm/static/src/js/slide_course_page.js',
            'namtn_scorm/static/src/js/slide_course_page_full_screen.js'
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/screenshot_1.png',
        'static/description/screenshot_2.png'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 0.0,  # nếu miễn phí
    'currency': 'USD',
}
