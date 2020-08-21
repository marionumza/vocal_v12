odoo.define('shipping_per_product.checkout', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');

    /* Handle interactive carrier choice + cart update */
    var $pay_button = $('#o_payment_form_pay');

    var $carriers = $(".sol_delivery_carrier input[name^='delivery_type']");
    $carriers.click(function(ev) {
        var $this = $(this)
        $pay_button.prop('disabled', true);
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
                var $carrier_badge = del_div.find('input[name^="delivery_type"][value=' + result.carrier_id + '] ~ .badge.hidden');
                var $compute_badge = del_div.find('input[name^="delivery_type"][value=' + result.carrier_id + '] ~ .o_delivery_compute');
                var $check_sol_del = del_div.find('input[name^="line_delivery_name"]');
                if (result.status === true) {
                    $amount_delivery.text(result.new_total_delivery_amount);
                    $amount_untaxed.text(result.new_amount_untaxed);
                    $amount_tax.text(result.new_amount_tax);
                    $amount_total.text(result.new_amount_total);
                    $carrier_badge.children('span').text(result.new_amount_delivery);
                    $carrier_badge.removeClass('hidden');
                    $compute_badge.addClass('hidden');
                    $pay_button.prop('disabled', false);
                    $check_sol_del.val("SOL Delivery Selected");
                }
                else {
                    $compute_badge.text(result.error_message);
                }
          });
    });

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
