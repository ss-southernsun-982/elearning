/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_slides/js/slides_course_join";
import Fullscreen from "@website_slides/js/slides_course_fullscreen_player";
import { rpc } from "@web/core/network/rpc";
import { scormAPI, SCORM_KEY } from "./scorm_api";
import { renderToElement } from "@web/core/utils/render";

/**
 * Helper: Get the slide dict matching the given criteria
 *
 * @private
 * @param {Array<Object>} slideList List of dict reprensenting a slide
 * @param {[string] : any} matcher
 */
var findSlide = function (slideList, matcher) {
  return slideList.find((slide) => {
    return Object.keys(matcher).every((key) => matcher[key] === slide[key]);
  });
};

publicWidget.registry.preventLearningAdmin = publicWidget.Widget.extend({
  selector:
    ".o_wslides_js_slides_list_slide_link,.o_wslides_lesson_aside_list_link a,.next-slide-link",
  xmlDependencies: ["/website_slides/static/src/xml/website_slides_upload.xml"],

  init() {
    this._super(...arguments);
    this.rpc = rpc;
  },
});

var NTFLmsFullScreen = Fullscreen.include({
  selector: ".o_wslides_fs_main",

  init: function (parent, slides, defaultSlideId, channelData) {
    var result = this._super.apply(this, arguments);
    this.slides = slides;
    this.channel = channelData;
    var slide;
    const urlParams = new URL(window.location).searchParams;
    if (defaultSlideId) {
      slide = findSlide(this.slides, {
        id: defaultSlideId,
        isQuiz: String(urlParams.get("quiz")) === "1",
      });
    } else {
      slide = this.slides[0];
    }
    this._slideValue = slide;
    this.rpc = rpc;
    return result;
  },

  _preprocessSlideData: function (slidesDataList) {
    var res = this._super.apply(this, arguments);
    slidesDataList.map((slideData) => {
      if (slideData.category === "scorm") {
        slideData.embedUrl = $(slideData.embedCode).attr("src");
      }
      if (slideData.category === "embedded") {
        slideData.embedUrl = $(slideData.embedCode).attr("src");
      }
      return slideData;
    });
    return res;
  },

  _renderSlide: async function () {
    var def = this._super.apply(this, arguments);
    var $content = this.$(".o_wslides_fs_content");
    const slide = this._slideValue;
    await this.rpc("/slide/slide/get_session_info", {
      slide_id: slide.id,
    })
      .then((data) => {
        let latestChunk = data[SCORM_KEY.chunk] ?? "";
        let latestBookmark = data[SCORM_KEY.bookmark] ?? "";
        if (slide.category === "scorm") {
          let scormApi = scormAPI(
            window,
            slide.id,
            this.rpc,
            latestChunk,
            latestBookmark,
            () => {},
            () => {
              this._backToCourse();
            },
            (isCompleted) => {
              if (isCompleted) {
                slide.canSelfMarkCompleted = true;
                this._toggleSlideCompleted(slide, true);
              }
            }
          );
          window.API = scormApi;
          window.parent.API = scormApi;
          window.API_1484_11 = scormApi;
          window.parent.API_1484_11 = scormApi;
          $content.empty().append(slide.embedCode);
        }
        if (slide.category === "embedded") {
          $content.empty().append(
            renderToElement("namtn_scorm.slide_embedded_player", {
              slide: slide,
            })
          );
        }
      })
      .catch((error) => {
        console.log(error);
      });
    return Promise.all([def]);
  },
});

export default {
  NTFLmsFullScreen,
};
