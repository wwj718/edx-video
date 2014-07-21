describe "CMS.Views.SectionShow", ->
    describe "Basic", ->
        beforeEach ->
            spyOn(CMS.Views.SectionShow.prototype, "switchToEditView")
                .andCallThrough()
            @model = new CMS.Models.Section({
                id: 42
                name: "Life, the Universe, and Everything"
            })
            @view = new CMS.Views.SectionShow({model: @model})
            @view.render()

        it "should contain the model name", ->
            expect(@view.$el).toHaveText(@model.get('name'))

        it "should call switchToEditView when clicked", ->
            @view.$el.click()
            expect(@view.switchToEditView).toHaveBeenCalled()

        it "should pass the same element to SectionEdit when switching views", ->
            spyOn(CMS.Views.SectionEdit.prototype, 'initialize').andCallThrough()
            @view.switchToEditView()
            expect(CMS.Views.SectionEdit.prototype.initialize).toHaveBeenCalled()
            expect(CMS.Views.SectionEdit.prototype.initialize.mostRecentCall.args[0].el).toEqual(@view.el)

describe "CMS.Views.SectionEdit", ->
    describe "Basic", ->
        tpl = readFixtures('section-name-edit.underscore')
        feedback_tpl = readFixtures('system-feedback.underscore')

        beforeEach ->
            setFixtures($("<script>", {id: "section-name-edit-tpl", type: "text/template"}).text(tpl))
            appendSetFixtures($("<script>", {id: "system-feedback-tpl", type: "text/template"}).text(feedback_tpl))
            spyOn(CMS.Views.SectionEdit.prototype, "switchToShowView")
                .andCallThrough()
            spyOn(CMS.Views.SectionEdit.prototype, "showInvalidMessage")
                .andCallThrough()
            window.analytics = jasmine.createSpyObj('analytics', ['track'])
            window.course_location_analytics = jasmine.createSpy()
            @requests = requests = []
            @xhr = sinon.useFakeXMLHttpRequest()
            @xhr.onCreate = (xhr) -> requests.push(xhr)

            @model = new CMS.Models.Section({
                id: 42
                name: "Life, the Universe, and Everything"
            })
            @view = new CMS.Views.SectionEdit({model: @model})
            @view.render()

        afterEach ->
            @xhr.restore()
            delete window.analytics
            delete window.course_location_analytics

        it "should have the model name as the default text value", ->
            expect(@view.$("input[type=text]").val()).toEqual(@model.get('name'))

        it "should call switchToShowView when cancel button is clicked", ->
            @view.$("input.cancel-button").click()
            expect(@view.switchToShowView).toHaveBeenCalled()

        it "should save model when save button is clicked", ->
            spyOn(@model, 'save')
            @view.$("input[type=submit]").click()
            expect(@model.save).toHaveBeenCalled()

        it "should call switchToShowView when save() is successful", ->
            @view.$("input[type=submit]").click()
            @requests[0].respond(200)
            expect(@view.switchToShowView).toHaveBeenCalled()

        it "should call showInvalidMessage when validation is unsuccessful", ->
            spyOn(@model, 'validate').andReturn("BLARRGH")
            @view.$("input[type=submit]").click()
            expect(@view.showInvalidMessage).toHaveBeenCalledWith(
                jasmine.any(Object), "BLARRGH", jasmine.any(Object))
            expect(@view.switchToShowView).not.toHaveBeenCalled()

        it "should not save when validation is unsuccessful", ->
            spyOn(@model, 'validate').andReturn("BLARRGH")
            @view.$("input[type=text]").val("changed")
            @view.$("input[type=submit]").click()
            expect(@model.get('name')).not.toEqual("changed")

