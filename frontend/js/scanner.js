let html5QrCode = null;

function initScanner() {
  html5QrCode = new Html5Qrcode("reader");
  startScanner();
}

function startScanner() {
  if (!html5QrCode) return;

  const config = { fps: 10, qrbox: { width: 200, height: 200 } };

  html5QrCode.start(
    { facingMode: "environment" }, // Prefers rear camera on phones
    config,
    onScanSuccess,
    onScanFailure
  ).catch(err => {
    console.warn("Camera start failed (or permission denied):", err);
    document.getElementById("reader").innerHTML = 
      `<p class="text-rose-400 text-xs text-center p-4">Camera unavailable or access denied.<br/>Use 'Manual ID' tab or open via HTTPS/localhost.</p>`;
  });
}

function stopScanner() {
  if (html5QrCode && html5QrCode.isScanning) {
    html5QrCode.stop().catch(err => console.error("Scanner stop error:", err));
  }
}

function onScanSuccess(decodedText, decodedResult) {
  sendDeliveryRecord(decodedText);
}

function onScanFailure(error) {
  // Silent fail during active scan frame polling
}