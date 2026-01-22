/*
 Copyright 2025 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __setFunctionName = (this && this.__setFunctionName) || function (f, name, prefix) {
    if (typeof name === "symbol") name = name.description ? "[".concat(name.description, "]") : "";
    return Object.defineProperty(f, "name", { configurable: true, value: prefix ? "".concat(prefix, " ", name) : name });
};
import { SignalWatcher } from "@lit-labs/signals";
import { provide } from "@lit/context";
import { LitElement, html, css, nothing, unsafeCSS, } from "lit";
import { customElement, state } from "lit/decorators.js";
import { theme as uiTheme } from "./theme/default-theme.js";
import { A2UIClient } from "./client.js";
import { SnackType, } from "./types/types.js";
import { repeat } from "lit/directives/repeat.js";
import { v0_8 } from "@a2ui/lit";
import * as UI from "@a2ui/lit/ui";
// App elements.
import "./ui/ui.js";
import { config as restaurantConfig } from "./configs/restaurant.js";
import { config as contactsConfig } from "./configs/contacts.js";
import { styleMap } from "lit/directives/style-map.js";
const configs = {
    restaurant: restaurantConfig,
    contacts: contactsConfig,
};
let A2UILayoutEditor = (() => {
    let _classDecorators = [customElement("a2ui-shell")];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    let _classSuper = SignalWatcher(LitElement);
    let _theme_decorators;
    let _theme_initializers = [];
    let _theme_extraInitializers = [];
    let _private_requesting_decorators;
    let _private_requesting_initializers = [];
    let _private_requesting_extraInitializers = [];
    let _private_requesting_descriptor;
    let _private_error_decorators;
    let _private_error_initializers = [];
    let _private_error_extraInitializers = [];
    let _private_error_descriptor;
    let _private_lastMessages_decorators;
    let _private_lastMessages_initializers = [];
    let _private_lastMessages_extraInitializers = [];
    let _private_lastMessages_descriptor;
    let _config_decorators;
    let _config_initializers = [];
    let _config_extraInitializers = [];
    let _private_loadingTextIndex_decorators;
    let _private_loadingTextIndex_initializers = [];
    let _private_loadingTextIndex_extraInitializers = [];
    let _private_loadingTextIndex_descriptor;
    var A2UILayoutEditor = class extends _classSuper {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(_classSuper[Symbol.metadata] ?? null) : void 0;
            _theme_decorators = [provide({ context: UI.Context.themeContext })];
            _private_requesting_decorators = [state()];
            _private_error_decorators = [state()];
            _private_lastMessages_decorators = [state()];
            _config_decorators = [state()];
            _private_loadingTextIndex_decorators = [state()];
            __esDecorate(this, null, _theme_decorators, { kind: "accessor", name: "theme", static: false, private: false, access: { has: obj => "theme" in obj, get: obj => obj.theme, set: (obj, value) => { obj.theme = value; } }, metadata: _metadata }, _theme_initializers, _theme_extraInitializers);
            __esDecorate(this, _private_requesting_descriptor = { get: __setFunctionName(function () { return this.#requesting_accessor_storage; }, "#requesting", "get"), set: __setFunctionName(function (value) { this.#requesting_accessor_storage = value; }, "#requesting", "set") }, _private_requesting_decorators, { kind: "accessor", name: "#requesting", static: false, private: true, access: { has: obj => #requesting in obj, get: obj => obj.#requesting, set: (obj, value) => { obj.#requesting = value; } }, metadata: _metadata }, _private_requesting_initializers, _private_requesting_extraInitializers);
            __esDecorate(this, _private_error_descriptor = { get: __setFunctionName(function () { return this.#error_accessor_storage; }, "#error", "get"), set: __setFunctionName(function (value) { this.#error_accessor_storage = value; }, "#error", "set") }, _private_error_decorators, { kind: "accessor", name: "#error", static: false, private: true, access: { has: obj => #error in obj, get: obj => obj.#error, set: (obj, value) => { obj.#error = value; } }, metadata: _metadata }, _private_error_initializers, _private_error_extraInitializers);
            __esDecorate(this, _private_lastMessages_descriptor = { get: __setFunctionName(function () { return this.#lastMessages_accessor_storage; }, "#lastMessages", "get"), set: __setFunctionName(function (value) { this.#lastMessages_accessor_storage = value; }, "#lastMessages", "set") }, _private_lastMessages_decorators, { kind: "accessor", name: "#lastMessages", static: false, private: true, access: { has: obj => #lastMessages in obj, get: obj => obj.#lastMessages, set: (obj, value) => { obj.#lastMessages = value; } }, metadata: _metadata }, _private_lastMessages_initializers, _private_lastMessages_extraInitializers);
            __esDecorate(this, null, _config_decorators, { kind: "accessor", name: "config", static: false, private: false, access: { has: obj => "config" in obj, get: obj => obj.config, set: (obj, value) => { obj.config = value; } }, metadata: _metadata }, _config_initializers, _config_extraInitializers);
            __esDecorate(this, _private_loadingTextIndex_descriptor = { get: __setFunctionName(function () { return this.#loadingTextIndex_accessor_storage; }, "#loadingTextIndex", "get"), set: __setFunctionName(function (value) { this.#loadingTextIndex_accessor_storage = value; }, "#loadingTextIndex", "set") }, _private_loadingTextIndex_decorators, { kind: "accessor", name: "#loadingTextIndex", static: false, private: true, access: { has: obj => #loadingTextIndex in obj, get: obj => obj.#loadingTextIndex, set: (obj, value) => { obj.#loadingTextIndex = value; } }, metadata: _metadata }, _private_loadingTextIndex_initializers, _private_loadingTextIndex_extraInitializers);
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            A2UILayoutEditor = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        }
        #theme_accessor_storage = __runInitializers(this, _theme_initializers, uiTheme);
        get theme() { return this.#theme_accessor_storage; }
        set theme(value) { this.#theme_accessor_storage = value; }
        #requesting_accessor_storage = (__runInitializers(this, _theme_extraInitializers), __runInitializers(this, _private_requesting_initializers, false));
        get #requesting() { return _private_requesting_descriptor.get.call(this); }
        set #requesting(value) { return _private_requesting_descriptor.set.call(this, value); }
        #error_accessor_storage = (__runInitializers(this, _private_requesting_extraInitializers), __runInitializers(this, _private_error_initializers, null));
        get #error() { return _private_error_descriptor.get.call(this); }
        set #error(value) { return _private_error_descriptor.set.call(this, value); }
        #lastMessages_accessor_storage = (__runInitializers(this, _private_error_extraInitializers), __runInitializers(this, _private_lastMessages_initializers, []));
        get #lastMessages() { return _private_lastMessages_descriptor.get.call(this); }
        set #lastMessages(value) { return _private_lastMessages_descriptor.set.call(this, value); }
        #config_accessor_storage = (__runInitializers(this, _private_lastMessages_extraInitializers), __runInitializers(this, _config_initializers, configs.restaurant));
        get config() { return this.#config_accessor_storage; }
        set config(value) { this.#config_accessor_storage = value; }
        #loadingTextIndex_accessor_storage = (__runInitializers(this, _config_extraInitializers), __runInitializers(this, _private_loadingTextIndex_initializers, 0));
        get #loadingTextIndex() { return _private_loadingTextIndex_descriptor.get.call(this); }
        set #loadingTextIndex(value) { return _private_loadingTextIndex_descriptor.set.call(this, value); }
        #loadingInterval = __runInitializers(this, _private_loadingTextIndex_extraInitializers);
        static { this.styles = [
            unsafeCSS(v0_8.Styles.structuralStyles),
            css `
      * {
        box-sizing: border-box;
      }

      :host {
        display: block;
        max-width: 640px;
        margin: 0 auto;
        min-height: 100%;
        color: light-dark(var(--n-10), var(--n-90));
        font-family: var(--font-family);
      }

      #hero-img {
        width: 100%;
        max-width: 400px;
        aspect-ratio: 1280/720;
        height: auto;
        margin-bottom: var(--bb-grid-size-6);
        display: block;
        margin: 0 auto;
        background: var(--background-image-light) center center / contain
          no-repeat;
      }

      #surfaces {
        width: 100%;
        max-width: 100svw;
        padding: var(--bb-grid-size-3);
        animation: fadeIn 1s cubic-bezier(0, 0, 0.3, 1) 0.3s backwards;
      }

      form {
        display: flex;
        flex-direction: column;
        flex: 1;
        gap: 16px;
        align-items: center;
        padding: 16px 0;
        animation: fadeIn 1s cubic-bezier(0, 0, 0.3, 1) 1s backwards;

        & h1 {
          color: light-dark(var(--p-40), var(--n-90));
        }

        & > div {
          display: flex;
          flex: 1;
          gap: 16px;
          align-items: center;
          width: 100%;

          & > input {
            display: block;
            flex: 1;
            border-radius: 32px;
            padding: 16px 24px;
            border: 1px solid var(--p-60);
            background: light-dark(var(--n-100), var(--n-10));
            font-size: 16px;
          }

          & > button {
            display: flex;
            align-items: center;
            background: var(--p-40);
            color: var(--n-100);
            border: none;
            padding: 8px 16px;
            border-radius: 32px;
            opacity: 0.5;

            &:not([disabled]) {
              cursor: pointer;
              opacity: 1;
            }
          }
        }
      }

      .rotate {
        animation: rotate 1s linear infinite;
      }

      .pending {
        width: 100%;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: fadeIn 1s cubic-bezier(0, 0, 0.3, 1) 0.3s backwards;
        gap: 16px;
      }

      .spinner {
        width: 48px;
        height: 48px;
        border: 4px solid rgba(255, 255, 255, 0.1);
        border-left-color: var(--p-60);
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }

      .theme-toggle {
        padding: 0;
        margin: 0;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        position: fixed;
        top: var(--bb-grid-size-3);
        right: var(--bb-grid-size-4);
        background: light-dark(var(--n-100), var(--n-0));
        border-radius: 50%;
        color: var(--p-30);
        cursor: pointer;
        width: 48px;
        height: 48px;
        font-size: 32px;

        & .g-icon {
          pointer-events: none;

          &::before {
            content: "dark_mode";
          }
        }
      }

      @container style(--color-scheme: dark) {
        .theme-toggle .g-icon::before {
          content: "light_mode";
          color: var(--n-90);
        }

        #hero-img {
          background-image: var(--background-image-dark);
        }
      }

      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }

      @keyframes pulse {
        0% {
          opacity: 0.6;
        }
        50% {
          opacity: 1;
        }
        100% {
          opacity: 0.6;
        }
      }

      .error {
        color: var(--e-40);
        background-color: var(--e-95);
        border: 1px solid var(--e-80);
        padding: 16px;
        border-radius: 8px;
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
        }

        to {
          opacity: 1;
        }
      }

      @keyframes rotate {
        from {
          rotate: 0deg;
        }

        to {
          rotate: 360deg;
        }
      }
    `,
        ]; }
        #processor = v0_8.Data.createSignalA2uiMessageProcessor();
        #a2uiClient = new A2UIClient();
        #snackbar = undefined;
        #pendingSnackbarMessages = [];
        #maybeRenderError() {
            if (!this.#error)
                return nothing;
            return html `<div class="error">${this.#error}</div>`;
        }
        connectedCallback() {
            super.connectedCallback();
            // Load config from URL
            const urlParams = new URLSearchParams(window.location.search);
            const appKey = urlParams.get("app") || "restaurant";
            this.config = configs[appKey] || configs.restaurant;
            // Apply the theme directly, which will use the Lit context.
            if (this.config.theme) {
                this.theme = this.config.theme;
            }
            window.document.title = this.config.title;
            window.document.documentElement.style.setProperty("--background", this.config.background);
            // Initialize client with configured URL
            this.#a2uiClient = new A2UIClient(this.config.serverUrl);
        }
        render() {
            return [
                this.#renderThemeToggle(),
                this.#maybeRenderForm(),
                this.#maybeRenderData(),
                this.#maybeRenderError(),
            ];
        }
        #renderThemeToggle() {
            return html ` <div>
      <button
        @click=${(evt) => {
                if (!(evt.target instanceof HTMLButtonElement))
                    return;
                const { colorScheme } = window.getComputedStyle(evt.target);
                if (colorScheme === "dark") {
                    document.body.classList.add("light");
                    document.body.classList.remove("dark");
                }
                else {
                    document.body.classList.add("dark");
                    document.body.classList.remove("light");
                }
            }}
        class="theme-toggle"
      >
        <span class="g-icon filled-heavy"></span>
      </button>
    </div>`;
        }
        #maybeRenderForm() {
            if (this.#requesting)
                return nothing;
            if (this.#lastMessages.length > 0)
                return nothing;
            return html ` <form
      @submit=${async (evt) => {
                evt.preventDefault();
                if (!(evt.target instanceof HTMLFormElement)) {
                    return;
                }
                const data = new FormData(evt.target);
                const body = data.get("body") ?? null;
                if (!body) {
                    return;
                }
                const message = body;
                await this.#sendAndProcessMessage(message);
            }}
    >
      ${this.config.heroImage
                ? html `<div
            style=${styleMap({
                    "--background-image-light": `url(${this.config.heroImage})`,
                    "--background-image-dark": `url(${this.config.heroImageDark ?? this.config.heroImage})`,
                })}
            id="hero-img"
          ></div>`
                : nothing}
      <h1 class="app-title">${this.config.title}</h1>
      <div>
        <input
          required
          value="${this.config.placeholder}"
          autocomplete="off"
          id="body"
          name="body"
          type="text"
          ?disabled=${this.#requesting}
        />
        <button type="submit" ?disabled=${this.#requesting}>
          <span class="g-icon filled-heavy">send</span>
        </button>
      </div>
    </form>`;
        }
        #startLoadingAnimation() {
            if (Array.isArray(this.config.loadingText) &&
                this.config.loadingText.length > 1) {
                this.#loadingTextIndex = 0;
                this.#loadingInterval = window.setInterval(() => {
                    this.#loadingTextIndex =
                        (this.#loadingTextIndex + 1) %
                            this.config.loadingText.length;
                }, 2000);
            }
        }
        #stopLoadingAnimation() {
            if (this.#loadingInterval) {
                clearInterval(this.#loadingInterval);
                this.#loadingInterval = undefined;
            }
        }
        async #sendMessage(message) {
            try {
                this.#requesting = true;
                this.#startLoadingAnimation();
                const response = this.#a2uiClient.send(message);
                await response;
                this.#requesting = false;
                this.#stopLoadingAnimation();
                return response;
            }
            catch (err) {
                this.snackbar(err, SnackType.ERROR);
            }
            finally {
                this.#requesting = false;
                this.#stopLoadingAnimation();
            }
            return [];
        }
        #maybeRenderData() {
            if (this.#requesting) {
                let text = "Awaiting an answer...";
                if (this.config.loadingText) {
                    if (Array.isArray(this.config.loadingText)) {
                        text = this.config.loadingText[this.#loadingTextIndex];
                    }
                    else {
                        text = this.config.loadingText;
                    }
                }
                return html ` <div class="pending">
        <div class="spinner"></div>
        <div class="loading-text">${text}</div>
      </div>`;
            }
            const surfaces = this.#processor.getSurfaces();
            if (surfaces.size === 0) {
                return nothing;
            }
            return html `<section id="surfaces">
      ${repeat(this.#processor.getSurfaces(), ([surfaceId]) => surfaceId, ([surfaceId, surface]) => {
                return html `<a2ui-surface
              @a2uiaction=${async (evt) => {
                    const [target] = evt.composedPath();
                    if (!(target instanceof HTMLElement)) {
                        return;
                    }
                    const context = {};
                    if (evt.detail.action.context) {
                        const srcContext = evt.detail.action.context;
                        for (const item of srcContext) {
                            if (item.value.literalBoolean) {
                                context[item.key] = item.value.literalBoolean;
                            }
                            else if (item.value.literalNumber) {
                                context[item.key] = item.value.literalNumber;
                            }
                            else if (item.value.literalString) {
                                context[item.key] = item.value.literalString;
                            }
                            else if (item.value.path) {
                                const path = this.#processor.resolvePath(item.value.path, evt.detail.dataContextPath);
                                const value = this.#processor.getData(evt.detail.sourceComponent, path, surfaceId);
                                context[item.key] = value;
                            }
                        }
                    }
                    const message = {
                        userAction: {
                            name: evt.detail.action.name,
                            surfaceId,
                            sourceComponentId: target.id,
                            timestamp: new Date().toISOString(),
                            context,
                        },
                    };
                    await this.#sendAndProcessMessage(message);
                }}
              .surfaceId=${surfaceId}
              .surface=${surface}
              .processor=${this.#processor}
            ></a2-uisurface>`;
            })}
    </section>`;
        }
        async #sendAndProcessMessage(request) {
            const messages = await this.#sendMessage(request);
            console.log(messages);
            this.#lastMessages = messages;
            this.#processor.clearSurfaces();
            this.#processor.processMessages(messages);
        }
        snackbar(message, type, actions = [], persistent = false, id = globalThis.crypto.randomUUID(), replaceAll = false) {
            if (!this.#snackbar) {
                this.#pendingSnackbarMessages.push({
                    message: {
                        id,
                        message,
                        type,
                        persistent,
                        actions,
                    },
                    replaceAll,
                });
                return;
            }
            return this.#snackbar.show({
                id,
                message,
                type,
                persistent,
                actions,
            }, replaceAll);
        }
        unsnackbar(id) {
            if (!this.#snackbar) {
                return;
            }
            this.#snackbar.hide(id);
        }
        static {
            __runInitializers(_classThis, _classExtraInitializers);
        }
    };
    return A2UILayoutEditor = _classThis;
})();
export { A2UILayoutEditor };
//# sourceMappingURL=app.js.map