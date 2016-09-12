function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // $& means the whole matched string
}

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(escapeRegExp(search), 'g'), replacement);
};

$().ready(() => {
  var convert = (string, counter) => {
    return string.replaceAll("$$ i $$", counter);
  };

  var createPeopleEntries = (numPeople) => {
    var template = $('#personCollectionTemplate').html();
    var colSize = Math.floor(12 / numPeople);
    console.log(colSize);
    $('#personCollectionRow').html(''); // clear existing html

    var wrappedHTML = template +'</div>';
    var wrappedHTMLOffset = '<div class="col-xs-offset-' +
                            Math.floor((12 - (colSize * numPeople)) / 2) +
                            ' col-xs-'+ colSize + '">' +
                            wrappedHTML;
    wrappedHTML = '<div class="col-xs-' + colSize + '">' + wrappedHTML;

    // if unbalanced col size, need offset for first col
    if (colSize * numPeople != 12) {
      $('#personCollectionRow').append(convert(wrappedHTMLOffset, 1));
    } else {
      $('#personCollectionRow').append(convert(wrappedHTML, 1));
    }
    for (var i = 2; i <= numPeople; i++) {
      $('#personCollectionRow').append(convert(wrappedHTML, i));
    }
  };

  createPeopleEntries(parseInt($('#numPeople').val())); // once on load

  // bind value change to update
  $('#numPeople').change(() => {
    var val = parseInt($('#numPeople').val());
    if (val < 1)
      val = 1;
    if (val > 12)
      val = 12;
    createPeopleEntries(val);
  });
});