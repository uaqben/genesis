import Ember from "ember";
import timezones from "../utils/timezones";
import ENV from "../config/environment";


export default Ember.ObjectController.extend({
  timezones: timezones,
  config: {},
  hostname: "",
  tzRegion: "",
  tzZone: "",
  tzZones: function() {
    var self = this;
    var tzo = timezones.find(function(i) {
      return i.region.replace(" ", "_") == self.get('tzRegion');
    });
    if (tzo.region == "GMT" || tzo.region == "UTC") {
      return [tzo.region];
    } else {
      return tzo.zones;
    };
  }.property('tzRegion'),
  offset: function() {
    return this.get('model').datetime.datetime.offset.toFixed(2);
  }.property('model.datetime'),
  actions: {
    save: function() {
      var self = this;
      $.ajax({
        url: ENV.APP.krakenHost+'/api/config',
        type: 'PUT',
        data: JSON.stringify({config: self.get('config'), hostname: self.get('hostname'), 
            timezone: {region: self.get('tzRegion'), zone: self.get('tzZone').replace(" ", "_")}}),
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status == 500) self.transitionToRoute("error", e);
        }
      });
      self.message.success("System preferences saved successfully");
    }
  }
});
