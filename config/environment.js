/* jshint node: true */

module.exports = function(environment) {
  var ENV = {
    modulePrefix: 'genesis',
    environment: environment,
    baseURL: '/',
    locationType: 'auto',
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      }
    },

    APP: {
      GRMHost: 'https://grm-test.arkos.io',
      dateFormat: 'DD MMM YYYY',
      timeFormat: 'HH:mm:ss'
    },
    
    contentSecurityPolicy: {
      'default-src': "'none'",
      'script-src': "'self'",
      'font-src': "'self'",
      'connect-src': "'self' http://localhost:8000",
      'img-src': "'self'",
      'style-src': "'self' 'unsafe-inline'",
      'media-src': "'self'"
    }
  };

  if (environment === 'development') {
    ENV.APP.krakenHost = 'http://localhost:8000';
  }

  if (environment === 'test') {
    // Testem prefers this...
    ENV.baseURL = '/';
    ENV.locationType = 'none';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.krakenHost = 'http://localhost:8000';
    ENV.APP.rootElement = '#ember-testing';
  }

  if (environment === 'production') {
    ENV.APP.krakenHost = '';
  }
  
  ENV['simple-auth'] = {
    authorizer: 'simple-auth-authorizer:token',
    crossOriginWhitelist: [ENV.APP.krakenHost]
  };
  ENV['simple-auth-token'] = {
    serverTokenEndpoint: ENV.APP.krakenHost+'/api/token',
    serverTokenRefreshEndpoint: ENV.APP.krakenHost+'/api/token/refresh',
    refreshAccessTokens: true,
    timeFactor: 1000,
    refreshLeeway: 300
  };

  return ENV;
};
