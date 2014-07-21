class @Courseware
  @prefix: ''

  constructor: ->
    Courseware.prefix = $("meta[name='path_prefix']").attr('content')
    new Navigation
    Logger.bind()
    @render()

  @start: ->
    new Courseware

  render: ->
    XModule.loadModules()
    $('.course-content .histogram').each ->
      id = $(this).attr('id').replace(/histogram_/, '')
      try
        histg = new Histogram id, $(this).data('histogram')
      catch error
        histg = error
        if console?
          console.log(error)
      return histg
