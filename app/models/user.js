import DS from "ember-data";


export default DS.Model.extend({
    name: DS.attr('string'),
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    fullName: function() {
      return this.get('firstName')+' '+this.get('lastName');
    }.property('firstName', 'lastName'),
    admin: DS.attr('boolean', {defaultValue: false}),
    sudo: DS.attr('boolean', {defaultValue: false}),
    domain: DS.attr('string'),
    passwd: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    mailAddresses: DS.attr(),
    addressSuffix: function() {
      return "@"+this.get('domain');
    }.property('domain'),
    selectId: function() {
      return this.get('name');
    }.property('name'),
    selectText: function() {
      return this.get('name');
    }.property('name')
});
