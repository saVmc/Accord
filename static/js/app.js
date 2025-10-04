if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/js/sw.js") 
      .then(res => console.log("Service Worker registered!", res))
      .catch(err => console.log("Service Worker registration failed:", err));
  });
}