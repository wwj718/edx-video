describe 'CombinedOpenEnded', ->
  beforeEach ->
    spyOn Logger, 'log'
    # load up some fixtures
    loadFixtures 'combined-open-ended.html'
    jasmine.Clock.useMock()
    @element = $('.course-content')


  describe 'constructor', ->
    beforeEach ->
      spyOn(Collapsible, 'setCollapsibles')
      @combined = new CombinedOpenEnded @element

    it 'set the element', ->
      expect(@combined.element).toEqual @element

    it 'get the correct values from data fields', ->
      expect(@combined.ajax_url).toEqual '/courses/MITx/6.002x/2012_Fall/modx/i4x://MITx/6.002x/combinedopenended/CombinedOE'
      expect(@combined.state).toEqual 'assessing'
      expect(@combined.task_count).toEqual 2
      expect(@combined.task_number).toEqual 1

    it 'subelements are made collapsible', -> 
      expect(Collapsible.setCollapsibles).toHaveBeenCalled()


  describe 'poll', ->
    beforeEach =>
      # setup the spies
      @combined = new CombinedOpenEnded @element
      spyOn(@combined, 'reload').andCallFake -> return 0
      window.setTimeout = jasmine.createSpy().andCallFake (callback, timeout) -> return 5

    it 'polls at the correct intervals', =>
      fakeResponseContinue = state: 'not done'
      spyOn($, 'postWithPrefix').andCallFake (url, callback) -> callback(fakeResponseContinue)
      @combined.poll()
      expect(window.setTimeout).toHaveBeenCalledWith(@combined.poll, 10000)
      expect(window.queuePollerID).toBe(5)

    it 'polling stops properly', =>
      fakeResponseDone = state: "done" 
      spyOn($, 'postWithPrefix').andCallFake (url, callback) -> callback(fakeResponseDone)
      @combined.poll()
      expect(window.queuePollerID).toBeUndefined()
      expect(window.setTimeout).not.toHaveBeenCalled()

  describe 'rebind', ->
    beforeEach ->
      @combined = new CombinedOpenEnded @element
      spyOn(@combined, 'queueing').andCallFake -> return 0
      spyOn(@combined, 'skip_post_assessment').andCallFake -> return 0
      window.setTimeout = jasmine.createSpy().andCallFake (callback, timeout) -> return 5

    it 'when our child is in an assessing state', ->
      @combined.child_state = 'assessing'
      @combined.rebind()
      expect(@combined.answer_area.attr("disabled")).toBe("disabled")
      expect(@combined.submit_button.val()).toBe("Submit assessment")
      expect(@combined.queueing).toHaveBeenCalled()

    it 'when our child state is initial', -> 
      @combined.child_state = 'initial'
      @combined.rebind()
      expect(@combined.answer_area.attr("disabled")).toBeUndefined()
      expect(@combined.submit_button.val()).toBe("Submit")

    it 'when our child state is post_assessment', -> 
      @combined.child_state = 'post_assessment'
      @combined.rebind()
      expect(@combined.answer_area.attr("disabled")).toBe("disabled")
      expect(@combined.submit_button.val()).toBe("Submit post-assessment")

    it 'when our child state is done', -> 
      spyOn(@combined, 'next_problem').andCallFake ->
      @combined.child_state = 'done'
      @combined.rebind()
      expect(@combined.answer_area.attr("disabled")).toBe("disabled")
      expect(@combined.next_problem).toHaveBeenCalled()

  describe 'next_problem', ->
    beforeEach ->
      @combined = new CombinedOpenEnded @element
      @combined.child_state = 'done'

    it 'handling a successful call', ->
      fakeResponse = 
        success: true
        html: "dummy html"
        allow_reset: false
      spyOn($, 'postWithPrefix').andCallFake (url, val, callback) -> callback(fakeResponse)
      spyOn(@combined, 'reinitialize')
      spyOn(@combined, 'rebind')
      @combined.next_problem()
      expect($.postWithPrefix).toHaveBeenCalled()
      expect(@combined.reinitialize).toHaveBeenCalledWith(@combined.element)
      expect(@combined.rebind).toHaveBeenCalled()
      expect(@combined.answer_area.val()).toBe('')
      expect(@combined.child_state).toBe('initial')

    it 'handling an unsuccessful call', ->
      fakeResponse =
        success: false
        error: 'This is an error'
      spyOn($, 'postWithPrefix').andCallFake (url, val, callback) -> callback(fakeResponse)
      @combined.next_problem()
      expect(@combined.errors_area.html()).toBe(fakeResponse.error)



