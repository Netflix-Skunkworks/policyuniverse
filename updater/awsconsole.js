var system = require('system');
var fs = require('fs');
var webPage = require('webpage');

if (system.args.length != 3) {
    console.log('Usage: access_adviser.js <signinToken> <output_file>');
    phantom.exit(-1);
}

var iam_url = 'https://console.aws.amazon.com/iam/home?region=us-east-1';
var federation_base_url = 'https://signin.aws.amazon.com/federation';

var signinToken = system.args[1];
// var arn_file = system.args[2];
var OUTPUT_FILE = system.args[2];

// var arns = JSON.parse(fs.read(arn_file));

var page = webPage.create();
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36';
page.settings.javascriptEnabled = true;
page.settings.loadImages = false;  //Script is much faster with this field set to false
phantom.cookiesEnabled = true;
phantom.javascriptEnabled = true;

page.onConsoleMessage = function(msg) {
    console.log('>>> ' + msg);
};

page.onCallback = function(results) {
  console.log("WRITING RESULTS");
  var json_results = JSON.stringify(results, null, 2);
  console.log("WRITING RESULTS");
  fs.write(OUTPUT_FILE, json_results, 'w');
  console.log("EXITING!");
  phantom.exit(0);
};

page.onResourceReceived = function(resource) {
    if(resource.url.indexOf("signin.aws.amazon.com") > -1)
    {
      statusCode = resource.status;
    }
};

var getSessionCookies = function(token) {
    var url = federation_base_url + '?Action=login'
                                  + '&Issuer=tripleA'
                                  + '&Destination=' + encodeURIComponent(iam_url)
                                  + '&SigninToken='+token;

    statusCode = 400; // default fail

    var onComplete = function(response) {
        if(statusCode < 400) {
            console.log('Successfully logged in')
            page.includeJs(
                "https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js",
                function() {
                    page.evaluate(advisor);
                }
            );
        } else {
            console.log('Failed to log in')
            console.log('Account '+response+'.');
            phantom.exit(-1);
        }
    };
    page.open(url, function(response) { setTimeout(onComplete, 20000, response) });
};

getSessionCookies(signinToken);

var advisor = function() {
    var PERIOD = 5000; // 10 seconds
    var results = {};
    var progress = {};

    XSRF_TOKEN = window.Csrf.fromCookie(null);
    // XSRF_TOKEN = app.orcaCsrf.token;

    var collectServices = function() {
        console.log("Asking for services.");
        jQuery.ajax({
            type: "GET",
            url: "/iam/api/services",
            dataType: 'json',
            beforeSend: function(xhr) {if (XSRF_TOKEN != 'NOT_DEFINED') {xhr.setRequestHeader('X-CSRF-Token', XSRF_TOKEN);} else {system.stderr.writeLine('NOT ADDING XSRF TOKEN');}},
            success: function (data) {
                console.log("Done Collecting Services!");
                results['services'] = data;

                Object.keys(results['services']['_embedded']).forEach(
                    function(service_url) {
                        var service_data = results['services']['_embedded'][service_url];
                        var actions_url = service_data['_links']['actions']['href'];
                        var service_name = service_data['serviceName'];
                        progress[actions_url] = "NOT_STARTED";
                        results['actions'] = {};
                        collectServiceActions(actions_url, service_name);
                    }
                );
            
                checkProgress();
            },
            error: function(asdf) {
                console.log("ERROR");
                phantom.exit(-1);
            }
        });
    };

    var collectServiceActions = function(actions_url, service_name) {
        console.log("Asking for actions.");
        jQuery.ajax({
            type: "GET",
            url: actions_url,
            dataType: 'json',
            beforeSend: function(xhr) {if (XSRF_TOKEN != 'NOT_DEFINED') {xhr.setRequestHeader('X-CSRF-Token', XSRF_TOKEN);} else {system.stderr.writeLine('NOT ADDING XSRF TOKEN');}},
            success: function (data) {
                if (typeof results['actions'][service_name] != "undefined") { // Merge if a new version is added by AWS with same service name prefix
                    results['actions'][service_name]['_links']['results'].push(data['_links']['results']);
                    merge( results['actions'][service_name]['_embedded'], data['_embedded']);
                } else {
                    results['actions'][service_name] = data;
                }
                progress[actions_url] = 'COMPLETE';
            },
            error: function(asdf) {
                console.log("ERROR - "+actions_url);
                progress[actions_url] = 'ERROR';

            }
        });
    };

    var merge = function(objOne, objTwo) {
        Object.keys(objTwo).forEach(function(key) { objOne[key] = objTwo[key]; });
        return objOne;
    }

    var checkProgress = function() {
        for (var idx in Object.keys(progress)) {
            var key = Object.keys(progress)[idx];
            if (progress[key] != 'COMPLETE' && progress[key] != 'ERROR' ) {
                console.log("Object "+key+" is not yet complete. "+progress[key]);
                setTimeout(function() { checkProgress() }, PERIOD);
                return;
            } else {
                console.log("DONE w/"+key)
            }
        }
        console.log('PROGRESS COMPLETE');
        window.callPhantom(results);
    };

    collectServices();
};


