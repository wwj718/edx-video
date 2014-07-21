class @WrapperDescriptor extends XModule.Descriptor
  constructor: (@element) ->
    console.log 'WrapperDescriptor'
    @$items = $(@element).find(".vert-mod")
    @$items.sortable(
      update: (event, ui) => @update()
    )

  save: ->
    children: $('.vert-mod li', @element).map((idx, el) -> $(el).data('id')).toArray()
