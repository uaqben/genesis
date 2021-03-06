import ApplicationSerializer from "./application";


export default ApplicationSerializer.extend({
  serialize: function(record, options) {
    var json = this._super(record, options);
    if (json) {
      json.country = record.get("country") || "";
      json.state = record.get("state") || "";
      json.locale = record.get("locale") || "";
      json.email = record.get("email") || "";
    }
    return json;
  }
});
