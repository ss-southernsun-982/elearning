/** @odoo-module **/

import { SlideCoursePage } from "@website_slides/js/slides_course_page";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

import { _t } from "@web/core/l10n/translation";

import { scormAPI, SCORM_KEY } from "./scorm_api";

SlideCoursePage.prototype._onClickComplete = function (ev) {
  ev.stopPropagation();
  ev.preventDefault();
  return;
};

publicWidget.registry.SlideScorm = SlideCoursePage.extend({
  selector: ".o_wslides_lesson_main",

  init: function () {
    this._super.apply(this, arguments);
    this.rpc = rpc;
  },

  /**
   * @override
   */
  start: function () {
    const res = this._super(...arguments);
    var self = this;
    var slideId = parseInt(
      $(".o_wslides_lesson_aside_list_link.active").data("id")
    );
    const slide = $(
      `.o_wslides_sidebar_done_button[data-id="${slideId}"]`
    ).data();
    const slideIframe = $("#iframe_src").data();
    if (slide && slideIframe && slideIframe.slideCategory === "scorm") {
      this.rpc("/slide/slide/get_session_info", {
        slide_id: slide.id,
      }).then((data) => {
        let latestChunk = data[SCORM_KEY.chunk];
        let latestBookmark = data[SCORM_KEY.bookmark];
        let scormApi = scormAPI(
          window,
          slide.id,
          this.rpc,
          latestChunk,
          latestBookmark,
          () => {},
          () => {},
          (isCompleted) => {
            if (isCompleted) {
              self._toggleSlideCompleted(slide, true);
            }
          }
        );
        window.API = scormApi;
        window.parent.API = scormApi;
        window.API_1484_11 = scormApi;
        window.parent.API_1484_11 = scormApi;
        $("#scorm_content").append($("#iframe_src").attr("value"));
        $("#iframe_src").remove();
      });
    }
    return res;
  },
});

export default publicWidget.registry.SlideScorm;
