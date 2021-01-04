/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('odoo_magento_connect.MobDashboard', function (require) {
"use strict";
var core = require('web.core');
var session = require('web.session');
var KanbanView = require('web.KanbanView');
var KanbanRenderer = require('web.KanbanRenderer');
var view_registry = require('web.view_registry');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var MOBSetRenderer = KanbanRenderer.extend({
    events: _.extend({}, KanbanRenderer.prototype.events, {
        'click .o_dashboard_action': 'on_dashboard_action_clicked',
    }),

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Notifies the controller that the target has changed.
     *
     * @private
     * @param {string} target_name the name of the changed target
     * @param {string} value the new value
     */
    _notifyTargetChange: function (target_name, value) {
        this.trigger_up('dashboard_edit_target', {
            target_name: target_name,
            target_value: value,
        });
    },
  /**
     * @override
     * @private
     * @returns {Deferred}
     */

    fetch_data: function() {
        return $.when();
    },
    _render: function () {
        var super_render = this._super;
        var self = this;
        var values = {};
        return this.fetch_data().then(function(result){
            self._rpc({
                    model: 'mob.dashboard',
                    method: 'get_connection_info',
                    args: [],
                })
            .then(function(res){
                values = res;
                var sales_dashboard = QWeb.render('odoo_magento_connect.MobDashboard', {
                    widget: self,
                    connrecs : values,
                });
            super_render.call(self);
            $(sales_dashboard).prependTo(self.$el);
            });
        });

    },
    on_dashboard_action_clicked: function(e) {
        e.preventDefault();
        var self = this;
        var $action = $(e.currentTarget);
        var name_attr = $action.attr('name');
        var action_extra = $action.data('extra');
        var action_context = {};
        if (name_attr === 'odoo_magento_connect.magento_configure_tree_action') {
            if (action_extra === 'inactive'){
                action_context.search_default_inactive = 1;
            }else if(action_extra === 'all'){
                action_context.active_test = false;
            }
        }
        if (name_attr === 'odoo_magento_connect.magento_configure_tree_action_2') {
          name_attr = 'odoo_magento_connect.magento_configure_tree_action'
          if(action_extra === 'connected'){
              action_context.search_default_success = 1;
          }else if(action_extra === 'error'){
              action_context.search_default_error = 1;
          }
        }
        this.do_action(name_attr, {additional_context: action_context});
    },
});

var MagentoBridgeDashboardView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Renderer: MOBSetRenderer,}),
    display_name: _lt('MOB Dashboard'),
    icon: 'fa-dashboard',
    searchview_hidden: true,
});
view_registry.add('odoo_magento_connect_dashboard', MagentoBridgeDashboardView);

return {
    Renderer: MOBSetRenderer,
};

});
