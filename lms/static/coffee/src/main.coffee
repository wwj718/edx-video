AjaxPrefix.addAjaxPrefix(jQuery, -> Courseware.prefix)

$ ->
  $.ajaxSetup
    headers : { 'X-CSRFToken': $.cookie 'csrftoken' }
    dataType: 'json'

  window.onTouchBasedDevice = ->
    navigator.userAgent.match /iPhone|iPod|iPad/i

  $('body').addClass 'touch-based-device' if onTouchBasedDevice()

  # $("a[rel*=leanModal]").leanModal()
  $('#csrfmiddlewaretoken').attr 'value', $.cookie('csrftoken')

  new Calculator
  new FeedbackForm
  if $('body').hasClass('courseware')
    Courseware.start()

  # Preserved for backward compatibility
  window.submit_circuit = (circuit_id) ->
    $("input.schematic").each (index, el) ->
      el.schematic.update_value()

    schematic_value $("#schematic_#{circuit_id}").attr("value")
    $.postWithPrefix "/save_circuit/#{circuit_id}", schematic: schematic_value, (data) ->
      alert('Saved') if data.results == 'success'

  window.postJSON = (url, data, callback) ->
    $.postWithPrefix url, data, callback

  $('#login').click ->
    $('#login_form input[name="email"]').focus()
    _gaq.push(['_trackPageview', '/login'])
    false

  $('#signup').click ->
    $('#signup-modal input[name="email"]').focus()
    _gaq.push(['_trackPageview', '/signup'])
    false

  # fix for ie
  if !Array::indexOf
  	Array::indexOf = (obj, start = 0) ->
  		for ele, i in this[start..]
            if ele is obj
                return i + start
        return -1
