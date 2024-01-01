import { ClientOptions } from "openai";
import { Response } from "@whatwg-node/fetch";

type OnRapidaLog = (response: Response) => Promise<void>;
type OnRapidaFeedback = (result: Response) => Promise<void>;

interface IRapidaMeta {
  apiKey?: string;
  properties?: { [key: string]: any };
  cache?: boolean;
  retry?: boolean | { [key: string]: any };
  rateLimitPolicy?: string | { [key: string]: any };
  user?: string;
  baseUrl?: string;
  onLog?: OnRapidaLog;
  onFeedback?: OnRapidaFeedback;
}

interface IRapidaProxyClientOptions extends ClientOptions {
  rapidaMeta: Omit<IRapidaMeta, "onLog">;
}

interface IRapidaAsyncClientOptions extends ClientOptions {
  rapidaMeta: Omit<IRapidaMeta, "cache" | "retry" | "rateLimitPolicy">;
}

export {
  IRapidaMeta,
  IRapidaProxyClientOptions,
  IRapidaAsyncClientOptions,
  OnRapidaLog,
  OnRapidaFeedback,
};
