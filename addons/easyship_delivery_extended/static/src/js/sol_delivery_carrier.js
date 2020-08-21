odoo.define('shipping_per_product.checkout', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();
    var session = require('web.session');
    var qweb = core.qweb;
    var xml_load = ajax.loadXML('/easyship_delivery_extended/static/src/xml/easyship_service_template.xml',qweb);

    /* Handle interactive carrier choice + cart update */
    var $pay_button = $('#o_payment_form_pay');

    var $carriers = $(".sol_delivery_carrier input[name^='delivery_type']");
    $carriers.click(function(ev) {
        var $this = $(this)
        $pay_button.prop('disabled', true);
        var $cur_target = $(ev.currentTarget.parentElement);
        var del_div = $this.closest('.sol_delivery_carrier');
        var carrier_id = $(ev.currentTarget).val();
        var sol_id = parseInt(del_div.find('#sale_order_line_id').data('sale_order_line_id'), 10);
        var $empty_sol_del_error = del_div.find('.empty_sol_del_error');
        var values = {'carrier_id': carrier_id, 'order_line': sol_id};
        $empty_sol_del_error.hide();
        ajax.jsonRpc('/shop/sol/update_carrier', 'call', values)
          .then(function(result){
                var $amount_delivery = $('#order_delivery span.oe_currency_value');
                var $amount_untaxed = $('#order_total_untaxed span.oe_currency_value');
                var $amount_tax = $('#order_total_taxes span.oe_currency_value');
                var $amount_total = $('#order_total span.oe_currency_value');
                var $carrier_badge = del_div.find('input[name^="delivery_type"][value=' + result.carrier_id + '] ~ .badge:not(.o_delivery_compute)');
                var $est_delivery_days = del_div.find('input[name^="delivery_type"][value=' + result.carrier_id + '] ~ .delivery_eta');
                var $compute_badge = del_div.find('input[name^="delivery_type"][value=' + result.carrier_id + '] ~ .o_delivery_compute');
                var $check_sol_del = del_div.find('input[name^="line_delivery_name"]');
                if (result.status === true) {
                    $amount_delivery.text(result.new_total_delivery_amount);
                    $amount_untaxed.text(result.new_amount_untaxed);
                    $amount_tax.text(result.new_amount_tax);
                    $amount_total.text(result.new_amount_total);
                    $carrier_badge.children('span').text(result.new_amount_delivery);
                    $carrier_badge.removeClass('d-none');
                    if (result.est_delivery_days){
                        $est_delivery_days.removeClass('d-none');
                    }
                    $compute_badge.addClass('d-none');
                    $pay_button.prop('disabled', false);
                    $check_sol_del.val("SOL Delivery Selected");

                    if (result.es_service_ids) {
                        $check_sol_del.val("");
                        var delivery_service_id = '#delivery_services_'+sol_id;
                        $(delivery_service_id).remove();
                        var $delivery_services = $(delivery_service_id);
                        xml_load.then(function () {
                            var $service_temp = $(qweb.render(
                                'easyship_delivery_extended.easyship_delivery_service',
                                {es_service_ids : result.es_service_ids,es_service_id:result.es_service_id,order_line_id:sol_id,delivery_method_id:carrier_id}
                            ));
                            $cur_target.append($service_temp);

                        });

                        var $carriers_service = $(delivery_service_id+" input[name^='service_type']");
                        $carriers_service.click(_onCarrierServiceClick);
                        $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .badge').text(_t('Select Delivery Service'));
                        if ($carriers_service.length > 0) {
                            $carriers_service.filter(':checked').click();
                        }
                    }
                    else {
                        $('#delivery_services_'+sol_id).remove();
                    }
                }
                else {
                    $compute_badge.text(result.error_message);
                }
          });
    });

    //Add sale order line based on selected service and then update values from frontend using function..//
    var _onCarrierServiceClick = function(ev) {
        var $this = $(this);
        var es_service_id = $(ev.currentTarget).val();
        var sol_id = parseInt($this[0].getAttribute('sale_order_line_id'), 10);
        var delivery_method_id = parseInt($this[0].getAttribute('delivery_method_id'), 10);
        var values = {'es_service_id': es_service_id,
                      'order_line_id':sol_id};
        dp.add(ajax.jsonRpc('/shop/update_es_service', 'call', values)).then(function(result){
            var $amount_delivery = $('#order_delivery span.oe_currency_value');
            $amount_delivery.text(result.new_total_delivery_amount);
            var del_div = $this.closest('.sol_delivery_carrier');
            var $check_sol_del = del_div.find('input[name^="line_delivery_name"]');
            $check_sol_del.val("SOL Delivery Selected");
            var $carrier_badge = del_div.find('input[name^="delivery_type"][value=' + delivery_method_id + '] ~ .badge:not(.o_delivery_compute)');
            $carrier_badge.children('span').text(result.new_line_delivery_amount);
        //    Update order details to right side, like total untaxed amount and total amount
            var $amount_untaxed = $('#order_total_untaxed span.oe_currency_value');
            var $amount_tax = $('#order_total_taxes span.oe_currency_value');
            var $amount_total = $('#order_total span.oe_currency_value');
            $amount_untaxed.text(result.new_amount_untaxed);
            $amount_tax.text(result.new_amount_tax);
            $amount_total.text(result.new_amount_total);

        });
    };

    //Called when choose easyship delivery method......//
    //if response got success from easyship then display services
    // var _addEasyshipDeliveryService = function(result) {
    //     if (result.es_service_ids) {
    //         var $product_view = $('#single_product_table_'+result.order_line_id)
    //         var $delivery_services = $('#delivery_services');
    //         xml_load.then(function () {
    //             var $message = $(qweb.render(
    //                 'easyship_delivery_extended.easyship_delivery_service',
    //                 {es_service_ids : result.es_service_ids,es_service_id:result.es_service_id,order_line_id:result.order_line_id}
    //             ));
    //             $product_view.html($message);
    //         });
    //
    //         var $carriers_service = $(".delivery_services input[name^='service_type']");
    //         $carriers_service.click(_onCarrierServiceClick);
    //         $('#delivery_carrier input[name="delivery_type"][value=' + result.carrier_id + '] ~ .badge').text(_t('Select Delivery Service'));
    //         if ($carriers_service.length > 0) {
    //             $carriers_service.filter(':checked').click();
    //         }
    //         if (!result.es_service_id){
    //             $pay_button.prop('disabled', true);
    //         }
    //     }
    // }

    function check_sol_delivery(){
        var count = 1
        $('.line_delivery_name').each(function () {
            var $this = $(this);
            var $empty_sol_del_error = $this.closest('.sol_delivery_carrier').find('.empty_sol_del_error');
            if($(this).val() == ''){
                count = 0;
                $empty_sol_del_error.show();
                setTimeout(function() {$empty_sol_del_error.hide()},12000);
                return false;
            }
        });
        return count;
    }

    $('#o_payment_form_pay').click(function(event){
        var $this = $(this);
        var check_sol_del_func = check_sol_delivery();
        var result = check_sol_del_func;
        if(result == 0){
            event.preventDefault();
            event.stopPropagation();
        }
    });

});
