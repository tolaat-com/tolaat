
$.fn.select2.defaults.set('amdLanguageBase', 'select2/i18n/');

$(document).ready(function() {

    function bind_select_by_type(root, type) {
        var t = type;
      $('#select-'+type).select2({
            language: 'he',
            escapeMarkup: function(x){return x},
            ajax: {
                url: function (params){
                    return root+'search-query/'+t+'/'+(params.term || 'Empty')+'/'+(params.page || 1);
                },
                dataType: 'json'
            }
        });
    }

    function configure_search_boxes() {
        var boxes = ['case', 'J', 'L', 'S'];
        var root = $('#config_rootpath').html();

        for(var i=0; i < boxes.length; i++)
        {
            var t = boxes[i];
            bind_select_by_type(root, t);
        }
    }

    configure_search_boxes();

     $('.js-example-basic-single2').select2({
        language: 'he', width:'resolve'});



    $('.js-example-basic-single').on('select2:select', function (e) {
        url = e.params.data.url;
        window.location.href = url;
    });



});