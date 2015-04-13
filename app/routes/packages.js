import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').find('package');
  },
  actions: {
    refresh: function() {
      var self = this;
      $.getJSON(ENV.APP.krakenHost+"/system/packages?refresh=true", function(j){
        self.refresh();
      });
    }
  }
});
