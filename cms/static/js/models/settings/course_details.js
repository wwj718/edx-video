if (!CMS.Models['Settings']) CMS.Models.Settings = new Object();

CMS.Models.Settings.CourseDetails = Backbone.Model.extend({
    defaults: {
        location : null,	// the course's Location model, required
        start_date: null,	// maps to 'start'
        end_date: null,		// maps to 'end'
        enrollment_start: null,
        enrollment_end: null,
        syllabus: null,
        overview: "",
        intro_video: null,
        effort: null	// an int or null
    },

    // When init'g from html script, ensure you pass {parse: true} as an option (2nd arg to reset)
    parse: function(attributes) {
        if (attributes['course_location']) {
            attributes.location = new CMS.Models.Location(attributes.course_location, {parse:true});
        }
        if (attributes['start_date']) {
            attributes.start_date = new Date(attributes.start_date);
        }
        if (attributes['end_date']) {
            attributes.end_date = new Date(attributes.end_date);
        }
        if (attributes['enrollment_start']) {
            attributes.enrollment_start = new Date(attributes.enrollment_start);
        }
        if (attributes['enrollment_end']) {
            attributes.enrollment_end = new Date(attributes.enrollment_end);
        }
        return attributes;
    },

    validate: function(newattrs) {
        // Returns either nothing (no return call) so that validate works or an object of {field: errorstring} pairs
        // A bit funny in that the video key validation is asynchronous; so, it won't stop the validation.
        var errors = {};
        if (newattrs.start_date === null) {
            errors.start_date = gettext("The course must have an assigned start date.");
        }
        if (newattrs.start_date && newattrs.end_date && newattrs.start_date >= newattrs.end_date) {
            errors.end_date = gettext("The course end date cannot be before the course start date.");
        }
        if (newattrs.start_date && newattrs.enrollment_start && newattrs.start_date < newattrs.enrollment_start) {
            errors.enrollment_start = gettext("The course start date cannot be before the enrollment start date.");
        }
        if (newattrs.enrollment_start && newattrs.enrollment_end && newattrs.enrollment_start >= newattrs.enrollment_end) {
            errors.enrollment_end = gettext("The enrollment start date cannot be after the enrollment end date.");
        }
        if (newattrs.end_date && newattrs.enrollment_end && newattrs.end_date < newattrs.enrollment_end) {
            errors.enrollment_end = gettext("The enrollment end date cannot be after the course end date.");
        }
        if (newattrs.intro_video && newattrs.intro_video !== this.get('intro_video')) {
            // TODO check if video's url using illegal characters
            // if (this._videourl_illegal_chars.exec(newattrs.intro_video)) {
            //     errors.intro_video = "Key should only contain letters, numbers, _, or -";
            // }
        }
        if (!_.isEmpty(errors)) return errors;
        // NOTE don't return empty errors as that will be interpreted as an error state
    },

    // _videokey_illegal_chars : /[^a-zA-Z0-9_-]/g,
    set_videosource: function(newsource) {
        if (_.isEmpty(newsource) && !_.isEmpty(this.get('intro_video'))) this.set({'intro_video': null}, {validate: true});
        // TODO remove all whitespace w/in string
        else {
            if (this.get('intro_video') !== newsource) this.set('intro_video', newsource, {validate: true});
        }

        return this.videosourceSample();
    },
    videosourceSample : function() {
        if (this.has('intro_video')) return "/static/player/introvideo.html?" + this.videosourceType(this.get('intro_video')) + "&&" + this.get('intro_video');
        else return "";
    },
    videosourceType : function(videosource) {
        if (videosource.indexOf("youtube") != -1)
            return "video/youtube";
        else if (videosource.indexOf(".") != -1) {
            var pieces = videosource.split(".");
            var ext = pieces[pieces.length - 1].toLowerCase();
            if (ext == "ogv")
                return "video/ogg";
            else if (ext == "webm" || ext == "mov" || ext == "wmv" || ext == "flv" || ext == "swf")
                return "video/" + ext;
        }
        return "video/mp4";
    }
});
