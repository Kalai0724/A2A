import { LitElement, HTMLTemplateResult } from "lit";
import { SnackbarAction, SnackbarUUID, SnackType } from "./types/types.js";
import { v0_8 } from "@a2ui/lit";
import "./ui/ui.js";
import { AppConfig } from "./configs/types.js";
declare const A2UILayoutEditor_base: typeof LitElement;
export declare class A2UILayoutEditor extends A2UILayoutEditor_base {
    #private;
    accessor theme: v0_8.Types.Theme;
    accessor config: AppConfig;
    static styles: import("lit").CSSResult[];
    connectedCallback(): void;
    render(): (symbol | import("lit-html").TemplateResult<1>)[];
    snackbar(message: string | HTMLTemplateResult, type: SnackType, actions?: SnackbarAction[], persistent?: boolean, id?: `${string}-${string}-${string}-${string}-${string}`, replaceAll?: boolean): `${string}-${string}-${string}-${string}-${string}`;
    unsnackbar(id?: SnackbarUUID): void;
}
export {};
//# sourceMappingURL=app.d.ts.map