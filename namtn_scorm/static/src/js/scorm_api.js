/** @odoo-module **/

const SCORM_KEY = {
  bookmark: "BOOKMARK",
  chunk: "CHUNK",
};
const scormAPI = function (
  window,
  slideId,
  rpc,
  latestChunk,
  latestBookmark,
  setReachedEndCallback,
  onExitCourseCallback,
  setSlideComplete
) {
  let recordMultipleChoices = [];
  window.parent.INTERACTION_RESULT_CORRECT = true;
  window.parent.INTERACTION_RESULT_WRONG = false;
  window.INTERACTION_RESULT_CORRECT = true;
  window.INTERACTION_RESULT_WRONG = false;
  window.CommitData = function () {
    console.log("Full Screen Commit data");
  };
  window.ConcedeControl = function () {
    console.log("Full Screen Concede Control");
    onExitCourseCallback();
    // #TODO: Finish to cource or next slide
    // Thoát cources => quay về màn hình danh sách khoá học
  };
  window.CreateResponseIdentifier = function (strShort, strLong) {
    console.log("Full Screen Create Response Identifier: ", strLong, strShort);
  };
  window.Finish = function () {
    console.log("Full Screen Finised");
  };
  window.GetStatus = function () {
    console.log("Full Screen Get statuss");
  };
  window.MatchingResponse = function (source, target) {
    console.log("Full Screen Matching Resource Target:", source, target);
  };
  window.RecordFillInInteraction = function (
    strID,
    strResponse,
    blnCorrect,
    strCorrectResponse,
    strDescription,
    intWeighting,
    intLatency,
    strLearningObjectiveID
  ) {
    console.log(
      "Record Fill In Interaction:",
      strID,
      strResponse,
      blnCorrect,
      strCorrectResponse,
      strDescription,
      intWeighting,
      intLatency,
      strLearningObjectiveID
    );
  };
  window.RecordMatchingInteraction = function (
    strID,
    aryResponse,
    blnCorrect,
    aryCorrectResponse,
    strDescription,
    intWeighting,
    intLatency,
    strLearningObjectiveID
  ) {
    console.log(
      "Record Matching Interaction",
      strID,
      aryResponse,
      blnCorrect,
      aryCorrectResponse,
      strDescription,
      intWeighting,
      intLatency,
      strLearningObjectiveID
    );
  };
  window.RecordMultipleChoiceInteraction = function (
    strID,
    aryResponse,
    blnCorrect,
    aryCorrectResponse,
    strDescription,
    intWeighting,
    intLatency,
    strLearningObjectiveID
  ) {
    console.log(
      "Record Multiple Choice Interaction",
      "strID",
      strID,
      "aryResponse",
      aryResponse,
      "blnCorrect",
      blnCorrect,
      "aryCorrectResponse",
      aryCorrectResponse,
      "strDescription",
      strDescription,
      "intWeighting",
      intWeighting,
      "intLatency",
      intLatency,
      "strLearningObjectiveID",
      strLearningObjectiveID
    );
    recordMultipleChoices.push({
      id: strID,
      correct: blnCorrect,
      title: strDescription,
    });
  };
  window.ResetStatus = function () {
    console.log("Full Screen Reset status");
  };
  window.SetBookmark = function (strBookmark, strDesc) {
    return rpc("/slide/slide/set_session_info", {
      slide_id: slideId,
      element: SCORM_KEY.bookmark,
      value: strBookmark,
    });
  };
  if (latestBookmark) {
    window.GetBookmark = () => {
      return latestBookmark;
    };
  }
  window.SetDataChunk = function (chunk) {
    if (chunk) {
      const obj = JSON.parse(chunk);
      const decoded = lzwDecompress(obj.d);
      const jsonDecode = JSON.parse(decoded);
      const lessons = jsonDecode.progress.lessons;
      const lessonKey = Object.keys(lessons)[0];
      const items = lessons[lessonKey].i || {};

      const itemKeys = Object.keys(items);
      if (itemKeys.length > 1) {
        const lastKey = itemKeys[itemKeys.length - 2];
        const lastItem = items[lastKey];
        const lastCompleted = lastItem.c === 1 ? true : false;
        setSlideComplete(lastCompleted);
      } else {
        setSlideComplete(true);
      }
      return rpc("/slide/slide/set_session_info", {
        slide_id: slideId,
        element: SCORM_KEY.chunk,
        value: chunk,
      });
    }
  };
  window.GetDataChunk = () => {
    // console.log("GET CHUNK.....", latestChunk);
    return latestChunk || "{}";
  };
  window.SetFailed = function () {
    console.log("Full Screen Set failure");
  };
  window.SetPassed = function () {
    console.log("Full Screen Set passed");
    // nextSlide();
  };
  window.SetReachedEnd = function () {
    console.log("Full Screen Set reached End");
    // setReachedEndCallback();
  };
  window.SetScore = function (intScore, intMaxScore, intMinScore) {
    console.log("Full Screen Set score", intScore, intMaxScore, intMinScore);
  };
  window.WriteToDebug = function (strInfo) {
    console.log("Full Screen Write Debug", strInfo);
  };
  window.SetObjectiveStatus = function (strObjectiveID, Lesson_Status) {
    console.log(
      "Full Screen Set Objective Status",
      strObjectiveID,
      Lesson_Status
    );
  };
  window.GetObjectStatus = function (strObjectiveID) {
    console.log("Full Screen Get Objective Status", strObjectiveID);
  };
  window.parent.IsLmsPresent = function () {
    return true;
  };
  window.IsLmsPresent = function () {
    return true;
  };
  window.GetStudentID = function () {
    return "student_id";
  };
  window.SetLanguagePreference = function (strLanguage) {
    console.log("Full Screen Set Language Preference", strLanguage);
  };
  window.SetValue = function (element, value) {
    console.log("Full Screen Set Value", element, value);
  };
  window.LMSSetValue = function (element, value) {
    console.log("Full Screen Set Value", element, value);
  };
  window.LMSGetValue = function LMSGetValue(varname) {
    console.log("LMSGetValue: " + varname);
    //invokeCSharp("LMSGetValue: " + varname);
    return "";
  };
  window.LMSSetValue = function LMSSetValue(varname, varvalue) {
    console.log("LMSSetValue: " + varname + "=" + varvalue);
    // invokeCSharp("LMSSetValue: " + varname + "=" + varvalue);
    // return "";
  };
};

function lzwDecompress(compressed) {
  let dict = {};
  let data = [];
  let currChar = String.fromCharCode(compressed[0]);
  let oldPhrase = currChar;
  let out = [currChar];
  let code = 256;
  let phrase;

  for (let i = 1; i < compressed.length; i++) {
    let currCode = compressed[i];
    if (currCode < 256) {
      phrase = String.fromCharCode(compressed[i]);
    } else {
      phrase = dict[currCode] ? dict[currCode] : oldPhrase + currChar;
    }
    out.push(phrase);
    currChar = phrase.charAt(0);
    dict[code] = oldPhrase + currChar;
    code++;
    oldPhrase = phrase;
  }
  return out.join("");
}

export { scormAPI, SCORM_KEY };
