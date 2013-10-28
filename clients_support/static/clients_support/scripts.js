function render_ticket(ticket, msg_form) {
    msg_form = msg_form || '';
    return '<dt class="dcs-tickets_item dcs-tickets_item__active" data-id="' + ticket.id + '">'
    + '<span class="dcs-tickets_title">' + ticket.subject + '</span>'
    + '</dt>'
    + '<dd class="dcs-tickets_description">'
    + '<ul class="dcs-tickets_history">'
    + '<li class="dcs-tickets_reply"><p>' + ticket.text 
    + '</p><p class="dcs-tickets_author dcs-tickets_author__self">' + ticket.created_at 
    + '</p></li>' + msg_form + '</ul></dd>';

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
    var $dcs_overlay = $(".dcs-overlay"),
        $dcs_form = $("#clients_support-form"),
        $msg_form = $(".dcs-form.messages"),
        $tickets_list = $dcs_form.find('.tickets-list'),
        $common_tickets = $tickets_list.find('.common-tickets'),
        add_message_form = $('#add-message-form').text();


    function get_all_tickets(term){
        term = term || '';
        (function(callback) {
            var i = 0;
            function run_callback() {
                if (i >= $tickets_list.find('.dcs-tickets').length)
                    callback();
            }

            function get_tickets(current_user, term, kind_tickets){

                term = term || '';
                var _u = current_user || false;
                var with_form = _u?add_message_form:'';

                $.getJSON(
                    '/clients_support/tickets/',
                    {
                        'current_user': _u,
                        'term': term
                    },
                    function(data) {
                        var html = '',
                            tickets = data.results?data.results:data;
                        for (var index in tickets) {
                            html += render_ticket(tickets[index], with_form);
                        }
                        $(kind_tickets).html(html);
                        /*$('#dcs-pager').pagination(20,{callback:function(page, component){
                            console.log(component);
                        }});*/
                        i++;
                        run_callback();
                    }
                );
            }

            if ($tickets_list.find('.common-tickets').length){
                /* Common tickets (from guest) */
                get_tickets(false, term, '.common-tickets');
            } else {
                /* Your tickets */
                get_tickets(true, term, '.your-tickets');

                /* Other tickets */
                get_tickets(false, term, '.other-tickets');
            }

        }) (function() {
            $dcs_form.show();
            $msg_form.hide();
            if (!(term||$dcs_form.find('.dcs-tickets .dcs-tickets_item').length)){
                $dcs_form.find('.dcs-add_button').trigger('click');
            }
        });
    }

    $(".dcs-plate").on("click", function(e){
        e.preventDefault();
        $dcs_overlay.show();

        get_all_tickets();
    });

    $(".dcs-form_close, .dcs-overlay").on("click", function(e){
        e.preventDefault();
        $dcs_form.find('.dcs-addticket').hide();
        $dcs_form.find('.tickets-list, .dcs-search, .dcs-add_button').show();
        $dcs_form.hide();
        $dcs_overlay.hide();
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

    /* Search tickets */
    $dcs_form.on('keyup', '.dcs-search_input', function() {
        get_all_tickets($.trim($(this).val()));
    });

    /* Add messages */
    $dcs_form.find('.dcs-tickets').on('submit', 'form', function() {
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
                $dcs_form.hide();
                $msg_form.show();
            }
        }).fail(function(data){
                show_field_error($form, data);
            });
        return false;
    });


    /* Add ticket */
    $dcs_form.find('.dcs-add_button').click(function() {
        $.getJSON('/clients_support/ticket_types/', function(data) {
            var $dcs_select = $dcs_form.find('.dcs-select');
            $dcs_select.empty();
            for (var index in data) {
                $dcs_select.append('<option value="' + data[index].id + '">' 
                                            + data[index].name + '</option>')
            }
            $dcs_form.find('.dcs-addticket').show();
            $dcs_form.find('.tickets-list, .dcs-search, .dcs-add_button').hide();
        })
    });

    $dcs_form.find('#addticket-form').submit(function() {
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
                $dcs_form.find('.dcs-addticket').hide();
                $dcs_form.find('.tickets-list, .dcs-search, .dcs-add_button').show();
                $dcs_form.hide();
                $msg_form.show();
            }
        }).fail(function(data){
                show_field_error($form, data);
            });
        return false;
    });
});