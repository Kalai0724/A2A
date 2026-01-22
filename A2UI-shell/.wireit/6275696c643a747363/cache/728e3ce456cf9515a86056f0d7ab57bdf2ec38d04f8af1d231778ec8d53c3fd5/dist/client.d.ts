import { v0_8 } from "@a2ui/lit";
export declare class A2UIClient {
    #private;
    constructor(serverUrl?: string);
    get ready(): Promise<void>;
    send(message: v0_8.Types.A2UIClientEventMessage | string): Promise<v0_8.Types.ServerToClientMessage[]>;
}
//# sourceMappingURL=client.d.ts.map