CMS.Views.ShowTextbook = Backbone.View.extend({
    initialize: function() {
        this.template = _.template($("#show-textbook-tpl").text());
        this.listenTo(this.model, "change", this.render);
    },
    tagName: "section",
    className: "textbook",
    events: {
        "click .edit": "editTextbook",
        "click .delete": "confirmDelete",
        "click .show-chapters": "showChapters",
        "click .hide-chapters": "hideChapters"
    },
    render: function() {
        var attrs = $.extend({}, this.model.attributes);
        attrs.bookindex = this.model.collection.indexOf(this.model);
        attrs.course = window.section.attributes;
        this.$el.html(this.template(attrs));
        return this;
    },
    editTextbook: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.set("editing", true);
    },
    confirmDelete: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        var textbook = this.model, collection = this.model.collection;
        var msg = new CMS.Views.Prompt.Warning({
            title: _.template(gettext("Delete “<%= name %>”?"),
                {name: textbook.escape('name')}),
            message: gettext("Deleting a textbook cannot be undone and once deleted any reference to it in your courseware's navigation will also be removed."),
            actions: {
                primary: {
                    text: gettext("Delete"),
                    click: function(view) {
                        view.hide();
                        var delmsg = new CMS.Views.Notification.Mini({
                            title: gettext("Deleting") + "&hellip;"
                        }).show();
                        textbook.destroy({
                            complete: function() {
                                delmsg.hide();
                            }
                        });
                    }
                },
                secondary: {
                    text: gettext("Cancel"),
                    click: function(view) {
                        view.hide();
                    }
                }
            }
        }).show();
    },
    showChapters: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.set('showChapters', true);
    },
    hideChapters: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.set('showChapters', false);
    }
});
CMS.Views.EditTextbook = Backbone.View.extend({
    initialize: function() {
        this.template = _.template($("#edit-textbook-tpl").text());
        this.listenTo(this.model, "invalid", this.render);
        var chapters = this.model.get('chapters');
        this.listenTo(chapters, "add", this.addOne);
        this.listenTo(chapters, "reset", this.addAll);
        this.listenTo(chapters, "all", this.render);
    },
    tagName: "section",
    className: "textbook",
    render: function() {
        this.$el.html(this.template({
            name: this.model.escape('name'),
            error: this.model.validationError
        }));
        this.addAll();
        return this;
    },
    events: {
        "change input[name=textbook-name]": "setName",
        "submit": "setAndClose",
        "click .action-cancel": "cancel",
        "click .action-add-chapter": "createChapter"
    },
    addOne: function(chapter) {
        var view = new CMS.Views.EditChapter({model: chapter});
        this.$("ol.chapters").append(view.render().el);
        return this;
    },
    addAll: function() {
        this.model.get('chapters').each(this.addOne, this);
    },
    createChapter: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.setValues();
        this.model.get('chapters').add([{}]);
    },
    setName: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.set("name", this.$("#textbook-name-input").val(), {silent: true});
    },
    setValues: function() {
        this.setName();
        var that = this;
        _.each(this.$("li"), function(li, i) {
            var chapter = that.model.get('chapters').at(i);
            if(!chapter) { return; }
            chapter.set({
                "name": $(".chapter-name", li).val(),
                "asset_path": $(".chapter-asset-path", li).val()
            });
        });
        return this;
    },
    setAndClose: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.setValues();
        if(!this.model.isValid()) { return; }
        var saving = new CMS.Views.Notification.Mini({
            title: gettext("Saving") + "&hellip;"
        }).show();
        var that = this;
        this.model.save({}, {
            success: function() {
                that.model.setOriginalAttributes();
                that.close();
            },
            complete: function() {
                saving.hide();
            }
        });
    },
    cancel: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.reset();
        return this.close();
    },
    close: function() {
        var textbooks = this.model.collection;
        this.remove();
        if(this.model.isNew()) {
            // if the textbook has never been saved, remove it
            textbooks.remove(this.model);
        }
        // don't forget to tell the model that it's no longer being edited
        this.model.set("editing", false);
        return this;
    }
});
CMS.Views.ListTextbooks = Backbone.View.extend({
    initialize: function() {
        this.emptyTemplate = _.template($("#no-textbooks-tpl").text());
        this.listenTo(this.collection, 'all', this.render);
        this.listenTo(this.collection, 'destroy', this.handleDestroy);
    },
    tagName: "div",
    className: "textbooks-list",
    render: function() {
        var textbooks = this.collection;
        if(textbooks.length === 0) {
            this.$el.html(this.emptyTemplate());
        } else {
            this.$el.empty();
            var that = this;
            textbooks.each(function(textbook) {
                var view;
                if (textbook.get("editing")) {
                    view = new CMS.Views.EditTextbook({model: textbook});
                } else {
                    view = new CMS.Views.ShowTextbook({model: textbook});
                }
                that.$el.append(view.render().el);
            });
        }
        return this;
    },
    events: {
        "click .new-button": "addOne"
    },
    addOne: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.collection.add([{editing: true}]);
    },
    handleDestroy: function(model, collection, options) {
        collection.remove(model);
    }
});
CMS.Views.EditChapter = Backbone.View.extend({
    initialize: function() {
        this.template = _.template($("#edit-chapter-tpl").text());
        this.listenTo(this.model, "change", this.render);
    },
    tagName: "li",
    className: function() {
        return "field-group chapter chapter" + this.model.get('order');
    },
    render: function() {
        this.$el.html(this.template({
            name: this.model.escape('name'),
            asset_path: this.model.escape('asset_path'),
            order: this.model.get('order'),
            error: this.model.validationError
        }));
        return this;
    },
    events: {
        "change .chapter-name": "changeName",
        "change .chapter-asset-path": "changeAssetPath",
        "click .action-close": "removeChapter",
        "click .action-upload": "openUploadDialog",
        "submit": "uploadAsset"
    },
    changeName: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.set({
            name: this.$(".chapter-name").val()
        }, {silent: true});
        return this;
    },
    changeAssetPath: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.set({
            asset_path: this.$(".chapter-asset-path").val()
        }, {silent: true});
        return this;
    },
    removeChapter: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.collection.remove(this.model);
        return this.remove();
    },
    openUploadDialog: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.model.set({
            name: this.$("input.chapter-name").val(),
            asset_path: this.$("input.chapter-asset-path").val()
        });
        var msg = new CMS.Models.FileUpload({
            title: _.template(gettext("Upload a new PDF to “<%= name %>”"),
                {name: section.escape('name')}),
            message: "Files must be in PDF format."
        });
        var view = new CMS.Views.UploadDialog({model: msg, chapter: this.model});
        $(".wrapper-view").after(view.show().el);
    }
});

CMS.Views.UploadDialog = Backbone.View.extend({
    options: {
        shown: true,
        successMessageTimeout: 2000 // 2 seconds
    },
    initialize: function() {
        this.template = _.template($("#upload-dialog-tpl").text());
        this.listenTo(this.model, "change", this.render);
    },
    render: function() {
        var isValid = this.model.isValid();
        var selectedFile = this.model.get('selectedFile');
        var oldInput = this.$("input[type=file]").get(0);
        this.$el.html(this.template({
            shown: this.options.shown,
            url: CMS.URL.UPLOAD_ASSET,
            title: this.model.escape('title'),
            message: this.model.escape('message'),
            selectedFile: selectedFile,
            uploading: this.model.get('uploading'),
            uploadedBytes: this.model.get('uploadedBytes'),
            totalBytes: this.model.get('totalBytes'),
            finished: this.model.get('finished'),
            error: this.model.validationError
        }));
        // Ideally, we'd like to tell the browser to pre-populate the
        // <input type="file"> with the selectedFile if we have one -- but
        // browser security prohibits that. So instead, we'll swap out the
        // new input (that has no file selected) with the old input (that
        // already has the selectedFile selected). However, we only want to do
        // this if the selected file is valid: if it isn't, we want to render
        // a blank input to prompt the user to upload a different (valid) file.
        if (selectedFile && isValid) {
            $(oldInput).removeClass("error");
            this.$('input[type=file]').replaceWith(oldInput);
        }
        return this;
    },
    events: {
        "change input[type=file]": "selectFile",
        "click .action-cancel": "hideAndRemove",
        "click .action-upload": "upload"
    },
    selectFile: function(e) {
        this.model.set({
            selectedFile: e.target.files[0] || null
        });
    },
    show: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.options.shown = true;
        $body.addClass('dialog-is-shown');
        return this.render();
    },
    hide: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        this.options.shown = false;
        $body.removeClass('dialog-is-shown');
        return this.render();
    },
    hideAndRemove: function(e) {
        if(e && e.preventDefault) { e.preventDefault(); }
        return this.hide().remove();
    },
    upload: function(e) {
        this.model.set('uploading', true);
        this.$("form").ajaxSubmit({
            success: _.bind(this.success, this),
            error: _.bind(this.error, this),
            uploadProgress: _.bind(this.progress, this),
            data: {
                // don't show the generic error notification; we're in a modal,
                // and we're better off modifying it instead.
                notifyOnError: false
            }
        });
    },
    progress: function(event, position, total, percentComplete) {
        this.model.set({
            "uploadedBytes": position,
            "totalBytes": total
        });
    },
    success: function(response, statusText, xhr, form) {
        this.model.set({
            uploading: false,
            finished: true
        });
        var chapter = this.options.chapter;
        if(chapter) {
            var options = {};
            if(!chapter.get("name")) {
                options.name = response.displayname;
            }
            options.asset_path = response.url;
            chapter.set(options);
        }
        var that = this;
        this.removalTimeout = setTimeout(function() {
            that.hide().remove();
        }, this.options.successMessageTimeout);
    },
    error: function() {
        this.model.set({
            "uploading": false,
            "uploadedBytes": 0,
            "title": gettext("We're sorry, there was an error")
        });
    }
});
