## Functions

renameTag = (node, name) ->
  unless node.jquery
    node = $(node)
  node2 = $('<'+name+'/>').html node.html()
  node.replaceWith node2
  node2

## Main

Flockly.getProfile (data, status, xhr) ->
  console.log 'logged in'
, ->
  location.replace '/'

$('#search-input').on 'input', ->
  needle = new RegExp($(@).val(), 'i')
  $('#blocks ol').each (_, el) ->
    el.style.display = ''
    renameTag el, 'li'
  $('#blocks li').each (_, el) ->
    unless $('.block-name', el).text().match needle
      x = renameTag(el, 'ol')
      x[0].style.display = 'none'

blockItemTpt = Handlebars.compile $('#block-item-tpt').html()

$.getJSON '/get_blockly_list', (data) ->
  _.pluck(data, 'id').forEach (id) ->
    $('#blocks').append $('<li/>').html blockItemTpt id: id, name: 'meow', mtime: 0