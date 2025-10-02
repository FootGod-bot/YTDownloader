(function () {
  const buttonText = "Download";
  const gapSize = 10; // change this number to adjust left/right margin in pixels

  function addButton() {
    const micButton = document.querySelector('ytd-microphone-button-renderer, #voice-search-button, [aria-label="Search with your voice"]');
    const createButton = document.querySelector('ytd-create-icon, #create-icon, [aria-label="Create"]');

    if (micButton && createButton && !document.getElementById('send-to-yt-dlp-btn')) {
      const btn = document.createElement("button");
      btn.id = "send-to-yt-dlp-btn";
      btn.className = "yt-spec-button-shape-next yt-spec-button-shape-next--tonal yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m";
      btn.setAttribute("aria-label", buttonText);
      btn.style.alignSelf = "center";
      btn.style.margin = `0 ${gapSize}px`;
      btn.innerHTML = `<div class="cbox">${buttonText}</div>`;

      btn.addEventListener("click", () => {
        const url = window.location.href;
        fetch("http://127.0.0.1:5000/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url }),
        }).catch(() => {});
      });

      createButton.parentNode.insertBefore(btn, createButton);
    }
  }

  const observer = new MutationObserver(() => addButton());
  observer.observe(document.body, { childList: true, subtree: true });

  addButton();
})();
