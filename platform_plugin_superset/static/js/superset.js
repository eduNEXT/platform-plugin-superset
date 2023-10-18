/* Javascript for SupersetXBlock. */
function SupersetXBlock(runtime, element, context) {

  const dashboard_uuid = context.dashboard_uuid;
  const superset_url = context.superset_url;
  const superset_token = context.superset_token;

  function initSuperset(supersetEmbeddedSdk, service) {
    supersetEmbeddedSdk
      .embedDashboard({
        id: dashboard_uuid, // given by the Superset embedding UI
        supersetDomain: superset_url, // your Superset instance
        mountPoint: document.getElementById("superset-embedded-container"), // any html element that can contain an iframe
        fetchGuestToken: () => superset_token, // function that returns a Promise with the guest token
        dashboardUiConfig: {
          // dashboard UI config: hideTitle, hideTab, hideChartControls, filters.visible, filters.expanded (optional)
          hideTitle: true,
          filters: {
            expanded: false,
          },
          hideTab: true,
          hideChartControls: true,
          hideFilters: true,
        },
      })
      .then((dashboard) => {
        mountPoint = document.getElementById("superset-embedded-container");
        /*
                    Perform extra operations on the dashboard object or the container
                    when the dashboard is loaded
                    */
      });
  }

  if (typeof require === "function") {
    require(["supersetEmbeddedSdk"], function (supersetEmbeddedSdk) {
      initSuperset(supersetEmbeddedSdk, "cms");
    });
  } else {
    loadJS(function () {
      initSuperset(window.supersetEmbeddedSdk, "lms");
    });
  }
}


function loadJS(callback) {
  if (window.supersetEmbeddedSdk) {
    callback();
  } else {
    $.getScript(
      "https://cdn.jsdelivr.net/npm/@superset-ui/embedded-sdk@0.1.0-alpha.10/bundle/index.min.js"
    )
      .done(function () {
        window.supersetEmbeddedSdk = supersetEmbeddedSdk;
        callback();
      })
      .fail(function () {
        console.error("Error loading supersetEmbeddedSdk.");
      });
  }
}
