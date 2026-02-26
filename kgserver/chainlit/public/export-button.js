/**
 * Inject a "Save as Markdown" button next to the settings gear in the Chainlit input bar.
 * On click, sends a magic message that the backend handles to export the chat.
 */
(function () {
    var MAGIC = "[Save as Markdown]";
    var BTN_ID = "kgraph-export-chat-btn";

    function findComposer() {
        var textarea = document.querySelector("textarea");
        if (textarea) return textarea.closest("form") || textarea.parentElement;
        var editable = document.querySelector("[contenteditable='true']");
        if (editable) return editable.closest("form") || editable.parentElement;
        return document.querySelector("form");
    }

    function findSendButton(container) {
        if (!container) return null;
        var submit = container.querySelector('button[type="submit"]');
        if (submit) return submit;
        var buttons = container.querySelectorAll("button");
        return buttons.length > 0 ? buttons[buttons.length - 1] : null;
    }

    function findSettingsGear(container) {
        if (!container) return null;
        var buttons = container.querySelectorAll("button");
        for (var i = 0; i < buttons.length; i++) {
            var btn = buttons[i];
            var label = (btn.getAttribute("aria-label") || "").toLowerCase();
            var title = (btn.getAttribute("title") || "").toLowerCase();
            if (label.indexOf("setting") >= 0 || title.indexOf("setting") >= 0) return btn;
            if (btn.querySelector("svg") && i < buttons.length - 1) return btn;
        }
        return buttons.length >= 2 ? buttons[1] : buttons[0] || null;
    }

    function getInput(container) {
        if (!container) return null;
        var textarea = container.querySelector("textarea");
        if (textarea) return textarea;
        return container.querySelector("[contenteditable='true']");
    }

    function injectButton() {
        if (document.getElementById(BTN_ID)) return;
        var composer = findComposer();
        if (!composer) return;
        var sendBtn = findSendButton(composer);
        var insertAfter = findSettingsGear(composer);
        if (!insertAfter && sendBtn) insertAfter = sendBtn.previousElementSibling;
        if (!insertAfter) insertAfter = sendBtn;
        if (!insertAfter) return;

        var btn = document.createElement("button");
        btn.id = BTN_ID;
        btn.type = "button";
        btn.setAttribute("data-kgraph-export", "true");
        btn.className = insertAfter.className || "";
        btn.style.cssText = "display:inline-flex;align-items:center;gap:6px;padding:6px 10px;cursor:pointer;margin-left:4px;";
        btn.innerHTML = "<span>Save as Markdown</span>";
        btn.title = "Export this chat to a Markdown file";

        btn.addEventListener("click", function () {
            var input = getInput(composer);
            var send = findSendButton(composer);
            if (!input || !send) return;
            if (input.tagName === "TEXTAREA") {
                input.value = MAGIC;
                input.dispatchEvent(new Event("input", { bubbles: true }));
            } else if (input.isContentEditable) {
                input.textContent = MAGIC;
                input.dispatchEvent(new Event("input", { bubbles: true }));
            }
            send.click();
        });

        insertAfter.parentNode.insertBefore(btn, insertAfter.nextSibling);
    }

    function run() {
        injectButton();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", run);
    } else {
        run();
    }
    setTimeout(run, 500);
    setTimeout(run, 2000);
})();
