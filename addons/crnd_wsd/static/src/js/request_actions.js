odoo.define('crnd_wsd.request_actions', function (require) {
    'use strict';

    var trumbowyg = require('crnd_wsd.trumbowyg');

    var Dialog = require("web.Dialog");

    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var blockui = require('crnd_wsd.blockui');

    var _t = core._t;

    var snippet_animation = require('website.content.snippets.animation');
    var snippet_registry = snippet_animation.registry;

    ajax.loadXML('/crnd_wsd/static/src/xml/templates.xml', qweb);

    var WDialog = Dialog.extend({
        init: function (parent, options) {
            var opts = options || {};
            this._super(parent, _.extend({}, {
                buttons: [
                    {
                        text: opts.save_text || _t("Save"),
                        classes: "btn-primary o_save_button",
                        click: this.save,
                    },
                    {
                        text: _t("Discard"), close: true,
                    },
                ],
            }, opts));

            this.destroyAction = "cancel";

            var self = this;
            this.opened().then(function () {
                self.$('input:first').focus();
            });
            this.on("closed", this, function () {
                this.trigger(this.destroyAction, this.final_data || null);
            });
        },
        save: function () {
            this.destroyAction = "save";
            this.close();
        },
    });


    var RequestActionHelper = snippet_animation.Class.extend({
        selector: '.wsd_request',

        start: function () {
            var self = this;

            self.request_id = self.$target.data('request-id');
            self.$target.removeData('request-id');

            self.$request_body_text = self.$target.find("#request-body-text");

            // Register handlers for request actions
            self.$target.find("#request-head-actions a.request-action").on(
                'click', function () {
                    self.on_request_action($(this));
                });

            self.$request_body_text.find("> span.open-editor").on(
                'click', function () {
                    self.on_request_editor_open();
                });
        },

        on_request_editor_open: function () {
            var self = this;
            self.$request_text_content = self.$request_body_text.find(
                "#request-body-text-content");

            self.$editor_content = $(
                qweb.render('crnd_wsd.request_text_editor', {
                    'request_text': self.$request_text_content.html(),
                })
            );

            self.$request_body_text.append(self.$editor_content);
            self.$editor = self.$editor_content.find("> textarea");
            self.$editor.trumbowyg(trumbowyg.trumbowygOptions);


            self.$request_text_content.hide();

            // Bind editor events
            self.$editor_content.find(".btn-cancel").on('click', function () {
                self.on_request_editor_cancel();
            });
            self.$editor_content.find(".btn-save").on('click', function () {
                self.on_request_editor_save();
            });

            self.$request_body_text.find(".open-editor").hide();

        },

        on_request_editor_cancel: function () {
            var self = this;
            self.$editor_content.remove();
            self.$request_text_content.show();
            self.$request_body_text.find(".open-editor").show();
        },

        on_request_editor_save: function () {
            var self = this;

            var request_text = self.$editor.val();
            blockui.blockUI();
            ajax.jsonRpc(
                '/crnd_wsd/api/request/update-text',
                'call', {
                    'request_text': request_text,
                    'request_id': self.request_id,
                }
            ).then(function (result) {
                blockui.unblockUI();
                if (result.error) {
                    return Dialog.alert(null, result.error, {
                        title: _t("Error"),
                    });
                }

                self.$request_text_content.html(result.request_text);
                self.$editor_content.remove();
                self.$request_text_content.show();
                self.$request_body_text.find(".open-editor").show();

            }).fail(function (error) {
                blockui.unblockUI();
                return Dialog.alert(null, error.message, {
                    title: _t("Error"),
                });
            });
        },

        _do_request_action: function (action_id, response_text) {
            var self = this;
            blockui.blockUI();
            ajax.jsonRpc(
                '/crnd_wsd/api/request/do-action',
                'call', {
                    'request_id': self.request_id,
                    'action_id': action_id,
                    'response_text': response_text,
                }
            ).then(function (result) {
                blockui.unblockUI();
                if (result.error) {
                    return Dialog.alert(null, result.error, {
                        title: _t("Error"),
                    });
                }
                location.reload(true);
            }).fail(function (error) {
                blockui.unblockUI();
                return Dialog.alert(null, error.message, {
                    title: _t("Error"),
                });
            });

        },

        on_request_action: function (act) {
            var self = this;
            var action_id = act.data('action-id');
            var require_response = act.data('require-response');

            if (require_response === "True") {
                var $response_content = $('<div/>').html(
                    '<textarea id="dialog-response-text"/>');
                var response_dialog = new WDialog(self, {
                    title: _t("Please, fill response text!"),
                    $content: $response_content,
                });
                response_dialog.on('save', self, function () {
                    self._do_request_action(action_id, $response_content.find(
                        'textarea').val());
                });
                response_dialog.opened(function () {
                    $response_content.find('textarea').trumbowyg(_.extend(
                        trumbowyg.trumbowygOptions, {
                            btns: [
                                ['formatting'],
                                ['strong', 'em', 'del'],
                                ['undo', 'redo'],
                                ['superscript', 'subscript'],
                                ['link'],
                                ['upload_dd'],
                                ['justifyLeft', 'justifyCenter',
                                    'justifyRight', 'justifyFull'],
                                ['unorderedList', 'orderedList'],
                                ['table'],
                                ['horizontalRule'],
                                ['removeformat'],
                            ],
                        }));
                });
                response_dialog.open();
            } else {
                self._do_request_action(action_id, false);
            }
        },


    });

    snippet_registry.RequestActionHelper = RequestActionHelper;

    return {
        RequestActionHelper: RequestActionHelper,
    };

});
