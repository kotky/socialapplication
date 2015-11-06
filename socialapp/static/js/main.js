
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
_baseUrl = "http://127.0.0.1:8000"
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
    ImagePreviewPostInputInitialize();
    SetAjaxEvents();
    SetWebSockets();

});
ImagePreviewPostInputInitialize = function()
{
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
}
SetAjaxEvents = function()
{
    $(document).on("click", ".remove_button", function(event){
        var url = _baseUrl+$(this).attr("data-url");
        AjaxCaller(url,null,RemoveElement );
    });
    $(document).on("click", ".like_button", function(event){
        var url = _baseUrl+$(this).attr("data-url");
        AjaxCaller(url,null,ParseLikeResonse );
    });
    $(document).on("click", ".add_friend", function(event){
        var url = _baseUrl+$(this).attr("data-url");
        AjaxCaller(url,null,ManageFriend );
    });

}
SetWebSockets = function()
{
    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:8080/ws',
        realm: 'realm1'
    });

    connection.onopen = function (session) {

        // 1) subscribe to a topic
        console.log("uspjesna konekcija")
        function onevent(args) {
            var dict = args[0];
            console.log("args:", args[0]);
        }
        userId = $("#user_data").attr("data-userId");
        session.subscribe("User_"+userId, onevent);
    };
    connection.open();
}
RemoveElement = function(data)
{
    console.log(data);
    if (data.status=="deleted")
    {
        $(data.id).remove();
    }
}
ParseLikeResonse = function(data)
{
    console.log(data);
    var like_button = $(data.id).find(".like_button");
    if (data.status=="liked")
    {

        like_button.attr("data-url",like_button.attr("data-url").replace("/like/","/unlike/"));
        like_button.addClass("btn-success");
    }
    else if (data.status=="unliked")
    {
        like_button.attr("data-url",like_button.attr("data-url").replace("/unlike/","/like/"));
        like_button.removeClass("btn-success");
    }
}
ManageFriend = function(data)
{
    console.log(data);
    var friend_button = $(data.id).find(".add_friend");
    if (data.status=="friend_added")
    {

        friend_button.attr("data-url",friend_button.attr("data-url").replace("/add/","/remove/"));
        friend_button.addClass("btn-success");
        friend_button.html("Unfriend friend!");
    }
    else if (data.status=="friend_removed")
    {
        friend_button.attr("data-url",friend_button.attr("data-url").replace("/remove/","/add/"));
        friend_button.removeClass("btn-success");
        friend_button.html("Add as friend!");
    }
}
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