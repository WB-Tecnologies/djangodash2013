function render_ticket(ticket, msg_form) {
    var html = 
      '<dt class="dcs-tickets_item dcs-tickets_item__active" data-id="' + ticket.id + '">'
    + '<span class="dcs-tickets_title">' + ticket.subject + '</span>'
    + '</dt>'
    + '<dd class="dcs-tickets_description">'
    + '<ul class="dcs-tickets_history">'
    + '<li class="dcs-tickets_reply"><p>' + ticket.text 
    + '</p><p class="dcs-tickets_author dcs-tickets_author__self">' + ticket.created_at 
    + '</p></li></ul></dd>';

    return html;
}

function render_my_ticket(ticket, msg_form) {
    var html = 
      '<dt class="dcs-tickets_item dcs-tickets_item__active" data-id="' + ticket.id + '">'
    + '<span class="dcs-tickets_title">' + ticket.subject + '</span>'
    + '</dt>'
    + '<dd class="dcs-tickets_description">'
    + '<ul class="dcs-tickets_history">'
    + '<li class="dcs-tickets_reply"><p>' + ticket.text
    + '</p><p class="dcs-tickets_author dcs-tickets_author__self">' + ticket.created_at 
    + '</p></li>' + msg_form + '</ul></dd>';

    return html;
}

function render_message(message) {
    var html = '<li class="dcs-tickets_reply">'
    + '<p>' + message.text + '</p>'
    + '<p class="dcs-tickets_author dcs-tickets_author__self">' + message.created_at + '</p>'
    + '</li>';

    return html;
}

function show_field_error($form, data){
    if (data.status==400){
        var errors = data.responseJSON;
        for (var key in errors){
            $form.find('.field-error[data-name='+key+']').removeClass('hide').text(errors[key][0]);
        }
    }
}

$(function(){
    var add_message_form = $('#add-message-form').text();

    $(".dcs-plate").on("click", function(e){
        e.preventDefault();
        $(".dcs-overlay").show();

        (function(callback) {
            var i = 0;
            function run_callback() {
                if (i >= 2) 
                    callback();
            }
            /* Your tickets */
            $.getJSON('/clients_support/tickets/', {'current_user': 'true'}, function(data) {
                var html = '';
                for (var index in data) {
                    html += render_my_ticket(data[index], add_message_form);
                }
                $('.your-tickets').html(html);
                i++;
                run_callback();
            });

            /* Other tickets */
            $.getJSON('/clients_support/tickets/', {'current_user': 'false'}, function(data) {
                var html = '';
                for (var index in data) {
                    html += render_ticket(data[index]);
                }
                $('.other-tickets').html(html);
                i++;
                run_callback();
            });
        }) (function() {
            $(".dcs-form").show();
            $('.messages').hide();
        });
    });

    $(".dcs-form_close, .dcs-overlay").on("click", function(e){
        e.preventDefault();
        $('.dcs-addticket').hide();
        $('.tickets-list, .dcs-search, .dcs-search_button').show();
        $(".dcs-form").hide();
        $(".dcs-overlay").hide();
    });


    /* Load ticket messages */
    $('.dcs-tickets').on('click', '.dcs-tickets_item', function() {
        $(this).next().toggle();
        var $this = $(this).next();
        if (!$this.is(':visible') || $this.attr('data-loaded'))
            return false;
        var id = $(this).attr('data-id');
        $.getJSON('/clients_support/messages/', {'ticket': id}, function(data) {
            var html = '';
            for (var index in data) {
                html += render_message(data[index]);
            }
            $(html).insertAfter($this.find('li:first'));
            $this.attr('data-loaded', 'true');
        });
    });


    // $('.other-tickets').on('click', '.dcs-tickets_item', function() {
    //     $(this).next().toggle();
    //     if (!$(this).next().is(':visible'))
    //         return false
    //     var id = $(this).attr('data-id');
    // });


    /* Add messages */
    $('.your-tickets').on('submit', 'form', function() {
        var id = $(this).closest('.dcs-tickets_description').prev().attr('data-id');
        var data = {
            'ticket': id,
            'text': $(this).find('textarea[name="text"]').val()
        };
        var $form=$(this);
        $.ajax({
            'url': '/clients_support/messages/',
            'method': 'POST',
            'data': data,
            'dataType': 'json',
            'success': function(resp) {
                $('.tickets').hide();
                $('.messages').show();
            }
        }).fail(function(data){
                show_field_error($form, data);
            });
        return false;
    });


    /* Add ticket */
    $('.dcs-search_button').click(function() {
        $.getJSON('/clients_support/ticket_types/', function(data) {
            var $dcs_select = $('.dcs-select');
            $dcs_select.empty();
            for (var index in data) {
                $dcs_select.append('<option value="' + data[index].id + '">' 
                                            + data[index].name + '</option>')
            }
            $('.dcs-addticket').show();
            $('.tickets-list, .dcs-search, .dcs-search_button').hide();
        })
    });

    $('#addticket-form').submit(function() {
        var $form = $(this),
            guest_name = $form.find('#addticket-guest_name').val(),
            guest_email = $form.find('#addticket-guest_email').val(),
            type = $form.find('#addticket-topic').val(),
            title = $form.find('#addticket-title').val(),
            description = $form.find('#addticket-description').val();
        var data = {
            'guest_name': guest_name,
            'guest_email': guest_email,
            'type': type,
            'subject': title,
            'text': description
        };
        $form.find('.field-error').addClass('hide');
        $.ajax({
            'url': '/clients_support/tickets/',
            'method': 'POST',
            'data': data,
            'dataType': 'json',
            'success': function(resp) {
                $('.dcs-addticket').hide();
                $('.tickets-list, .dcs-search, .dcs-search_button').show();
                $('.tickets').hide();
                $('.messages').show();
            }
        }).fail(function(data){
                show_field_error($form, data);
            });
        return false;
    });
});