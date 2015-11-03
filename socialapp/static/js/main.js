
/*
window.addEventListener("load", function() {

    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:8080/ws',
        realm: 'realm1'
    });

    connection.onopen = function (session) {

        // 1) subscribe to a topic
        function onevent(args) {
            var dict = args[0];
            console.log("args:", args[0]);
        }

        session.subscribe("SocialUserId.", onevent);
    };
    connection.open();
});
*/
$(document).on('click', '#close-preview', function(){
    $('.image-preview').popover('hide');
    // Hover befor close the preview
    $('.image-preview').hover(
        function () {
           $('.image-preview').popover('show');
        },
         function () {
           $('.image-preview').popover('hide');
        }
    );
});

$(function() {
    // Create the close button
    var closebtn = $('<button/>', {
        type:"button",
        text: 'x',
        id: 'close-preview',
        style: 'font-size: initial;',
    });
    closebtn.attr("class","close pull-right");
    // Set the popover default content
    $('.image-preview').popover({
        trigger:'manual',
        html:true,
        title: "<strong>Preview</strong>"+$(closebtn)[0].outerHTML,
        content: "There's no image",
        placement:'bottom'
    });
    // Clear event
    $('.image-preview-clear').click(function(){
        $('.image-preview').attr("data-content","").popover('hide');
        $('.image-preview-filename').val("");
        $('.image-preview-clear').hide();
        $('.image-preview-input input:file').val("");
        $(".image-preview-input-title").text("Browse");
    });
    // Create the preview image
    $(".image-preview-input input:file").change(function (){
        var img = $('<img/>', {
            id: 'dynamic',
            width:250,
            height:200
        });
        var file = this.files[0];
        var reader = new FileReader();
        // Set preview image into the popover data-content
        reader.onload = function (e) {
            $(".image-preview-input-title").text("Change");
            $(".image-preview-clear").show();
            $(".image-preview-filename").val(file.name);
            img.attr('src', e.target.result);
            $(".image-preview").attr("data-content",$(img)[0].outerHTML).popover("show");
        }
        reader.readAsDataURL(file);
    });

    $(document).on("click", ".remove_post", function(event){
        $(this).data("target").split("_")[1];
        AjaxCaller()
    });
});

AjaxCaller = function(url, data, callback)
{
    $.ajax({
        url: url,
        data: data,
        dataType: "json"
    })
    .done(function(data) {
      callback(data)
    })
    .fail(function() {
      alert("Ajax failed to fetch data")
    })
}